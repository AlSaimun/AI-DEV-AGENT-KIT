# Django Project — Coding Rules

This file is read automatically by your AI assistant every time you work in this project.
Every code suggestion, edit, and review **must** follow these conventions.

---

## Architecture: 4-Layer Service Pattern

All features follow a strict 4-layer separation. Never skip a layer or call across layers.

```
HTTP Request → View → Service → Repository → Database
```

| Layer | File location | Responsibility | Forbidden |
|-------|---------------|----------------|-----------|
| **Model** | `apps/<app>/models/<name>.py` | Schema + Meta only | Business logic, ORM queries |
| **Repository** | `apps/<app>/repositories/<name>_repository.py` | ORM queries only | Business logic |
| **Service** | `apps/<app>/services/<name>_service.py` | Business logic + orchestration | `Model.objects` calls |
| **View** | `apps/<app>/api/v1/views/<name>_view.py` | HTTP in/out only | `Model.objects`, business logic |

---

## Base Classes — Always Use These

| Layer | Base class | Package |
|-------|-----------|---------|
| Model | `BaseModel` | `dxh_common.base.base_model` |
| Repository | `BaseRepository` | `dxh_common.base.base_repository` |
| Service | `BaseService` | `dxh_common.base.base_service` |
| View | `BaseApiView` | `dxh_common.base.base_api_view` |

❌ Never inherit from `models.Model`, `APIView`, or `ViewSet` directly.

---

## Import Order (4 Groups, Strictly Enforced)

Always use this exact order, with a blank line between each group:

```python
# Group 1 — Standard library
import os
import uuid

# Group 2 — Django / DRF
from django.db import models
from rest_framework import status

# Group 3 — dxh packages (internal shared library)
from dxh_common.base.base_model import BaseModel
from dxh_libraries.translation import gettext_lazy as _

# Group 4 — Local app imports
from apps.core.models import Company
```

❌ Never mix groups. Never place local imports before dxh packages.

---

## Model Rules

```python
from django.db import models
from dxh_common.base.base_model import BaseModel
from dxh_libraries.translation import gettext_lazy as _

class Invoice(BaseModel):
    number = models.CharField(max_length=50, verbose_name=_("Number"))
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Amount"))

    class Meta:
        db_table = "billing_invoices"        # plural snake_case: appname_modelnames
        verbose_name = _("Invoice")
        verbose_name_plural = _("Invoices")

    def __str__(self):
        return self.number
```

Rules:
- Always inherit from `BaseModel`
- Always set `db_table` → `"appname_modelnames"` (plural, snake_case)
- Always set `verbose_name` and `verbose_name_plural` wrapped in `_("...")`
- Always implement `__str__`
- Raw strings for labels: ❌ `"Name"` → ✅ `_("Name")`

---

## Repository Rules

```python
from dxh_common.base.base_repository import BaseRepository
from apps.billing.models import Invoice

class InvoiceRepository(BaseRepository):
    def __init__(self):
        super().__init__(Invoice)
```

Rules:
- Only place allowed to use `Model.objects` directly
- No business logic — data access only
- Always inherit from `BaseRepository`

---

## Service Rules

```python
from dxh_common.logger import Logger
from dxh_common.base.base_repository import RepositoryError
from dxh_common.base.base_service import BaseService, ServiceError
from apps.billing.repositories import InvoiceRepository

logger = Logger(__name__)

class InvoiceService(BaseService):
    def __init__(self):
        super().__init__(InvoiceRepository())

    def get_invoices(self, **filters):
        try:
            items = self.get_all().order_by(filters.get("ordering", "-created_at"))
            if "status" in filters:
                items = items.filter(status=filters["status"])
            return items
        except RepositoryError as e:
            logger.error({"event": "InvoiceService:get_invoices", "error": str(e)})
            raise ServiceError(f"Failed to get invoices: {e}")
```

Rules:
- Always inherit from `BaseService`
- Constructor: `super().__init__(MyModelRepository())`
- Use `self.get(...)`, `self.get_all()`, `self.create(...)`, `self.update(...)`, `self.delete(...)` — **never** `Model.objects`
- Always wrap every method: `try/except RepositoryError as e: raise ServiceError(...)`
- Module-level logger: `logger = Logger(__name__)`
- Logger format: `logger.error({"event": "ClassName:method", "error": str(e)})`

---

## View Rules

```python
from rest_framework import status
from dxh_common.base.base_api_view import BaseApiView
from apps.billing.services import InvoiceService

class InvoiceView(BaseApiView):
    def get(self, request):
        try:
            service = InvoiceService()
            invoices = service.get_invoices(**request.query_params)
            return self.paginated_response(invoices)
        except Exception as e:
            return self.error_response(str(e), status.HTTP_400_BAD_REQUEST)
```

Rules:
- Always inherit from `BaseApiView`
- Never call `Model.objects` or ORM directly
- Always use named constants: `status.HTTP_200_OK` — never raw integers (`200`)

**Response shapes:**
```python
# List
{"count": n, "results": [...]}

# Detail
{"data": {...}}

# Error
{"error": "message", "code": "ERROR_CODE"}
```

❌ Wrong:
```python
return Response(data, 200)                    # raw integer
return Response({"success": True})            # wrong shape
agents = Agent.objects.filter(company=co)     # ORM in view
```

---

## Queryset Optimization Rules

| ❌ Bad | ✅ Good |
|--------|---------|
| `len(queryset)` | `.count()` |
| `if queryset:` | `.exists()` |
| No joins, N+1 queries | `select_related("fk_field")` for FK |
| No prefetch, N+1 on M2M | `prefetch_related("m2m_field")` |
| `list(qs)` just to check | `.exists()` |

---

## Serializer Rules

```python
class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = ["id", "number", "amount", "status"]   # explicit — never "__all__"
        read_only_fields = ["id"]
```

---

## Constants — Use Django Choices (Never Raw Integers)

```python
from django.db import models
from dxh_libraries.translation import gettext_lazy as _

class InvoiceStatus(models.IntegerChoices):
    DRAFT = 1, _("Draft")
    SENT  = 2, _("Sent")
    PAID  = 3, _("Paid")
```

Define in `apps/<app>/constants/<name>_constants.py`.

---

## File Locations

| Layer | Path |
|-------|------|
| Model | `apps/<app>/models/<name>.py` |
| Repository | `apps/<app>/repositories/<name>_repository.py` |
| Service | `apps/<app>/services/<name>_service.py` |
| Serializer | `apps/<app>/api/v1/serializers/<name>_serializer.py` |
| View | `apps/<app>/api/v1/views/<name>_view.py` |
| URLs | `apps/<app>/api/v1/urls.py` |
| Constants | `apps/<app>/constants/<name>_constants.py` |

Always export new classes from the app's `__init__.py`.

---

## Logger — Dict Format Only

```python
# ✅ Correct
logger.error({"event": "ClassName:method_name", "error": str(e)})
logger.info({"event": "ClassName:method_name", "id": instance.id})

# ❌ Wrong
logger.error(f"Error in get: {e}")
logger.error("Something failed")
logging.error(str(e))
```
