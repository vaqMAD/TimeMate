# TimeMate
A lightweight, powerful and fully API-first backend for time tracking and task management, inspired by [Toggl.com's](https://toggl.com/) functionality.
**Key features:**
- 🔄 Intelligent caching layer for sub-millisecond response times  
- ✅ Over 100 unit & integration tests ensuring rock-solid stability

## 🤔 Why?

At the start of my programming journey, trying to understand how time-related objects and operations work gave me a few gray hairs 😉  
Back then, I relied heavily on time trackers — both at my previous job to measure time spent on tasks, and for personal motivation while learning to code.

So I drew inspiration from Toggl.com’s features and built my own API service to tackle the problem hands-on.  
That’s how **TimeMate** was born — a backend project where I could organize my knowledge, learn best practices, and, incidentally, create something that actually works.
Along the way, I deepened my understanding of:  
- International date/time standards like **`ISO 8601`**  
- Converting between formats (string ↔ Python/Django datetime objects)  
- Formatting time objects into the exact representation you need

## ⚙️ Installation
Choose one of the following methods to get **TimeMate** up and running:


### 1. From source with Docker Compose

1. Clone the repository:
```bash
git clone https://github.com/your-username/timemate.git
cd timemate
```
2. Build and start containers:
```bash
docker compose up --build -d
```
--- 
### 2. Pull pre-built image from Docker Hub
1. Pull the latest image:
```bash
docker pull vaqmadx/timemate:latest
```
2. Run the container:
```bash
docker run -d --name timemate -p 8000:8000 vaqmadx/timemate:latest
```

---
## 🚀 Quick Start 
1. **Access the running app**  
   After building and starting the containers, TimeMate is available at: `http://127.0.0.1:8000` or `http://localhost:8000`
2. **Explore the API docs**  
   Swagger UI is served at:  `http://127.0.0.1:8000/api/schema/swagger-ui/`
3. **Superuser credentials**  
   If you need to log into the Django admin or make authenticated API calls, use:
   ```
   Username:  admin@admin.com
   Password:  1234
   Token:     9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
   ```
4. Your first API request
   - In your client (Postman, curl, etc.), add this header to authenticate `Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b`
   - 📊 Explore sample data:
     The application comes with demo data that you can explore right away by querying the following endpoints:
     - View time entries sorted by date: `GET http://127.0.0.1:8000/time-entries/sorted-by-date/`
     - View time entries sorted by task name: `GET http://127.0.0.1:8000/time-entries/sorted-by-task-name/`
   - Filtering & ordering
     You can apply query parameters as shown in the docs, for example: `GET http://127.0.0.1:8000/time-entries/?ordering=-end_time&end_time_after=2025-04-29`
   - Creating your own entries:
     If you send an invalid payload, TimeMate will return a clear error. For instance, trying to set end_time before start_time:
     ```bash
     POST http://127.0.0.1:8000/time-entries/
     Content-Type: application/json
     Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b

      {
        "task": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "start_time": "2025-05-05T19:25:01.788Z",
        "end_time":   "2025-05-05T18:25:01.788Z"
      }
     ```
