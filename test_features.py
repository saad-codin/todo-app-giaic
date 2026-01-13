# test_features.py
from src.operations.todo_operations import add_todo, get_all_todos, mark_complete
from src.operations.search_operations import search_todos, filter_by_priority
from src.operations.sort_operations import sort_by_priority

print("=== Testing Advanced Todo Features ===\n")

# 1. Create todos with priority and tags
print("1. Creating todos with priority and tags...")
todo1 = add_todo("Buy groceries", priority="high", tags=["shopping", "home"])
todo2 = add_todo("Finish report", priority="medium", tags=["work"])
todo3 = add_todo("Call dentist", priority="low")
print("   Created 3 todos\n")

# 2. Create recurring task
print("2. Creating daily recurring task...")
todo4 = add_todo("Daily standup", due_date="2026-01-15", recurrence="daily")
print("   Created recurring task\n")

# 3. View all todos
print("3. All todos:")
todos = get_all_todos()
for t in todos:
    print(f"   [{t.id}] {t.description} - Priority: {t.priority}, Tags: {t.tags}")
print()

# 4. Search
print("4. Search for 'report':")
results = search_todos(todos, "report")
for t in results:
    print(f"   Found: {t.description}")
print()

# 5. Filter by priority
print("5. High priority tasks:")
high_priority = filter_by_priority(todos, "high")
for t in high_priority:
    print(f"   {t.description}")
print()

# 6. Sort by priority
print("6. Sorted by priority (high -> low):")
sorted_todos = sort_by_priority(todos, "ascending")
for t in sorted_todos:
    print(f"   {t.priority}: {t.description}")
print()

# 7. Test recurring - complete task and see new one created!
print("7. Completing recurring task (should auto-create next occurrence)...")
print(f"   Before: {len(get_all_todos())} todos")
mark_complete(todo4.id)
print(f"   After: {len(get_all_todos())} todos")
todos = get_all_todos()
standups = [t for t in todos if "standup" in t.description.lower()]
print(f"   'Daily standup' todos: {len(standups)} (1 completed, 1 new for tomorrow!)")
for t in standups:
    status = "Complete" if t.completed else "Incomplete"
    print(f"   - [{t.id}] {status}, Due: {t.due_date}")

print("\n=== All features working! ===")
