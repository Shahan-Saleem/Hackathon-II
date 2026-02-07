# Data Model: Phase I - In-Memory Python Console Todo App

**Feature**: Phase I - In-Memory Python Console Todo App
**Date**: 2026-01-31

## Entities

### Task
Represents a user's todo item with attributes: ID (unique identifier), Title (required string), Description (optional string), Status (completed/incomplete boolean), CreatedBy (user identifier)

**Attributes**:
- `id`: int (unique identifier, sequential numbering per user)
- `title`: str (required, non-empty string)
- `description`: str (optional, can be empty string)
- `completed`: bool (default: False)
- `created_by`: str (user identifier)

**Validation Rules**:
- `title` must not be empty or None
- `id` must be unique within a user's task list
- `completed` must be boolean value

### User Session
Represents a user's interaction with the system, maintaining their isolated task list

**Attributes**:
- `user_id`: str (identifier for the user)
- `tasks`: List[Task] (collection of Task objects belonging to this user)

**Relationships**:
- One User Session to Many Tasks (one-to-many relationship)
- Each task belongs to exactly one user session

## Storage Structure

### In-Memory Data Structure
```
storage: Dict[str, List[Task]]
  - Key: user_id (string)
  - Value: List of Task objects belonging to that user
```

**Operations**:
- Create: Add new Task to user's list in storage[user_id]
- Read: Access Task list from storage[user_id]
- Update: Modify existing Task in storage[user_id]
- Delete: Remove Task from storage[user_id]

## State Transitions

### Task Status Transition
- Initial state: `completed = False`
- Transition to completed: `completed = True` (via complete operation)
- No reverse transition (completed tasks remain completed)

## Constraints

### User Isolation Constraint
- Users can only access tasks in their own user session
- Cross-user access is prohibited by design
- Enforcement through user_id validation on all operations

### Data Integrity Constraints
- Task titles must not be empty or None
- Task IDs must be unique per user
- Task objects must have valid attribute types