"""In-memory repository for todo storage."""

from datetime import date, datetime
from typing import Optional
from src.models.todo import Todo
from src.validation.priority import validate_priority
from src.validation.dates import validate_date, validate_datetime
from src.validation.recurrence import validate_recurrence


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

    def add(
        self,
        description: str,
        priority: str = "medium",
        tags: Optional[list[str]] = None,
        due_date: Optional[date] = None,
        reminder_time: Optional[datetime] = None,
        recurrence: str = "none",
    ) -> Todo | str:
        """Create and store a new todo with auto-assigned ID.

        Args:
            description: Task description
            priority: Priority level ("high", "medium", or "low")
            tags: List of tags for categorization
            due_date: Optional due date
            reminder_time: Optional reminder datetime
            recurrence: Recurrence pattern ("none", "daily", "weekly", or "monthly")

        Returns:
            Created Todo object if successful, error message string if validation fails
        """
        # Validate priority
        priority_error = validate_priority(priority)
        if priority_error:
            return priority_error

        # Validate recurrence
        recurrence_error = validate_recurrence(recurrence)
        if recurrence_error:
            return recurrence_error

        # Create todo with validated fields
        todo = Todo(
            id=self._next_id,
            description=description,
            completed=False,
            priority=priority,
            tags=tags if tags is not None else [],
            due_date=due_date,
            reminder_time=reminder_time,
            recurrence=recurrence,
        )
        self._todos[self._next_id] = todo
        self._next_id += 1
        return todo

    def add_existing(self, todo: Todo) -> Todo:
        """Add a pre-constructed todo to storage.

        This method is used for recurring tasks where the next occurrence
        is created with specific dates and a new ID needs to be assigned.

        Args:
            todo: Pre-constructed Todo object (id will be reassigned)

        Returns:
            The stored Todo object with newly assigned ID
        """
        # Assign new ID to the pre-constructed todo
        todo.id = self._next_id
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

    def update(self, id: int, **kwargs) -> Optional[Todo] | str:
        """Update a todo's fields.

        Args:
            id: Todo ID to update
            **kwargs: Fields to update (description, priority, tags, due_date,
                     reminder_time, recurrence, completed)

        Returns:
            Updated Todo object if successful, None if not found,
            error message string if validation fails
        """
        todo = self._todos.get(id)
        if not todo:
            return None

        # Validate priority if provided
        if "priority" in kwargs:
            priority_error = validate_priority(kwargs["priority"])
            if priority_error:
                return priority_error

        # Validate recurrence if provided
        if "recurrence" in kwargs:
            recurrence_error = validate_recurrence(kwargs["recurrence"])
            if recurrence_error:
                return recurrence_error

        # Update all provided fields
        for field, value in kwargs.items():
            if hasattr(todo, field):
                setattr(todo, field, value)

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
