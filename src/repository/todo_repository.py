"""In-memory repository for todo storage."""

from typing import Optional
from src.models.todo import Todo


class TodoRepository:
    """Singleton repository for in-memory todo storage.

    Uses a dictionary to store todos with O(1) lookup by ID.
    IDs are auto-incremented and never reused.
    """

    _instance: Optional['TodoRepository'] = None
    _todos: dict[int, Todo]
    _next_id: int

    def __new__(cls) -> 'TodoRepository':
        """Ensure only one instance exists (singleton pattern)."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._todos = {}
            cls._instance._next_id = 1
        return cls._instance

    def add(self, description: str) -> Todo:
        """Create and store a new todo with auto-assigned ID.

        Args:
            description: Task description

        Returns:
            Created Todo object
        """
        todo = Todo(id=self._next_id, description=description, completed=False)
        self._todos[self._next_id] = todo
        self._next_id += 1
        return todo

    def get(self, id: int) -> Optional[Todo]:
        """Retrieve a todo by ID.

        Args:
            id: Todo ID to retrieve

        Returns:
            Todo object if found, None otherwise
        """
        return self._todos.get(id)

    def get_all(self) -> list[Todo]:
        """Retrieve all todos sorted by ID.

        Returns:
            List of all Todo objects, sorted by ID (ascending)
        """
        return sorted(self._todos.values(), key=lambda t: t.id)

    def update(self, id: int, description: str) -> Optional[Todo]:
        """Update a todo's description.

        Args:
            id: Todo ID to update
            description: New description

        Returns:
            Updated Todo object if found, None otherwise
        """
        todo = self._todos.get(id)
        if todo:
            todo.description = description
        return todo

    def delete(self, id: int) -> bool:
        """Remove a todo from storage.

        Args:
            id: Todo ID to delete

        Returns:
            True if deleted, False if not found
        """
        if id in self._todos:
            del self._todos[id]
            return True
        return False

    def mark_complete(self, id: int) -> Optional[Todo]:
        """Mark a todo as complete.

        Args:
            id: Todo ID to mark complete

        Returns:
            Updated Todo object if found, None otherwise
        """
        todo = self._todos.get(id)
        if todo:
            todo.completed = True
        return todo

    def mark_incomplete(self, id: int) -> Optional[Todo]:
        """Mark a todo as incomplete.

        Args:
            id: Todo ID to mark incomplete

        Returns:
            Updated Todo object if found, None otherwise
        """
        todo = self._todos.get(id)
        if todo:
            todo.completed = False
        return todo
