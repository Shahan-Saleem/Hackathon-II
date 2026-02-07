"""
Project-based Python console todo app for Phase 4
Extends Phase 3 with project organization that groups related tasks
"""
import argparse
import sys
import json
import os
from datetime import datetime
from typing import List, Optional


class Project:
    """
    Project model class with basic properties
    """
    def __init__(self, project_id: str, name: str, user: str):
        self.id = project_id
        self.name = name
        self.user = user  # Username of the project owner
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()

    def to_dict(self):
        """Convert project to dictionary representation"""
        return {
            'id': self.id,
            'name': self.name,
            'user': self.user,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    @classmethod
    def from_dict(cls, data):
        """Create Project instance from dictionary representation"""
        project = cls(
            project_id=data['id'],
            name=data['name'],
            user=data['user']
        )
        project.created_at = data.get('created_at', datetime.now().isoformat())
        project.updated_at = data.get('updated_at', datetime.now().isoformat())
        return project


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
        user.created_at = data.get('created_at', datetime.now().isoformat())
        return user

    def __str__(self):
        return self.username


class Task:
    """
    Task model class with basic properties and project association
    """
    def __init__(self, task_id: int, title: str, description: str = "", completed: bool = False,
                 user: str = None, project_id: str = None):
        self.id = task_id
        self.title = title
        self.description = description
        self.completed = completed
        self.user = user  # Username of the task owner
        self.project_id = project_id  # Associated project ID
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
            'project_id': self.project_id,
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
            user=data['user'],
            project_id=data.get('project_id')
        )
        task.created_at = data.get('created_at', datetime.now().isoformat())
        task.updated_at = data.get('updated_at', datetime.now().isoformat())
        return task

    def to_string(self) -> str:
        """Convert task to string representation for display"""
        status = "X" if self.completed else "O"
        project_info = f" (Project: {self.project_id})" if self.project_id else ""
        return f"{status} [{self.id}] {self.title}{project_info}\n    Description: {self.description}\n    User: {self.user}"

    def mark_completed(self):
        """Mark the task as completed"""
        self.completed = True
        self.updated_at = datetime.now().isoformat()


