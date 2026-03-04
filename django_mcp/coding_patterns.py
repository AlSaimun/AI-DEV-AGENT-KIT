"""
Coding patterns and templates for the ai-agents-backend project.
These patterns are served by the MCP server to provide consistent
code generation guidelines to GitHub Copilot.
"""

# ---------------------------------------------------------------------------
# IMPORT ORDER GUIDELINES
# ---------------------------------------------------------------------------

IMPORT_ORDER = """
## Import Order Convention

Always order imports in this sequence, separated by blank lines:

1. **Python standard library**
   import os
   import json
   from typing import Optional, List

2. **Django core & third-party Django packages**
   from django.db import models
   from django.db.models import Q
   from django.conf import settings
   from django.urls import path

3. **Third-party dxh packages** (dxh_libraries then dxh_common)
   from dxh_libraries.translation import gettext_lazy as _
   from dxh_libraries.rest_framework import Response, status, serializers
   from dxh_common.base.base_model import BaseModel
   from dxh_common.base.base_repository import BaseRepository, RepositoryError
   from dxh_common.base.base_service import BaseService, ServiceError
   from dxh_common.base.base_api_view import BaseApiView
   from dxh_common.base.base_serializer import BaseModelSerializer
   from dxh_common.logger import Logger
   from dxh_common.paginations import CustomPagination

4. **Local app imports** (models → repositories → services → serializers → constants/enums)
   from apps.<app>.models import MyModel
   from apps.<app>.repositories import MyRepository
   from apps.<app>.services import MyService
   from apps.<app>.api.v1.serializers import MySerializer
   from apps.<app>.constants import MyChoices
   from apps.identity.decorators import require_permissions
"""

# ---------------------------------------------------------------------------
# MODEL TEMPLATE
# ---------------------------------------------------------------------------

MODEL_TEMPLATE = '''
## Model Pattern

File location: apps/<app_name>/models/<model_name>.py

```python
# 1. Django
from django.db import models

# 2. dxh packages
from dxh_libraries.translation import gettext_lazy as _
from dxh_common.base.base_model import BaseModel


class {ModelName}(BaseModel):
    """
    {ModelName} model.
    """
    # ForeignKey example
    # parent = models.ForeignKey(
    #     "self",
    #     on_delete=models.SET_NULL,
    #     null=True,
    #     blank=True,
    #     related_name="children",
    #     verbose_name=_("Parent")
    # )

    name = models.CharField(
        max_length=200,
        unique=True,
        db_index=True,
        verbose_name=_("{ModelName} Name")
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("Description")
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Is Active")
    )

    class Meta:
        db_table = "<app_name>_{model_name_plural}"
        verbose_name = _("{ModelName}")
        verbose_name_plural = _("{ModelName}s")

    def __str__(self):
        return self.name
```

### BaseModel provides these fields automatically:
- `id` (UUID primary key)
- `created_at` (DateTimeField)
- `updated_at` (DateTimeField)
- `is_deleted` (BooleanField, default=False)
- `deleted_at` (DateTimeField, nullable)
- `deleted_by` (ForeignKey to user, nullable)
'''

# ---------------------------------------------------------------------------
# CONSTANTS / ENUMS TEMPLATE
# ---------------------------------------------------------------------------

CONSTANTS_TEMPLATE = '''
## Constants / Enums Pattern

File location: apps/<app_name>/constants.py

```python
# 1. Django
from django.db import models

# 2. dxh packages
from dxh_libraries.translation import gettext_lazy as _


class {ResourceName}Status(models.TextChoices):
    ACTIVE   = "active",   _("Active")
    INACTIVE = "inactive", _("Inactive")
    PENDING  = "pending",  _("Pending")
    ARCHIVED = "archived", _("Archived")


class {ResourceName}Type(models.TextChoices):
    TYPE_A = "type_a", _("Type A")
    TYPE_B = "type_b", _("Type B")


# Module-level scalar constants
MAX_RETRY_COUNT = 3
DEFAULT_PAGE_SIZE = 20
```

### Rules:
- Use `models.TextChoices` (not plain Enum) so values are usable directly in model fields.
- All human-readable labels must be wrapped in `_()` for translation.
- Group related choices in separate classes.
- Scalar constants live at module level (no class).
'''

