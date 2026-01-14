"""ChatKit server implementation for AI-powered todo chatbot with MCP tools."""

from collections import defaultdict
from collections.abc import AsyncIterator
from datetime import datetime

from fastapi import APIRouter, Request
from fastapi.responses import Response, StreamingResponse

from agents import Runner
from chatkit.server import ChatKitServer, StreamingResult
from chatkit.store import Store, NotFoundError
from chatkit.types import (
    Attachment,
    Page,
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
from sqlmodel import Session
from agent.runner import todo_assistant, set_context, TodoContext

router = APIRouter(prefix="/api", tags=["ChatKit"])


class RequestContext:
    """Context passed through ChatKit operations."""
    def __init__(self, user_id: str, db_session: Session = None):
        self.user_id = user_id
        self.db_session = db_session


class InMemoryChatKitStore(Store[RequestContext]):
    """In-memory store for ChatKit threads and items."""

    def __init__(self):
        self.threads: dict[str, ThreadMetadata] = {}
        self.items: dict[str, list[ThreadItem]] = defaultdict(list)
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
        self.items[thread_id].append(item)

    async def save_item(self, thread_id: str, item: ThreadItem, context: RequestContext) -> None:
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
        self.items[thread_id] = [i for i in self.items.get(thread_id, []) if i.id != item_id]

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
        """Generate response using the todo agent with MCP tools."""

        # Set up context for MCP tool operations
        set_context(TodoContext(
            user_id=context.user_id,
            session=context.db_session,
        ))

        try:
            # Load conversation history
            items_page = await self.store.load_thread_items(
                thread.id, after=None, limit=20, order="asc", context=context
            )

            # Convert to agent input format
            input_items = await simple_to_agent_input(items_page.data)

            # Create agent context
            agent_context = AgentContext(
                thread=thread,
                store=self.store,
                request_context=context,
            )

            # Run agent with MCP tools and stream response
            result = Runner.run_streamed(
                todo_assistant,
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
server = TodoChatKitServer(store=store)


@router.post("/chatkit")
async def chatkit_endpoint(request: Request):
    """Main ChatKit endpoint - handles all chat operations."""

    # Extract user from auth cookie
    auth_header = request.headers.get("authorization", "")
    user_id = "anonymous"

    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
        try:
            from auth import decode_token
            payload = decode_token(token)
            user_id = payload.get("sub", "anonymous")
        except Exception:
            pass

    # Create database session
    with Session(engine) as db_session:
        context = RequestContext(user_id=user_id, db_session=db_session)

        result = await server.process(await request.body(), context)

        if isinstance(result, StreamingResult):
            return StreamingResponse(result, media_type="text/event-stream")
        return Response(content=result.json, media_type="application/json")
