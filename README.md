# Films API

A modern REST API for managing films, persons, and genres built with FastAPI, PostgreSQL, and Docker. Features automatic database initialization, comprehensive CRUD operations, search functionality, and smart pagination.

## 🚀 Features

- **Full CRUD Operations**: Create, Read, Update, Delete for Films, Persons, and Genres
- **Advanced Search**: Search films by title and persons by name
- **Smart Filtering**: Filter films by genre with pagination
- **Flexible Sorting**: Sort films by rating, title, and other fields
- **Automatic Database Setup**: Smart initialization that only runs on first startup
- **Docker Support**: Complete containerized setup with PostgreSQL
- **Async Architecture**: Full async/await support for better performance
- **Dependency Injection**: Clean separation of concerns with service layer
- **Repository Pattern**: Abstract data access layer
- **Comprehensive API Documentation**: Auto-generated with FastAPI

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI App   │    │  Service Layer  │    │ Repository Layer│
│   (Controllers) │───▶│  (Business      │───▶│  (Data Access)  │
│                 │    │   Logic)        │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │  Dependency     │    │   PostgreSQL    │
                       │  Injection      │    │   Database      │
                       └─────────────────┘    └─────────────────┘
```

## 📋 Prerequisites

- Docker and Docker Compose
- Python 3.10+ (for local development)
- PostgreSQL 15+ (handled by Docker)

## 🛠️ Installation & Setup

### Quick Start

For a complete setup guide with step-by-step instructions, see **[QUICK_START.md](QUICK_START.md)**.

**Prerequisites:**
- Docker and Docker Compose
- Git

**Required Files:**
Make sure you have all the essential files in your project root:
- `docker-compose.yml`, `Dockerfile`, `entrypoint.sh`
- `init.sql` (1.9MB database initialization file)
- `main.py`, `requirements.txt`, `alembic.ini`, `database.py`
- `main_app/` directory (application source code)
- `alembic/` directory (database migrations)
- **Create `.env` file** with database configuration (see QUICK_START.md)

**Quick Commands:**
```bash
# Clone and setup
git clone <repository-url>
cd kazm_test

# Create .env file (see QUICK_START.md for content)
# Start application
docker-compose up --build

# Access API
# http://localhost:8000/docs
```

## 🗄️ Database Initialization

The application features smart database initialization:

- **First Run**: Automatically creates schema and loads sample data from `init.sql`
- **Subsequent Runs**: Skips initialization if data already exists
- **Fresh Start**: Use `docker-compose down -v` to reset database

### Sample Data Included

- **999 Films** with ratings, descriptions, and metadata
- **26 Genres** covering various film categories
- **2,231 Persons** (actors, directors, writers)
- **Relationships** between films, genres, and persons

## 📚 API Documentation

### Base URL
```
http://localhost:8000/api/v1
```

### Authentication
Currently, the API doesn't require authentication for development purposes.

### Response Format
All responses are in JSON format with consistent structure.

## 🎬 Films Endpoints

### Get All Films
```http
GET /api/v1/films/
```

**Query Parameters:**
- `sort` (optional): Sort field with prefix `-` for descending (default: `-rating`)
- `page_size` (optional): Number of items per page (1-100, default: 50)
- `page_number` (optional): Page number (default: 1)
- `genre` (optional): Filter by genre UUID

**Example:**
```bash
curl "http://localhost:8000/api/v1/films/?sort=-rating&page_size=10&page_number=1"
```

### Search Films
```http
GET /api/v1/films/search/
```

**Query Parameters:**
- `query` (required): Search query
- `page_size` (optional): Number of items per page (1-100, default: 50)
- `page_number` (optional): Page number (default: 1)

**Example:**
```bash
curl "http://localhost:8000/api/v1/films/search/?query=star&page_size=10"
```

### Get Film Details
```http
GET /api/v1/films/{film_id}/
```

**Example:**
```bash
curl "http://localhost:8000/api/v1/films/3d825f60-9fff-4dfe-b294-1a45fa1e115d/"
```

### Create Film
```http
POST /api/v1/films/
```

**Request Body:**
```json
{
  "title": "New Film",
  "description": "Film description",
  "type": "movie",
  "rating": 8.5,
  "creation_date": "2023-01-15"
}
```

### Update Film
```http
PUT /api/v1/films/{film_id}/
```

### Delete Film
```http
DELETE /api/v1/films/{film_id}/
```

## 👥 Persons Endpoints

### Search Persons
```http
GET /api/v1/persons/search/
```

### Get Person Details
```http
GET /api/v1/persons/{person_id}/
```

### Get Person Films
```http
GET /api/v1/persons/{person_id}/film/
```

### Create Person
```http
POST /api/v1/persons/
```

**Request Body:**
```json
{
  "full_name": "John Doe"
}
```

### Update Person
```http
PUT /api/v1/persons/{person_id}/
```

### Delete Person
```http
DELETE /api/v1/persons/{person_id}/
```

## 🎭 Genres Endpoints

### Get All Genres
```http
GET /api/v1/genres/
```

### Get Genre Details
```http
GET /api/v1/genres/{genre_id}/
```

### Create Genre
```http
POST /api/v1/genres/
```

**Request Body:**
```json
{
  "name": "New Genre",
  "description": "Genre description"
}
```

### Update Genre
```http
PUT /api/v1/genres/{genre_id}/
```

### Delete Genre
```http
DELETE /api/v1/genres/{genre_id}/
```

## 🔧 Utility Endpoints

### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy"
}
```

