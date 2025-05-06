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

### 1. Clone the Repository & Build with Docker Compose
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

Once your container is running, you can start interacting with the API. Here’s how:

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

- **Intelligent Caching**  
  `CacheListMixin` speeds up repetitive queries, and Django's signals make sure that after each change, the cached data is immediately invalidated - the API remains fast and consistent. [Architecture diagram](https://i.imgur.com/ejYuZhe.png)
- **Comprehensive Test Suite**  
  Over 100 unit & integration tests with 99% code coverage, guaranteeing stability and confidence in every release.

- **Robust Business Logic - for example:**  
  - Unique task names per user enforced at serialization time via custom validators.  
  - Time range validation preventing `end_time <= start_time`.  
  - Ownership validation using `IsObjectOwner` permission class and validators to secure resources.

- **Security**  
  - Database-level constraints (`Meta.constraints`) related for business logic.  
  - UUID primary keys for unguessable resource identifiers.  
  - Token-based authentication for all API endpoints.  
  - Protection against N+1 queries through `select_related` and `prefetch_related`.

- **Clean, Well-Documented API**  
  - Full REST compliance with predictable URL patterns.  
  - Swagger/OpenAPI docs with clear examples, pagination, filtering, and sorting out of the box.

- **Modular, Scalable, and Testable Architecture**  
  - Code organized into logical modules: mixins, filters, validators, signals, and helpers.  
  - Reusable components follow SOLID & DRY principles.  
  - Easy to extend and plug into new features.

- **Containerized Multi-Service Setup**  
  - Docker Compose orchestrates the web app, database and cache.

- **Agile-Friendly Repository**  
  - Feature-branch workflow with clear Git history.  

