# Alpine.js + FastAPI Skeleton Project

A simple skeleton project combining Alpine.js with Tailwind CSS for the frontend and FastAPI for the backend.

## Project Structure

```
goofyFE/
├── main.py              # FastAPI application
├── database.py          # Database configuration
├── models.py            # Database and Pydantic models
├── requirements.txt     # Python dependencies
├── venv/                # Virtual environment (created during setup)
├── static/
│   └── index.html      # Frontend with Alpine.js and Tailwind CSS
├── tests/
│   └── unit/           # Unit tests
└── README.md
```

## Setup Instructions

### Setup

1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env file with your database credentials
   ```

4. Run the FastAPI server:
   ```bash
   python main.py
   ```

   Or using uvicorn directly:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

### Running Tests

**Important**: Always activate the virtual environment before running tests:

```bash
# Activate virtual environment first
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Run tests
pytest                    # Run all tests
pytest tests/unit/        # Run only unit tests  
pytest -v                 # Run with verbose output
```

If you get `ModuleNotFoundError` when running tests, make sure you've activated the virtual environment first.

### Frontend

The frontend is served automatically by FastAPI. Once the application is running, visit:
- http://localhost:8000 for the main application
- http://localhost:8000/docs for FastAPI interactive documentation

## Features

### Backend (FastAPI)
- CORS enabled for frontend integration
- Static file serving for frontend assets
- Sample API endpoints:
  - `GET /api/hello` - Simple hello message
  - `GET /api/items` - Sample data list

### Frontend (Alpine.js + Tailwind CSS)
- Responsive design with Tailwind CSS
- Interactive components with Alpine.js
- API integration examples
- Loading states and error handling
- Sample counter component

## Development

- Application runs on http://localhost:8000
- Frontend is served from the `/` route
- API endpoints are available under `/api/`
- FastAPI docs available at `/docs`
- Static files served from `/static/`

## Next Steps

1. Add more API endpoints in `main.py`
2. Extend frontend functionality in `static/index.html`
3. Configure your PostgreSQL database in `.env`
4. Implement authentication
5. Add more comprehensive tests
6. Add form handling and validation