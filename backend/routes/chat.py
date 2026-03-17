"""REST chat endpoint for AI-powered todo chatbot with MCP tools."""

import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import Response
from pydantic import BaseModel

from agents import Runner

from auth import get_current_user
from db import engine
from sqlmodel import Session, select
from sqlalchemy import func
from models import Conversation, ChatMessage, MessageRole, User

router = APIRouter(prefix="/api", tags=["Chat"])


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------

class ChatRestRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None


class ChatRestResponse(BaseModel):
    conversation_id: str
    response: str
    tool_calls: Optional[list[dict]] = None


# ---------------------------------------------------------------------------
# Shared chat logic
# ---------------------------------------------------------------------------

async def _run_chat(user_id: str, body: ChatRestRequest, app) -> ChatRestResponse:
    """Core chat logic shared by auth and user-id endpoints."""
    agent = getattr(app.state, "todo_agent", None)
    if agent is None:
        raise HTTPException(
            status_code=503,
            detail="Chat service unavailable — AI agent not initialized. Check OPENAI_API_KEY.",
        )

    with Session(engine) as db:
        # Get or create conversation
        conversation = None
        if body.conversation_id:
            conversation = db.get(Conversation, body.conversation_id)
            if not conversation or conversation.user_id != user_id:
                conversation = None

        if conversation is None:
            conversation = Conversation(
                id=str(uuid.uuid4()),
                user_id=user_id,
                title=body.message[:100],
            )
            db.add(conversation)
            db.commit()
            db.refresh(conversation)

        # Load last 20 messages as history
        history_rows = db.exec(
            select(ChatMessage)
            .where(ChatMessage.conversation_id == conversation.id)
            .order_by(ChatMessage.created_at.desc())
            .limit(20)
        ).all()
        history_rows = list(reversed(history_rows))

        # Build agent input
        input_messages = [
            {"role": "system", "content": f"The current user_id is: {user_id}. Always pass this user_id to every tool call."},
        ]
        for row in history_rows:
            input_messages.append({"role": row.role.value, "content": row.content})
        input_messages.append({"role": "user", "content": body.message})

        # Save user message
        user_msg = ChatMessage(
            id=str(uuid.uuid4()),
            conversation_id=conversation.id,
            role=MessageRole.user,
            content=body.message,
        )
        db.add(user_msg)
        db.commit()

        # Run agent
        result = await Runner.run(agent, input_messages)

        # Extract response text
        response_text = result.final_output or ""

        # Collect tool call info
        tool_calls_info = []
        for item in result.new_items:
            if hasattr(item, "raw_item") and hasattr(item.raw_item, "type"):
                if item.raw_item.type == "function_call_output":
                    tool_calls_info.append({
                        "call_id": getattr(item.raw_item, "call_id", None),
                        "output": getattr(item.raw_item, "output", None),
                    })

        # Save assistant message
        assistant_msg = ChatMessage(
            id=str(uuid.uuid4()),
            conversation_id=conversation.id,
            role=MessageRole.assistant,
            content=response_text,
            tool_calls=tool_calls_info if tool_calls_info else None,
        )
        db.add(assistant_msg)

        conversation.updated_at = datetime.utcnow()
        db.add(conversation)
        db.commit()

        # Capture id before session closes (avoids DetachedInstanceError)
        conversation_id = conversation.id

    return ChatRestResponse(
        conversation_id=conversation_id,
        response=response_text,
        tool_calls=tool_calls_info if tool_calls_info else None,
    )


# ---------------------------------------------------------------------------
# POST /api/chat — auth-based (extracts user_id from JWT)
# ---------------------------------------------------------------------------

@router.post("/chat", response_model=ChatRestResponse)
async def auth_chat(
    body: ChatRestRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
):
    """Chat endpoint using JWT auth — no user_id required in URL."""
    return await _run_chat(current_user.id, body, request.app)


# ---------------------------------------------------------------------------
# POST /api/{user_id}/chat — legacy endpoint (user_id in URL)
# ---------------------------------------------------------------------------

@router.post("/{user_id}/chat", response_model=ChatRestResponse)
async def rest_chat(user_id: str, body: ChatRestRequest, request: Request):
    """Stateless REST chat endpoint with DB-persisted conversations."""
    return await _run_chat(user_id, body, request.app)


# ---------------------------------------------------------------------------
# GET /api/chat/conversations — list conversations for current user
# ---------------------------------------------------------------------------

class ConversationSummary(BaseModel):
    id: str
    title: Optional[str]
    created_at: str
    updated_at: str
    message_count: int


class ConversationListResponse(BaseModel):
    conversations: list[ConversationSummary]
    total: int


@router.get("/chat/conversations", response_model=ConversationListResponse)
async def list_conversations(
    request: Request,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
):
    """List conversations for the authenticated user."""
    with Session(engine) as db:
        rows = db.exec(
            select(Conversation)
            .where(Conversation.user_id == current_user.id)
            .order_by(Conversation.updated_at.desc())
            .limit(limit)
        ).all()

        summaries = []
        for conv in rows:
            count = db.exec(
                select(func.count(ChatMessage.id))
                .where(ChatMessage.conversation_id == conv.id)
            ).one()
            summaries.append(ConversationSummary(
                id=conv.id,
                title=conv.title,
                created_at=conv.created_at.isoformat(),
                updated_at=conv.updated_at.isoformat(),
                message_count=count,
            ))

    return ConversationListResponse(conversations=summaries, total=len(summaries))


# ---------------------------------------------------------------------------
# GET /api/chat/conversations/{id} — conversation detail with messages
# ---------------------------------------------------------------------------

class ChatMessageOut(BaseModel):
    id: str
    role: str
    content: str
    tool_calls: Optional[list[dict]] = None
    created_at: str


class ConversationDetailResponse(BaseModel):
    id: str
    title: Optional[str]
    messages: list[ChatMessageOut]
    created_at: str
    updated_at: str


@router.get("/chat/conversations/{conversation_id}", response_model=ConversationDetailResponse)
async def get_conversation(
    conversation_id: str,
    request: Request,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
):
    """Get a conversation with its messages."""
    with Session(engine) as db:
        conversation = db.get(Conversation, conversation_id)
        if not conversation or conversation.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="Conversation not found")

        messages = db.exec(
            select(ChatMessage)
            .where(ChatMessage.conversation_id == conversation_id)
            .order_by(ChatMessage.created_at.asc())
            .limit(limit)
        ).all()

    return ConversationDetailResponse(
        id=conversation.id,
        title=conversation.title,
        messages=[
            ChatMessageOut(
                id=m.id,
                role=m.role.value,
                content=m.content,
                tool_calls=m.tool_calls if isinstance(m.tool_calls, list) else None,
                created_at=m.created_at.isoformat(),
            )
            for m in messages
        ],
        created_at=conversation.created_at.isoformat(),
        updated_at=conversation.updated_at.isoformat(),
    )


# ---------------------------------------------------------------------------
# ChatKit stub (kept for compatibility, returns 501)
# ---------------------------------------------------------------------------

@router.api_route("/chatkit", methods=["GET", "POST"])
async def chatkit_endpoint(request: Request):
    """ChatKit endpoint stub — use POST /api/chat instead."""
    if request.method == "GET":
        return Response(
            content='{"status": "ok", "service": "chatkit"}',
            media_type="application/json"
        )
    return Response(
        content='{"error": "ChatKit server not available. Use POST /api/chat instead."}',
        media_type="application/json",
        status_code=501
    )