# ---------------------------------------------------------------------------
# REPOSITORY TEMPLATE
# ---------------------------------------------------------------------------

REPOSITORY_TEMPLATE = '''
## Repository Pattern

File location: apps/<app_name>/repositories/<model_name>_repository.py

```python
# 1. Django
from django.db.models import Q

# 2. dxh packages
from dxh_common.base.base_repository import BaseRepository

# 3. Local
from apps.<app_name>.models import {ModelName}


class {ModelName}Repository(BaseRepository):
    def __init__(self):
        super().__init__({ModelName})

    # Add custom query methods below.
    # BaseRepository already provides:
    #   get(**filters), filter(**filters), get_all(),
    #   create(**data), get_or_create(**data),
    #   update(instance, **data), delete(instance),
    #   bulk_create(objects), bulk_update(instances, fields)

    def get_active(self):
        """Return all non-deleted active records."""
        return self.model.objects.filter(is_deleted=False, is_active=True)

    def search(self, query: str):
        """Full-text icontains search across name and description."""
        return self.model.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
```

### Exports: apps/<app_name>/repositories/__init__.py
```python
from apps.<app_name>.repositories.<model_name>_repository import {ModelName}Repository

__all__ = ["{ModelName}Repository"]
```
'''

# ---------------------------------------------------------------------------
# SERVICE TEMPLATE
# ---------------------------------------------------------------------------

SERVICE_TEMPLATE = '''
## Service Pattern

File location: apps/<app_name>/services/<model_name>_service.py

```python
# 1. Django
from django.db.models import Q

# 2. dxh packages
from dxh_common.logger import Logger
from dxh_common.base.base_repository import RepositoryError
from dxh_common.base.base_service import BaseService, ServiceError

# 3. Local
from apps.<app_name>.repositories import {ModelName}Repository

logger = Logger(__name__)


class {ModelName}Service(BaseService):
    def __init__(self):
        super().__init__({ModelName}Repository())

    # BaseService already provides:
    #   get(**filters), list(**filters), get_all(),
    #   create(**data), update(instance, **data), delete(instance),
    #   bulk_create(objects), bulk_update(instances, fields),
    #   soft_delete(instance, deleted_by=None)

    def get_{model_name}(self, id, request_user):
        """Retrieve a single {model_name} by id, with permission check."""
        try:
            if not request_user.is_superuser:
                # Non-superusers can only access their own company's data
                if str(request_user.company.id) != str(id):
                    return None

            return self.repository.get(id=id)

        except RepositoryError as e:
            raise ServiceError(f"Service error during get operation: {{e}}")

    def get_{model_name_plural}(self, request_user=None, **filters):
        """Return filtered and optionally searched queryset."""
        try:
            if request_user and not request_user.is_superuser:
                qs = self.repository.model.objects.filter(
                    company=request_user.company
                )
            else:
                qs = self.get_all()

            qs = qs.order_by(filters.get("ordering", "name"))

            if "search" in filters:
                qs = qs.filter(
                    Q(name__icontains=filters["search"])
                )

            return qs

        except RepositoryError as e:
            raise ServiceError(f"Service error during list operation: {{e}}")
```

### Exports: apps/<app_name>/services/__init__.py
```python
from apps.<app_name>.services.<model_name>_service import {ModelName}Service

__all__ = ["{ModelName}Service"]
```
'''

# ---------------------------------------------------------------------------
# SERIALIZER TEMPLATE
# ---------------------------------------------------------------------------

