# Quickstart Guide: In-Memory Python Console Todo App

**Feature**: 001-console-todo
**Date**: 2026-01-02
**Purpose**: Setup and run instructions for Phase I console todo application

## Prerequisites

- **Python 3.13+** installed on your system
- **UV** (Python package and project manager) installed
- **Git** (optional, for cloning the repository)

### Install UV

If you don't have UV installed:

**macOS/Linux**:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows**:
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Verify installation:
```bash
uv --version
```

## Quick Start (5 minutes)

### 1. Clone or Navigate to Repository

```bash
# If cloning
git clone <repository-url>
cd <repository-name>

# If already cloned
cd <repository-name>
```

### 2. Checkout Feature Branch

```bash
git checkout 001-console-todo
```

### 3. Run the Application

**Option A: Using UV (recommended)**
```bash
uv run python src/cli/console_app.py
```

**Option B: Using Python directly**
```bash
python3.13 src/cli/console_app.py
```

The application will start and display the main menu:

```
=== Todo Application ===
1. Add Todo
2. View All Todos
3. Update Todo
4. Delete Todo
5. Mark Todo Complete
6. Mark Todo Incomplete
7. Exit

Enter your choice (1-7):
```

## Usage Examples

### Example 1: Add and View Todos

1. Run the application
2. Enter `1` to add a todo
3. Enter description: `Buy groceries`
4. Todo is created with ID 1
5. Enter `2` to view all todos
6. You'll see:
   ```
   [ ] 1: Buy groceries
   ```
7. Enter `7` to exit

### Example 2: Complete CRUD Workflow

```
Choose 1: Add Todo
  → Enter: "Buy groceries"
  → Todo created: [ ] 1: Buy groceries

Choose 1: Add Todo
  → Enter: "Call dentist"
  → Todo created: [ ] 2: Call dentist

Choose 2: View All Todos
  → Shows:
    [ ] 1: Buy groceries
    [ ] 2: Call dentist

Choose 5: Mark Todo Complete
  → Enter ID: 1
  → Todo marked complete: [✓] 1: Buy groceries

Choose 3: Update Todo
  → Enter ID: 2
  → Enter new description: "Call dentist at 3pm"
  → Todo updated: [ ] 2: Call dentist at 3pm

Choose 4: Delete Todo
  → Enter ID: 1
  → Todo deleted

Choose 2: View All Todos
  → Shows:
    [ ] 2: Call dentist at 3pm

Choose 7: Exit
  → Application exits, all data is lost (expected behavior)
```

## Project Structure

```
repository-root/
├── src/
│   ├── models/
│   │   └── todo.py              # Todo data model
│   ├── repository/
│   │   └── todo_repository.py   # In-memory storage
│   ├── operations/
│   │   └── todo_operations.py   # Business logic
│   └── cli/
│       └── console_app.py       # Main application (RUN THIS)
├── tests/
│   └── manual/
│       └── test_scenarios.md    # Manual test cases
├── specs/
│   └── 001-console-todo/
│       ├── spec.md              # Feature specification
│       ├── plan.md              # Implementation plan
│       ├── data-model.md        # Data model details
│       ├── quickstart.md        # This file
│       └── contracts/
│           └── operations.md    # Operation contracts
├── pyproject.toml               # UV project configuration
└── README.md                    # General project information
```

## Features

This Phase I application supports:

✅ **Add Todo** - Create new todos with auto-assigned IDs
✅ **View All Todos** - List all todos with status indicators
✅ **Update Todo** - Modify todo descriptions
✅ **Delete Todo** - Remove todos by ID
✅ **Mark Complete/Incomplete** - Toggle todo completion status

## Important Notes

### In-Memory Storage
- **All data is stored in memory only**
- **Data is lost when the application exits** (expected behavior)
- **No persistence to files or databases** (per Phase I requirements)

This is intentional for Phase I. Persistence will be added in Phase II.

### ID Management
- IDs start at 1 and auto-increment
- IDs are never reused, even after deletion
- After deleting ID 2, the next new todo will still get the next sequential ID

### Error Handling
- Empty descriptions are rejected
- Invalid IDs show "Todo not found" message
- Invalid menu choices prompt for valid input
- Application never crashes - all errors are handled gracefully

## Troubleshooting

### "Command not found: uv"
**Solution**: Install UV following the instructions in Prerequisites section

### "Python 3.13 not found"
**Solution**: Install Python 3.13+ from [python.org](https://www.python.org/downloads/)

### "ModuleNotFoundError: No module named 'src'"
**Solution**: Make sure you're running from the repository root directory, not from inside `src/`

### Application doesn't show menu
**Solution**: Check that you're running `src/cli/console_app.py`, not other files

### Data not persisting
**This is expected behavior** - Phase I stores data in memory only. Data resets on restart.

## Testing

### Manual Test Scenarios

See `tests/manual/test_scenarios.md` for comprehensive test scenarios covering:
- All user stories (P1-P4)
- All acceptance scenarios
- Edge cases

### Running Manual Tests

1. Follow the test scenarios in `tests/manual/test_scenarios.md`
2. Execute each scenario step-by-step
3. Verify expected outcomes match actual results
4. Record pass/fail for each scenario

## Next Steps

After successfully running the Phase I application:

1. **Explore the code** in `src/` to understand the implementation
2. **Run manual tests** from `tests/manual/test_scenarios.md`
3. **Read the specification** in `specs/001-console-todo/spec.md`
4. **Review the architecture** in `specs/001-console-todo/plan.md`

## Phase II Preview

Phase II will evolve this application into a full-stack web app:
- **Frontend**: Next.js web interface
- **Backend**: FastAPI REST API
- **Database**: Neon PostgreSQL for persistence
- **Reuses**: Todo model and business logic from Phase I

The console application will remain functional alongside the web version.

## Support

For issues or questions:
- Check the specification: `specs/001-console-todo/spec.md`
- Review the implementation plan: `specs/001-console-todo/plan.md`
- Read operation contracts: `specs/001-console-todo/contracts/operations.md`
- Consult the constitution: `.specify/memory/constitution.md`

## Success Criteria Validation

After running the application, verify these success criteria (from spec.md):

- ✅ **SC-001**: You can complete all CRUD operations within 5 minutes
- ✅ **SC-002**: Application responds instantly (under 100ms)
- ✅ **SC-003**: All valid operations complete without crashes
- ✅ **SC-004**: Code generated entirely via Claude Code
- ✅ **SC-005**: Application state resets on restart (expected)
- ✅ **SC-006**: Error messages are clear and helpful
- ✅ **SC-007**: Menu navigation is intuitive

If all criteria are met, Phase I is successfully complete!
