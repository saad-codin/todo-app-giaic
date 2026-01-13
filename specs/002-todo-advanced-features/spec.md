# Feature Specification: In-Memory Todo App — Advanced Features

**Feature Branch**: `002-todo-advanced-features`
**Created**: 2026-01-09
**Status**: Draft
**Input**: User description: "In-Memory Todo App — Advanced Features: Target audience: Individuals using a todo application to organize and manage daily tasks. Focus: Making an in-memory todo app more practical and usable through organization, search, and intelligent task behavior"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Task Organization with Priority and Tags (Priority: P1)

As a user managing multiple responsibilities, I want to assign priority levels and tags to my tasks so that I can quickly identify what needs my immediate attention and organize tasks by context (work, home, personal).

**Why this priority**: Priority and tags are fundamental organizational features that provide immediate value for categorizing and managing tasks. Without these, users cannot effectively organize growing task lists. This is the foundation for all other advanced features.

**Independent Test**: Can be fully tested by creating tasks with different priority levels (high, medium, low) and various tags (work, home, personal), then verifying they are stored and displayed correctly with their metadata.

**Acceptance Scenarios**:

1. **Given** I am creating a new task, **When** I specify priority as "high" and tags as "work, urgent", **Then** the task is created with priority=high and tags=[work, urgent]
2. **Given** I have an existing task, **When** I update its priority from "medium" to "high", **Then** the priority change is reflected in the task data
3. **Given** I have an existing task with tags ["work"], **When** I add a new tag "urgent", **Then** the task has tags ["work", "urgent"]
4. **Given** I create a task without specifying priority, **When** the task is created, **Then** it defaults to priority="medium"
5. **Given** I create a task without specifying tags, **When** the task is created, **Then** it has an empty tags list
6. **Given** I attempt to set an invalid priority level, **When** I provide priority="critical", **Then** I receive an error message indicating valid values are "high", "medium", or "low"

---

### User Story 2 - Search and Filter Tasks (Priority: P2)

As a user with many tasks, I want to search tasks by keyword and filter by completion status, priority, or tag so that I can quickly find specific tasks or view relevant subsets of my task list.

**Why this priority**: Search and filtering become essential as the task list grows beyond 10-15 items. This enables users to manage larger lists effectively and find tasks quickly. Depends on P1 (priority/tags) being implemented first.

**Independent Test**: Can be tested by creating 10+ tasks with various priorities, tags, and completion states, then verifying search returns matching results and filters correctly narrow the list.

**Acceptance Scenarios**:

1. **Given** I have 10 tasks with various descriptions, **When** I search for keyword "meeting", **Then** all tasks containing "meeting" in title or description are returned
2. **Given** I have tasks with mixed completion status, **When** I filter by completed=true, **Then** only completed tasks are displayed
3. **Given** I have tasks with priorities high/medium/low, **When** I filter by priority="high", **Then** only high-priority tasks are displayed
4. **Given** I have tasks with various tags, **When** I filter by tag="work", **Then** only tasks tagged "work" are displayed
5. **Given** I search for a keyword that matches no tasks, **When** I execute the search, **Then** an empty result list is returned with a message "No tasks found matching 'keyword'"
6. **Given** I apply multiple filters (priority="high" AND tag="work"), **When** filters are applied, **Then** only tasks matching ALL criteria are returned
7. **Given** I search with case variations, **When** I search for "Meeting" or "MEETING", **Then** the search is case-insensitive and returns all matches

---

### User Story 3 - Sort Tasks by Multiple Criteria (Priority: P3)

As a user organizing my workflow, I want to sort my task list by due date, priority, or alphabetical order so that I can view tasks in the most useful order for my current needs.

**Why this priority**: Sorting helps users prioritize their work but is less critical than basic organization (P1) and finding tasks (P2). Users can work effectively with unsorted lists if they have search/filter capabilities.

