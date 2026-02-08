"""ChatKit server and REST chat endpoint for AI-powered todo chatbot with MCP tools."""

import uuid
from collections.abc import AsyncIterator
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Request
from fastapi.responses import Response, StreamingResponse
from pydantic import BaseModel

from agents import Runner
from chatkit.server import ChatKitServer, StreamingResult
from chatkit.store import Store, NotFoundError, Page
from chatkit.types import (
    Attachment,
    ThreadItem,
    ThreadMetadata,
    UserMessageItem,
    ThreadStreamEvent,
    AssistantMessageItem,
    AssistantMessageContent,
    ThreadItemDoneEvent,
)
from chatkit.agents import AgentContext, simple_to_agent_input, stream_agent_response

from db import engine
from sqlmodel import Session, select
from models import Conversation, ChatMessage, MessageRole

router = APIRouter(prefix="/api", tags=["Chat"])


# ---------------------------------------------------------------------------
# REST endpoint: POST /api/{user_id}/chat
# ---------------------------------------------------------------------------

class ChatRestRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None


class ChatRestResponse(BaseModel):
    conversation_id: str
    response: str
    tool_calls: Optional[list[dict]] = None


@router.post("/{user_id}/chat", response_model=ChatRestResponse)
async def rest_chat(user_id: str, body: ChatRestRequest, request: Request):
    """Stateless REST chat endpoint with DB-persisted conversations."""
    agent = request.app.state.todo_agent

    with Session(engine) as db:
        # Get or create conversation
        if body.conversation_id:
            conversation = db.get(Conversation, body.conversation_id)
            if not conversation or conversation.user_id != user_id:
                conversation = None

        if not body.conversation_id or conversation is None:
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

    return ChatRestResponse(
        conversation_id=conversation.id,
        response=response_text,
        tool_calls=tool_calls_info if tool_calls_info else None,
    )


# ---------------------------------------------------------------------------
# ChatKit server (streaming, used by the ChatKit frontend widget)
# ---------------------------------------------------------------------------

class RequestContext:
    """Context passed through ChatKit operations."""
    def __init__(self, user_id: str, agent=None):
        self.user_id = user_id
        self.agent = agent


class InMemoryChatKitStore(Store[RequestContext]):
    """In-memory store for ChatKit threads and items."""

    def __init__(self):
        self.threads: dict[str, ThreadMetadata] = {}
        self.items: dict[str, list[ThreadItem]] = {}
        self.attachments: dict[str, Attachment] = {}

    async def load_thread(self, thread_id: str, context: RequestContext) -> ThreadMetadata:
        if thread_id not in self.threads:
            raise NotFoundError(f"Thread {thread_id} not found")
        return self.threads[thread_id]

    async def save_thread(self, thread: ThreadMetadata, context: RequestContext) -> None:
        self.threads[thread.id] = thread

    async def load_threads(
        self, limit: int, after: str | None, order: str, context: RequestContext
    ) -> Page[ThreadMetadata]:
        threads = list(self.threads.values())
        return self._paginate(threads, after, limit, order, lambda t: t.created_at, lambda t: t.id)

    async def load_thread_items(
        self, thread_id: str, after: str | None, limit: int, order: str, context: RequestContext
    ) -> Page[ThreadItem]:
        items = self.items.get(thread_id, [])
        return self._paginate(items, after, limit, order, lambda i: i.created_at, lambda i: i.id)

    async def add_thread_item(self, thread_id: str, item: ThreadItem, context: RequestContext) -> None:
        if thread_id not in self.items:
            self.items[thread_id] = []
        self.items[thread_id].append(item)

    async def save_item(self, thread_id: str, item: ThreadItem, context: RequestContext) -> None:
        if thread_id not in self.items:
            self.items[thread_id] = []
        items = self.items[thread_id]
        for idx, existing in enumerate(items):
            if existing.id == item.id:
                items[idx] = item
                return
        items.append(item)

    async def load_item(self, thread_id: str, item_id: str, context: RequestContext) -> ThreadItem:
        for item in self.items.get(thread_id, []):
            if item.id == item_id:
                return item
        raise NotFoundError(f"Item {item_id} not found")

    async def delete_thread(self, thread_id: str, context: RequestContext) -> None:
        self.threads.pop(thread_id, None)
        self.items.pop(thread_id, None)

    async def delete_thread_item(self, thread_id: str, item_id: str, context: RequestContext) -> None:
        if thread_id in self.items:
            self.items[thread_id] = [i for i in self.items[thread_id] if i.id != item_id]

    async def save_attachment(self, attachment: Attachment, context: RequestContext) -> None:
        self.attachments[attachment.id] = attachment

    async def load_attachment(self, attachment_id: str, context: RequestContext) -> Attachment:
        if attachment_id not in self.attachments:
            raise NotFoundError(f"Attachment {attachment_id} not found")
        return self.attachments[attachment_id]

    async def delete_attachment(self, attachment_id: str, context: RequestContext) -> None:
        self.attachments.pop(attachment_id, None)

    def _paginate(self, rows, after, limit, order, sort_key, cursor_key):
        sorted_rows = sorted(rows, key=sort_key, reverse=order == "desc")
        start = 0
        if after:
            for idx, row in enumerate(sorted_rows):
                if cursor_key(row) == after:
                    start = idx + 1
                    break
        data = sorted_rows[start:start + limit]
        has_more = start + limit < len(sorted_rows)
        next_after = cursor_key(data[-1]) if has_more and data else None
        return Page(data=data, has_more=has_more, after=next_after)


