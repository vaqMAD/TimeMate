# drf_spectacular imports
from drf_spectacular.extensions import OpenApiFilterExtension
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiTypes
# Internal imports
from .serializers import (
    TimeEntryCreateSerializer,
    TimeEntryListSerializer,
    TimeEntryDetailSerializer,
    TimeEntryUpdateSerializer,
    TaskWithTimeEntriesSerializer,
    GroupedTimeEntriesSerializerForSchema
)

# Filter extension for TimeEntryFilter
class TimeEntryFilterExtension(OpenApiFilterExtension):
    target_class = 'TimeMate.time_entries.filters.TimeEntryFilter'
    match_subclasses = True

# Parameters for TimeEntry filtering and ordering
TIME_ENTRY_FILTER_PARAMS = [
    OpenApiParameter(
        name="start_time_after",
        description="Include entries with start_time on or after this ISO8601 timestamp",
        required=False,
        type=OpenApiTypes.DATETIME,
    ),
    OpenApiParameter(
        name="start_time_before",
        description="Include entries with start_time on or before this ISO8601 timestamp",
        required=False,
        type=OpenApiTypes.DATETIME,
    ),
    OpenApiParameter(
        name="end_time_after",
        description="Include entries with end_time on or after this ISO8601 timestamp",
        required=False,
        type=OpenApiTypes.DATETIME,
    ),
    OpenApiParameter(
        name="end_time_before",
        description="Include entries with end_time on or before this ISO8601 timestamp",
        required=False,
        type=OpenApiTypes.DATETIME,
    ),
    OpenApiParameter(
        name="task",
        description="Filter by task name (case-insensitive substring)",
        required=False,
        type=OpenApiTypes.STR,
    ),
]

TIME_ENTRY_ORDERING_PARAM = OpenApiParameter(
    name="ordering",
    description=(
        "Comma-separated fields to sort by: `start_time`, `-start_time`, `end_time`, `-end_time`,"
        " `task__name`, `-task__name`, `duration`, `-duration`"
    ),
    required=False,
    type=OpenApiTypes.STR,
)

# Schemas
TIME_ENTRY_LIST_CREATE_SCHEMA = extend_schema_view(
    get=extend_schema(
        summary="List all time entries",
        description=(
            "Returns a paginated list of TimeEntry objects belonging to the current user.\n"
            "Supports filtering by start/end times and task name."
        ),
        parameters=TIME_ENTRY_FILTER_PARAMS + [TIME_ENTRY_ORDERING_PARAM],
        responses={200: TimeEntryListSerializer(many=True)},
    ),
    post=extend_schema(
        summary="Create a new time entry",
        description=(
            "Creates a new TimeEntry for the current user.\n"
            "**Request body:** `task` (ID), `start_time`, `end_time`, optional `notes`."
        ),
        request=TimeEntryCreateSerializer,
        responses={201: TimeEntryCreateSerializer},
    ),
)

TIME_ENTRY_DETAIL_SCHEMA = extend_schema_view(
    get=extend_schema(
        summary="Retrieve a time entry",
        description="Fetch full details of a single TimeEntry by ID.",
        responses={200: TimeEntryDetailSerializer},
    ),
    put=extend_schema(
        summary="Replace a time entry",
        description=(
            "Full update of all mutable fields (`task`, `start_time`, `end_time`, `notes`)."
        ),
        request=TimeEntryUpdateSerializer,
        responses={200: TimeEntryDetailSerializer},
    ),
    patch=extend_schema(
        summary="Partial update a time entry",
        description="Modify one or more fields of the TimeEntry. Only changed fields are required.",
        request=TimeEntryUpdateSerializer,
        responses={200: TimeEntryDetailSerializer},
    ),
    delete=extend_schema(
        summary="Delete a time entry",
        description="Permanently remove the TimeEntry. Returns HTTP 204 on success.",
    ),
)

TASK_WITH_ENTRIES_SCHEMA = extend_schema(
    summary="List Tasks with their TimeEntries",
    description=(
        "Returns each Task owned by the user, with a nested `entries` list of all its TimeEntries."
    ),
    responses={200: TaskWithTimeEntriesSerializer(many=True)},
)

TIME_ENTRY_BY_DATE_SCHEMA = extend_schema(
    summary="List TimeEntries grouped by day",
    description=(
        "Returns TimeEntries owned by the user, annotated with `day` (YYYY-MM-DD) and grouped in the response."
    ),
    parameters=TIME_ENTRY_FILTER_PARAMS + [TIME_ENTRY_ORDERING_PARAM],
    responses={200: GroupedTimeEntriesSerializerForSchema(many=True)},
)