SERIALIZER_TEMPLATE = '''
## Serializer Pattern

File location: apps/<app_name>/api/v1/serializers/<model_name>_serializer.py

```python
# 1. Django
from django.conf import settings

# 2. dxh packages
from dxh_libraries.rest_framework import serializers
from dxh_common.base.base_serializer import BaseModelSerializer

# 3. Local
from apps.<app_name>.models import {ModelName}


class {ModelName}Serializer(BaseModelSerializer):
    """Write serializer — used for create / update."""

    class Meta:
        model = {ModelName}
        fields = [
            "id",
            "name",
            "description",
            "is_active",
        ]


class {ModelName}DetailSerializer(BaseModelSerializer):
    """Read serializer — used for retrieve / list (may expand FK fields)."""

    related_object = serializers.SerializerMethodField()

    class Meta:
        model = {ModelName}
        fields = [
            "id",
            "name",
            "description",
            "is_active",
            "related_object",
            "created_at",
            "updated_at",
        ]

    def get_related_object(self, obj):
        if obj.related:
            return {"id": obj.related.id, "name": obj.related.name}
        return None
```

### Exports: apps/<app_name>/api/v1/serializers/__init__.py
```python
from apps.<app_name>.api.v1.serializers.<model_name>_serializer import (
    {ModelName}Serializer,
    {ModelName}DetailSerializer,
)
```
'''

# ---------------------------------------------------------------------------
# VIEW TEMPLATE
# ---------------------------------------------------------------------------

VIEW_TEMPLATE = '''
## View Pattern (API View)

File location: apps/<app_name>/api/v1/views/<model_name>_view.py

```python
# 1. dxh packages
from dxh_libraries.translation import gettext_lazy as _
from dxh_libraries.rest_framework import Response, status, MultiPartParser, FormParser
from dxh_common.logger import Logger
from dxh_common.base.base_api_view import BaseApiView
from dxh_common.paginations import CustomPagination

# 2. Local
from apps.<app_name>.services import {ModelName}Service
from apps.<app_name>.api.v1.serializers import {ModelName}Serializer, {ModelName}DetailSerializer
from apps.identity.decorators import require_permissions

logger = Logger(__name__)


class {ModelName}APIView(BaseApiView):
    parser_classes = (MultiPartParser, FormParser)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.{model_name}_service = {ModelName}Service()
        self.pagination_class = CustomPagination()

    def get(self, request, id=None):
        try:
            user = request.user

            if id:
                instance = self.{model_name}_service.get_{model_name}(id, user)
                if not instance:
                    return Response(
                        {{"message": _("{ModelName} not found")}},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                serializer = {ModelName}DetailSerializer(instance)
                return Response(
                    {{"message": _("{ModelName} retrieved successfully"), "data": serializer.data}},
                    status=status.HTTP_200_OK,
                )

            query_params = {{k: v for k, v in request.query_params.items() if v}}
            queryset = self.{model_name}_service.get_{model_name_plural}(request_user=user, **query_params)
            paginated_data = self.pagination_class.paginate_queryset(queryset, request)
            serializer = {ModelName}DetailSerializer(paginated_data, many=True)
            paginated_response = self.pagination_class.get_paginated_response(serializer.data)

            return Response(
                {{
                    "message": _("{ModelName}s retrieved successfully"),
                    "data": paginated_response.data["records"],
                    "pagination": paginated_response.data["pagination"],
                }},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            logger.error({{"event": "{ModelName}APIView:get", "message": "Unexpected error", "error": str(e)}})
            raise e

    def post(self, request):
        try:
            serializer = {ModelName}Serializer(data=request.data)
            if not serializer.is_valid():
                return Response(
                    {{"message": _("Invalid data"), "errors": serializer.errors}},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            instance = self.{model_name}_service.create(**serializer.validated_data)
            return Response(
                {{"message": _("{ModelName} created successfully"), "data": {ModelName}Serializer(instance).data}},
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            logger.error({{"event": "{ModelName}APIView:post", "message": "Unexpected error", "error": str(e)}})
            raise e

    def put(self, request, id):
        try:
            instance = self.{model_name}_service.get(id=id)
            if not instance:
                return Response(
                    {{"message": _("{ModelName} not found")}},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            serializer = {ModelName}Serializer(instance, data=request.data, partial=True)
            if not serializer.is_valid():
                return Response(
                    {{"message": _("Invalid data"), "errors": serializer.errors}},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            updated = self.{model_name}_service.update(instance, **serializer.validated_data)
            return Response(
                {{"message": _("{ModelName} updated successfully"), "data": {ModelName}Serializer(updated).data}},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            logger.error({{"event": "{ModelName}APIView:put", "message": "Unexpected error", "error": str(e), "id": id}})
            raise e

    def delete(self, request, id):
        try:
            instance = self.{model_name}_service.get(id=id)
            if not instance:
                return Response(
                    {{"message": _("{ModelName} not found or already deleted")}},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            self.{model_name}_service.delete(instance)
            return Response(
                {{"message": _("{ModelName} deleted successfully")}},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            logger.error({{"event": "{ModelName}APIView:delete", "message": "Unexpected error", "error": str(e), "id": id}})
            raise e
```

### Exports: apps/<app_name>/api/v1/views/__init__.py
```python
from apps.<app_name>.api.v1.views.<model_name>_view import {ModelName}APIView
```
'''