# Global store instance
store = InMemoryChatKitStore()


class TodoChatKitServer(ChatKitServer[RequestContext]):
    """ChatKit server with MCP tools for todo management."""

    async def respond(
        self,
        thread: ThreadMetadata,
        input_user_message: UserMessageItem | None,
        context: RequestContext,
    ) -> AsyncIterator[ThreadStreamEvent]:
        """Generate response using the MCP-backed todo agent."""
        agent = context.agent
        if agent is None:
            yield ThreadItemDoneEvent(
                item=AssistantMessageItem(
                    thread_id=thread.id,
                    id=self.store.generate_item_id("message", thread, context),
                    created_at=datetime.now(),
                    content=[AssistantMessageContent(
                        text="Agent not available. Please try again later."
                    )],
                )
            )
            return

        try:
            # Load conversation history
            items_page = await self.store.load_thread_items(
                thread.id, after=None, limit=20, order="asc", context=context
            )

            # Convert to agent input format and prepend user_id system message
            input_items = await simple_to_agent_input(items_page.data)
            input_items.insert(0, {
                "role": "system",
                "content": f"The current user_id is: {context.user_id}. Always pass this user_id to every tool call.",
            })

            # Create agent context
            agent_context = AgentContext(
                thread=thread,
                store=self.store,
                request_context=context,
            )

            # Run agent with MCP tools and stream response
            result = Runner.run_streamed(
                agent,
                input_items,
                context=agent_context,
            )

            async for event in stream_agent_response(agent_context, result):
                yield event

        except Exception as e:
            print(f"ChatKit error: {e}")
            yield ThreadItemDoneEvent(
                item=AssistantMessageItem(
                    thread_id=thread.id,
                    id=self.store.generate_item_id("message", thread, context),
                    created_at=datetime.now(),
                    content=[AssistantMessageContent(
                        text="I'm having trouble right now. Please try again."
                    )],
                )
            )


# Create server instance
chatkit_server = TodoChatKitServer(store=store)


@router.api_route("/chatkit", methods=["GET", "POST"])
async def chatkit_endpoint(request: Request):
    """Main ChatKit endpoint - handles all chat operations."""

    if request.method == "GET":
        return Response(
            content='{"status": "ok", "service": "chatkit"}',
            media_type="application/json"
        )

    # Extract user from auth header
    auth_header = request.headers.get("authorization", "")
    user_id = "anonymous"

    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
        try:
            from auth import decode_token
            payload = decode_token(token)
            if payload:
                user_id = payload.get("sub", "anonymous")
        except Exception:
            pass

    # Get agent from app state
    agent = request.app.state.todo_agent

    context = RequestContext(user_id=user_id, agent=agent)

    try:
        result = await chatkit_server.process(await request.body(), context)
    except Exception as e:
        raise e

    if isinstance(result, StreamingResult):
        return StreamingResponse(result, media_type="text/event-stream")

    return Response(content=result.json, media_type="application/json")
