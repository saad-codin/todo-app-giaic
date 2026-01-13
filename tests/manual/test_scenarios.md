# Manual Test Scenarios: In-Memory Python Console Todo App

**Feature**: 001-console-todo
**Testing Standard**: Phase I - Manual testing only (no automated tests)
**Purpose**: Validate all acceptance scenarios from spec.md

## Test Execution Instructions

1. Run the application: `python src/cli/console_app.py`
2. Follow the test scenarios below in order
3. Record PASS/FAIL for each scenario
4. Note any deviations from expected behavior

## User Story 1: Create and View Todos (Priority: P1)

### Test Scenario 1.1: Create Todo with Valid Description

**Given**: The console app is running
**When**: I select menu option 1 (Add Todo) and enter "Buy groceries"
**Then**:
- Todo is created with ID 1
- Todo is marked as incomplete
- Success message displayed

**Expected Output**:
```
Todo added successfully: ID 1 - Buy groceries
```

**Result**: [ ] PASS / [ ] FAIL

---

### Test Scenario 1.2: View Multiple Todos

**Given**: I have added 3 todos ("Buy groceries", "Call dentist", "Finish report")
**When**: I select menu option 2 (View All Todos)
**Then**: All 3 todos are displayed with IDs, descriptions, and completion status

**Expected Output**:
```
[ ] 1: Buy groceries
[ ] 2: Call dentist
[ ] 3: Finish report
```

**Result**: [ ] PASS / [ ] FAIL

---

### Test Scenario 1.3: View Empty Todo List

**Given**: No todos exist (fresh start)
**When**: I select menu option 2 (View All Todos)
**Then**: A message indicates the list is empty

**Expected Output**:
```
No todos found. Your list is empty.
```

**Result**: [ ] PASS / [ ] FAIL

---

### Test Scenario 1.4: Add Todo with Empty Description

**Given**: The console app is running
**When**: I select menu option 1 and enter an empty string (just press Enter)
**Then**: Error message displayed, todo is NOT created

**Expected Output**:
```
Error: Description cannot be empty
```

**Result**: [ ] PASS / [ ] FAIL

---

## User Story 2: Update Todo Descriptions (Priority: P2)

### Test Scenario 2.1: Update Existing Todo

**Given**: A todo exists with ID 1 and description "Buy milk"
**When**: I select menu option 3 (Update Todo), enter ID 1, and provide "Buy organic milk"
**Then**: Todo description is updated successfully

**Expected Output**:
```
Todo updated successfully: ID 1 - Buy organic milk
```

**Result**: [ ] PASS / [ ] FAIL

---

### Test Scenario 2.2: Update Non-Existent Todo