**Independent Test**: Can be tested by creating tasks with various due dates, priorities, and titles, then verifying each sort option produces the correct ordering.

**Acceptance Scenarios**:

1. **Given** I have tasks with different due dates, **When** I sort by due date ascending, **Then** tasks are ordered with nearest due date first, followed by tasks without due dates
2. **Given** I have tasks with different priorities, **When** I sort by priority descending, **Then** tasks are ordered high → medium → low
3. **Given** I have tasks with various titles, **When** I sort alphabetically ascending, **Then** tasks are ordered A-Z by title
4. **Given** I have tasks with various titles, **When** I sort alphabetically descending, **Then** tasks are ordered Z-A by title
5. **Given** some tasks have no due date, **When** I sort by due date, **Then** tasks without due dates appear at the end of the sorted list
6. **Given** I sort by priority, **When** multiple tasks have the same priority, **Then** they maintain their relative order (stable sort)

---

### User Story 4 - Due Dates and Reminder Times (Priority: P4)

As a user tracking time-sensitive tasks, I want to assign optional due dates and reminder times to tasks so that I know when tasks should be completed and when I should be reminded.

**Why this priority**: Due dates add temporal awareness to task management but don't require complex logic. This is a simple metadata extension that enables sorting by date (P3) but doesn't change core task behavior.

**Independent Test**: Can be tested by creating tasks with various due dates and reminder times, then verifying the metadata is stored correctly and can be retrieved.

**Acceptance Scenarios**:

1. **Given** I am creating a task, **When** I specify due_date="2026-01-15" and reminder_time="2026-01-15 09:00", **Then** the task stores both date and time values
2. **Given** I have an existing task, **When** I update its due date to "2026-01-20", **Then** the due date is updated
3. **Given** I create a task without a due date, **When** the task is created, **Then** due_date is None
4. **Given** I create a task without a reminder time, **When** the task is created, **Then** reminder_time is None
5. **Given** I set a reminder time without a due date, **When** the task is saved, **Then** both fields are stored independently (reminder doesn't require due date)
6. **Given** I specify an invalid date format, **When** I attempt to set due_date="tomorrow", **Then** I receive an error indicating expected format is "YYYY-MM-DD"
7. **Given** I specify an invalid time format, **When** I attempt to set reminder_time="9am", **Then** I receive an error indicating expected format is "YYYY-MM-DD HH:MM"

---

### User Story 5 - Recurring Tasks with Auto-Creation (Priority: P5)

As a user with routine tasks, I want to create recurring tasks (daily, weekly, monthly) that automatically generate the next occurrence when completed so that I don't have to manually re-create repetitive tasks.

**Why this priority**: Recurring tasks add significant value for routine task management but require complex logic (recurrence rules, auto-creation on completion). This is the most sophisticated feature and should be built last after all other features are stable.

**Independent Test**: Can be tested by creating a recurring task (e.g., "daily standup"), marking it complete, and verifying a new incomplete instance is automatically created with the next occurrence date.

**Acceptance Scenarios**:

1. **Given** I create a task with recurrence="daily" and due_date="2026-01-10", **When** the task is marked complete, **Then** a new incomplete task is created with due_date="2026-01-11"
2. **Given** I create a task with recurrence="weekly" and due_date="2026-01-10", **When** the task is marked complete, **Then** a new incomplete task is created with due_date="2026-01-17"
3. **Given** I create a task with recurrence="monthly" and due_date="2026-01-10", **When** the task is marked complete, **Then** a new incomplete task is created with due_date="2026-02-10"
4. **Given** I create a non-recurring task, **When** the task is marked complete, **Then** no new task is created
5. **Given** I complete a recurring task, **When** the next occurrence is created, **Then** it has the same title, description, priority, tags, and recurrence settings as the original
6. **Given** I complete a recurring task, **When** the next occurrence is created, **Then** it receives a new unique ID
7. **Given** I complete a recurring task with reminder_time="09:00", **When** the next occurrence is created, **Then** its reminder_time is set to the next due date at 09:00
8. **Given** I attempt to set an invalid recurrence value, **When** I provide recurrence="yearly", **Then** I receive an error indicating valid values are "none", "daily", "weekly", "monthly"
9. **Given** I mark an incomplete recurring task as incomplete again, **When** the operation completes, **Then** no new task is created (only completion triggers recurrence)

---

### Edge Cases

- What happens when searching with special characters or regex patterns in the keyword?
- How does the system handle tasks with extremely long tag lists (50+ tags)?
- What happens when filtering by multiple tags (AND vs OR logic)?
- How does sorting handle null/missing values (tasks without due dates when sorting by date)?
- What happens when a recurring task is deleted - are future occurrences also deleted?
- How does the system handle recurring tasks across month boundaries (e.g., monthly task due on Jan 31)?
- What happens when a user tries to set a due date in the past?
- How does sorting interact with filtering (sort filtered results or filter sorted results)?
- What happens when marking a recurring task complete multiple times rapidly?
- How does the system handle timezone considerations for due dates and reminder times?

## Requirements *(mandatory)*

### Functional Requirements

**Task Metadata and Organization:**

- **FR-001**: System MUST support three priority levels for tasks: "high", "medium", "low"
- **FR-002**: System MUST default new tasks to priority="medium" if not specified
- **FR-003**: System MUST validate priority values and reject invalid priorities with clear error messages
- **FR-004**: System MUST support tags/categories as a list of strings per task (e.g., ["work", "urgent", "home"])
- **FR-005**: System MUST allow tasks to have zero or more tags
- **FR-006**: System MUST support optional due_date field in ISO 8601 date format (YYYY-MM-DD)
- **FR-007**: System MUST support optional reminder_time field in ISO 8601 datetime format (YYYY-MM-DD HH:MM)
- **FR-008**: System MUST allow due_date and reminder_time to be set independently (neither requires the other)
- **FR-009**: System MUST validate date and datetime formats and reject invalid formats with clear error messages

**Search and Filter:**

- **FR-010**: System MUST provide case-insensitive keyword search across task title and description fields
- **FR-011**: System MUST return all tasks containing the search keyword as a substring
- **FR-012**: System MUST support filtering tasks by completion status (completed=true/false)
- **FR-013**: System MUST support filtering tasks by priority level (high/medium/low)
- **FR-014**: System MUST support filtering tasks by tag (return tasks containing the specified tag)
- **FR-015**: System MUST support combining multiple filters with AND logic (all conditions must match)
- **FR-016**: System MUST return empty result set with informative message when no tasks match search/filter criteria

**Sorting:**

- **FR-017**: System MUST support sorting tasks by due_date in ascending order (earliest first)
- **FR-018**: System MUST support sorting tasks by due_date in descending order (latest first)
- **FR-019**: System MUST support sorting tasks by priority (high → medium → low, or reverse)
- **FR-020**: System MUST support sorting tasks alphabetically by title (A-Z or Z-A)
- **FR-021**: System MUST place tasks without due dates at the end when sorting by due_date
- **FR-022**: System MUST use stable sorting (preserve relative order for equal elements)

**Recurring Tasks:**

- **FR-023**: System MUST support four recurrence types: "none" (default), "daily", "weekly", "monthly"
- **FR-024**: System MUST validate recurrence values and reject invalid recurrence types with clear error messages
- **FR-025**: System MUST automatically create the next occurrence when a recurring task is marked complete
- **FR-026**: System MUST calculate next occurrence date based on recurrence type (daily: +1 day, weekly: +7 days, monthly: +1 month)
- **FR-027**: System MUST copy task metadata (title, description, priority, tags, recurrence, reminder offset) to the next occurrence
- **FR-028**: System MUST assign a new unique ID to the next occurrence
- **FR-029**: System MUST set the next occurrence to incomplete status
- **FR-030**: System MUST NOT create new occurrences when non-recurring tasks are completed
- **FR-031**: System MUST NOT create new occurrences when recurring tasks are marked incomplete

**General Constraints:**

- **FR-032**: System MUST store all data in memory only (no persistence to disk)
- **FR-033**: System MUST use Python 3.13+ with standard library only (no external packages)
- **FR-034**: System MUST provide all functionality as deterministic, testable logic functions (no UI, no CLI parsing, no notifications)
- **FR-035**: System MUST maintain backward compatibility with basic todo operations from feature 001 (add, view, update, delete, mark complete/incomplete)
- **FR-036**: System MUST preserve existing todo IDs and not break existing functionality when advanced features are added

### Key Entities

- **Todo (Extended)**: Extends the basic Todo entity from feature 001 with additional optional fields:
  - **priority** (string): Task priority level - "high", "medium", or "low" (defaults to "medium")
  - **tags** (list of strings): Categories or labels for organization (e.g., ["work", "home", "urgent"])
  - **due_date** (date or None): Optional target completion date in YYYY-MM-DD format
  - **reminder_time** (datetime or None): Optional reminder timestamp in YYYY-MM-DD HH:MM format
  - **recurrence** (string): Recurrence pattern - "none", "daily", "weekly", or "monthly" (defaults to "none")
  - All basic fields preserved: id (int), description (string), completed (boolean)

- **SearchFilter**: Represents search and filter criteria for querying tasks:
  - **keyword** (string or None): Search term for title/description matching
  - **completed** (boolean or None): Filter by completion status
  - **priority** (string or None): Filter by priority level
  - **tag** (string or None): Filter by specific tag

- **SortCriteria**: Represents sort ordering for task lists:
  - **field** (string): Field to sort by - "due_date", "priority", "title"
  - **direction** (string): Sort direction - "ascending" or "descending"

### Assumptions

- **Priority Default**: Tasks without specified priority default to "medium" (balanced default)
- **Tag Storage**: Tags are stored as lowercase strings to enable case-insensitive filtering
- **Date Format**: All dates use ISO 8601 format (YYYY-MM-DD) for consistency and unambiguous parsing
- **Time Format**: Reminder times include both date and time (YYYY-MM-DD HH:MM) to specify exact moment
- **Timezone Handling**: All times are treated as local time (no timezone conversion in Phase II)
- **Recurrence Calculation**: Monthly recurrence uses simple month addition (Jan 31 → Feb 28/29 for months with fewer days)
- **Search Matching**: Search uses substring matching (not full-text search or fuzzy matching)
- **Filter Combination**: Multiple filters use AND logic (all must match); OR logic not supported in Phase II
- **Sorting Stability**: Sorting maintains relative order of equal elements (stable sort)
- **Recurring Completion**: Only the completion action triggers next occurrence creation (not update or other operations)
- **In-Memory Only**: No persistence means recurring tasks don't generate future occurrences after app restart
- **No Notifications**: Reminder times are stored but not acted upon (no active notification system in Phase II)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can create a task with priority and tags in a single operation
- **SC-002**: Search returns results instantly (under 100ms) for task lists up to 1000 items
- **SC-003**: Filter operations reduce a 100-task list to relevant subset in under 50ms
- **SC-004**: Sorting reorders a 100-task list in under 50ms regardless of sort criteria
- **SC-005**: Completing a recurring task creates the next occurrence within 10ms
- **SC-006**: All search, filter, and sort operations work correctly on empty task lists without errors
- **SC-007**: Users can combine search + filter + sort to find specific tasks (e.g., "incomplete work tasks sorted by priority")
- **SC-008**: 100% of advanced features work without breaking any basic todo functionality from feature 001
- **SC-009**: All date/time parsing errors provide clear messages indicating expected format
- **SC-010**: Recurring task logic correctly handles all recurrence types (daily, weekly, monthly) across month/year boundaries
