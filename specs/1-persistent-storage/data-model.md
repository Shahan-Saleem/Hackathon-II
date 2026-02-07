# Data Model: Persistent Storage Integration

## Task Entity

### Attributes
- **id** (string/UUID): Unique identifier for the task
  - Generated using UUID4 for uniqueness
  - Immutable once created
  - Required field

- **description** (string): Text description of the task
  - User-provided text
  - Mutable through update operations
  - Required field

- **completed** (boolean): Status indicator for task completion
  - Initially false when created
  - Set to true when task is completed
  - Mutable through complete/delete operations

- **created_at** (ISO 8601 timestamp): Timestamp of task creation
  - Automatically set when task is created
  - Immutable once set
  - Required field

- **updated_at** (ISO 8601 timestamp): Timestamp of last task update
  - Automatically updated when task is modified
  - Required field

### Relationships
- Tasks exist independently (no parent-child relationships)
- All tasks belong to the same application instance

### Validation Rules
- Description must not be empty or whitespace-only
- ID must follow UUID format
- Timestamps must be in ISO 8601 format
- Completed status must be boolean

### State Transitions
- **Created**: New task with `completed = false`
- **Updated**: Existing task with modified description, `updated_at` changed
- **Completed**: Existing task with `completed = true`, `updated_at` changed
- **Deleted**: Task removed from storage

## Persistence Structure

### File Format
- JSON file containing an array of Task objects
- File named `tasks.json` in application directory
- UTF-8 encoded

### Example Structure
```json
{
  "version": "1.0",
  "tasks": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "description": "Sample task",
      "completed": false,
      "created_at": "2026-02-01T08:30:00Z",
      "updated_at": "2026-02-01T08:30:00Z"
    }
  ]
}
```

### Metadata
- **version**: Schema version for future compatibility
- **tasks**: Array of Task entities