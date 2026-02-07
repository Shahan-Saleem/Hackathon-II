# Quickstart Guide: Console UI (UI-First)

## Overview
Getting started with the console-based UI for Phase II task management. This guide covers installation, setup, and basic usage.

## Prerequisites
- Python 3.11 or higher
- Access to Phase I implementation (existing task management system)
- Terminal/command prompt access

## Setup
1. Clone or download the project repository
2. Navigate to the project directory
3. Ensure Phase I implementation is accessible (dependencies met)

## Running the Console UI
```bash
python src/console_ui/main.py
```

## Basic Commands
Once the UI is running, you can use the following commands:

### Add a Task
```
add "Task title goes here"
```
Creates a new task with the specified title.

### List All Tasks
```
list
```
Displays all tasks with their ID, title, and completion status.

### Complete a Task
```
complete <task_id>
```
Marks the specified task as completed.

### Update a Task
```
update <task_id> "New title for the task"
```
Updates the title of the specified task.

### Delete a Task
```
delete <task_id>
```
Removes the specified task permanently.

### Exit the Application
```
exit
```
Terminates the console UI session.

## Example Workflow
```
> add "Buy groceries"
Task added with ID: 1

> add "Walk the dog"
Task added with ID: 2

> list
ID  | Title          | Status
----|----------------|--------
1   | Buy groceries  | Pending
2   | Walk the dog   | Pending

> complete 1
Task 1 marked as completed

> list
ID  | Title          | Status
----|----------------|--------
1   | Buy groceries  | Completed
2   | Walk the dog   | Pending

> exit
Goodbye!
```

## Error Handling
If you enter an invalid command or incorrect parameters, you'll see a clear error message:

```
> invalidcommand
Error: Unknown command 'invalidcommand'. Valid commands are: add, update, delete, complete, list, exit

> complete
Error: Missing task ID. Usage: complete <task_id>
```

## Troubleshooting
- If the application won't start, ensure Python 3.11+ is installed and accessible
- If commands don't work, check that you're following the exact syntax shown above
- If you see internal error messages, contact support as this indicates an unexpected issue