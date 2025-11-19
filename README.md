# Simple Form API

A FastAPI-based web application with a form interface for submitting and displaying data.

## Features

- Simple HTML form for data input
- Real-time data display
- RESTful API endpoints
- In-memory data storage
- Form validation using Pydantic
- Responsive UI with modern design

## Prerequisites

- Python 3.8 or higher
- pip or uv package manager

## Installation

1. Clone or navigate to this directory:
```bash
cd /Users/mehulmathur/Opius/practice/subagents
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

Start the FastAPI server:

```bash
python main.py
```

Or using uvicorn directly:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The application will be available at: http://localhost:8000

## API Endpoints

### GET /
- **Description:** Serves the main HTML page with form and data display
- **Response:** HTML page

### POST /postDetails
- **Description:** Submit new details
- **Request Body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "message": "Hello, this is a test message"
}
```
- **Response:**
```json
{
  "id": "uuid-here",
  "name": "John Doe",
  "email": "john@example.com",
  "message": "Hello, this is a test message",
  "created_at": "2025-11-14 12:34:56"
}
```

### GET /getDetails
- **Description:** Retrieve all submitted details
- **Response:** Array of detail objects

### GET /getDetails/{detail_id}
- **Description:** Retrieve a specific detail by ID
- **Response:** Single detail object or 404 error

### DELETE /clearDetails
- **Description:** Clear all stored details
- **Response:**
```json
{
  "message": "All details cleared successfully",
  "count": 0
}
```

### GET /health
- **Description:** Health check endpoint
- **Response:**
```json
{
  "status": "healthy",
  "total_records": 0
}
```

## Testing with cURL

### Submit details:
```bash
curl -X POST "http://localhost:8000/postDetails" \
  -H "Content-Type: application/json" \
  -d '{"name":"John Doe","email":"john@example.com","message":"Test message"}'
```

### Get all details:
```bash
curl "http://localhost:8000/getDetails"
```

### Get specific detail:
```bash
curl "http://localhost:8000/getDetails/{detail_id}"
```

### Clear all details:
```bash
curl -X DELETE "http://localhost:8000/clearDetails"
```

## Project Structure

```
subagents/
├── main.py              # FastAPI application with all endpoints
├── requirements.txt     # Python dependencies
├── README.md           # This file
└── .gitignore          # Git ignore rules
```

## Tech Stack

- **FastAPI:** Modern web framework for building APIs
- **Uvicorn:** ASGI server for running FastAPI
- **Pydantic:** Data validation using Python type annotations
- **Jinja2:** Template engine (for future extensions)

## Notes

- Data is stored in-memory and will be lost when the server restarts
- For production use, consider adding a proper database (PostgreSQL, MongoDB, etc.)
- The application includes basic email validation via regex
- CORS is not configured - add if needed for cross-origin requests

## Future Enhancements

- Add persistent database storage
- Implement authentication and authorization
- Add pagination for large datasets
- Include data export functionality
- Add more comprehensive validation
- Implement rate limiting