class ProjectStorage:
    """
    Project-aware persistent storage mechanism to hold tasks by user and project
    """
    def __init__(self, storage_file: str = "todo_data.json"):
        self.storage_file = storage_file
        self.users = {}  # Dictionary to store User objects by username
        self.projects = {}  # Dictionary to store Project objects by project ID
        self.tasks_by_user = {}  # Dictionary to store tasks by user
        self.tasks_by_project = {}  # Dictionary to store tasks by project
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

                # Load projects
                for project_id, project_data in data.get('projects', {}).items():
                    project = Project.from_dict(project_data)
                    self.projects[project_id] = project

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

                # Load tasks by project
                for project_id, tasks_data in data.get('tasks_by_project', {}).items():
                    project_tasks = []
                    for task_data in tasks_data:
                        task = Task.from_dict(task_data)
                        project_tasks.append(task)
                    self.tasks_by_project[project_id] = project_tasks

                print(f"Data loaded from {self.storage_file}")

            except (json.JSONDecodeError, KeyError) as e:
                print(f"Warning: Could not load data from {self.storage_file}: {str(e)}. Starting with empty storage.")
                self._initialize_empty_storage()
        else:
            print(f"Storage file {self.storage_file} not found. Starting with empty storage.")
            self._initialize_empty_storage()

    def _initialize_empty_storage(self):
        """Initialize empty storage dictionaries"""
        self.users = {}
        self.projects = {}
        self.tasks_by_user = {}
        self.tasks_by_project = {}

    def save_data(self):
        """Save data to storage file"""
        try:
            data = {
                'users': {username: user.to_dict() for username, user in self.users.items()},
                'projects': {pid: project.to_dict() for pid, project in self.projects.items()},
                'tasks_by_user': {username: [task.to_dict() for task in tasks]
                                  for username, tasks in self.tasks_by_user.items()},
                'tasks_by_project': {pid: [task.to_dict() for task in tasks]
                                     for pid, tasks in self.tasks_by_project.items()}
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

    def create_project(self, project_id: str, name: str, user: str) -> bool:
        """Create a new project if not already exists"""
        if project_id in self.projects:
            return False  # Project already exists

        project = Project(project_id, name, user)
        self.projects[project_id] = project

        # Initialize task list for this project
        if project_id not in self.tasks_by_project:
            self.tasks_by_project[project_id] = []

        # Add project to user's project list (if needed)
        return True

    def project_exists(self, project_id: str) -> bool:
        """Check if project exists in storage"""
        return project_id in self.projects

    def get_project(self, project_id: str) -> Optional[Project]:
        """Get a project by ID"""
        return self.projects.get(project_id)

    def get_projects_for_user(self, username: str) -> List[Project]:
        """Get all projects for a specific user"""
        user_projects = []
        for project in self.projects.values():
            if project.user == username:
                user_projects.append(project)
        return user_projects

    def add_task(self, task: Task):
        """Add a task to user and project storage"""
        # Add to user's task list
        if task.user not in self.tasks_by_user:
            self.tasks_by_user[task.user] = []

        self.tasks_by_user[task.user].append(task)

        # Add to project's task list if project is specified
        if task.project_id:
            if task.project_id not in self.tasks_by_project:
                self.tasks_by_project[task.project_id] = []
            self.tasks_by_project[task.project_id].append(task)

        self.next_task_id += 1
        self.save_data()  # Auto-save after adding task

    def get_all_tasks(self, username: str) -> List[Task]:
        """Get all tasks for a specific user"""
        if username not in self.tasks_by_user:
            return []
        return self.tasks_by_user[username]

    def get_tasks_for_project(self, project_id: str) -> List[Task]:
        """Get all tasks for a specific project"""
        if project_id not in self.tasks_by_project:
            return []
        return self.tasks_by_project[project_id]

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
                # Also remove from project if it was associated with one
                if task.project_id and task.project_id in self.tasks_by_project:
                    project_tasks = self.tasks_by_project[task.project_id]
                    for j, proj_task in enumerate(project_tasks):
                        if proj_task.id == task_id:
                            self.tasks_by_project[task.project_id].pop(j)
                            break

                # Remove from user's task list
                self.tasks_by_user[username].pop(i)
                self.save_data()  # Auto-save after deleting task
                return True
        return False  # Task not found or not owned by user

    def delete_project(self, project_id: str, username: str) -> bool:
        """Delete a project if owned by the user"""
        if project_id not in self.projects:
            return False

        project = self.projects[project_id]
        if project.user != username:
            return False  # User doesn't own this project

        # Remove all tasks associated with this project
        if project_id in self.tasks_by_project:
            project_tasks = self.tasks_by_project[project_id]
            # Remove these tasks from user's task lists too
            for task in project_tasks:
                if task.user in self.tasks_by_user:
                    user_tasks = self.tasks_by_user[task.user]
                    self.tasks_by_user[task.user] = [t for t in user_tasks if t.id != task.id]

            del self.tasks_by_project[project_id]

        # Remove the project
        del self.projects[project_id]
        self.save_data()
        return True


class TodoAppProjects:
    """
    Main application class for the project-based console todo app
    """
    def __init__(self, storage_file: str = "todo_data.json"):
        self.storage = ProjectStorage(storage_file)
        self.current_user = None  # Track current user session
        self.active_project_id = None  # Track active project context

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

    def create_project(self, name: str, user: str = None):
        """Create a new project for a specific user"""
        # Use provided user or current user
        target_user = user if user else self.current_user

        if not target_user:
            print("Error: No user specified and no current user logged in")
            return

        if not self.storage.user_exists(target_user):
            print(f"Error: User '{target_user}' does not exist")
            return

        if not name.strip():
            print("Error: Project name cannot be empty")
            return

        # Generate a unique project ID
        import uuid
        project_id = str(uuid.uuid4())

        success = self.storage.create_project(project_id, name, target_user)
        if success:
            print(f"Project '{name}' created with ID {project_id}")
        else:
            print(f"Error: Project creation failed")

    def select_project(self, project_id: str, user: str = None):
        """Select a project to set as active context"""
        # Use provided user or current user
        target_user = user if user else self.current_user

        if not target_user:
            print("Error: No user specified and no current user logged in")
            return

        if not self.storage.user_exists(target_user):
            print(f"Error: User '{target_user}' does not exist")
            return

        project = self.storage.get_project(project_id)
        if not project:
            print(f"Error: Project with ID '{project_id}' does not exist")
            return

        if project.user != target_user:
            print(f"Error: Project '{project_id}' does not belong to user '{target_user}'")
            return

        self.active_project_id = project_id
        print(f"Active project set to '{project.name}' (ID: {project_id})")

    def list_projects(self, user: str = None):
        """List all projects for a specific user"""
        # Use provided user or current user
        target_user = user if user else self.current_user

        if not target_user:
            print("Error: No user specified and no current user logged in")
            return

        if not self.storage.user_exists(target_user):
            print(f"Error: User '{target_user}' does not exist")
            return

        projects = self.storage.get_projects_for_user(target_user)

        if not projects:
            print(f"No projects found for user: {target_user}")
            return

        print(f"Projects for user: {target_user}:")
        for project in projects:
            print(f"- [{project.id}] {project.name}")

    def delete_project(self, project_id: str, user: str = None):
        """Delete a project for a specific user"""
        # Use provided user or current user
        target_user = user if user else self.current_user

        if not target_user:
            print("Error: No user specified and no current user logged in")
            return

        if not self.storage.user_exists(target_user):
            print(f"Error: User '{target_user}' does not exist")
            return

        success = self.storage.delete_project(project_id, target_user)
        if success:
            print(f"Project with ID '{project_id}' deleted successfully")
            # Clear active project if it was the one deleted
            if self.active_project_id == project_id:
                self.active_project_id = None
        else:
            print(f"Error: Project with ID '{project_id}' not found or not owned by user '{target_user}'")

    def add_task(self, title: str, description: str = "", user: str = None, project_id: str = None):
        """Add a new task for a specific user, optionally in a specific project"""
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

        # Use active project if no project specified
        final_project_id = project_id if project_id else self.active_project_id

        if final_project_id:
            # Verify project exists and belongs to user
            project = self.storage.get_project(final_project_id)
            if not project:
                print(f"Error: Project with ID '{final_project_id}' does not exist")
                return
            if project.user != target_user:
                print(f"Error: Project '{final_project_id}' does not belong to user '{target_user}'")
                return

        # Create new task with unique ID
        new_task = Task(self.storage.next_task_id, title, description, user=target_user, project_id=final_project_id)
        self.storage.add_task(new_task)

        project_info = f" in project '{final_project_id}'" if final_project_id else " with no project"
        print(f"Task added: {new_task.title} (ID: {new_task.id}){project_info}")

    def list_tasks(self, user: str = None, project_id: str = None):
        """List all tasks for a specific user, optionally filtered by project"""
        # Use provided user or current user
        target_user = user if user else self.current_user

        if not target_user:
            print("Error: No user specified and no current user logged in")
            return

        if not self.storage.user_exists(target_user):
            print(f"Error: User '{target_user}' does not exist")
            return

        # Use specified project or active project
        final_project_id = project_id if project_id else self.active_project_id

        if final_project_id:
            # List tasks for specific project
            tasks = self.storage.get_tasks_for_project(final_project_id)
            project = self.storage.get_project(final_project_id)
            if project:
                print(f"Tasks in project '{project.name}' (ID: {final_project_id}):")
            else:
                print(f"Tasks in project (ID: {final_project_id}):")
        else:
            # List all tasks for user
            tasks = self.storage.get_all_tasks(target_user)
            print(f"All tasks for user: {target_user}")

        if not tasks:
            print("No tasks found.")
            return

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
    """Main function to run the project-based console todo app"""
    parser = argparse.ArgumentParser(description='Project-Based File-Persistent Console Todo App')

    # Add storage file option
    parser.add_argument('--storage-file', default='todo_data.json', help='Path to storage file')

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Login command
    login_parser = subparsers.add_parser('login', help='Login to establish user context')
    login_parser.add_argument('--user', required=True, help='Username for login')

    # Project commands
    project_parser = subparsers.add_parser('project', help='Project management commands')
    project_subparsers = project_parser.add_subparsers(dest='project_command', help='Project commands')

    create_project_parser = project_subparsers.add_parser('create', help='Create a new project')
    create_project_parser.add_argument('--name', required=True, help='Project name')
    create_project_parser.add_argument('--user', help='Target user (defaults to current user)')

    select_project_parser = project_subparsers.add_parser('select', help='Select an active project')
    select_project_parser.add_argument('--id', required=True, help='Project ID')
    select_project_parser.add_argument('--user', help='Target user (defaults to current user)')

    list_projects_parser = project_subparsers.add_parser('list', help='List user projects')
    list_projects_parser.add_argument('--user', help='Target user (defaults to current user)')

    delete_project_parser = project_subparsers.add_parser('delete', help='Delete a project')
    delete_project_parser.add_argument('--id', required=True, help='Project ID')
    delete_project_parser.add_argument('--user', help='Target user (defaults to current user)')

    # Add command
    add_parser = subparsers.add_parser('add', help='Add a new task')
    add_parser.add_argument('--title', required=True, help='Task title')
    add_parser.add_argument('--description', default='', help='Task description')
    add_parser.add_argument('--user', help='Target user (defaults to current user)')
    add_parser.add_argument('--project', help='Project ID (defaults to active project)')

    # List command
    list_parser = subparsers.add_parser('list', help='List all tasks for a user')
    list_parser.add_argument('--user', help='Target user (defaults to current user)')
    list_parser.add_argument('--project', help='Project ID (defaults to active project)')

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

    # Create app instance with specified storage file
    app = TodoAppProjects(storage_file=args.storage_file)

    try:
        if args.command == 'login':
            app.login(args.user)
        elif args.command == 'project':
            if args.project_command == 'create':
                app.create_project(args.name, args.user)
            elif args.project_command == 'select':
                app.select_project(args.id, args.user)
            elif args.project_command == 'list':
                app.list_projects(args.user)
            elif args.project_command == 'delete':
                app.delete_project(args.id, args.user)
            else:
                project_parser.print_help()
        elif args.command == 'add':
            app.add_task(args.title, args.description, args.user, args.project)
        elif args.command == 'list':
            app.list_tasks(args.user, args.project)
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