# ---------------------------------------------------------------------------
# URL TEMPLATE
# ---------------------------------------------------------------------------

URL_TEMPLATE = '''
## URL Pattern

### App-level: apps/<app_name>/urls.py
```python
# 1. Django
from django.urls import path, include

app_name = "<app_name>"
api_url = "apps.<app_name>.api.v1.urls"

urlpatterns = [
    path("v1/", include(api_url)),
]
```

### Version-level: apps/<app_name>/api/v1/urls.py
```python
# 1. Django
from django.urls import path

# 2. Local
from apps.<app_name>.api.v1 import views

urlpatterns = [
    path("{model_name_plural}/<uuid:id>/", views.{ModelName}APIView.as_view(), name="{model_name_plural}-detail"),
    path("{model_name_plural}/",           views.{ModelName}APIView.as_view(), name="{model_name_plural}-list-create"),
]
```

### Config-level: config/urls.py (add one line)
```python
path("api/<app_name>/", include("apps.<app_name>.urls", namespace="<app_name>")),
```

### Rules:
- Use `uuid:id` for UUID primary keys (BaseModel default).
- Detail endpoint always comes before list endpoint so Django matches correctly.
- Namespace must match `app_name` declared in the app-level urls.py.
'''

# ---------------------------------------------------------------------------
# DIRECTORY STRUCTURE
# ---------------------------------------------------------------------------

DIRECTORY_STRUCTURE = '''
## App Directory Structure

```
apps/<app_name>/
├── __init__.py
├── admin.py
├── apps.py
├── constants.py          ← TextChoices enums + scalar constants
├── enums.py              ← (optional) additional enums
├── urls.py               ← includes api/v1/urls
├── models/
│   ├── __init__.py       ← exports all models
│   └── <model>.py
├── repositories/
│   ├── __init__.py       ← exports all repositories
│   └── <model>_repository.py
├── services/
│   ├── __init__.py       ← exports all services
│   └── <model>_service.py
├── api/
│   └── v1/
│       ├── __init__.py
│       ├── urls.py
│       ├── views/
│       │   ├── __init__.py   ← exports all views
│       │   └── <model>_view.py
│       └── serializers/
│           ├── __init__.py   ← exports all serializers
│           └── <model>_serializer.py
├── migrations/
├── tests/
├── fixtures/
└── tasks/
```
'''

# ---------------------------------------------------------------------------
# FULL EXAMPLE (Company resource)
# ---------------------------------------------------------------------------