**Given**: I attempt to update a todo
**When**: I provide ID 999 (which doesn't exist)
**Then**: Error message indicating todo was not found

**Expected Output**:
```
Error: Todo with ID 999 not found
```

**Result**: [ ] PASS / [ ] FAIL

---

### Test Scenario 2.3: Update with Empty Description

**Given**: A todo exists with ID 1
**When**: I select Update Todo and provide an empty description
**Then**: Error message displayed, original description unchanged

**Expected Output**:
```
Error: Description cannot be empty
```

**Result**: [ ] PASS / [ ] FAIL

---

### Test Scenario 2.4: Update with Whitespace-Only Description

**Given**: A todo exists with ID 1
**When**: I provide a description with only spaces ("   ")
**Then**: Error message displayed

**Expected Output**:
```
Error: Description cannot be whitespace-only
```

**Result**: [ ] PASS / [ ] FAIL

---

## User Story 3: Mark Todos Complete/Incomplete (Priority: P3)

### Test Scenario 3.1: Mark Todo Complete

**Given**: An incomplete todo exists with ID 1
**When**: I select menu option 5 (Mark Complete) and enter ID 1
**Then**: Todo status changes to complete

**Expected Output**:
```
Todo marked as complete: ID 1
```

**Result**: [ ] PASS / [ ] FAIL

---

### Test Scenario 3.2: Mark Todo Incomplete

**Given**: A complete todo exists with ID 1
**When**: I select menu option 6 (Mark Incomplete) and enter ID 1
**Then**: Todo status changes to incomplete

**Expected Output**:
```
Todo marked as incomplete: ID 1
```

**Result**: [ ] PASS / [ ] FAIL

---

### Test Scenario 3.3: Mark Non-Existent Todo

**Given**: I attempt to mark a todo complete
**When**: I provide ID 999 (which doesn't exist)
**Then**: Error message indicating todo was not found

**Expected Output**:
```
Error: Todo with ID 999 not found
```

**Result**: [ ] PASS / [ ] FAIL

---

### Test Scenario 3.4: Visual Distinction of Completed Todos

**Given**: I have 3 todos, with ID 2 marked complete
**When**: I select View All Todos
**Then**: Completed todos show [✓], incomplete show [ ]

**Expected Output**:
```
[ ] 1: Buy groceries
[✓] 2: Call dentist
[ ] 3: Finish report
```

**Result**: [ ] PASS / [ ] FAIL

---

## User Story 4: Delete Todos (Priority: P4)

### Test Scenario 4.1: Delete Existing Todo

**Given**: A todo exists with ID 1
**When**: I select menu option 4 (Delete Todo) and enter ID 1
**Then**: Todo is removed from the list

**Expected Output**:
```
Todo deleted successfully: ID 1
```

**Result**: [ ] PASS / [ ] FAIL

---

### Test Scenario 4.2: Delete Non-Existent Todo

**Given**: I attempt to delete a todo
**When**: I provide ID 999 (which doesn't exist)
**Then**: Error message indicating todo was not found

**Expected Output**:
```
Error: Todo with ID 999 not found
```

**Result**: [ ] PASS / [ ] FAIL

---

### Test Scenario 4.3: Verify Deletion Removes Todo

**Given**: I have 3 todos (IDs 1, 2, 3)
**When**: I delete todo with ID 2, then view all todos
**Then**: Only todos 1 and 3 are displayed

**Expected Output**:
```
[ ] 1: Buy groceries
[ ] 3: Finish report
```

**Result**: [ ] PASS / [ ] FAIL

---

### Test Scenario 4.4: ID Non-Reuse After Deletion

**Given**: I delete a todo with ID 2
**When**: I create a new todo
**Then**: New todo receives ID 4 (next sequential, not reusing 2)

**Expected Output**:
```
Todo added successfully: ID 4 - New task
```

**Result**: [ ] PASS / [ ] FAIL

---

## Edge Cases

### Test Scenario EC1: Invalid Menu Choice

**Given**: Main menu is displayed
**When**: I enter "9" or "abc"
**Then**: Error message, menu redisplays

**Expected Output**:
```
Error: Invalid choice. Please enter a number between 1 and 7
```

**Result**: [ ] PASS / [ ] FAIL

---

### Test Scenario EC2: Non-Numeric ID Input

**Given**: I select Update/Delete/Mark operation
**When**: I enter "abc" instead of a number
**Then**: Error message, operation fails gracefully

**Expected Output**:
```
Error: Invalid ID. Please enter a number
```

**Result**: [ ] PASS / [ ] FAIL

---

### Test Scenario EC3: Long Description (1000+ chars)

**Given**: I select Add Todo
**When**: I enter a description with 1000+ characters
**Then**: Todo is created successfully (Python handles long strings)

**Result**: [ ] PASS / [ ] FAIL

---

### Test Scenario EC4: Graceful Exit

**Given**: Application is running
**When**: I select menu option 7 (Exit)
**Then**: Application exits cleanly with message

**Expected Output**:
```
Thank you for using Todo App!
```

**Result**: [ ] PASS / [ ] FAIL

---

## Success Criteria Validation

### SC-001: Complete all CRUD operations within 5 minutes

**Test**: Time yourself performing: Add 3 todos, view list, update one, mark one complete, delete one, view final list
**Expected**: Complete in under 5 minutes
**Result**: [ ] PASS / [ ] FAIL / Time: _______

---

### SC-002: Instant response (under 100ms)

**Test**: All operations feel instant with no perceptible delay
**Expected**: No delays noticed during any operation
**Result**: [ ] PASS / [ ] FAIL

---

### SC-003: 100% operation success rate

**Test**: All valid operations complete without crashes
**Expected**: No application crashes during testing
**Result**: [ ] PASS / [ ] FAIL

---

### SC-004: Code generated via Claude Code

**Test**: Verify all source files were generated by Claude Code
**Expected**: No manual edits to generated code
**Result**: [ ] PASS / [ ] FAIL

---

### SC-005: State resets on restart

**Test**: Add todos, exit app, restart - verify list is empty
**Expected**: All data lost on restart (in-memory only)
**Result**: [ ] PASS / [ ] FAIL

---

### SC-006: Clear error messages

**Test**: Trigger various errors (invalid ID, empty description, etc.)
**Expected**: All error messages are self-explanatory
**Result**: [ ] PASS / [ ] FAIL

---

### SC-007: Intuitive menu navigation

**Test**: First-time user can complete all operations without help
**Expected**: Menu is self-explanatory and easy to use
**Result**: [ ] PASS / [ ] FAIL

---

## Test Execution Summary

**Date**: _________________
**Tester**: _________________
**Total Scenarios**: 23
**Passed**: _______
**Failed**: _______
**Pass Rate**: _______

**Notes**:
-
-
-

**Overall Result**: [ ] PASS / [ ] FAIL

---

# Feature 002: In-Memory Todo App — Advanced Features

**Feature**: 002-todo-advanced-features
**Testing Standard**: Phase I - Manual testing only (no automated tests)
**Purpose**: Validate advanced feature acceptance scenarios from spec.md

---

## User Story 1: Task Organization with Priority and Tags (Priority: P1)

### Test Scenario US1.1: Create Todo with Priority

**Given**: The application is running
**When**: I create a todo with description "Urgent meeting" and priority "high"
**Then**:
- Todo is created with ID assigned
- Priority is set to "high"
- Default values applied (completed=False, tags=[], etc.)

**Test Steps**:
```python
from src.operations.todo_operations import add_todo
result = add_todo("Urgent meeting", priority="high")
# Verify result is a Todo object
# Verify result.priority == "high"
# Verify result.description == "Urgent meeting"
```

**Expected**: Todo created with high priority
**Result**: [ ] PASS / [ ] FAIL

---

### Test Scenario US1.2: Create Todo with Tags

**Given**: The application is running
**When**: I create a todo with description "Buy groceries" and tags ["shopping", "home"]
**Then**:
- Todo is created with normalized tags
- Tags are stored as lowercase: ["shopping", "home"]

**Test Steps**:
```python
result = add_todo("Buy groceries", tags=["Shopping", "HOME"])
# Verify result.tags == ["shopping", "home"]
```

**Expected**: Tags normalized to lowercase
**Result**: [ ] PASS / [ ] FAIL

---

### Test Scenario US1.3: Create Todo with Invalid Priority

**Given**: The application is running
**When**: I attempt to create a todo with priority "urgent" (invalid value)
**Then**: Error message returned indicating valid priority values

**Test Steps**:
```python
result = add_todo("Task", priority="urgent")
# Verify isinstance(result, str) and "Invalid priority" in result
```

**Expected Output**:
```
Error: Invalid priority 'urgent'. Valid values: high, medium, low
```

**Result**: [ ] PASS / [ ] FAIL

---

### Test Scenario US1.4: Update Todo Priority

**Given**: A todo exists with ID 1 and priority "medium"
**When**: I update the todo's priority to "high"
**Then**: Priority is updated successfully

**Test Steps**:
```python
todo = add_todo("Task")  # Creates with default medium priority
result = update_todo(todo.id, priority="high")
# Verify result.priority == "high"
```

**Expected**: Priority changed from medium to high
**Result**: [ ] PASS / [ ] FAIL

---

### Test Scenario US1.5: Add Tag to Existing Todo

**Given**: A todo exists with ID 1 and no tags
**When**: I add tag "work" to the todo
**Then**: Tag is added and normalized

**Test Steps**:
```python
from src.operations.todo_operations import add_todo, add_tag
todo = add_todo("Task")
result = add_tag(todo.id, "Work")
# Verify "work" in result.tags
```

**Expected**: Tag "work" added (lowercase)
**Result**: [ ] PASS / [ ] FAIL

---

### Test Scenario US1.6: Remove Tag from Todo

**Given**: A todo exists with tags ["work", "urgent"]
**When**: I remove tag "work"
**Then**: Tag is removed, "urgent" remains

**Test Steps**:
```python
from src.operations.todo_operations import add_todo, remove_tag
todo = add_todo("Task", tags=["work", "urgent"])
result = remove_tag(todo.id, "work")
# Verify result.tags == ["urgent"]
```

**Expected**: Only "urgent" tag remains
**Result**: [ ] PASS / [ ] FAIL

---

## Test Execution Summary - Feature 002, User Story 1

**Date**: _________________
**Tester**: _________________
**Total Scenarios (US1)**: 6
**Passed**: _______
**Failed**: _______
**Pass Rate**: _______

**Notes**:
-
-
-

**Overall Result**: [ ] PASS / [ ] FAIL

---

## User Story 2: Search and Filter Tasks (Priority: P2)

### Test Scenario US2.1: Search by Keyword

**Given**: 3 todos exist: "Buy groceries", "Call dentist", "Buy milk"
**When**: I search with keyword "buy"
**Then**: Returns 2 todos (case-insensitive match)

**Test Steps**:
```python
from src.operations.todo_operations import add_todo
from src.operations.search_operations import search_todos
todo1 = add_todo("Buy groceries")
todo2 = add_todo("Call dentist")
todo3 = add_todo("Buy milk")
all_todos = [todo1, todo2, todo3]
result = search_todos(all_todos, "buy")
# Verify len(result) == 2
# Verify todo1 in result and todo3 in result
```

**Expected**: Returns "Buy groceries" and "Buy milk"
**Result**: [ ] PASS / [ ] FAIL

---

### Test Scenario US2.2: Filter by Completion Status

**Given**: 3 todos, 2 incomplete and 1 complete
**When**: I filter by completed=False
**Then**: Returns only the 2 incomplete todos

**Test Steps**:
```python
from src.operations.todo_operations import add_todo, mark_complete
from src.operations.search_operations import filter_by_completed
todo1 = add_todo("Task 1")
todo2 = add_todo("Task 2")
todo3 = add_todo("Task 3")
mark_complete(todo2.id)
all_todos = [todo1, todo2, todo3]
result = filter_by_completed(all_todos, False)
# Verify len(result) == 2
# Verify todo1 in result and todo3 in result
```

**Expected**: Returns only incomplete todos
**Result**: [ ] PASS / [ ] FAIL

---

### Test Scenario US2.3: Filter by Priority

**Given**: Todos with different priorities (high, medium, low)
**When**: I filter by priority="high"
**Then**: Returns only high priority todos

**Test Steps**:
```python
from src.operations.todo_operations import add_todo
from src.operations.search_operations import filter_by_priority
todo1 = add_todo("Urgent", priority="high")
todo2 = add_todo("Normal", priority="medium")
todo3 = add_todo("Later", priority="low")
all_todos = [todo1, todo2, todo3]
result = filter_by_priority(all_todos, "high")
# Verify len(result) == 1
# Verify result[0].description == "Urgent"
```

**Expected**: Returns only "Urgent" todo
**Result**: [ ] PASS / [ ] FAIL

---

### Test Scenario US2.4: Filter by Tag (Case-Insensitive)

**Given**: Todos with various tags
**When**: I filter by tag "work" (lowercase)
**Then**: Returns todos with "work" tag regardless of original case

**Test Steps**:
```python
from src.operations.todo_operations import add_todo
from src.operations.search_operations import filter_by_tag
todo1 = add_todo("Task 1", tags=["Work", "urgent"])
todo2 = add_todo("Task 2", tags=["home"])
todo3 = add_todo("Task 3", tags=["work", "project"])
all_todos = [todo1, todo2, todo3]
result = filter_by_tag(all_todos, "work")
# Verify len(result) == 2
# Verify todo1 in result and todo3 in result
```

**Expected**: Returns Task 1 and Task 3 (case-insensitive)
**Result**: [ ] PASS / [ ] FAIL

---

### Test Scenario US2.5: Combined Filters with AND Logic

**Given**: 5 todos with various attributes
**When**: I apply filter: keyword="report" AND completed=False AND priority="high"
**Then**: Returns only todos matching ALL criteria

**Test Steps**:
```python
from src.operations.todo_operations import add_todo, mark_complete
from src.operations.search_operations import apply_filters
from src.models.filters import SearchFilter

todo1 = add_todo("Write report", priority="high")
todo2 = add_todo("Review report", priority="high")
todo3 = add_todo("Send report", priority="medium")
mark_complete(todo2.id)

all_todos = [todo1, todo2, todo3]
search_filter = SearchFilter(keyword="report", completed=False, priority="high")
result = apply_filters(all_todos, search_filter)
# Verify len(result) == 1
# Verify result[0].description == "Write report"
```

**Expected**: Returns only "Write report" (matches all 3 criteria)
**Result**: [ ] PASS / [ ] FAIL

---

### Test Scenario US2.6: Search with No Results

**Given**: Multiple todos exist
**When**: I search with keyword that doesn't match any todo
**Then**: Returns empty list

**Test Steps**:
```python
from src.operations.todo_operations import add_todo
from src.operations.search_operations import search_todos
todo1 = add_todo("Task 1")
todo2 = add_todo("Task 2")
all_todos = [todo1, todo2]
result = search_todos(all_todos, "nonexistent")
# Verify len(result) == 0
```

**Expected**: Returns empty list
**Result**: [ ] PASS / [ ] FAIL

---

### Test Scenario US2.7: Filter with Empty Criteria

**Given**: Multiple todos exist
**When**: I apply SearchFilter with all None values
**Then**: Returns all todos unchanged

**Test Steps**:
```python
from src.operations.todo_operations import add_todo
from src.operations.search_operations import apply_filters
from src.models.filters import SearchFilter

todo1 = add_todo("Task 1")
todo2 = add_todo("Task 2")
all_todos = [todo1, todo2]
search_filter = SearchFilter()  # All None
result = apply_filters(all_todos, search_filter)
# Verify len(result) == 2
# Verify result == all_todos
```

**Expected**: Returns all todos
**Result**: [ ] PASS / [ ] FAIL

---

## Test Execution Summary - Feature 002, User Story 2

**Date**: _________________
**Tester**: _________________
**Total Scenarios (US2)**: 7
**Passed**: _______
**Failed**: _______
**Pass Rate**: _______

**Notes**:
-
-
-

**Overall Result**: [ ] PASS / [ ] FAIL

---

## User Story 4: Due Dates and Reminder Times (Priority: P4)

### Test Scenario US4.1: Create Todo with Due Date

**Given**: The application is running
**When**: I create a todo with due date "2026-02-15"
**Then**: Todo is created with parsed date object

**Test Steps**:
```python
from src.operations.todo_operations import add_todo
result = add_todo("Submit report", due_date="2026-02-15")
# Verify result.due_date is a date object
# Verify result.due_date.year == 2026
# Verify result.due_date.month == 2
# Verify result.due_date.day == 15
```

**Expected**: Due date stored as date(2026, 2, 15)
**Result**: [ ] PASS / [ ] FAIL

---

### Test Scenario US4.2: Create Todo with Reminder Time

**Given**: The application is running
**When**: I create a todo with reminder_time "2026-02-15 14:30"
**Then**: Todo is created with parsed datetime object

**Test Steps**:
```python
result = add_todo("Meeting", reminder_time="2026-02-15 14:30")
# Verify result.reminder_time is a datetime object
# Verify result.reminder_time.hour == 14
# Verify result.reminder_time.minute == 30
```

**Expected**: Reminder time stored as datetime(2026, 2, 15, 14, 30)
**Result**: [ ] PASS / [ ] FAIL

---

### Test Scenario US4.3: Create Todo with Both Due Date and Reminder

**Given**: The application is running
**When**: I create a todo with both due_date and reminder_time
**Then**: Both fields are stored independently

**Test Steps**:
```python
result = add_todo("Important task", due_date="2026-03-01", reminder_time="2026-02-28 09:00")
# Verify result.due_date == date(2026, 3, 1)
# Verify result.reminder_time == datetime(2026, 2, 28, 9, 0)
```

**Expected**: Both fields stored correctly
**Result**: [ ] PASS / [ ] FAIL

---

### Test Scenario US4.4: Create Todo with Invalid Due Date Format

**Given**: The application is running
**When**: I attempt to create a todo with due_date "02/15/2026" (wrong format)
**Then**: Error message returned

**Test Steps**:
```python
result = add_todo("Task", due_date="02/15/2026")
# Verify isinstance(result, str)
# Verify "Invalid date format" in result
```

**Expected Output**:
```
Error: Invalid date format. Expected YYYY-MM-DD
```

**Result**: [ ] PASS / [ ] FAIL

---

### Test Scenario US4.5: Create Todo with Invalid Reminder Time Format

**Given**: The application is running
**When**: I attempt to create a todo with reminder_time "2pm" (wrong format)
**Then**: Error message returned

**Test Steps**:
```python
result = add_todo("Task", reminder_time="2pm")
# Verify isinstance(result, str)
# Verify "Invalid datetime format" in result
```

**Expected Output**:
```
Error: Invalid datetime format. Expected YYYY-MM-DD HH:MM
```

**Result**: [ ] PASS / [ ] FAIL

---

### Test Scenario US4.6: Update Todo Due Date

**Given**: A todo exists without a due date
**When**: I update it to add due_date "2026-04-01"
**Then**: Due date is added successfully

**Test Steps**:
```python
from src.operations.todo_operations import add_todo, update_todo
todo = add_todo("Task")
result = update_todo(todo.id, due_date="2026-04-01")
# Verify result.due_date == date(2026, 4, 1)
```

**Expected**: Due date added to existing todo
**Result**: [ ] PASS / [ ] FAIL

---

### Test Scenario US4.7: Create Todo with None Values (Optional Fields)

**Given**: The application is running
**When**: I create a todo without due_date or reminder_time
**Then**: Both fields are None (optional)

**Test Steps**:
```python
result = add_todo("Simple task")
# Verify result.due_date is None
# Verify result.reminder_time is None
```

**Expected**: Optional fields are None by default
**Result**: [ ] PASS / [ ] FAIL

---

## Test Execution Summary - Feature 002, User Story 4

**Date**: _________________
**Tester**: _________________
**Total Scenarios (US4)**: 7
**Passed**: _______
**Failed**: _______
**Pass Rate**: _______

**Notes**:
-
-
-

**Overall Result**: [ ] PASS / [ ] FAIL

---

## User Story 5: Recurring Tasks with Auto-Creation (Priority: P5)

### Test Scenario US5.1: Daily Recurring Task Creation

**Given**: A daily recurring todo with due_date "2026-01-15"
**When**: I mark it complete
**Then**: New occurrence created with due_date "2026-01-16"

**Test Steps**:
```python
from src.operations.todo_operations import add_todo, mark_complete, get_all_todos
todo = add_todo("Daily standup", due_date="2026-01-15", recurrence="daily")
original_id = todo.id
mark_complete(original_id)

all_todos = get_all_todos()
# Verify len(all_todos) == 2 (original + new)
# Find new todo (different ID, incomplete)
new_todo = [t for t in all_todos if t.id != original_id and not t.completed][0]
# Verify new_todo.due_date == date(2026, 1, 16)
# Verify new_todo.description == "Daily standup"
# Verify new_todo.recurrence == "daily"
```

**Expected**: New todo created with due_date 2026-01-16, same description, incomplete
**Result**: [ ] PASS / [ ] FAIL

---

### Test Scenario US5.2: Weekly Recurring Task Creation

**Given**: A weekly recurring todo with due_date "2026-01-15"
**When**: I mark it complete
**Then**: New occurrence created with due_date "2026-01-22" (+7 days)

**Test Steps**:
```python
todo = add_todo("Weekly review", due_date="2026-01-15", recurrence="weekly")
original_id = todo.id
mark_complete(original_id)

all_todos = get_all_todos()
new_todo = [t for t in all_todos if t.id != original_id and not t.completed][0]
# Verify new_todo.due_date == date(2026, 1, 22)
```

**Expected**: New todo created with due_date 2026-01-22 (+7 days)
**Result**: [ ] PASS / [ ] FAIL

---

### Test Scenario US5.3: Monthly Recurring Task Creation

**Given**: A monthly recurring todo with due_date "2026-01-15"
**When**: I mark it complete
**Then**: New occurrence created with due_date "2026-02-15"

**Test Steps**:
```python
todo = add_todo("Monthly report", due_date="2026-01-15", recurrence="monthly")
original_id = todo.id
mark_complete(original_id)

all_todos = get_all_todos()
new_todo = [t for t in all_todos if t.id != original_id and not t.completed][0]
# Verify new_todo.due_date == date(2026, 2, 15)
```

**Expected**: New todo created with due_date 2026-02-15 (next month, same day)
**Result**: [ ] PASS / [ ] FAIL

---

### Test Scenario US5.4: Monthly Recurring with Day Overflow

**Given**: A monthly recurring todo with due_date "2026-01-31"
**When**: I mark it complete
**Then**: New occurrence created with due_date "2026-02-28" (Feb has no day 31)

**Test Steps**:
```python
todo = add_todo("End of month task", due_date="2026-01-31", recurrence="monthly")
mark_complete(todo.id)

all_todos = get_all_todos()
new_todo = [t for t in all_todos if t.id != todo.id and not t.completed][0]
# Verify new_todo.due_date == date(2026, 2, 28)  # Feb 2026 ends on 28
```

**Expected**: New todo created with due_date 2026-02-28 (last day of February)
**Result**: [ ] PASS / [ ] FAIL

---

### Test Scenario US5.5: Recurring Task with Reminder Time

**Given**: A daily recurring todo with due_date and reminder_time
**When**: I mark it complete
**Then**: New occurrence preserves time component of reminder

**Test Steps**:
```python
todo = add_todo("Daily task", due_date="2026-01-15", reminder_time="2026-01-15 09:00", recurrence="daily")
mark_complete(todo.id)

all_todos = get_all_todos()
new_todo = [t for t in all_todos if t.id != todo.id and not t.completed][0]
# Verify new_todo.due_date == date(2026, 1, 16)
# Verify new_todo.reminder_time == datetime(2026, 1, 16, 9, 0)  # Same time
```

**Expected**: New todo has reminder_time "2026-01-16 09:00" (time preserved)
**Result**: [ ] PASS / [ ] FAIL

---

### Test Scenario US5.6: Recurring Task Copies Metadata

**Given**: A recurring todo with priority "high" and tags ["work", "urgent"]
**When**: I mark it complete
**Then**: New occurrence has same priority and tags

**Test Steps**:
```python
todo = add_todo("Important task", priority="high", tags=["work", "urgent"],
                due_date="2026-01-15", recurrence="daily")
mark_complete(todo.id)

all_todos = get_all_todos()
new_todo = [t for t in all_todos if t.id != todo.id and not t.completed][0]
# Verify new_todo.priority == "high"
# Verify new_todo.tags == ["work", "urgent"]
```

**Expected**: New todo has same priority and tags as original
**Result**: [ ] PASS / [ ] FAIL

---

### Test Scenario US5.7: Non-Recurring Todo (No Auto-Creation)

**Given**: A regular todo (recurrence="none") with due_date
**When**: I mark it complete
**Then**: NO new occurrence is created

**Test Steps**:
```python
todo = add_todo("One-time task", due_date="2026-01-15", recurrence="none")
original_count = len(get_all_todos())
mark_complete(todo.id)
new_count = len(get_all_todos())
# Verify new_count == original_count (no new todo created)
```

**Expected**: No new todo created, count unchanged
**Result**: [ ] PASS / [ ] FAIL

---

### Test Scenario US5.8: Recurring Todo Without Due Date (No Auto-Creation)

**Given**: A recurring todo WITHOUT due_date
**When**: I mark it complete
**Then**: NO new occurrence is created (due_date required for recurrence)

**Test Steps**:
```python
todo = add_todo("Task without date", recurrence="daily")  # No due_date
original_count = len(get_all_todos())
mark_complete(todo.id)
new_count = len(get_all_todos())
# Verify new_count == original_count (no new todo created)
```

**Expected**: No new todo created (recurrence requires due_date)
**Result**: [ ] PASS / [ ] FAIL

---

### Test Scenario US5.9: Create Recurring Todo with Invalid Recurrence

**Given**: The application is running
**When**: I attempt to create a todo with recurrence="hourly" (invalid)
**Then**: Error message returned

**Test Steps**:
```python
result = add_todo("Task", recurrence="hourly")
# Verify isinstance(result, str)
# Verify "Invalid recurrence" in result
```

**Expected Output**:
```
Error: Invalid recurrence 'hourly'. Valid values: none, daily, weekly, monthly
```

**Result**: [ ] PASS / [ ] FAIL

---

## Test Execution Summary - Feature 002, User Story 5

**Date**: _________________
**Tester**: _________________
**Total Scenarios (US5)**: 9
**Passed**: _______
**Failed**: _______
**Pass Rate**: _______

**Notes**:
-
-
-

**Overall Result**: [ ] PASS / [ ] FAIL

---

## User Story 3: Sort Tasks by Multiple Criteria (Priority: P3)

### Test Scenario US3.1: Sort by Due Date Ascending

**Given**: 3 todos with due dates "2026-03-01", "2026-01-15", "2026-02-10"
**When**: I sort by due_date ascending
**Then**: Returns todos in chronological order

**Test Steps**:
```python
from src.operations.todo_operations import add_todo
from src.operations.sort_operations import sort_by_due_date

todo1 = add_todo("Task A", due_date="2026-03-01")
todo2 = add_todo("Task B", due_date="2026-01-15")
todo3 = add_todo("Task C", due_date="2026-02-10")
all_todos = [todo1, todo2, todo3]

result = sort_by_due_date(all_todos, "ascending")
# Verify result[0].description == "Task B" (2026-01-15)
# Verify result[1].description == "Task C" (2026-02-10)
# Verify result[2].description == "Task A" (2026-03-01)
```

**Expected**: Todos sorted chronologically (earliest first)
**Result**: [ ] PASS / [ ] FAIL

---

### Test Scenario US3.2: Sort by Due Date with None Values

**Given**: 3 todos, 2 with due dates and 1 without
**When**: I sort by due_date ascending
**Then**: None values appear at end

**Test Steps**:
```python
todo1 = add_todo("Task A", due_date="2026-02-01")
todo2 = add_todo("Task B")  # No due date (None)
todo3 = add_todo("Task C", due_date="2026-01-01")
all_todos = [todo1, todo2, todo3]

result = sort_by_due_date(all_todos, "ascending")
# Verify result[0].description == "Task C" (2026-01-01)
# Verify result[1].description == "Task A" (2026-02-01)
# Verify result[2].description == "Task B" (None at end)
```

**Expected**: Todos with dates first, None at end
**Result**: [ ] PASS / [ ] FAIL

---

### Test Scenario US3.3: Sort by Priority Ascending

**Given**: Todos with priorities "low", "high", "medium"
**When**: I sort by priority ascending
**Then**: Returns high → medium → low

**Test Steps**:
```python
from src.operations.sort_operations import sort_by_priority

todo1 = add_todo("Task A", priority="low")
todo2 = add_todo("Task B", priority="high")
todo3 = add_todo("Task C", priority="medium")
all_todos = [todo1, todo2, todo3]

result = sort_by_priority(all_todos, "ascending")
# Verify result[0].priority == "high"
# Verify result[1].priority == "medium"
# Verify result[2].priority == "low"
```

**Expected**: Sorted high → medium → low
**Result**: [ ] PASS / [ ] FAIL

---

### Test Scenario US3.4: Sort by Priority Descending

**Given**: Todos with priorities "low", "high", "medium"
**When**: I sort by priority descending
**Then**: Returns low → medium → high

**Test Steps**:
```python
result = sort_by_priority(all_todos, "descending")
# Verify result[0].priority == "low"
# Verify result[1].priority == "medium"
# Verify result[2].priority == "high"
```

**Expected**: Sorted low → medium → high (reverse)
**Result**: [ ] PASS / [ ] FAIL

---

### Test Scenario US3.5: Sort Alphabetically (Case-Insensitive)

**Given**: Todos with descriptions "banana", "Apple", "cherry"
**When**: I sort alphabetically ascending
**Then**: Returns Apple → banana → cherry (case-insensitive)

**Test Steps**:
```python
from src.operations.sort_operations import sort_alphabetically

todo1 = add_todo("banana")
todo2 = add_todo("Apple")
todo3 = add_todo("cherry")
all_todos = [todo1, todo2, todo3]

result = sort_alphabetically(all_todos, "ascending")
# Verify result[0].description == "Apple"
# Verify result[1].description == "banana"
# Verify result[2].description == "cherry"
```

**Expected**: Sorted alphabetically (case-insensitive)
**Result**: [ ] PASS / [ ] FAIL

---

### Test Scenario US3.6: Apply Sort with SortCriteria

**Given**: Multiple todos
**When**: I use apply_sort() with SortCriteria(field="priority", direction="ascending")
**Then**: Dispatches to sort_by_priority() correctly

**Test Steps**:
```python
from src.operations.sort_operations import apply_sort
from src.models.filters import SortCriteria

todo1 = add_todo("Task A", priority="medium")
todo2 = add_todo("Task B", priority="high")
todo3 = add_todo("Task C", priority="low")
all_todos = [todo1, todo2, todo3]

sort_criteria = SortCriteria(field="priority", direction="ascending")
result = apply_sort(all_todos, sort_criteria)
# Verify result[0].priority == "high"
# Verify result[1].priority == "medium"
# Verify result[2].priority == "low"
```

**Expected**: Correctly dispatches and sorts by priority
**Result**: [ ] PASS / [ ] FAIL

---

## Test Execution Summary - Feature 002, User Story 3

**Date**: _________________
**Tester**: _________________
**Total Scenarios (US3)**: 6
**Passed**: _______
**Failed**: _______
**Pass Rate**: _______

**Notes**:
-
-
-

**Overall Result**: [ ] PASS / [ ] FAIL
