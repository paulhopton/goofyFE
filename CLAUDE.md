# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an Alpine.js + FastAPI skeleton project with a PostgreSQL database backend. The application serves a single-page frontend with multiple views and provides REST API endpoints for user management.

## Development Commands

### Backend Setup
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Copy and configure environment variables
cp .env.example .env
# Edit .env file with your actual database credentials
```

### Running the Application
```bash
source venv/bin/activate  # Ensure virtual environment is activated
python main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Running Tests
```bash
source venv/bin/activate  # Ensure virtual environment is activated
pytest  # Run all tests
pytest tests/unit/  # Run only unit tests
pytest tests/integration/  # Run only integration tests
pytest -v  # Run with verbose output
```

### Database Configuration
- Environment variables are loaded from `.env` file (create from `.env.example`)
- Uses `DATABASE_URL` for main database connection
- Uses `TEST_DATABASE_URL` for integration tests
- Database tables are created automatically on startup
- **Important**: Never commit `.env` file - it contains sensitive credentials

## Architecture

### Project Structure
- **main.py**: FastAPI application with CORS, static file serving, and API endpoints
- **database.py**: SQLAlchemy database configuration and session management
- **models.py**: Database models (UserDB) and Pydantic schemas (UserCreate, UserUpdate, UserResponse)
- **static/**: Frontend files (HTML, CSS, JS)
- **tests/**: Unit and integration tests

### Frontend Structure
- **static/index.html**: Single-page application using Alpine.js and Tailwind CSS
- Multi-page SPA with sidebar navigation (Dashboard, API Tests, Items, Counter)
- Alpine.js components for state management and API interactions

### API Endpoints
- `GET /` - Serves the frontend HTML
- `GET /api/hello` - Simple hello message
- `GET /api/items` - Sample data list
- `POST /api/users` - Create user
- `GET /api/users` - List users (with pagination)
- `GET /api/users/{user_id}` - Get specific user
- `PUT /api/users/{user_id}` - Update user
- `DELETE /api/users/{user_id}` - Delete user

### Database Schema
- **users** table: id, name, email (unique), created_at, updated_at

## Development URLs
- Main application: http://localhost:8000
- API documentation: http://localhost:8000/docs
- API endpoints: http://localhost:8000/api/*

## Key Dependencies
- FastAPI 0.104.1
- SQLAlchemy 2.0.23 with PostgreSQL (psycopg2-binary)
- Alembic for migrations
- python-dotenv for environment variable management
- pytest 7.4.3 with pytest-asyncio for testing
- httpx for async HTTP client testing
- Alpine.js 3.x (CDN)
- Tailwind CSS (CDN)

## Testing Structure
- **Unit tests** (`tests/unit/`): Test individual components and models
- **Integration tests** (`tests/integration/`): Test API endpoints and full request/response cycles with PostgreSQL
- Integration tests use separate test database configured via `TEST_DATABASE_URL`
- Unit tests can use SQLite in-memory database for isolation
- Async tests supported with pytest-asyncio

## Notes
- Frontend is served directly by FastAPI (no separate build process)
- CORS is enabled for all origins
- Email validation is enforced on user endpoints
- Database connection uses PostgreSQL by default