# Quick Start

## 1. Clone the repository
```bash
git clone <repo-url>
cd kazm_test
```

## 2. Set up environment variables and db data
- Copy or create a `.env` file with your DB and app settings in project root
- Copy 'init.sql' to dump test data into DB in project root

## 3. Build and start services
```bash
docker-compose up --build
```
- This starts the database and API app.

## 4. Run tests
- **In the app container:**
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

## 5. Access the API
- Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
- Health: [http://localhost:8000/health](http://localhost:8000/health)

---
For more, see [TESTING.md](./TESTING.md). 