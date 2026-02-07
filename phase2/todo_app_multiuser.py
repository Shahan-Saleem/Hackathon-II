"""
Multi-user in-memory Python console todo app for Phase 2
Extends Phase 1 with user authentication and multi-user support
"""
import argparse
import sys
from datetime import datetime
from typing import List, Optional


class User:
    """
    User model class with basic properties
    """
    def __init__(self, username: str):
        self.username = username
        self.created_at = datetime.now()

    def __str__(self):
        return self.username


class Task:
    """
    Task model class with basic properties and user association
    """
    def __init__(self, task_id: int, title: str, description: str = "", completed: bool = False, user: str = None):
        self.id = task_id
        self.title = title
        self.description = description
        self.completed = completed
        self.user = user  # Username of the task owner
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def to_string(self) -> str:
        """Convert task to string representation for display"""
        status = "X" if self.completed else "O"
        return f"{status} [{self.id}] {self.title}\n    Description: {self.description}\n    User: {self.user}"

    def mark_completed(self):
        """Mark the task as completed"""
        self.completed = True
        self.updated_at = datetime.now()


class MultiUserInMemoryStorage:
    """
    Multi-user in-memory storage mechanism to hold tasks by user
    """
    def __init__(self):
        self.users = {}  # Dictionary to store User objects by username
        self.tasks_by_user = {}  # Dictionary to store tasks by user
        self.next_task_id = 1  # Counter for generating unique task IDs

    def add_user(self, username: str) -> bool:
        """Add a user to storage if not already exists"""
        if username in self.users:
            return False  # User already exists

        user = User(username)
        self.users[username] = user
        self.tasks_by_user[username] = []  # Initialize task list for this user
        return True

    def user_exists(self, username: str) -> bool:
        """Check if user exists in storage"""
        return username in self.users

    def get_user(self, username: str) -> Optional[User]:
        """Get a user by username"""
        return self.users.get(username)

    def add_task(self, task: Task):
        """Add a task to a user's storage"""
        if task.user not in self.tasks_by_user:
            self.tasks_by_user[task.user] = []

        self.tasks_by_user[task.user].append(task)
        self.next_task_id += 1

    def get_all_tasks(self, username: str) -> List[Task]:
        """Get all tasks for a specific user"""
        if username not in self.tasks_by_user:
            return []
        return self.tasks_by_user[username]

    def get_task_by_id(self, task_id: int) -> Optional[Task]:
        """Get a specific task by ID from any user's task list"""
        for user_tasks in self.tasks_by_user.values():
            for task in user_tasks:
                if task.id == task_id:
                    return task
        return None

    def get_task_by_id_for_user(self, username: str, task_id: int) -> Optional[Task]:
        """Get a specific task by user and ID"""
        if username not in self.tasks_by_user:
            return None

        for task in self.tasks_by_user[username]:
            if task.id == task_id:
                return task
        return None

    def update_task(self, username: str, task_id: int, title: str = None, description: str = None):
        """Update an existing task if owned by the user"""
        task = self.get_task_by_id_for_user(username, task_id)
        if not task:
            return False

        if task.user != username:
            return False  # User doesn't own this task

        if title is not None:
            task.title = title
        if description is not None:
            task.description = description
        task.updated_at = datetime.now()
        return True

    def complete_task(self, username: str, task_id: int) -> bool:
        """Mark a task as completed if owned by the user"""
        task = self.get_task_by_id_for_user(username, task_id)
        if not task or task.user != username:
            return False  # Task not found or user doesn't own it
        task.mark_completed()
        return True

    def delete_task(self, username: str, task_id: int) -> bool:
        """Delete a task from storage if owned by the user"""
        if username not in self.tasks_by_user:
            return False

        for i, task in enumerate(self.tasks_by_user[username]):
            if task.id == task_id and task.user == username:
                self.tasks_by_user[username].pop(i)
                return True
        return False  # Task not found or not owned by user


