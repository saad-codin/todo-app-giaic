"""Console application for in-memory todo management."""

import sys
from src.models.todo import Todo
from src.operations import todo_operations

# Configure stdout for UTF-8 to support checkmark characters
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')


def display_menu() -> None:
    """Display the main menu."""
    print("\n" + "="*30)
    print("=== Todo Application ===")
    print("="*30)
    print("1. Add Todo")
    print("2. View All Todos")
    print("3. Update Todo")
    print("4. Delete Todo")
    print("5. Mark Todo Complete")
    print("6. Mark Todo Incomplete")
    print("7. Exit")
    print("="*30)


def format_todo(todo: Todo) -> str:
    """Format a todo for display with checkbox indicator.

    Args:
        todo: Todo object to format

    Returns:
        Formatted string with checkbox and todo details
    """
    checkbox = "[✓]" if todo.completed else "[ ]"
    return f"{checkbox} {todo.id}: {todo.description}"


def handle_add_todo() -> None:
    """Handle the Add Todo menu option."""
    print("\n--- Add New Todo ---")
    description = input("Enter todo description: ")

    result = todo_operations.add_todo(description)

    if isinstance(result, str):
        # Error message
        print(f"\n{result}")
    else:
        # Success - Todo object returned
        print(f"\nTodo added successfully: ID {result.id} - {result.description}")


def handle_view_todos() -> None:
    """Handle the View All Todos menu option."""
    print("\n--- All Todos ---")
    todos = todo_operations.get_all_todos()

    if not todos:
        print("No todos found. Your list is empty.")
    else:
        for todo in todos:
            print(format_todo(todo))


def handle_update_todo() -> None:
    """Handle the Update Todo menu option."""
    print("\n--- Update Todo ---")

    try:
        todo_id = int(input("Enter todo ID to update: "))
        new_description = input("Enter new description: ")

        result = todo_operations.update_todo(todo_id, new_description)

        if isinstance(result, str):
            # Error message
            print(f"\n{result}")
        else:
            # Success - Todo object returned
            print(f"\nTodo updated successfully: ID {result.id} - {result.description}")

    except ValueError:
        print("\nError: Invalid ID. Please enter a number")


def handle_delete_todo() -> None:
    """Handle the Delete Todo menu option."""
    print("\n--- Delete Todo ---")

    try:
        todo_id = int(input("Enter todo ID to delete: "))

        result = todo_operations.delete_todo(todo_id)

        if isinstance(result, str):
            # Error message
            print(f"\n{result}")
        else:
            # Success - True returned
            print(f"\nTodo deleted successfully: ID {todo_id}")

    except ValueError:
        print("\nError: Invalid ID. Please enter a number")


def handle_mark_complete() -> None:
    """Handle the Mark Todo Complete menu option."""
    print("\n--- Mark Todo Complete ---")

    try:
        todo_id = int(input("Enter todo ID to mark complete: "))

        result = todo_operations.mark_complete(todo_id)

        if isinstance(result, str):
            # Error message
            print(f"\n{result}")
        else:
            # Success - Todo object returned
            print(f"\nTodo marked as complete: ID {result.id}")

    except ValueError:
        print("\nError: Invalid ID. Please enter a number")


def handle_mark_incomplete() -> None:
    """Handle the Mark Todo Incomplete menu option."""
    print("\n--- Mark Todo Incomplete ---")

    try:
        todo_id = int(input("Enter todo ID to mark incomplete: "))

        result = todo_operations.mark_incomplete(todo_id)

        if isinstance(result, str):
            # Error message
            print(f"\n{result}")
        else:
            # Success - Todo object returned
            print(f"\nTodo marked as incomplete: ID {result.id}")

    except ValueError:
        print("\nError: Invalid ID. Please enter a number")


def handle_exit() -> bool:
    """Handle the Exit menu option.

    Returns:
        False to signal application should exit
    """
    print("\nThank you for using Todo App!")
    print("All data will be lost (in-memory storage only).")
    return False


def main() -> None:
    """Main application loop."""
    print("Welcome to the In-Memory Todo Application!")
    print("All data is stored in memory and will be lost on exit.")

    running = True

    while running:
        try:
            display_menu()
            choice = input("\nEnter your choice (1-7): ").strip()

            if choice == "1":
                handle_add_todo()
            elif choice == "2":
                handle_view_todos()
            elif choice == "3":
                handle_update_todo()
            elif choice == "4":
                handle_delete_todo()
            elif choice == "5":
                handle_mark_complete()
            elif choice == "6":
                handle_mark_incomplete()
            elif choice == "7":
                running = handle_exit()
            else:
                print("\nError: Invalid choice. Please enter a number between 1 and 7")

        except KeyboardInterrupt:
            print("\n\nInterrupted. Exiting...")
            running = False
        except Exception as e:
            print(f"\nAn unexpected error occurred: {e}")
            print("Please try again.")


if __name__ == "__main__":
    main()
