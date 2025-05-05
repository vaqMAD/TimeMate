# TimeMate
A lightweight, powerful and fully API-first backend for time tracking and task management, inspired by [Toggl.com's](https://toggl.com/) functionality.
**Key features:**
- 🔄 Intelligent caching layer for sub-millisecond response times  
- ✅ Over 100 unit & integration tests ensuring rock-solid stability

## 🤔 Why?

At the start of my programming journey, trying to understand how time-related objects and operations work gave me a few gray hairs 😉  
Back then, I relied heavily on time trackers — both at my previous job to measure time spent on tasks, and for personal motivation while learning to code.

So I drew inspiration from Toggl.com’s features and built my own API service to tackle the problem hands-on.  
That’s how **TimeMate** was born—a backend project where I could organize my knowledge, learn best practices, and, incidentally, create something that actually works.
Along the way, I deepened my understanding of:  
- International date/time standards like **`ISO 8601`**  
- Converting between formats (string ↔ Python/Django datetime objects)  
- Formatting time objects into the exact representation you need

## ⚙️ Installation

Choose one of the following methods to get **TimeMate** up and running:

---

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
### 2. From source with Docker Compose
  1. Pull the latest image:
  ```bash
  docker pull vaqmadx/timemate:latest
  ```
  2. Run the container:
  ```bash
  docker run -d \
  --name timemate \
  -p 8000:8000 \
  vaqmadx/timemate:latest
  ```
  
