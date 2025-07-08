# Quick Start Guide

This guide will help you get the Films API up and running quickly.

## Prerequisites

- Docker and Docker Compose installed
- Git installed

## Step 1: Clone the Repository

```bash
git clone <repository-url>
cd kazm_test
```

## Step 2: Verify Required Files

Make sure the following files are present in the project root:

### Essential Files (should be included in repository):
- ✅ `docker-compose.yml` - Docker services configuration
- ✅ `Dockerfile` - Application container definition
- ✅ `entrypoint.sh` - Container startup script
- ✅ `init.sql` - Database initialization data (1.9MB)
- ✅ `main.py` - FastAPI application entry point
- ✅ `requirements.txt` - Python dependencies
- ✅ `alembic.ini` - Alembic configuration
- ✅ `database.py` - Database connection setup
- ✅ `main_app/` - Application source code
- ✅ `alembic/` - Database migrations
- ✅ `Films_API.postman_collection.json` - Postman collection for API testing

### Files You Need to Create:
- 🔧 `.env` - Environment variables (see Step 3)

## Step 3: Create Environment File

Create a `.env` file in the project root:

```bash
# Database Configuration
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=films_db

# Database URLs
SYNC_DATABASE_URL=postgresql://postgres:password@db:5432/films_db
ASYNC_DATABASE_URL=postgresql+asyncpg://postgres:password@db:5432/films_db
```

## Step 4: Start the Application

```bash
# Build and start all services
docker-compose up --build
```

## Step 5: Verify Installation

Once the containers are running, you should see:

```
fastapi_app     | ✅ База данных готова
fastapi_app     | 🔄 База данных уже содержит данные. Пропускаем инициализацию.
fastapi_app     | ✅ База данных уже инициализирована, пропускаем миграции и дамп
fastapi_app     | ▶ Запуск uvicorn...
fastapi_app     | INFO:     Uvicorn running on http://0.0.0.0:8000
```

## Step 6: Access the API

- **API Base URL**: http://localhost:8000
- **Interactive Documentation**: http://localhost:8000/docs
- **Alternative Documentation**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## Quick Test

Test that everything is working:

```bash
# Health check
curl http://localhost:8000/health

# Get some films
curl http://localhost:8000/api/v1/films/?page_size=3
```

## Troubleshooting

### Permission Denied Error
If you see `permission denied: /app/entrypoint.sh`, run:
```bash
chmod +x entrypoint.sh
docker-compose up --build
```

### Port Already in Use
If port 8000 is already in use, modify the port in `docker-compose.yml`:
```yaml
ports:
  - "8001:8000"  # Change 8000 to 8001
```

### Database Connection Issues
If the app can't connect to the database:
```bash
# Stop all containers
docker-compose down

# Remove volumes and restart
docker-compose down -v
docker-compose up --build
```

## Next Steps

- Import the `Films_API.postman_collection.json` into Postman for testing
- Check the main README.md for detailed API documentation
- Explore the interactive documentation at http://localhost:8000/docs

## Stopping the Application

```bash
# Stop all services
docker-compose down

# Stop and remove all data (fresh start)
docker-compose down -v
``` 