class TodoAppMultiUser:
    """
    Main application class for the multi-user console todo app
    """
    def __init__(self):
        self.storage = MultiUserInMemoryStorage()
        self.current_user = None  # Track current user session

    def login(self, username: str):
        """Establish user context for the session"""
        if not username.strip():
            print("Error: Username cannot be empty")
            return False

        # Create user if doesn't exist
        user_created = self.storage.add_user(username)
        self.current_user = username

        if user_created:
            print(f"New user created: {username}")

        print(f"Login successful. User context established: {username}")
        return True

    def add_task(self, title: str, description: str = "", user: str = None):
        """Add a new task for a specific user"""
        # Use provided user or current user
        target_user = user if user else self.current_user

        if not target_user:
            print("Error: No user specified and no current user logged in")
            return

        if not self.storage.user_exists(target_user):
            print(f"Error: User '{target_user}' does not exist")
            return

        if not title.strip():
            print("Error: Task title cannot be empty")
            return

        # Create new task with unique ID
        new_task = Task(self.storage.next_task_id, title, description, user=target_user)
        self.storage.add_task(new_task)
        print(f"Task added: {new_task.title} (ID: {new_task.id}) for user: {target_user}")

    def list_tasks(self, user: str = None):
        """List all tasks for a specific user"""
        # Use provided user or current user
        target_user = user if user else self.current_user

        if not target_user:
            print("Error: No user specified and no current user logged in")
            return

        if not self.storage.user_exists(target_user):
            print(f"Error: User '{target_user}' does not exist")
            return

        tasks = self.storage.get_all_tasks(target_user)

        if not tasks:
            print(f"No tasks found for user: {target_user}")
            return

        print(f"Tasks for user: {target_user}")
        for task in tasks:
            print(task.to_string())

    def update_task(self, task_id: int, user: str = None, title: str = None, description: str = None):
        """Update an existing task for a specific user"""
        # Use provided user or current user
        target_user = user if user else self.current_user

        if not target_user:
            print("Error: No user specified and no current user logged in")
            return

        if not self.storage.user_exists(target_user):
            print(f"Error: User '{target_user}' does not exist")
            return

        success = self.storage.update_task(target_user, task_id, title, description)
        if success:
            print(f"Task {task_id} updated successfully for user: {target_user}")
        else:
            print(f"Error: Task with ID {task_id} not found or not owned by user {target_user}")

    def complete_task(self, task_id: int, user: str = None):
        """Mark a task as completed for a specific user"""
        # Use provided user or current user
        target_user = user if user else self.current_user

        if not target_user:
            print("Error: No user specified and no current user logged in")
            return

        if not self.storage.user_exists(target_user):
            print(f"Error: User '{target_user}' does not exist")
            return

        success = self.storage.complete_task(target_user, task_id)
        if success:
            print(f"Task {task_id} marked as completed for user: {target_user}")
        else:
            print(f"Error: Task with ID {task_id} not found or not owned by user {target_user}")

    def delete_task(self, task_id: int, user: str = None):
        """Delete a task for a specific user"""
        # Use provided user or current user
        target_user = user if user else self.current_user

        if not target_user:
            print("Error: No user specified and no current user logged in")
            return

        if not self.storage.user_exists(target_user):
            print(f"Error: User '{target_user}' does not exist")
            return

        success = self.storage.delete_task(target_user, task_id)
        if success:
            print(f"Task {task_id} deleted successfully for user: {target_user}")
        else:
            print(f"Error: Task with ID {task_id} not found or not owned by user {target_user}")


def main():
    """Main function to run the multi-user console todo app"""
    app = TodoAppMultiUser()

    # Set up command-line argument parser
    parser = argparse.ArgumentParser(description='Multi-User In-Memory Console Todo App')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Login command
    login_parser = subparsers.add_parser('login', help='Login to establish user context')
    login_parser.add_argument('--user', required=True, help='Username for login')

    # Add command
    add_parser = subparsers.add_parser('add', help='Add a new task')
    add_parser.add_argument('--title', required=True, help='Task title')
    add_parser.add_argument('--description', default='', help='Task description')
    add_parser.add_argument('--user', help='Target user (defaults to current user)')

    # List command
    list_parser = subparsers.add_parser('list', help='List all tasks for a user')
    list_parser.add_argument('--user', help='Target user (defaults to current user)')

    # Update command
    update_parser = subparsers.add_parser('update', help='Update a task')
    update_parser.add_argument('--id', type=int, required=True, help='Task ID')
    update_parser.add_argument('--user', help='Target user (defaults to current user)')
    update_parser.add_argument('--title', help='New task title')
    update_parser.add_argument('--description', help='New task description')

    # Complete command
    complete_parser = subparsers.add_parser('complete', help='Mark task as completed')
    complete_parser.add_argument('--id', type=int, required=True, help='Task ID')
    complete_parser.add_argument('--user', help='Target user (defaults to current user)')

    # Delete command
    delete_parser = subparsers.add_parser('delete', help='Delete a task')
    delete_parser.add_argument('--id', type=int, required=True, help='Task ID')
    delete_parser.add_argument('--user', help='Target user (defaults to current user)')

    # Help command
    help_parser = subparsers.add_parser('help', help='Show help information')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        if args.command == 'login':
            app.login(args.user)
        elif args.command == 'add':
            app.add_task(args.title, args.description, args.user)
        elif args.command == 'list':
            app.list_tasks(args.user)
        elif args.command == 'update':
            app.update_task(args.id, args.user, args.title, args.description)
        elif args.command == 'complete':
            app.complete_task(args.id, args.user)
        elif args.command == 'delete':
            app.delete_task(args.id, args.user)
        elif args.command == 'help':
            parser.print_help()
        else:
            parser.print_help()
    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()