FULL_EXAMPLE = '''
## Full Example – Company Resource

### Model (apps/core/models/company.py)
```python
from django.db import models
from dxh_libraries.translation import gettext_lazy as _
from dxh_common.base.base_model import BaseModel


class Company(BaseModel):
    parent = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="child_companies", verbose_name=_("Parent Company")
    )
    name    = models.CharField(max_length=200, unique=True, db_index=True, verbose_name=_("Company Name"))
    email   = models.EmailField(unique=True, verbose_name=_("Company Email"))
    country = models.ForeignKey("core.Country", on_delete=models.SET_NULL, null=True, blank=True,
                                related_name="companies", verbose_name=_("Country"))
    is_default = models.BooleanField(default=False, verbose_name=_("Is Default"))

    class Meta:
        db_table = "core_companies"
        verbose_name = _("Company")
        verbose_name_plural = _("Companies")

    def __str__(self):
        return self.name
```

### Repository (apps/core/repositories/company_repository.py)
```python
from dxh_common.base.base_repository import BaseRepository
from apps.core.models import Company


class CompanyRepository(BaseRepository):
    def __init__(self):
        super().__init__(Company)
```

### Service (apps/core/services/company_service.py)
```python
from django.db.models import Q
from dxh_common.logger import Logger
from dxh_common.base.base_repository import RepositoryError
from dxh_common.base.base_service import BaseService, ServiceError
from apps.core.repositories import CompanyRepository

logger = Logger(__name__)


class CompanyService(BaseService):
    def __init__(self):
        super().__init__(CompanyRepository())

    def get_default_company(self):
        try:
            return self.get(is_default=True)
        except RepositoryError as e:
            raise ServiceError(f"Service error during get operation: {e}")

    def get_companies(self, request_user=None, **filters):
        try:
            if request_user and not request_user.is_superuser:
                qs = self.repository.model.objects.filter(id=request_user.company.id)
            else:
                qs = self.get_all()
            qs = qs.order_by(filters.get("ordering", "name"))
            if "search" in filters:
                qs = qs.filter(
                    Q(name__icontains=filters["search"]) |
                    Q(email__icontains=filters["search"])
                )
            return qs
        except RepositoryError as e:
            raise ServiceError(f"Service error during list operation: {e}")
```

### View (apps/core/api/v1/views/company_view.py)
```python
from dxh_libraries.translation import gettext_lazy as _
from dxh_libraries.rest_framework import Response, status, MultiPartParser, FormParser
from dxh_common.logger import Logger
from dxh_common.base.base_api_view import BaseApiView
from dxh_common.paginations import CustomPagination

from apps.core.services.company_service import CompanyService
from apps.core.api.v1.serializers import CompanySerializer, CompanyDetailsSerializer
from apps.identity.decorators import require_permissions

logger = Logger(__name__)


class CompanyAPIView(BaseApiView):
    parser_classes = (MultiPartParser, FormParser)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.company_service = CompanyService()
        self.pagination_class = CustomPagination()

    def get(self, request, id=None):
        try:
            user = request.user
            if id:
                company = self.company_service.get_company(id, user)
                if not company:
                    return Response({"message": _("Company not found")}, status=status.HTTP_400_BAD_REQUEST)
                return Response({"message": _("Company retrieved successfully"),
                                 "data": CompanyDetailsSerializer(company).data}, status=status.HTTP_200_OK)

            query_params = {k: v for k, v in request.query_params.items() if v}
            companies = self.company_service.get_companies(request_user=user, **query_params)
            paginated_data = self.pagination_class.paginate_queryset(companies, request)
            paginated_response = self.pagination_class.get_paginated_response(
                CompanyDetailsSerializer(paginated_data, many=True).data
            )
            return Response({"message": _("Companies retrieved successfully"),
                             "data": paginated_response.data["records"],
                             "pagination": paginated_response.data["pagination"]}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error({"event": "CompanyAPIView:get", "message": "Unexpected error", "error": str(e)})
            raise e

    def post(self, request):
        try:
            serializer = CompanySerializer(data=request.data)
            if not serializer.is_valid():
                return Response({"message": _("Invalid data"), "errors": serializer.errors},
                                status=status.HTTP_400_BAD_REQUEST)
            company = self.company_service.create(**serializer.validated_data)
            return Response({"message": _("Company created successfully"),
                             "data": CompanySerializer(company).data}, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error({"event": "CompanyAPIView:post", "message": "Unexpected error", "error": str(e)})
            raise e

    def put(self, request, id):
        try:
            company = self.company_service.get(id=id)
            if not company:
                return Response({"message": _("Company not found")}, status=status.HTTP_400_BAD_REQUEST)
            serializer = CompanySerializer(company, data=request.data, partial=True)
            if not serializer.is_valid():
                return Response({"message": _("Invalid data"), "errors": serializer.errors},
                                status=status.HTTP_400_BAD_REQUEST)
            updated = self.company_service.update(company, **serializer.validated_data)
            return Response({"message": _("Company updated successfully"),
                             "data": CompanySerializer(updated).data}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error({"event": "CompanyAPIView:put", "message": "Unexpected error", "error": str(e), "id": id})
            raise e

    def delete(self, request, id):
        try:
            company = self.company_service.get(id=id)
            if not company:
                return Response({"message": _("Company not found or already deleted")},
                                status=status.HTTP_400_BAD_REQUEST)
            self.company_service.delete(company)
            return Response({"message": _("Company deleted successfully")}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error({"event": "CompanyAPIView:delete", "message": "Unexpected error", "error": str(e), "id": id})
            raise e
```

### URLs (apps/core/api/v1/urls.py)
```python
from django.urls import path
from apps.core.api.v1 import views

urlpatterns = [
    path("companies/<uuid:id>/", views.CompanyAPIView.as_view(), name="companies-detail"),
    path("companies/",           views.CompanyAPIView.as_view(), name="companies-list-create"),
]
```
'''

