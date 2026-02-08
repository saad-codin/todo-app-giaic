"""FastAPI main application entry point."""

import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from agents import Agent
from agents.mcp import MCPServerStdio

from db import create_db_and_tables
from routes.auth import router as auth_router
from routes.tasks import router as tasks_router
from routes.chat import router as chat_router

load_dotenv()

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

AGENT_INSTRUCTIONS = """You are a helpful todo task assistant. Your job is to help users manage their tasks through natural conversation.

You can:
- Create new tasks (with optional priority, due date, and tags)
- List and view tasks (with optional filters)
- Mark tasks as complete
- Update task details (description, priority, due date, tags)
- Delete tasks

Guidelines:
1. Be friendly and conversational
2. Confirm actions clearly (e.g., "I've added 'buy groceries' to your list")
3. When listing tasks, format them nicely and ask if the user wants to take action
4. When a task isn't found, offer to show the task list or suggest alternatives
5. For ambiguous references like "it" or "that one", use context from the conversation
6. If the user's message isn't about tasks, politely redirect them

IMPORTANT: Every tool call requires a user_id parameter. You will receive the user_id
in a system message at the start of the conversation. Always pass that user_id to every
tool call you make.

Remember to use natural language dates when possible (today, tomorrow, Friday)."""


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler - starts MCP subprocess."""
    create_db_and_tables()

    mcp_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mcp_server.py")
    mcp_server = MCPServerStdio(
        name="TodoMCP",
        params={
            "command": sys.executable,
            "args": [mcp_script],
            "cwd": os.path.dirname(os.path.abspath(__file__)),
            "env": {**os.environ},
        },
        cache_tools_list=True,
    )

    server = await mcp_server.__aenter__()
    app.state.mcp_server = mcp_server
    app.state.todo_agent = Agent(
        name="TodoAssistant",
        instructions=AGENT_INSTRUCTIONS,
        model="gpt-4o-mini",
        mcp_servers=[server],
    )

    yield

    await mcp_server.__aexit__(None, None, None)


app = FastAPI(
    title="Todo App API",
    description="Backend API for Todo App Frontend Dashboard",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        FRONTEND_URL,
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://todo-app-giaic.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(tasks_router)
app.include_router(chat_router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Todo App API", "version": "1.0.0"}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}
