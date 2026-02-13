# ZebraStream IoT Pipeline — Setup & Configuration Guide

> ⚠️ **Security Note:** Never commit API keys or passwords to git. Use `.env` files (which should be in `.gitignore`) and environment variables. If you've shared a key in chat, rotate it immediately at [platform.openai.com](https://platform.openai.com/api-keys).

---

## Quick Reference: Logins & URLs

| Service | URL | Login |
|---------|-----|-------|
| **Dashboard / Demo** | http://localhost:8000/ | — |
| **Airflow** | http://localhost:8080 | `admin` / `admin` |
| **FastAPI (Swagger)** | http://localhost:8000/docs | — |
| **FastAPI (Health)** | http://localhost:8000/health | — |

---

## Part 1: PostgreSQL Database Configuration

You need a PostgreSQL database before running the pipeline. Choose one option below.

### Option A: Use Docker (Recommended — No Local Install)

PostgreSQL will run in Docker when you start the project. **You don't need to install PostgreSQL on your machine.**

1. When we build the project, `docker-compose.yml` will define a PostgreSQL container.
2. You'll set the password via an environment variable (e.g., `POSTGRES_PASSWORD=your_secure_password`).
3. The app will connect automatically. **Just pick a password and give it to me** — I'll wire it into the config.

**Password to give me:** Any strong password (e.g., `ZebraStream2025!` or a random string). I'll use it in the Docker Compose and app config.

---

### Option B: Use an Existing Local PostgreSQL Install

If you already have PostgreSQL installed:

1. **Start PostgreSQL** (if not running):
   - **macOS (Homebrew):** `brew services start postgresql`
   - **macOS (Postgres.app):** Open the app
   - **Linux:** `sudo systemctl start postgresql`

2. **Create a database and user:**
   ```bash
   # Connect to PostgreSQL (may need: psql -U postgres or psql -U your_username)
   psql -U postgres

   # In the psql prompt, run:
   CREATE DATABASE zebrastream;
   CREATE USER zebra_app WITH PASSWORD 'your_password_here';
   GRANT ALL PRIVILEGES ON DATABASE zebrastream TO zebra_app;
   \q
   ```

3. **Give me these values:**
   - **Host:** `localhost` (or `127.0.0.1`)
   - **Port:** `5432` (default)
   - **Database:** `zebrastream`
   - **User:** `zebra_app`
   - **Password:** (whatever you set)

---

### Option C: Use a Cloud PostgreSQL (Supabase, Neon, Railway, etc.)

