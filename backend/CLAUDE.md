# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Stack

- FastAPI (Python)
- SQLModel (ORM)
- SQLite (local development)
- JWT Authentication (python-jose)

## Commands

```bash
# Development server
cd backend && uvicorn main:app --reload --port 8000

# Run tests
cd backend && pytest

# Run single test
cd backend && pytest tests/test_api.py -k "test_name"
```

## Project Structure

```
backend/
├── main.py           # FastAPI app entry point with CORS config
├── models.py         # SQLModel database models (User, Task)
├── db.py             # Database connection and session management
├── auth.py           # JWT authentication utilities
├── routes/
│   ├── __init__.py
│   ├── auth.py       # Auth endpoints (signup, signin, signout, me)
│   └── tasks.py      # Task CRUD endpoints
├── requirements.txt  # Python dependencies
└── .env              # Environment variables
```

## API Endpoints

### Authentication
- `POST /api/auth/signup` - Create account
- `POST /api/auth/signin` - Sign in (sets JWT cookie)
- `POST /api/auth/signout` - Sign out (clears cookie)
- `GET /api/auth/me` - Get current user

### Tasks (requires authentication)
- `GET /api/tasks` - List tasks with filtering/sorting
- `POST /api/tasks` - Create task
- `GET /api/tasks/:id` - Get single task
- `PATCH /api/tasks/:id` - Update task
- `DELETE /api/tasks/:id` - Delete task
- `POST /api/tasks/:id/complete` - Mark complete (handles recurring)
- `POST /api/tasks/:id/incomplete` - Mark incomplete

## API Conventions

- All routes under `/api/`
- Return JSON responses
- Use Pydantic models for request/response
- Handle errors with `HTTPException`
- JWT token stored in httpOnly cookie named `auth_token`

## Database

- SQLite database stored at `./todo.db`
- Auto-created on first run
- Connection string from `DATABASE_URL` environment variable

## Environment Variables

```env
DATABASE_URL=sqlite:///./todo.db
SECRET_KEY=your-secret-key-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
FRONTEND_URL=http://localhost:3000
```
