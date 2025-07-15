# 🕒 TimeMate – API-First Time Tracking Backend

A lightweight, powerful and fully API-first backend for time tracking and task management, inspired by [Toggl.com's](https://toggl.com/) functionality.  
Includes features such as intelligent caching, over 100 unit/integration tests, and a clean, modular architecture.

---

## ❓ Why

At the beginning of my programming journey, understanding how time-related operations work in code gave me quite a few headaches 😉.

Around that time, I was heavily relying on time trackers — both at my previous job, where I measured time spent on specific tasks, and for self-motivation during coding sessions.

So, I decided to turn that challenge into an opportunity and build my own API service, inspired by Toggl.com.

That’s how **TimeMate** was born — a backend project that helped me organize my knowledge, apply best practices, and build something that actually works.

Along the way, I learned more about:

- International time standards like **`ISO 8601`**
- Date format conversion (string ↔ Python/Django object)
- Formatting datetime objects into desired formats

---

## 🛠️ Installation

You can install and run the app using:

### Clone the Repository & Build with Docker Compose
```bash
git clone https://github.com/vaqMAD/TimeMate
cd timemate
docker compose up --build
```
---

## 🚀 Quick Start / Usage

### 1. Access the App
Once the container is running, the app will be available at:  
`http://127.0.0.1:8000` or `http://localhost:8000`

### 2. API Documentation
Visit the interactive docs at:  
`http://127.0.0.1:8000/api/schema/swagger-ui/`

### 3. Superuser Credentials (for testing)
- **Username:** `admin@admin.com`
- **Password:** `1234`
- **Auth Token:** `9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b`

---

### 📡 Your First API Request

You can start interacting with the API. Here’s how:

#### 🔐 Authenticate
Add the following header to your requests in Postman, curl, or any HTTP client:
```http
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

#### 📊 Explore Sample Data
The application comes with demo data that you can explore right away by querying:

- `GET http://127.0.0.1:8000/time-entries/sorted-by-date/`  
  _View time entries sorted by date_
- `GET http://127.0.0.1:8000/time-entries/sorted-by-task-name/`  
  _View time entries sorted by task name_

#### ⚙️ Filtering & Ordering
You can filter or sort time entries using query parameters (as documented in the schema). Example:
```http
GET http://127.0.0.1:8000/time-entries/?ordering=-end_time&end_time_after=2025-04-29
```

#### 🛠 Create Your Own Entries
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

## ⭐ What Sets TimeMate Apart

- **Intelligent View Caching**  
  `CacheListMixin` + Django signals = automatic invalidation on change. Speeds up frequent queries without risking stale data. Reduces DB load in real use cases.

- **Testing: Real, Not Just for Show**  
  +100 unit & integration tests, 99% coverage. Tests reflect real-world scenarios, e.g. authorization edge cases, time validation, ownership rules.

- **Solid Business Logic Implementation**  
  - Unique task names per user – enforced via custom serializer validator  
  - Time range validation – blocks `end_time <= start_time` at API layer  
  - Object ownership logic – enforced both in views (`IsObjectOwner`) and serializer level  
  - Reusable validation logic extracted to helper classes

- **Security by Design**  
  - UUIDs as primary keys = safe from enumeration  
  - DB-level constraints (`CheckConstraint`, `UniqueConstraint`) protect integrity  
  - Token-based auth for all endpoints  
  - Eliminated N+1 queries via `select_related` & `prefetch_related`

- **API That Speaks Human**  
  - Fully RESTful structure with intuitive endpoints  
  - Automatic docs via DRF Spectacular (OpenAPI/Swagger)  
  - Built-in pagination, filtering, ordering – with example queries

- **Modular Architecture Built for Growth**  
  - Reusable components (Mixins, Validators, Signals, Filters, Permissions)  
  - Based on **SOLID**, **KISS**, **DRY** principles  
  - Each component: isolated, testable, easy to extend/maintain

- **Ready for Production-like Workflow**  
  - Full Docker Compose setup: API, DB (Postgres), Cache (Redis)  
  - Consistent dev/prod parity

- **Git Workflow You’d Want in a Team**  
  - Feature branches with descriptive commits  
  - Git-flow inspired structure for clean history & traceability
 
  ---
  ## 🏗️ Architecture Overview

TimeMate is designed with **clean separation of concerns** and maintainability in mind.

### 📦 Layered Structure:
- **Views / Endpoints** – Handle HTTP requests, auth, and basic orchestration
- **Serializers** – Validate and transform data, enforce rules (e.g. unique task names)
- **Custom Logic** – Isolated in reusable:
  - **Mixins** – e.g. caching
  - **Validators** – e.g. business rules for time ranges
  - **Permissions** – e.g. ownership enforcement
  - **Signals** – e.g. auto-invalidate cache after model save/delete
- **Models** – Clean data layer with constraints (e.g. `CheckConstraint`, `UniqueConstraint`)
- **Tests** – Cover both unit (isolated logic) and integration (endpoints + DB)

### 🔁 Data Flow Example:
1. 🧍 User makes a `POST /time-entries/`
2. 🔐 Auth via Token
3. 🔄 Serializer validates logic (time range, ownership, task uniqueness)
4. ✅ Valid data hits Model → DB (PostgreSQL)
5. ⚠️ Signal triggers → Cache invalidated
6. 🔁 Next `GET /time-entries/` pulls fresh data → caches result

> TL;DR: You write once, test once, and sleep peacefully ever after. 😴

