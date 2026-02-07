"""
Persistent file-based Python console todo app for Phase 3
Extends Phase 2 with file-based storage that maintains data between application runs
"""
import argparse
import sys
import json
import os
from datetime import datetime
from typing import List, Optional


class User:
    """
    User model class with basic properties
    """
    def __init__(self, username: str):
        self.username = username
        self.created_at = datetime.now().isoformat()

    def to_dict(self):
        """Convert user to dictionary representation"""
        return {
            'username': self.username,
            'created_at': self.created_at
        }

    @classmethod
    def from_dict(cls, data):
        """Create User instance from dictionary representation"""
        user = cls(data['username'])
        user.created_at = data['created_at']
        return user

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
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()

    def to_dict(self) -> dict:
        """Convert task to dictionary representation"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'completed': self.completed,
            'user': self.user,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    @classmethod
    def from_dict(cls, data):
        """Create Task instance from dictionary representation"""
        task = cls(
            task_id=data['id'],
            title=data['title'],
            description=data.get('description', ''),
            completed=data.get('completed', False),
            user=data['user']
        )
        task.created_at = data.get('created_at', datetime.now().isoformat())
        task.updated_at = data.get('updated_at', datetime.now().isoformat())
        return task

    def to_string(self) -> str:
        """Convert task to string representation for display"""
        status = "X" if self.completed else "O"
        return f"{status} [{self.id}] {self.title}\n    Description: {self.description}\n    User: {self.user}"

    def mark_completed(self):
        """Mark the task as completed"""
        self.completed = True
        self.updated_at = datetime.now().isoformat()


class PersistentStorage:
    """
    File-based persistent storage mechanism to hold tasks by user
    """
    def __init__(self, storage_file: str = "todo_data.json"):
        self.storage_file = storage_file
        self.users = {}  # Dictionary to store User objects by username
        self.tasks_by_user = {}  # Dictionary to store tasks by user
        self.next_task_id = 1  # Counter for generating unique task IDs
        self.load_data()

    def load_data(self):
        """Load data from storage file"""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r') as f:
                    data = json.load(f)

                # Load users
                for username, user_data in data.get('users', {}).items():
                    user = User.from_dict(user_data)
                    self.users[username] = user

                # Load tasks
                for username, tasks_data in data.get('tasks_by_user', {}).items():
                    user_tasks = []
                    for task_data in tasks_data:
                        task = Task.from_dict(task_data)
                        user_tasks.append(task)
                        # Update next_task_id if necessary
                        if task.id >= self.next_task_id:
                            self.next_task_id = task.id + 1
                    self.tasks_by_user[username] = user_tasks

                print(f"Data loaded from {self.storage_file}")

            except (json.JSONDecodeError, KeyError) as e:
                print(f"Warning: Could not load data from {self.storage_file}: {str(e)}. Starting with empty storage.")
                self.users = {}
                self.tasks_by_user = {}
        else:
            print(f"Storage file {self.storage_file} not found. Starting with empty storage.")
            self.users = {}
            self.tasks_by_user = {}

    def save_data(self):
        """Save data to storage file"""
        try:
            data = {
                'users': {username: user.to_dict() for username, user in self.users.items()},
                'tasks_by_user': {username: [task.to_dict() for task in tasks]
                                  for username, tasks in self.tasks_by_user.items()}
            }

            with open(self.storage_file, 'w') as f:
                json.dump(data, f, indent=2)

            print(f"Data saved to {self.storage_file}")
        except Exception as e:
            print(f"Error saving data to {self.storage_file}: {str(e)}")

    def add_user(self, username: str) -> bool:
        """Add a user to storage if not already exists"""
        if username in self.users:
            return False  # User already exists

        user = User(username)
        self.users[username] = user
        if username not in self.tasks_by_user:
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
        self.save_data()  # Auto-save after adding task

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
        task.updated_at = datetime.now().isoformat()
        self.save_data()  # Auto-save after updating task
        return True

    def complete_task(self, username: str, task_id: int) -> bool:
        """Mark a task as completed if owned by the user"""
        task = self.get_task_by_id_for_user(username, task_id)
        if not task or task.user != username:
            return False  # Task not found or user doesn't own it
        task.mark_completed()
        self.save_data()  # Auto-save after completing task
        return True

    def delete_task(self, username: str, task_id: int) -> bool:
        """Delete a task from storage if owned by the user"""
        if username not in self.tasks_by_user:
            return False

        for i, task in enumerate(self.tasks_by_user[username]):
            if task.id == task_id and task.user == username:
                self.tasks_by_user[username].pop(i)
                self.save_data()  # Auto-save after deleting task
                return True
        return False  # Task not found or not owned by user

    def backup_data(self, backup_file: str = None):
        """Create a backup of current data"""
        if backup_file is None:
            backup_file = f"{self.storage_file}.backup"

        try:
            data = {
                'users': {username: user.to_dict() for username, user in self.users.items()},
                'tasks_by_user': {username: [task.to_dict() for task in tasks]
                                  for username, tasks in self.tasks_by_user.items()}
            }

            with open(backup_file, 'w') as f:
                json.dump(data, f, indent=2)

            print(f"Backup created at {backup_file}")
            return True
        except Exception as e:
            print(f"Error creating backup: {str(e)}")
            return False

    def restore_from_backup(self, backup_file: str = None):
        """Restore data from backup"""
        if backup_file is None:
            backup_file = f"{self.storage_file}.backup"

        if not os.path.exists(backup_file):
            print(f"Backup file {backup_file} not found.")
            return False

        try:
            with open(backup_file, 'r') as f:
                data = json.load(f)

            # Load users
            self.users = {}
            for username, user_data in data.get('users', {}).items():
                user = User.from_dict(user_data)
                self.users[username] = user

            # Load tasks
            self.tasks_by_user = {}
            for username, tasks_data in data.get('tasks_by_user', {}).items():
                user_tasks = []
                for task_data in tasks_data:
                    task = Task.from_dict(task_data)
                    user_tasks.append(task)
                self.tasks_by_user[username] = user_tasks

            print(f"Data restored from {backup_file}")
            return True
        except Exception as e:
            print(f"Error restoring from backup: {str(e)}")
            return False


class TodoAppPersistent:
    """
    Main application class for the persistent console todo app
    """
    def __init__(self, storage_file: str = "todo_data.json"):
        self.storage = PersistentStorage(storage_file)
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

    def save_data(self):
        """Manually save data to storage"""
        self.storage.save_data()

    def load_data(self):
        """Manually load data from storage (redundant since it auto-loads on init)"""
        self.storage.load_data()

    def backup_data(self, backup_file: str = None):
        """Create a backup of current data"""
        self.storage.backup_data(backup_file)

    def restore_data(self, backup_file: str = None):
        """Restore data from backup"""
        success = self.storage.restore_from_backup(backup_file)
        if success:
            print("Data restored successfully. Please restart the application for changes to take effect.")


def main():
    """Main function to run the persistent console todo app"""
    parser = argparse.ArgumentParser(description='Persistent File-Based Console Todo App')

    # Add storage file option
    parser.add_argument('--storage-file', default='todo_data.json', help='Path to storage file')

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

    # Save command
    save_parser = subparsers.add_parser('save', help='Manually save data to storage')

    # Load command
    load_parser = subparsers.add_parser('load', help='Manually load data from storage')

    # Backup command
    backup_parser = subparsers.add_parser('backup', help='Create a backup of current data')
    backup_parser.add_argument('--file', help='Backup file path (default: storage_file.backup)')

    # Restore command
    restore_parser = subparsers.add_parser('restore', help='Restore data from backup')
    restore_parser.add_argument('--file', help='Backup file path (default: storage_file.backup)')

    # Help command
    help_parser = subparsers.add_parser('help', help='Show help information')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Create app instance with specified storage file
    app = TodoAppPersistent(storage_file=args.storage_file)

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
        elif args.command == 'save':
            app.save_data()
        elif args.command == 'load':
            app.load_data()
        elif args.command == 'backup':
            app.backup_data(args.file)
        elif args.command == 'restore':
            app.restore_data(args.file)
        elif args.command == 'help':
            parser.print_help()
        else:
            parser.print_help()
    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()