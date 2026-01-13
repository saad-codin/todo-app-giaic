"""AI Agent runner for todo chatbot.

Uses OpenAI Agents SDK for intent recognition and tool execution.
"""

import os
import json
from typing import Optional
from dataclasses import dataclass
from openai import OpenAI
from sqlmodel import Session

from mcp.tools import (
    create_task,
    list_tasks,
    search_tasks,
    complete_task,
    update_task,
    delete_task,
)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Tool definitions for the agent
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "create_task",
            "description": "Create a new task for the user. Use this when the user wants to add, create, or make a new task.",
            "parameters": {
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string",
                        "description": "The task description (what needs to be done)"
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["high", "medium", "low"],
                        "description": "Task priority level"
                    },
                    "due_date": {
                        "type": "string",
                        "description": "Due date - can be YYYY-MM-DD or natural language like 'tomorrow', 'Friday', 'next week'"
                    },
                    "due_time": {
                        "type": "string",
                        "description": "Due time in HH:MM format"
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Tags for organizing the task"
                    }
                },
                "required": ["description"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_tasks",
            "description": "List the user's tasks. Use this when the user wants to see, view, or show their tasks.",
            "parameters": {
                "type": "object",
                "properties": {
                    "completed": {
                        "type": "boolean",
                        "description": "Filter by completion status. True for completed tasks, False for incomplete."
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["high", "medium", "low"],
                        "description": "Filter by priority level"
                    },
                    "due_date": {
                        "type": "string",
                        "description": "Filter by due date - can be 'today', 'tomorrow', or YYYY-MM-DD"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_tasks",
            "description": "Search for tasks by description. Use this when the user is looking for a specific task.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query to find matching tasks"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "complete_task",
            "description": "Mark a task as complete. Use this when the user wants to mark, complete, finish, or check off a task.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "The ID of the task to complete (if known)"
                    },
                    "description_match": {
                        "type": "string",
                        "description": "Part of the task description to match (for finding the task)"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_task",
            "description": "Update a task's details. Use this when the user wants to change, modify, edit, or update a task.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "The ID of the task to update (if known)"
                    },
                    "description_match": {
                        "type": "string",
                        "description": "Part of the task description to match (for finding the task)"
                    },
                    "new_description": {
                        "type": "string",
                        "description": "New description for the task"
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["high", "medium", "low"],
                        "description": "New priority level"
                    },
                    "due_date": {
                        "type": "string",
                        "description": "New due date"
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "New tags list"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_task",
            "description": "Delete a task. Use this when the user wants to remove, delete, or discard a task.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "The ID of the task to delete (if known)"
                    },
                    "description_match": {
                        "type": "string",
                        "description": "Part of the task description to match (for finding the task)"
                    }
                }
            }
        }
    }
]

SYSTEM_PROMPT = """You are a helpful todo task assistant. Your job is to help users manage their tasks through natural conversation.

You can:
- Create new tasks (with optional priority, due date, time, and tags)
- List and view tasks (with optional filters)
- Search for specific tasks
- Mark tasks as complete
- Update task details (description, priority, due date, tags)
- Delete tasks

Guidelines:
1. Be friendly and conversational
2. Confirm actions clearly (e.g., "I've added 'buy groceries' to your list")
3. When listing tasks, format them nicely and ask if the user wants to take action
4. When a task isn't found, offer to show the task list or suggest alternatives
5. For ambiguous references like "it" or "that one", use context from the conversation
6. If the user's message isn't about tasks, politely redirect them: "I'm here to help manage your tasks. Would you like to add, view, or update a task?"

Remember to use natural language dates when possible (today, tomorrow, Friday) rather than asking for specific formats."""


@dataclass
class ToolResult:
    """Result from a tool execution."""
    tool: str
    success: bool
    task_id: Optional[str] = None
    count: Optional[int] = None
    error: Optional[str] = None


class TodoAgent:
    """Todo assistant agent using OpenAI."""

    def __init__(self, session: Session, user_id: str):
        self.session = session
        self.user_id = user_id
        self.tool_results: list[ToolResult] = []

    def _execute_tool(self, tool_name: str, arguments: dict) -> dict:
        """Execute a tool and return the result."""
        tool_map = {
            "create_task": create_task,
            "list_tasks": list_tasks,
            "search_tasks": search_tasks,
            "complete_task": complete_task,
            "update_task": update_task,
            "delete_task": delete_task,
        }

        if tool_name not in tool_map:
            return {"success": False, "error": f"Unknown tool: {tool_name}"}

        # Inject session and user_id (security: not from AI)
        result = tool_map[tool_name](
            session=self.session,
            user_id=self.user_id,
            **arguments
        )

        # Track tool result
        self.tool_results.append(ToolResult(
            tool=tool_name,
            success=result.get("success", False),
            task_id=result.get("task_id"),
            count=result.get("count"),
            error=result.get("error"),
        ))

        return result

    def run(
        self,
        user_message: str,
        conversation_history: list[dict] = None,
    ) -> tuple[str, list[dict]]:
        """Run the agent with a user message.

        Args:
            user_message: The user's natural language message
            conversation_history: Previous messages for context

        Returns:
            Tuple of (assistant_response, tool_results)
        """
        self.tool_results = []

        # Build messages for the API
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        # Add conversation history for context
        if conversation_history:
            for msg in conversation_history[-10:]:  # Last 10 messages
                messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", ""),
                })

        # Add current user message
        messages.append({"role": "user", "content": user_message})

        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
        )

        assistant_message = response.choices[0].message

        # Handle tool calls
        while assistant_message.tool_calls:
            # Add assistant's message with tool calls
            messages.append({
                "role": "assistant",
                "content": assistant_message.content or "",
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        }
                    }
                    for tc in assistant_message.tool_calls
                ]
            })

            # Execute each tool call
            for tool_call in assistant_message.tool_calls:
                tool_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)

                result = self._execute_tool(tool_name, arguments)

                # Add tool result to messages
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result),
                })

            # Get next response from the model
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                tools=TOOLS,
                tool_choice="auto",
            )
            assistant_message = response.choices[0].message

        # Return final response
        final_response = assistant_message.content or "I'm sorry, I couldn't process that request."

        tool_results_dicts = [
            {
                "tool": tr.tool,
                "success": tr.success,
                "task_id": tr.task_id,
                "count": tr.count,
                "error": tr.error,
            }
            for tr in self.tool_results
        ]

        return final_response, tool_results_dicts


def run_agent(
    session: Session,
    user_id: str,
    message: str,
    conversation_history: list[dict] = None,
) -> tuple[str, list[dict]]:
    """Convenience function to run the agent.

    Args:
        session: Database session
        user_id: User ID from JWT
        message: User's message
        conversation_history: Previous messages for context

    Returns:
        Tuple of (response, tool_results)
    """
    agent = TodoAgent(session, user_id)
    return agent.run(message, conversation_history)
