"""Chat API endpoints for AI-powered todo chatbot."""

import uuid
import time
from datetime import datetime
from typing import Optional
from collections import defaultdict
from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from sqlmodel import Session, select, func

from db import get_session
from auth import get_current_user
from models import (
    User,
    Conversation,
    ChatMessage,
    MessageRole,
    ChatRequest,
    ChatResponse,
    ConversationSummary,
    ConversationListResponse,
    ChatMessageResponse,
    ConversationDetailResponse,
)
from agent.runner import run_agent

router = APIRouter(prefix="/api/chat", tags=["Chat"])

# Simple in-memory rate limiting (per user)
# In production, use Redis or similar
RATE_LIMIT_REQUESTS = 10  # max requests
RATE_LIMIT_WINDOW = 60  # per 60 seconds
_rate_limit_store: dict[str, list[float]] = defaultdict(list)


def check_rate_limit(user_id: str) -> tuple[bool, int]:
    """Check if user is rate limited. Returns (is_limited, retry_after_seconds)."""
    now = time.time()
    window_start = now - RATE_LIMIT_WINDOW

    # Clean old entries
    _rate_limit_store[user_id] = [
        ts for ts in _rate_limit_store[user_id] if ts > window_start
    ]

    # Check limit
    if len(_rate_limit_store[user_id]) >= RATE_LIMIT_REQUESTS:
        oldest = min(_rate_limit_store[user_id])
        retry_after = int(oldest + RATE_LIMIT_WINDOW - now) + 1
        return True, retry_after

    # Record this request
    _rate_limit_store[user_id].append(now)
    return False, 0


def get_or_create_conversation(
    session: Session,
    user_id: str,
    conversation_id: Optional[str] = None,
) -> Conversation:
    """Get existing conversation or create a new one."""
    if conversation_id:
        conversation = session.exec(
            select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id,
            )
        ).first()
        if conversation:
            return conversation

    # Create new conversation
    conversation = Conversation(
        id=str(uuid.uuid4()),
        user_id=user_id,
    )
    session.add(conversation)
    session.commit()
    session.refresh(conversation)
    return conversation


def load_conversation_history(
    session: Session,
    conversation_id: str,
    limit: int = 10,
) -> list[dict]:
    """Load recent messages from a conversation."""
    messages = session.exec(
        select(ChatMessage)
        .where(ChatMessage.conversation_id == conversation_id)
        .order_by(ChatMessage.created_at.desc())
        .limit(limit)
    ).all()

    # Reverse to get chronological order
    messages = list(reversed(messages))

    return [
        {
            "role": msg.role.value,
            "content": msg.content,
            "tool_calls": msg.tool_calls,
        }
        for msg in messages
    ]


def save_message(
    session: Session,
    conversation_id: str,
    role: MessageRole,
    content: str,
    tool_calls: Optional[dict] = None,
) -> ChatMessage:
    """Save a message to the conversation."""
    message = ChatMessage(
        id=str(uuid.uuid4()),
        conversation_id=conversation_id,
        role=role,
        content=content,
        tool_calls=tool_calls,
    )
    session.add(message)
    session.commit()
    return message


@router.post("", response_model=ChatResponse)
async def send_chat_message(
    request: ChatRequest,
    response: Response,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Send a chat message and get AI response.

    The AI assistant will interpret the natural language message
    and perform task operations via MCP tools.
    """
    # Check rate limit
    is_limited, retry_after = check_rate_limit(current_user.id)
    if is_limited:
        response.headers["Retry-After"] = str(retry_after)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "code": "RATE_LIMIT",
                "message": "Too many requests. Please wait a moment.",
            },
        )

    # Validate message
    if not request.message or not request.message.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "VALIDATION_ERROR", "message": "Message cannot be empty"},
        )

    # Get or create conversation
    conversation = get_or_create_conversation(
        session,
        current_user.id,
        request.conversation_id,
    )

    # Load conversation history for context
    history = load_conversation_history(session, conversation.id)

    # Save user message
    save_message(session, conversation.id, MessageRole.user, request.message)

    try:
        # Run the AI agent
        response_text, tool_results = run_agent(
            session=session,
            user_id=current_user.id,
            message=request.message,
            conversation_history=history,
        )

        # Save assistant response
        save_message(
            session,
            conversation.id,
            MessageRole.assistant,
            response_text,
            tool_calls={"results": tool_results} if tool_results else None,
        )

        # Update conversation timestamp
        conversation.updated_at = datetime.utcnow()
        session.add(conversation)
        session.commit()

        return ChatResponse(
            response=response_text,
            conversation_id=conversation.id,
            tool_results=tool_results if tool_results else None,
        )

    except Exception as e:
        # Log error but return user-friendly message
        print(f"Chat error: {e}")
        error_response = "I'm having trouble processing your request right now. Please try again in a moment."

        # Save error response
        save_message(
            session,
            conversation.id,
            MessageRole.assistant,
            error_response,
        )

        return ChatResponse(
            response=error_response,
            conversation_id=conversation.id,
            tool_results=None,
        )


@router.get("/conversations", response_model=ConversationListResponse)
async def list_conversations(
    limit: int = Query(default=10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """List user's conversations ordered by most recent."""
    conversations = session.exec(
        select(Conversation)
        .where(Conversation.user_id == current_user.id)
        .order_by(Conversation.updated_at.desc())
        .limit(limit)
    ).all()

    # Get message counts for each conversation
    summaries = []
    for conv in conversations:
        count = session.exec(
            select(func.count(ChatMessage.id))
            .where(ChatMessage.conversation_id == conv.id)
        ).first() or 0

        summaries.append(ConversationSummary(
            id=conv.id,
            title=conv.title,
            created_at=conv.created_at.isoformat() + "Z",
            updated_at=conv.updated_at.isoformat() + "Z",
            message_count=count,
        ))

    total = session.exec(
        select(func.count(Conversation.id))
        .where(Conversation.user_id == current_user.id)
    ).first() or 0

    return ConversationListResponse(
        conversations=summaries,
        total=total,
    )


@router.get("/conversations/{conversation_id}", response_model=ConversationDetailResponse)
async def get_conversation(
    conversation_id: str,
    limit: int = Query(default=50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Get a conversation with its messages."""
    conversation = session.exec(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id,
        )
    ).first()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "Conversation not found"},
        )

    messages = session.exec(
        select(ChatMessage)
        .where(ChatMessage.conversation_id == conversation_id)
        .order_by(ChatMessage.created_at.asc())
        .limit(limit)
    ).all()

    return ConversationDetailResponse(
        id=conversation.id,
        title=conversation.title,
        messages=[
            ChatMessageResponse(
                id=msg.id,
                role=msg.role,
                content=msg.content,
                tool_calls=msg.tool_calls,
                created_at=msg.created_at.isoformat() + "Z",
            )
            for msg in messages
        ],
        created_at=conversation.created_at.isoformat() + "Z",
        updated_at=conversation.updated_at.isoformat() + "Z",
    )
