"""
Project description vector store.

Indexes docs from  <PROJECT_ROOT>/docs/  into a per-project ChromaDB collection
so Copilot can semantically search the project description, architecture, and
requirements docs.

Rules:
  - Scans PROJECT_ROOT/docs/  for .pdf and .md files.
  - Each file is split into overlapping chunks (chunk_size / overlap configurable).
  - A SHA-256 fingerprint of all doc bytes is stored; the collection is rebuilt
    only when the files change.  No manual rebuild step needed.
  - Storage: PROJECT_ROOT/.mcp_chroma/   (per-project, gitignored)
  - Collection: project_docs
  - MCP server can live anywhere (e.g. ~/mcp/) — isolation is via PROJECT_ROOT env var.

Drop a PDF or .md file into docs/  →  restart the server  →  search_project_docs picks it up.
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path

import chromadb
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction

# ── Defaults ──────────────────────────────────────────────────────────────────

_COLLECTION   = "project_docs"

# ── Chunking config ───────────────────────────────────────────────────────────

CHUNK_SIZE    = 800   # characters per chunk
CHUNK_OVERLAP = 150   # overlap between consecutive chunks


def _resolve_project_root(project_root: str | Path | None) -> Path:
    """
    Priority order:
      1. Explicit argument passed to init_store()
      2. PROJECT_ROOT environment variable  (set by each project's mcp.json)
      3. Fallback: parent of this file's directory  (mcp/../  == project root)
    """
    if project_root is not None:
        return Path(project_root).resolve()
    env = os.environ.get("PROJECT_ROOT")
    if env:
        return Path(env).resolve()
    return Path(__file__).parent.parent.resolve()


# ── Doc loading (PDF + Markdown) ─────────────────────────────────────────────

def _load_docs(docs_dir: Path) -> list[dict]:
    """
    Return a list of {filename, page, text} dicts for every page/section of
    every .pdf and .md file found in docs_dir.
    """
    pages: list[dict] = []

    # ── PDFs ──
    try:
        from pypdf import PdfReader
        for pdf_path in sorted(docs_dir.rglob("*.pdf")):
            reader = PdfReader(str(pdf_path))
            for page_num, page in enumerate(reader.pages, start=1):
                text = (page.extract_text() or "").strip()
                if text:
                    pages.append({
                        "filename": pdf_path.relative_to(docs_dir).as_posix(),
                        "page":     page_num,
                        "text":     text,
                    })
    except ImportError:
        pass  # pypdf not installed — skip PDFs silently

    # ── Markdown ──
    for md_path in sorted(docs_dir.rglob("*.md")):
        text = md_path.read_text(encoding="utf-8", errors="ignore").strip()
        if text:
            pages.append({
                "filename": md_path.relative_to(docs_dir).as_posix(),
                "page":     1,
                "text":     text,
            })

    return pages


def _chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Split text into overlapping chunks."""
    chunks, start = [], 0
    while start < len(text):
        end = start + size
        chunks.append(text[start:end])
        start += size - overlap
    return chunks


def _fingerprint(docs_dir: Path) -> str:
    """SHA-256 of all .pdf and .md file bytes — changes when any doc is added/modified."""
    h = hashlib.sha256()
    for p in sorted(docs_dir.rglob("*.pdf")) + sorted(docs_dir.rglob("*.md")):
        h.update(p.read_bytes())
    return h.hexdigest()


# ── Vector store ──────────────────────────────────────────────────────────────

class ProjectDocVectorStore:
    """
    Persistent ChromaDB collection backed by docs in <PROJECT_ROOT>/docs/.

    The MCP server can live anywhere (~/mcp/, a shared location, etc.).
    Isolation is achieved via the PROJECT_ROOT env var: every project gets
    its own  <PROJECT_ROOT>/.mcp_chroma/  directory as its vector DB.

    Public interface:
        search(query, n_results) → list[dict]
        doc_count() → int
        indexed_files() → list[str]
        project_root → Path
    """

    def __init__(self, project_root: str | Path | None = None) -> None:
        root           = _resolve_project_root(project_root)
        self.project_root = root
        self._docs_dir = root / "docs"          # project's existing docs/ folder
        chroma_path    = root / ".mcp_chroma"   # per-project, gitignored

        self._docs_dir.mkdir(parents=True, exist_ok=True)
        self._client = chromadb.PersistentClient(path=str(chroma_path))
        self._ef     = DefaultEmbeddingFunction()
        self._col    = self._client.get_or_create_collection(
            name=_COLLECTION,
            embedding_function=self._ef,          # type: ignore[arg-type]
            metadata={"hnsw:space": "cosine"},
        )
        self._ensure_seeded()

    # ── seeding ───────────────────────────────────────────────────────────

    def _ensure_seeded(self) -> None:
        fp = _fingerprint(self._docs_dir)
        if not fp:
            return  # no PDFs yet — nothing to seed

        sentinel = self._col.get(ids=["__fingerprint__"])
        if sentinel["ids"] and sentinel["metadatas"][0].get("hash") == fp:
            return  # already up-to-date

        self._seed(fp)

    def _seed(self, fingerprint: str) -> None:
        # Clear previous data
        existing = self._col.get()
        if existing["ids"]:
            self._col.delete(ids=existing["ids"])

        pages = _load_docs(self._docs_dir)
        if not pages:
            return

        print(f"[vector_store] Seeding {len(pages)} page(s) from {len({p['filename'] for p in pages})} file(s) "
              f"[{self._docs_dir}]...", flush=True)

        ids, documents, metadatas = [], [], []

        for page_info in pages:
            chunks = _chunk_text(page_info["text"])
            for chunk_idx, chunk_text in enumerate(chunks):
                chunk_id = f"{page_info['filename']}::p{page_info['page']}::c{chunk_idx}"
                ids.append(chunk_id)
                documents.append(chunk_text)
                metadatas.append({
                    "filename": page_info["filename"],
                    "page":     page_info["page"],
                    "chunk":    chunk_idx,
                })

        # Add sentinel last
        ids.append("__fingerprint__")
        documents.append("sentinel")
        metadatas.append({"hash": fingerprint})

        # Upsert in batches of 100 (ChromaDB limit)
        batch = 100
        for i in range(0, len(ids), batch):
            self._col.upsert(
                ids=ids[i:i+batch],
                documents=documents[i:i+batch],
                metadatas=metadatas[i:i+batch],
            )

    # ── search ────────────────────────────────────────────────────────────

    def search(self, query: str, n_results: int = 4) -> list[dict]:
        """
        Return top-n most relevant chunks from the project PDFs.

        Result dict keys: filename, page, chunk, distance, content
        """
        total = self._col.count() - 1  # exclude sentinel
        if total <= 0:
            return []

        results = self._col.query(
            query_texts=[query],
            n_results=min(n_results, total),
            where={"filename": {"$ne": "sentinel"}} if total > 0 else None,
        )

        output = []
        for i, doc_id in enumerate(results["ids"][0]):
            if doc_id == "__fingerprint__":
                continue
            meta = results["metadatas"][0][i]
            output.append({
                "filename": meta.get("filename", ""),
                "page":     meta.get("page", ""),
                "chunk":    meta.get("chunk", ""),
                "distance": round(results["distances"][0][i], 4),
                "content":  results["documents"][0][i],
            })
        return output

    def doc_count(self) -> int:
        """Number of indexed chunks (excluding sentinel)."""
        return max(0, self._col.count() - 1)

    def indexed_files(self) -> list[str]:
        """List of unique PDF filenames currently indexed."""
        if self._col.count() <= 1:
            return []
        all_meta = self._col.get(where={"filename": {"$ne": "sentinel"}})["metadatas"]
        return sorted({m["filename"] for m in all_meta if m.get("filename")})


# ── Singleton ─────────────────────────────────────────────────────────────────

_store: ProjectDocVectorStore | None = None


def init_store(project_root: str | Path | None = None) -> ProjectDocVectorStore:
    """
    Create the singleton for a specific project root.
    Call this once at server startup before any tool calls.
    Falls back to PROJECT_ROOT env var, then to the parent of mcp/.
    """
    global _store
    if _store is None:
        _store = ProjectDocVectorStore(project_root=project_root)
    return _store


def get_store() -> ProjectDocVectorStore:
    """Return the already-initialised singleton. Call init_store() first."""
    global _store
    if _store is None:
        _store = ProjectDocVectorStore()  # fallback: uses env var / __file__ heuristic
    return _store
