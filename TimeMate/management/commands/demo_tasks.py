DEMO_TASKS = [
    {
        'name': 'Define Project Requirements',
        'description': 'Gather and document functional and non-functional requirements for the time-tracking API.'
    },
    {
        'name': 'Design Database Schema',
        'description': 'Model tables for users, tasks, time entries and their relations in PostgreSQL.'
    },
    {
        'name': 'Implement User Authentication',
        'description': 'Set up registration, login endpoints and token-based auth using DRF AuthToken.'
    },
    {
        'name': 'Create Task CRUD Endpoints',
        'description': 'Build REST endpoints to create, read, update and delete tasks.'
    },
    {
        'name': 'Add TimeEntry CRUD Endpoints',
        'description': 'Implement endpoints for managing time entries (start, stop, list, delete).'
    },
    {
        'name': 'Input Validation & Serializers',
        'description': 'Write DRF serializers and custom validators for task and time entry payloads.'
    },
    {
        'name': 'Pagination & Filtering',
        'description': 'Enable page-based pagination and filtering by date, task, user.'
    },
    {
        'name': 'Unit & Integration Tests',
        'description': 'Write pytest or Django TestCase tests for all key API flows.'
    },
    {
        'name': 'Error Handling & Logging',
        'description': 'Standardize error responses and add logging for debugging and audits.'
    },
    {
        'name': 'API Rate Limiting',
        'description': 'Protect endpoints against abuse using DRF throttling classes.'
    },
    {
        'name': 'Swagger / OpenAPI Docs',
        'description': 'Generate interactive API documentation (drf-yasg or drf-spectacular).'
    },
    {
        'name': 'Dockerize Application',
        'description': 'Write Dockerfile and docker-compose for local development and testing.'
    },
    {
        'name': 'CI/CD Pipeline Setup',
        'description': 'Configure GitHub Actions to run tests, linting and build images on push.'
    },
    {
        'name': 'Environment & Secrets Management',
        'description': 'Use django-environ to load secrets and configs from .env securely.'
    },
    {
        'name': 'Health-check & Metrics',
        'description': 'Add endpoint exposing service health and basic metrics (uptime, request count).'
    },
    {
        'name': 'Role-based Permissions',
        'description': 'Implement admin vs. regular-user permissions for task/time-entry operations.'
    },
    {
        'name': 'Email Notifications',
        'description': 'Send emails on task assignment or when a time entry exceeds threshold.'
    },
    {
        'name': 'Data Export',
        'description': 'Provide CSV/JSON export of time entries for reporting.'
    },
    {
        'name': 'Soft Delete & Archive',
        'description': 'Implement soft-deletion for tasks and time entries with ability to restore.'
    },
    {
        'name': 'Performance Optimization',
        'description': 'Add select_related/prefetch_related and indexing to speed up list endpoints.'
    },
]