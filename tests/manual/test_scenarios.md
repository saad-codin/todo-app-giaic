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