### Root Endpoint
```http
GET /
```

**Response:**
```json
{
  "message": "Welcome to Films API",
  "version": "1.0.0",
  "architecture": "Dependency Injection + Repository Pattern + Service Layer",
  "docs": "/docs",
  "redoc": "/redoc"
}
```

## 📊 Response Examples

### Films List Response
```json
[
  {
    "uuid": "3d825f60-9fff-4dfe-b294-1a45fa1e115d",
    "title": "Star Wars: Episode IV - A New Hope",
    "imdb_rating": 8.6
  }
]
```

### Film Details Response
```json
{
  "uuid": "3d825f60-9fff-4dfe-b294-1a45fa1e115d",
  "title": "Star Wars: Episode IV - A New Hope",
  "imdb_rating": 8.6,
  "description": "Luke Skywalker joins forces with a Jedi Knight...",
  "genre": [
    {
      "uuid": "3d8d9bf5-0d90-4353-88ba-4ccc5d2c07ff",
      "name": "Sci-Fi"
    }
  ],
  "actors": [
    {
      "uuid": "a5a8f573-3cee-4ccc-8a2b-91cb9f55250a",
      "full_name": "Mark Hamill"
    }
  ],
  "writers": [...],
  "directors": [...]
}
```

## 🧪 Testing

### Using Postman Collection

1. Import the `Films_API.postman_collection.json` file into Postman
2. Set the `base_url` variable to `http://localhost:8000`
3. Use the provided requests to test all endpoints

### Using curl

```bash
# Get popular films
curl "http://localhost:8000/api/v1/films/?sort=-rating&page_size=5"

# Search for films
curl "http://localhost:8000/api/v1/films/search/?query=star"

# Get film details
curl "http://localhost:8000/api/v1/films/3d825f60-9fff-4dfe-b294-1a45fa1e115d/"

# Create a new film
curl -X POST "http://localhost:8000/api/v1/films/" \
  -H "Content-Type: application/json" \
  -d '{"title":"Test Film","type":"movie","rating":8.0}'
```

## 🐳 Docker Commands

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f app

# Restart application
docker-compose restart app

# Stop all services
docker-compose down

# Reset database (removes all data)
docker-compose down -v

# Rebuild containers
docker-compose up --build
```

## 📁 Project Structure

```
kazm_test/
├── alembic/                 # Database migrations
├── main_app/
│   ├── api/                # API endpoints
│   │   ├── endpoints/      # Route handlers
│   │   └── api.py         # Router configuration
│   ├── core/              # Core application logic
│   │   ├── config.py      # Configuration settings
│   │   ├── dependencies.py # Dependency injection
│   │   ├── factories.py   # Service factories
│   │   ├── repositories.py # Data access layer
│   │   ├── services.py    # Business logic
│   │   └── unit_of_work.py # Unit of work pattern
│   ├── models.py          # SQLAlchemy models
│   └── schemas.py         # Pydantic schemas
├── docker-compose.yml     # Docker services configuration
├── Dockerfile            # Application container
├── entrypoint.sh         # Container startup script
├── init.sql             # Database initialization data
├── main.py              # FastAPI application entry point
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `POSTGRES_USER` | PostgreSQL username | `postgres` |
| `POSTGRES_PASSWORD` | PostgreSQL password | `password` |
| `POSTGRES_DB` | Database name | `films_db` |
| `SYNC_DATABASE_URL` | Synchronous database URL | `postgresql://postgres:password@db:5432/films_db` |
| `ASYNC_DATABASE_URL` | Asynchronous database URL | `postgresql+asyncpg://postgres:password@db:5432/films_db` |

### API Configuration

- **Default Page Size**: 50 items
- **Maximum Page Size**: 100 items
- **Default Sort**: Films by rating (descending)
- **CORS**: Enabled for all origins (development)

## 🚀 Performance Features

- **Async/Await**: Full asynchronous support
- **Connection Pooling**: Optimized database connections
- **Pagination**: Efficient data retrieval
- **Indexing**: Database indexes on frequently queried fields
- **Lazy Loading**: Relationships loaded on demand

## 🔒 Security Considerations

- **Input Validation**: All inputs validated with Pydantic schemas
- **SQL Injection Protection**: Parameterized queries via SQLAlchemy
- **CORS Configuration**: Configurable cross-origin requests
- **Error Handling**: Proper HTTP status codes and error messages

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
1. Check the API documentation at `/docs`
2. Review the logs: `docker-compose logs app`
3. Test the health endpoint: `GET /health`

## 🔄 Changelog

### v1.0.0
- Initial release
- Complete CRUD operations for Films, Persons, and Genres
- Search functionality
- Docker support with automatic database initialization
- Comprehensive API documentation 