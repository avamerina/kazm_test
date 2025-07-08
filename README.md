# Films API

A FastAPI-based API for managing films, genres, and persons, using PostgreSQL and Docker.

## Quick Start

1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd kazm_test
   ```
2. **Set up your `.env` file** (see `.env.example` if available).
3. **Build and start services:**
   ```bash
   docker-compose up --build
   ```
   - This starts the database and API app.
4. **Access the API:**
   - Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
   - Health: [http://localhost:8000/health](http://localhost:8000/health)

## Running Tests

- **Inside the app container:**
  ```bash
  docker-compose exec app bash
  pytest tests/ -v
  ```
- **Or locally (with a virtual environment):**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  pip install -r requirements.txt
  pytest tests/ -v
  ```
- See [TESTING.md](./TESTING.md) for details.

## Project Structure
- `main.py` — App entrypoint
- `main_app/` — Application code
- `tests/` — Tests
- `Dockerfile`, `docker-compose.yml` — Container setup

## CI/CD
- Automated tests run on GitHub Actions for every push/PR.

---
For more, see [TESTING.md](./TESTING.md). 