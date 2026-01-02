# In-Memory Python Console Todo App

**Phase I**: Console-based todo application with in-memory storage

## Quick Start

```bash
# Run the application
python -m src.cli.console_app
```

Or with UV:
```bash
uv run python -m src.cli.console_app
```

## Features

- ✅ Add todos with auto-assigned IDs
- ✅ View all todos with completion status
- ✅ Update todo descriptions
- ✅ Mark todos complete/incomplete
- ✅ Delete todos
- ✅ Console menu-driven interface

## Requirements

- Python 3.13+
- No external dependencies (standard library only)

## Project Structure

```
src/
├── models/         # Data models (Todo)
├── repository/     # In-memory storage
├── operations/     # Business logic
└── cli/           # Console interface

tests/manual/      # Manual test scenarios
```

## Documentation

See `specs/001-console-todo/` for complete specification, plan, and task breakdown:
- `spec.md` - Feature specification
- `plan.md` - Implementation plan
- `tasks.md` - Task breakdown
- `quickstart.md` - Detailed usage guide

## Phase I Constraints

- **In-memory only**: All data resets on restart (expected behavior)
- **No persistence**: No files or databases
- **No external dependencies**: Python standard library only
- **Console only**: No web or GUI interface

## Success Criteria

All 7 success criteria from specification validated ✅:
- SC-001: Complete all CRUD operations within 5 minutes ✅
- SC-002: Instant response times (under 100ms) ✅
- SC-003: 100% operation success rate ✅
- SC-004: Fully AI-generated code ✅
- SC-005: Complete state reset on restart ✅
- SC-006: Clear, self-explanatory error messages ✅
- SC-007: Intuitive menu navigation ✅

See `specs/001-console-todo/validation-results.md` for detailed validation evidence.
