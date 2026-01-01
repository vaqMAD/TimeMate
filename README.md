# TimeMate – An API-First Time Tracking Backend

A RESTful API for time tracking built with Django REST Framework, PostgreSQL, and Redis, designed for reliability and maintainability.

---

##  Why ?

At the beginning of my programming journey, understanding how time-related operations work in code gave me quite a few headaches.
Around that time, I was heavily relying on time trackers — both at my previous job, where I measured time spent on tasks, and for self-motivation during coding sessions.
I was genuinely curious about how such tools are built, while also having the previosly mentioned issue constantly lingering in the back of my mind. 

So, I decided to finally make peace with it. This project is the result of that journey. Built from scratch.

Along the way, I learned more about:
- International time standards like **`ISO 8601`**
- Date format conversion (string ↔ Python/Django object)
- Formatting datetime objects into desired formats

>**Just want the highlights?** Skip ahead to **[What Sets TimeMate Apart](#-what-sets-timemate-apart)** or **[Architecture Overview](#architecture-overview)**.
---

##  Installation

You can install and run the app using:

```bash
git clone https://github.com/vaqMAD/TimeMate
cd timemate
docker compose up --build
```
---

## Quick Start / Usage

### 1. Access the App
Once the container is running, the app will be available at:  
`http://127.0.0.1:8000` or `http://localhost:8000`

### 2. API Documentation
Visit the interactive docs at:  
`http://127.0.0.1:8000/api/schema/swagger-ui/`

### 3. Demo Credentials (for testing)
The container spins up with a pre-configured superuser for testing:
- **Username:** `admin@admin.com`
- **Password:** `1234`
- **Auth Token:** `9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b`

---

### First Request Example

You can start interacting with the API. Here’s how:

#### Authenticate
Add the following header to your requests in Postman, curl, or any HTTP client:
```http
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

#### Explore Sample Data
The application comes with demo data that you can explore right away by querying:

- `GET http://127.0.0.1:8000/time-entries/sorted-by-date/`  
  _View time entries sorted by date_
- `GET http://127.0.0.1:8000/time-entries/sorted-by-task-name/`  
  _View time entries sorted by task name_

#### Filtering & Ordering
You can filter or sort time entries using query parameters (as documented in the schema). Example:
```http
GET http://127.0.0.1:8000/time-entries/?ordering=-end_time&end_time_after=2025-04-29
```

#### Create Your Own Entries
You can also post your own objects. The app includes business logic validation — for example, for time entries module if `end_time` is earlier than `start_time`, you’ll receive a clear error response:

```http
POST http://127.0.0.1:8000/time-entries/
Content-Type: application/json
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

```json
{
  "task": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "start_time": "2025-05-05T19:25:01.788Z",
  "end_time": "2025-05-05T18:25:01.788Z"
}
```

**Response:**
```json
{
  "non_field_errors": [
    "End time 2025-05-05 18:25:01.788000+00:00 must be greater than start time 2025-05-05 19:25:01.788000+00:00"
  ]
}
```

---

## What Sets TimeMate Apart ?

- **Intelligent View Caching**  
  The system avoids hitting the database for frequent read operations. `CacheListMixin` using `Redis` + Django signals = automatic invalidation on change. Speeds up frequent queries without risking stale data. 

- **Testing:**  
  +100 unit & integration tests, 99% coverage. Tests reflect real-world scenarios, e.g. authorization edge cases, time validation, ownership rules.

- **Data Integrity - examples:**  
  - Unique task names per user – enforced via custom serializer validator  
  - Time range validation – blocks `end_time <= start_time` at API layer  
  - Object ownership logic – enforced both in views (`IsObjectOwner`) and serializer level  
  - Reusable validation logic extracted to helper classes

- **Security by Design**  
  - UUIDs as primary keys = safe from enumeration  
  - DB-level business logic (`CheckConstraint`, `UniqueConstraint`) protects integrity  
  - Token-based auth for all endpoints  
  - Eliminated N+1 queries via `select_related` & `prefetch_related`

- **Clean Resful Api**  
  - Fully RESTful structure with intuitive endpoints  
  - Automatic docs via DRF Spectacular (OpenAPI/Swagger)  
  - Built-in pagination, filtering, ordering 
  
- **Modular Architecture**  
  - Reusable components (Mixins, Validators, Signals, Filters, Permissions)  
  - Based on **SOLID**, **KISS**, **DRY** principles  
  - Each component: isolated, testable, easy to extend/maintain

- **Workflow**  
  - Full Docker Compose setup: API, DB, Cache  
 
---

## Architecture Overview

**Important note** In this project I did not use any desing patter on purpose. Why ? Because the business logic is relatievly simple, and attempting to abstrac it away would lead to over-engineering and less readable code - in my opinion.

Instead, I too more 'raw' approach, using predefined tools provided by Django/DRF - grouping them into logical modules, files, classes and functions.

TimeMate is designed with **clean separation of concerns** and maintainability in mind.

### Structure:
- **Views / Endpoints** – Thin layer. Orchestrates request flow, delegates logic to Services/Mixins
- **Serializers** – Responsible for validation and data sanitization. (e.g. unique task names)
- **Utils/Mixins** Isolated, reusable logic (Caching, Permissions) following DRY/SOLID.
- **Models** – Clean data layer with constraints (e.g. `CheckConstraint`, `UniqueConstraint`)
- **Tests** – Cover both unit (isolated logic) and integration (endpoints + DB)

### Data Flow Example:
1. User makes a `POST /time-entries/`
2. Auth via Token
3. Serializer validates logic (time range, ownership, task uniqueness)
4. Valid data hits Model → DB (PostgreSQL)
5. Signal triggers → Cache invalidated
6. Next `GET /time-entries/` pulls fresh data → caches result

### High-Level Component Map:
```
TimeMate Project (Root)
│
├── TimeMate/                     # Django project's main directory
│   ├── Utils/                    # Helper modules, the "toolbox"
│   │   ├── mixins.py             # Mixins (e.g., OwnerRepresentationMixin, CacheListMixin)
│   │   ├── pagination.py         # Default pagination configuration
│   │   └── view_helpers.py       # Decorator s a nd helper functions for views
│   ├── Permissions/
│   │   └── owner_permissions.py  # Permission logic (e.g., IsObjectOwner)
│   ├── Serializers/
│   │   └── user_serializers.py   # Serializer for the User model
│   ├── Signals/
│   │   └── signals.py            # Signals for cache invalidation after model changes
│   ├── Tests/
│   │   ├── test_cache_and_signals.py # Integration tests for cache and signals
│   │   ├── test_mixins.py        # Tests for mixins
│   │   └── test_owner_permissions.py # Tests for permissions
│   ├── settings.py               # Main project settings (DB, Cache, DRF)
│   └── urls.py                   # Main project URLs (including Swagger)
│
├── Task/                         # Django app for Tasks
│   ├── Tests/                    # Tests for the Task app
│   ├── models.py                 # Task model with validators and DB constraints
│   ├── serializers.py            # Serializers for Task (Create, Detail, List, Update)
│   ├── validators.py             # Validators (e.g., unique task name per owner)
│   ├── views.py                  # API views (ListCreate, RetrieveUpdateDestroy)
│   └── urls.py                   # URLs for the Task app
│
├── TimeEntry/                    # Django app for Time Entries
│   ├── Tests/                    # Tests for the TimeEntry app
│   ├── models.py                 # TimeEntry model with `duration` calculation logic
│   ├── serializers.py            # Serializers for TimeEntry, including grouping ones
│   ├── validators.py             # Validator for correct time range (start < end)
│   ├── views.py                  # API views, including sorting and grouping
│   └── urls.py                   # URLs for the TimeEntry app
│
├── docker-compose.yml            # Container configuration (API, Database, Cache)
├── entrypoint.sh                 # Entrypoint script for the Docker container
├── requirements.txt              # Python dependencies
└── README.md                     # You are here ;)
```
---