1. Sign up for a provider (e.g., [Supabase](https://supabase.com) or [Neon](https://neon.tech)).
2. Create a new project/database.
3. Copy the connection string (usually `postgresql://user:password@host:port/database`).
4. **Give me:** The full connection string, or host, port, database, user, and password separately.

---

**What to send me:** Your chosen option (A, B, or C) and the password (and any other connection details if using B or C).

---

## Part 2: Environment Variables Setup

Create a `.env` file in the project root (`zebra-smart-factory/` or project root) with:

```env
# PostgreSQL (adjust if using Option B or C)
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=zebrastream
POSTGRES_USER=zebra_app
POSTGRES_PASSWORD=your_password_here

# OpenAI (for LangChain maintenance agent)
OPENAI_API_KEY=sk-proj-your-actual-key-here

# Optional: App settings
ENVIRONMENT=development
LOG_LEVEL=INFO
```

**Important:** Add `.env` to `.gitignore` so it's never committed.

---

## Part 3: Step-by-Step Configuration (After Project Is Built)

### Step 1: Install Prerequisites

- **Docker Desktop** — [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/)
- **Git** (if cloning)
- **Python 3.10+** (optional, for local dev without Docker)

**Verify Docker:**
```bash
docker --version
docker compose version
```

---

### Step 2: Clone/Navigate to Project

```bash
cd /Users/danielrafailov/Desktop/IOT\ Data\ Pipeline\ Project
# Or wherever the zebra-smart-factory folder lives
```

---

### Step 3: Create `.env` File

1. Copy the `.env.example` file (if provided) to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your values:
   - Replace `your_password_here` with your PostgreSQL password
   - Replace `sk-proj-your-actual-key-here` with your OpenAI API key

---

### Step 4: Build and Start Containers

```bash
docker compose build
docker compose up -d
```

**What runs:**
- PostgreSQL (port 5432)
- FastAPI app (port 8000)
- Airflow webserver (port 8080)
- Airflow scheduler

---

### Step 5: Verify Services

1. **FastAPI:** Open [http://localhost:8000/docs](http://localhost:8000/docs) — Swagger UI should load.
2. **Airflow:** Open [http://localhost:8080](http://localhost:8080) — default login is often `admin` / `admin` (check Airflow docs for your image).
3. **PostgreSQL:** From host:
   ```bash
   docker compose exec postgres psql -U zebra_app -d zebrastream -c "\dt"
   ```
   You should see tables (or an empty list if migrations haven’t run yet).

---

### Step 6: Run Database Migrations (If Applicable)

If the project uses Alembic or similar:

```bash
docker compose exec app alembic upgrade head
```

Or run migrations via a startup script if the app does it automatically.

---

### Step 7: Trigger Data Simulator (If Separate)

If there's a standalone simulator:

```bash
docker compose exec app python -m data_simulator.run
# Or whatever the project specifies
```

---

### Step 8: Trigger Airflow DAGs

1. Go to [http://localhost:8080](http://localhost:8080)
2. Find `iot_ingestion` and `daily_summary` DAGs
3. Toggle them ON (unpause)
4. Click "Trigger DAG" to run manually

---

## Part 4: Troubleshooting

### "no configuration file provided: not found"

- **Cause:** You ran `docker compose build` in a directory that doesn't have `docker-compose.yml`.
- **Fix:** Ensure you're in the `zebra-smart-factory` directory:
  ```bash
  cd /path/to/IOT\ Data\ Pipeline\ Project/zebra-smart-factory
  docker compose build
  ```
  The `docker-compose.yml` file must be in the current directory.

---

### Docker won't start / "Cannot connect to Docker daemon" / "no such file or directory" (docker.sock)

- **Cause:** Docker Desktop is not running.

- **Fix:** Start Docker Desktop and wait until it’s fully up. Check system tray for the whale icon.

---

### Port already in use (5432, 8000, 8080)

- **Cause:** Another process is using the port.
- **Fix:**
  ```bash
  # Find process on port 5432 (example)
  lsof -i :5432
  # Kill if needed (replace PID with actual number)
  kill -9 <PID>
  ```
  Or change ports in `docker-compose.yml` (e.g., `8001:8000` for the app).

---

### PostgreSQL: "connection refused" or "could not connect"

- **Cause:** DB not ready yet, wrong host/port, or wrong credentials.
- **Fix:**
  1. Wait 30–60 seconds after `docker compose up` for Postgres to initialize.
  2. Check `.env` matches `docker-compose.yml` (same user, password, db).
  3. Test connection:
     ```bash
     docker compose exec postgres psql -U zebra_app -d zebrastream -c "SELECT 1;"
     ```

---

### Airflow: "Broken DAG" or import errors

- **Cause:** Python path, missing deps, or DAG syntax errors.
- **Fix:**
  1. Check Airflow logs: `docker compose logs airflow-webserver`
  2. Ensure DAGs are in the correct folder (e.g., `dags/`).
  3. Restart Airflow: `docker compose restart airflow-webserver airflow-scheduler`

---

### FastAPI: "ModuleNotFoundError" or 500 errors

- **Cause:** Missing dependency or wrong Python path.
- **Fix:**
  1. Rebuild: `docker compose build --no-cache app`
  2. Check `requirements.txt` is complete.
  3. View logs: `docker compose logs app`

---

### OpenAI: "Invalid API key" or 401

- **Cause:** Wrong key, expired key, or key not loaded.
- **Fix:**
  1. Confirm `OPENAI_API_KEY` is set in `.env` and the app loads it.
  2. Rotate the key at [platform.openai.com](https://platform.openai.com/api-keys) if it was exposed.
  3. Ensure no extra spaces or quotes in `.env`: `OPENAI_API_KEY=sk-proj-...`

---

### Permission denied (e.g., on dags/ or logs/)

- **Cause:** File ownership or permissions.
- **Fix:**
  ```bash
  chmod -R 755 dags/
  # If using Linux/WSL with Docker, you may need to fix ownership:
  sudo chown -R $USER:$USER .
  ```

---

### "No space left on device" (Docker)

- **Cause:** Docker disk usage is high.
- **Fix:**
  ```bash
  docker system prune -a
  docker volume prune
  ```
  (This removes unused images and volumes.)

---

### Database tables don't exist

- **Cause:** Migrations not run.
- **Fix:**
  ```bash
  docker compose exec app alembic upgrade head
  # Or, if the app creates tables on startup, check logs for errors
  docker compose logs app
  ```

---

### PostgreSQL / Airflow: "password authentication failed" or connection errors with special characters in password

- **Cause:** Your password contains special characters (`&`, `^`, `*`, `/`, `#`, `@`, etc.) that break URL parsing in connection strings.
- **Fix:** Either:
  1. **Use a simpler password** (letters, numbers, underscores only) for development, or
  2. **URL-encode** the password in connection strings. Common encodings: `&` → `%26`, `^` → `%5E`, `*` → `%2A`, `/` → `%2F`, `#` → `%23`, `@` → `%40`.  
     For the `.env` file, keep the raw password. If Airflow fails to connect, you may need to set `AIRFLOW__DATABASE__SQL_ALCHEMY_CONN` manually in `docker-compose.yml` with the URL-encoded password.

---

### Airflow default login doesn't work

- **Cause:** Default credentials vary by image.
- **Fix:** Check the image docs or `docker-compose.yml` for `AIRFLOW_ADMIN_USERNAME` / `AIRFLOW_ADMIN_PASSWORD`. For a fresh install, it’s often `admin` / `admin`.

---

## Quick Reference: Useful Commands

| Task | Command |
|------|---------|
| Start all services | `docker compose up -d` |
| Stop all services | `docker compose down` |
| View logs | `docker compose logs -f app` |
| Rebuild after code change | `docker compose build app && docker compose up -d app` |
| Shell into app container | `docker compose exec app bash` |
| Run tests | `docker compose exec app pytest` |
| Reset database (careful!) | `docker compose down -v` (removes volumes) |

---

*Once you've configured PostgreSQL and created your `.env` file, share the password (and any connection overrides) so the project can be wired correctly. Never share API keys or passwords in chat after setup — use secure channels.*