# ---------------------------------------------------------------------------
# CODING RULES SUMMARY
# ---------------------------------------------------------------------------

CODING_RULES = """
## Coding Rules Summary

### Response Shape
Every API response must have a `message` key. Successful responses add `data`.
Paginated list responses add `pagination` alongside `data`.

```json
// single object
{"message": "...", "data": {...}}

// list (paginated)
{"message": "...", "data": [...], "pagination": {...}}

// error
{"message": "...", "errors": {...}}
```

### Error Handling
- Views catch `Exception` generically, log with `logger.error(...)`, then `raise e`.
- Services catch `RepositoryError` and re-raise as `ServiceError`.
- Repositories catch `DatabaseError` and re-raise as `RepositoryError`.

### Logging
Use `dxh_common.logger.Logger` (not Python's built-in logging):
```python
logger = Logger(__name__)
logger.error({"event": "ClassName:method", "message": "...", "error": str(e)})
```

### Soft Delete
Call `service.soft_delete(instance, deleted_by=request.user)` instead of `service.delete(instance)`
when records should be retained in DB with `is_deleted=True`.

### Pagination
Always use `dxh_common.paginations.CustomPagination` for list endpoints.
Never return raw querysets; always paginate.

### Permissions
Decorate view methods with `@require_permissions("app.permission_codename")` from
`apps.identity.decorators` when authorization is required.

### Model Primary Keys
BaseModel uses UUID as primary key. Use `<uuid:id>` in URL patterns, not `<int:id>`.
"""

# ---------------------------------------------------------------------------
# EXPORTED MAPPING for easy lookup by the MCP server
# ---------------------------------------------------------------------------

PATTERNS = {
    "import_order":    IMPORT_ORDER,
    "model":           MODEL_TEMPLATE,
    "constants":       CONSTANTS_TEMPLATE,
    "repository":      REPOSITORY_TEMPLATE,
    "service":         SERVICE_TEMPLATE,
    "serializer":      SERIALIZER_TEMPLATE,
    "view":            VIEW_TEMPLATE,
    "urls":            URL_TEMPLATE,
    "directory":       DIRECTORY_STRUCTURE,
    "full_example":    FULL_EXAMPLE,
    "coding_rules":    CODING_RULES,
}

ALL_PATTERNS = "\n\n".join(
    [
        "# AI-Agents Backend — Coding Structure Guide",
        IMPORT_ORDER,
        DIRECTORY_STRUCTURE,
        CODING_RULES,
        MODEL_TEMPLATE,
        CONSTANTS_TEMPLATE,
        REPOSITORY_TEMPLATE,
        SERVICE_TEMPLATE,
        SERIALIZER_TEMPLATE,
        VIEW_TEMPLATE,
        URL_TEMPLATE,
        FULL_EXAMPLE,
    ]
)
