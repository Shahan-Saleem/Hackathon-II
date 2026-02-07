"""
Basic in-memory Python console todo app for Phase 1
Implements core task management capabilities without persistent storage
"""
import argparse
import sys
from datetime import datetime
from typing import List, Optional


class Task:
    """
    Task model class with basic properties
    """
    def __init__(self, task_id: int, title: str, description: str = "", completed: bool = False):
        self.id = task_id
        self.title = title
        self.description = description
        self.completed = completed
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def to_string(self) -> str:
        """Convert task to string representation for display"""
        status = "X" if self.completed else "O"
        return f"{status} [{self.id}] {self.title}\n    Description: {self.description}"

    def mark_completed(self):
        """Mark the task as completed"""
        self.completed = True
        self.updated_at = datetime.now()


class InMemoryStorage:
    """
    In-memory storage mechanism to hold tasks
    """
    def __init__(self):
        self.tasks = []  # List to store Task objects
        self.next_id = 1  # Counter for generating unique IDs

    def add_task(self, task: Task):
        """Add a task to storage"""
        self.tasks.append(task)
        self.next_id += 1

    def get_all_tasks(self) -> List[Task]:
        """Get all tasks from storage"""
        return self.tasks

    def get_task_by_id(self, task_id: int) -> Optional[Task]:
        """Get a specific task by ID"""
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None

    def update_task(self, task_id: int, title: str = None, description: str = None):
        """Update an existing task"""
        task = self.get_task_by_id(task_id)
        if not task:
            return False

        if title is not None:
            task.title = title
        if description is not None:
            task.description = description
        task.updated_at = datetime.now()
        return True

    def complete_task(self, task_id: int) -> bool:
        """Mark a task as completed"""
        task = self.get_task_by_id(task_id)
        if not task:
            return False
        task.mark_completed()
        return True

    def delete_task(self, task_id: int) -> bool:
        """Delete a task from storage"""
        task = self.get_task_by_id(task_id)
        if not task:
            return False
        self.tasks.remove(task)
        return True


class TodoApp:
    """
    Main application class for the console todo app
    """
    def __init__(self):
        self.storage = InMemoryStorage()

    def add_task(self, title: str, description: str = ""):
        """Add a new task"""
        if not title.strip():
            print("Error: Task title cannot be empty")
            return

        # Create new task with unique ID
        new_task = Task(self.storage.next_id, title, description)
        self.storage.add_task(new_task)
        print(f"Task added: {new_task.title} (ID: {new_task.id})")

    def list_tasks(self):
        """List all tasks"""
        tasks = self.storage.get_all_tasks()

        if not tasks:
            print("No tasks found.")
            return

        print("All Tasks:")
        for task in tasks:
            print(task.to_string())

    def update_task(self, task_id: int, title: str = None, description: str = None):
        """Update an existing task"""
        success = self.storage.update_task(task_id, title, description)
        if success:
            print(f"Task {task_id} updated successfully")
        else:
            print(f"Error: Task with ID {task_id} not found")

    def complete_task(self, task_id: int):
        """Mark a task as completed"""
        success = self.storage.complete_task(task_id)
        if success:
            print(f"Task {task_id} marked as completed")
        else:
            print(f"Error: Task with ID {task_id} not found")

    def delete_task(self, task_id: int):
        """Delete a task"""
        success = self.storage.delete_task(task_id)
        if success:
            print(f"Task {task_id} deleted successfully")
        else:
            print(f"Error: Task with ID {task_id} not found")


def main():
    """Main function to run the console todo app"""
    app = TodoApp()

    # Set up command-line argument parser
    parser = argparse.ArgumentParser(description='In-Memory Console Todo App')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Add command
    add_parser = subparsers.add_parser('add', help='Add a new task')
    add_parser.add_argument('--title', required=True, help='Task title')
    add_parser.add_argument('--description', default='', help='Task description')

    # List command
    list_parser = subparsers.add_parser('list', help='List all tasks')

    # Update command
    update_parser = subparsers.add_parser('update', help='Update a task')
    update_parser.add_argument('--id', type=int, required=True, help='Task ID')
    update_parser.add_argument('--title', help='New task title')
    update_parser.add_argument('--description', help='New task description')

    # Complete command
    complete_parser = subparsers.add_parser('complete', help='Mark task as completed')
    complete_parser.add_argument('--id', type=int, required=True, help='Task ID')

    # Delete command
    delete_parser = subparsers.add_parser('delete', help='Delete a task')
    delete_parser.add_argument('--id', type=int, required=True, help='Task ID')

    # Help command
    help_parser = subparsers.add_parser('help', help='Show help information')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        if args.command == 'add':
            app.add_task(args.title, args.description)
        elif args.command == 'list':
            app.list_tasks()
        elif args.command == 'update':
            app.update_task(args.id, args.title, args.description)
        elif args.command == 'complete':
            app.complete_task(args.id)
        elif args.command == 'delete':
            app.delete_task(args.id)
        elif args.command == 'help':
            parser.print_help()
        else:
            parser.print_help()
    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()