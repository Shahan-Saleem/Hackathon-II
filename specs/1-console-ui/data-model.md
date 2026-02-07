# Data Model: Console UI (UI-First)

## Overview
Data structures and entities for the console-based UI that adheres to Phase II UI-First principles while preserving Phase I contracts.

## Task Entity
**Definition**: Core entity representing a user task with essential attributes

**Fields**:
- `id` (string/integer): Unique identifier for the task
- `title` (string): Human-readable description of the task
- `completed` (boolean): Status indicating whether the task is completed

**Validation rules**:
- `id` must be unique within the system
- `title` must not be empty or null
- `completed` must be a boolean value (true/false)

**State transitions**:
- `pending` → `completed`: When task completion is requested
- `completed` → `pending`: When task is marked as incomplete (reopened)

## Command Interface
**Definition**: Structure for representing UI commands and their parameters

**Commands**:
- `add`: Creates a new task
  - Parameters: `title` (required string)
- `update`: Modifies an existing task
  - Parameters: `id` (required identifier), `title` (optional string), `completed` (optional boolean)
- `delete`: Removes a task
  - Parameters: `id` (required identifier)
- `complete`: Marks a task as completed
  - Parameters: `id` (required identifier)
- `list`: Displays all tasks
  - Parameters: none
- `exit`: Terminates the application
  - Parameters: none

**Validation rules**:
- Each command must have the required parameters present
- Parameter types must match expected format
- Invalid commands must be rejected deterministically

## User Input Structure
**Definition**: Format for collecting and validating user input

**Fields**:
- `command` (string): Command name (must match one of the valid commands)
- `arguments` (dict): Key-value pairs of command parameters
- `raw_input` (string): Original user input for error reporting

**Validation rules**:
- Command must be one of the predefined valid commands
- Arguments must match the expected format for the command
- Required arguments must be present

## Output Format
**Definition**: Standardized format for displaying results to users

**List Operation Response**:
- Header with column names: ID, Title, Status
- Rows of task data with consistent formatting
- Footer with summary information (total tasks, completed tasks, etc.)

**Single Task Response**:
- Task ID
- Task title
- Completion status (Completed/Pending)

**Error Response**:
- Error message in human-readable format
- No internal system details exposed
- Consistent format across all error types

## Session State
**Definition**: Temporary state maintained during UI session (transient, not persisted)

**Fields**:
- `is_running` (boolean): Indicates if the UI session is active
- `last_command` (string): Most recently executed command (for debugging)
- `command_history` (list): Recent commands (limited to last N entries for memory efficiency)

**Constraints**:
- No persistent storage of session state
- All permanent state managed by Phase I mechanisms
- Session state cleared when UI exits