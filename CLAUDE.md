# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a FastAPI-based web application providing a simple form interface with RESTful API endpoints. The application serves both the frontend (embedded HTML/CSS/JS) and backend API from a single Python file.

## Development Commands

### Running the server
```bash
python main.py
```
Or with auto-reload for development:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Installing dependencies
```bash
pip install -r requirements.txt
```

### Testing API endpoints
```bash
# Submit details
curl -X POST "http://localhost:8000/postDetails" \
  -H "Content-Type: application/json" \
  -d '{"name":"John Doe","email":"john@example.com","message":"Test message"}'

# Get all details
curl "http://localhost:8000/getDetails"

# Clear all details
curl -X DELETE "http://localhost:8000/clearDetails"

# Health check
curl "http://localhost:8000/health"
```

## Architecture

### Project Structure

```
subagents/
├── main.py              # FastAPI application (all code in one file)
├── requirements.txt     # Python dependencies
├── README.md           # User documentation
├── CLAUDE.md           # This file (developer guidance)
├── __pycache__/        # Python bytecode cache (auto-generated)
└── venv/               # Virtual environment (not tracked)
```

### Monolithic Single-File Design
The entire application resides in `main.py:1-369`, including:
- Backend API endpoints (FastAPI)
- Frontend UI (HTML/CSS/JS embedded in Python string)
- Data models (Pydantic)
- In-memory storage

### Data Flow
1. **Storage Layer**: `data_store` (main.py:12) - Global list acting as in-memory database
2. **Validation Layer**: Pydantic models `DetailItem` (main.py:16-19) and `DetailResponse` (main.py:22-27)
3. **API Layer**: FastAPI endpoints handling CRUD operations
4. **Frontend Layer**: Embedded HTML page served at root with vanilla JavaScript for API calls

### Key Components

**Data Models (main.py:16-27)**
- `DetailItem`: Input validation model with constraints (name 1-100 chars, email regex, message 1-500 chars)
- `DetailResponse`: Output model including auto-generated UUID and timestamp

**API Endpoints (main.py:30-363)**
- `GET /`: Returns embedded HTML page with form and data display
- `POST /postDetails`: Creates new entry with UUID and timestamp (main.py:308-325)
- `GET /getDetails`: Returns all stored entries (main.py:328-333)
- `GET /getDetails/{detail_id}`: Returns single entry by ID (main.py:336-345)
- `DELETE /clearDetails`: Clears all data (main.py:348-354)
- `GET /health`: Health check with record count (main.py:357-363)

**Frontend Integration (main.py:33-304)**
- Self-contained SPA with form submission, data display, and refresh/clear actions
- Vanilla JavaScript (no frameworks) making fetch() calls to API
- XSS prevention via `escapeHtml()` function (main.py:296-300)

## Important Constraints

### In-Memory Storage
Data persists only during server runtime. All data is lost on restart. The `data_store` list (main.py:12) is the sole data storage mechanism.

### No Separation of Concerns
Frontend and backend are tightly coupled in a single file. To modify UI, edit the HTML string in `read_root()` (main.py:33-304). To modify API logic, edit the endpoint functions below line 307.

### Validation
Email validation uses regex pattern (main.py:18). Name and message have length constraints enforced by Pydantic Field validators.

## When Making Changes

- **Adding endpoints**: Follow existing async function pattern and use Pydantic models for validation
- **Modifying UI**: Edit the HTML string in `read_root()` function (lines 33-304)
- **Changing data structure**: Update both `DetailItem` and `DetailResponse` models, plus `data_store` dict structure
- **Adding persistence**: Replace `data_store` list with database connection (SQLAlchemy, MongoDB, etc.)
- for running the server - use the python in the venv - /Users/mehulmathur/Opius/practice/subagents/venv/bin/python3