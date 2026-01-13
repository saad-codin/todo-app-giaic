# Quickstart: AI-Powered Todo Chatbot

**Feature**: 004-ai-todo-chatbot
**Date**: 2026-01-13

## Prerequisites

- Node.js 18+ (for frontend)
- Python 3.11+ (for backend)
- Neon PostgreSQL database (existing from Phase II)
- OpenAI API key

## Environment Setup

### 1. Backend Environment

Create/update `backend/.env`:

```env
# Existing Phase II variables
DATABASE_URL=postgresql://user:pass@host/db?sslmode=require
SECRET_KEY=your-secret-key-min-32-characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
FRONTEND_URL=http://localhost:3000

# New Phase III variables
OPENAI_API_KEY=sk-your-openai-api-key
OPENAI_MODEL=gpt-4-turbo-preview
MAX_CONVERSATION_MESSAGES=10
```

### 2. Frontend Environment

Create/update `frontend/.env.local`:

```env
# Existing
NEXT_PUBLIC_API_URL=http://localhost:8000
BETTER_AUTH_SECRET=your-secret-key-min-32-characters
BETTER_AUTH_URL=http://localhost:3000
```

## Installation

### Backend

```bash
cd backend

# Install new dependencies
pip install openai agents-sdk mcp-sdk

# Or update requirements.txt and install
pip install -r requirements.txt

# Run database migrations (for conversation tables)
python -c "from db import create_db_and_tables; create_db_and_tables()"
```

### Frontend

```bash
cd frontend

# Install ChatKit dependency
npm install @openai/chatkit

# Start development server
npm run dev
```

## Running the Application

### Start Backend

```bash
cd backend
uvicorn main:app --reload --port 8000
```

### Start Frontend

```bash
cd frontend
npm run dev
```

### Access the Application

- **Dashboard**: http://localhost:3000/dashboard (existing Phase II)
- **Chat Interface**: http://localhost:3000/chat (new Phase III)
- **API Docs**: http://localhost:8000/docs

## Quick Test

### 1. Sign In

Use existing credentials or create account at http://localhost:3000

### 2. Open Chat

Navigate to http://localhost:3000/chat

### 3. Try These Commands

```
"Add buy groceries to my list"
→ Creates task with description "buy groceries"

"Show my tasks"
→ Lists all your tasks

"Add high priority task: finish report by Friday"
→ Creates task with high priority and due date

"Mark buy groceries as done"
→ Completes the task

"What do I need to do today?"
→ Shows tasks due today

"Delete the groceries task"
→ Removes the completed task
```

## API Testing

### Send Chat Message

```bash
# Get auth token first
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/signin \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}' \
  | jq -r '.token')

# Send chat message
curl -X POST http://localhost:8000/api/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Add buy milk to my list"}'
```

### Expected Response

```json
{
  "response": "I've added 'buy milk' to your tasks. Is there anything else you'd like to add?",
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "tool_results": [
    {
      "tool": "create_task",
      "success": true,
      "task_id": "660e8400-e29b-41d4-a716-446655440001"
    }
  ]
}
```

## Troubleshooting

### "OPENAI_API_KEY not set"

Ensure your `.env` file has a valid OpenAI API key:
```env
OPENAI_API_KEY=sk-...
```

### "I'm having trouble thinking right now"

The AI service may be unavailable. Check:
1. OpenAI API key is valid
2. OpenAI service status at status.openai.com
3. Rate limits not exceeded

### "Please sign in to continue"

JWT token missing or expired. Re-authenticate via `/api/auth/signin`.

### Database connection errors

Verify `DATABASE_URL` in `.env` and ensure Neon database is accessible.

## Architecture Overview

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Frontend      │     │    Backend      │     │   Database      │
│   (ChatKit)     │────▶│   (FastAPI)     │────▶│   (Neon PG)     │
└─────────────────┘     └────────┬────────┘     └─────────────────┘
                                 │
                        ┌────────▼────────┐
                        │  OpenAI Agent   │
                        │  (Agents SDK)   │
                        └────────┬────────┘
                                 │
                        ┌────────▼────────┐
                        │   MCP Tools     │
                        │ (Task Operations)│
                        └─────────────────┘
```

## Next Steps

1. **Implement backend chat endpoint** - `routes/chat.py`
2. **Create MCP tools** - `mcp/tools.py`
3. **Set up agent runner** - `agent/runner.py`
4. **Build chat UI** - `frontend/src/app/chat/page.tsx`
5. **Add conversation models** - `models.py`

See `tasks.md` (after running `/sp.tasks`) for detailed implementation tasks.
