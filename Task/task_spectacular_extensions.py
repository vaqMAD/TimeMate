# drf_spectacular imports
from drf_spectacular.extensions import OpenApiFilterExtension
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiTypes
# Internal imports
from .serializers import (
    TaskCreateSerializer,
    TaskDetailSerializer,
    TaskListSerializer,
    TaskUpdateSerializer,
)


class TaskFilterExtension(OpenApiFilterExtension):
    target_class = 'Task.filters.TaskFilter'
    match_subclasses = True


TASK_FILTER_PARAMS = [
    OpenApiParameter(
        name="name",
        description="Filter by task name (case-insensitive substring)",
        required=False,
        type=OpenApiTypes.STR,
    ),
    OpenApiParameter(
        name="created_at_after",
        description="Tasks created on or after this ISO8601 timestamp",
        required=False,
        type=OpenApiTypes.DATETIME,
    ),
    OpenApiParameter(
        name="created_at_before",
        description="Tasks created on or before this ISO8601 timestamp",
        required=False,
        type=OpenApiTypes.DATETIME,
    ),
]

TASK_ORDERING_PARAM = OpenApiParameter(
    name="ordering",
    description=(
        "Comma-separated fields to sort by: `created_at`, `-created_at`, `name`, `-name`"
    ),
    required=False,
    type=OpenApiTypes.STR,
)

TASK_DETAIL_SCHEMA = extend_schema_view(
    get=extend_schema(
        summary="Retrieve a Task",
        description=(
            "Fetch details of the Task by ID.\n"
        ),
        responses={200: TaskDetailSerializer},
    ),
    put=extend_schema(
        summary="Replace a Task",
        description=(
            "Full update of `name` and `description`.\n"
        ),
        responses={200: TaskUpdateSerializer},
    ),
    patch=extend_schema(
        summary="Partial update a Task",
        description=(
            "Modify one or more fields (`name`/`description`).\n"
            "**Response**: updated Task object."
        ),
        responses={200: TaskUpdateSerializer},
    ),
    delete=extend_schema(
        summary="Delete a Task",
        description="Remove the Task permanently. Returns HTTP 204."
    ),
)
TASK_LIST_CREATE_SCHEMA = extend_schema_view(
    get=extend_schema(
        summary="List all Tasks",
        description=(
            "Paginated list of Tasks owned by current user.\n"
            "**Filters**: name, created_at range.\n"
            "**Ordering**: created_at, name."
        ),
        parameters=TASK_FILTER_PARAMS + [TASK_ORDERING_PARAM],
        responses={200: TaskListSerializer},
    ),
    post=extend_schema(
        summary="Create a new Task",
        description=(
            "Create Task with `name` and `description`.\n"
            "**Response**: newly created Task."
        ),
        request=TaskCreateSerializer,
        responses={201: TaskCreateSerializer},
    ),
)
