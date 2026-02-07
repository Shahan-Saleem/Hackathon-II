# Quickstart Guide: Phase I - In-Memory Python Console Todo App

**Feature**: Phase I - In-Memory Python Console Todo App
**Date**: 2026-01-31

## Getting Started

### Prerequisites
- Python 3.6 or higher installed on your system

### Installation
1. Clone or download the repository
2. Navigate to the project directory
3. Ensure `implementation.py` is in the current directory

### Running the Application
```bash
python implementation.py [command] [arguments]
```

## Available Commands

### Add a Task
```bash
python implementation.py add --title "Buy groceries" --description "Milk, bread, eggs" --user "john_doe"
```

### Update a Task
```bash
python implementation.py update --id 1 --title "Buy groceries and cook dinner" --user "john_doe"
```

### Delete a Task
```bash
python implementation.py delete --id 1 --user "john_doe"
```

### Complete a Task
```bash
python implementation.py complete --id 1 --user "john_doe"
```

### List All Tasks
```bash
python implementation.py list --user "john_doe"
```

## Default Values
- If no user is specified, the default user "default_user" will be used
- New tasks are created with "completed" status as False by default

## Example Usage
```bash
# Add a task
python implementation.py add --title "Learn Python" --description "Complete the tutorial" --user "alice"

# List all tasks
python implementation.py list --user "alice"

# Mark task as completed (assuming task ID 1 exists)
python implementation.py complete --id 1 --user "alice"

# Update task
python implementation.py update --id 1 --title "Master Python" --user "alice"

# Delete task
python implementation.py delete --id 1 --user "alice"
```

## Features
- In-memory storage (tasks persist only during the session)
- User isolation (each user has their own task list)
- Task management (create, update, delete, complete, list)
- Command-line interface for easy interaction