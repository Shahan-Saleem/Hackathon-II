#!/usr/bin/env python3
"""
Enhanced Console UI for the Project-Based Task Management Application
Provides a colorful, user-friendly interface for all application functionality
"""

import os
import sys
from typing import Optional
try:
    from colorama import init, Fore, Back, Style
    init()  # Initialize colorama for Windows
except ImportError:
    # Define basic fallback colors if colorama is not installed
    class ColorFallback:
        def __getattr__(self, name):
            return ''

    Fore = ColorFallback()
    Back = ColorFallback()
    Style = ColorFallback()

from app import TaskManager, User


class ColoredConsoleUI:
    """Colorful console-based user interface for the task manager application"""

    # Colorama color codes
    COLORS = {
        'HEADER': Fore.MAGENTA,
        'BLUE': Fore.BLUE,
        'CYAN': Fore.CYAN,
        'GREEN': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'FAIL': Fore.RED,
        'ENDC': Style.RESET_ALL,
        'BOLD': Style.BRIGHT,
        'UNDERLINE': '\033[4m'  # ANSI underline
    }

    def __init__(self, task_manager: TaskManager):
        self.tm = task_manager
        self.current_user: Optional[User] = None

    def clear_screen(self):
        """Clear the console screen"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_colored(self, text: str, color: str = ''):
        """Print colored text"""
        color_code = self.COLORS.get(color.upper(), '')
        end_code = self.COLORS['ENDC'] if color_code else ''
        print(f"{color_code}{text}{end_code}")

    def print_header(self, title: str):
        """Print a formatted header with colors"""
        self.print_colored("=" * 60, 'HEADER')
        self.print_colored(f"{title:^60}", 'HEADER')
        self.print_colored("=" * 60, 'HEADER')

    def print_menu(self, title: str, options: list):
        """Print a formatted menu with options in color"""
        self.print_colored(f"\n{title}", 'CYAN')
        self.print_colored("-" * len(title), 'CYAN')
        for i, option in enumerate(options, 1):
            self.print_colored(f"{i}. {option}", 'BLUE')
        print()

    def get_input(self, prompt: str) -> str:
        """Get user input with a prompt in color"""
        return input(f"{self.COLORS['GREEN']}{prompt}:{self.COLORS['ENDC']} ").strip()

    def authenticate_user(self):
        """Handle user authentication flow with styling"""
        while True:
            self.clear_screen()
            self.print_header("TASK MANAGER - AUTHENTICATION")

            options = [
                "Sign Up",
                "Sign In",
                "Exit"
            ]

            for i, option in enumerate(options, 1):
                if i == 3:  # Exit option
                    self.print_colored(f"{i}. {option}", 'WARNING')
                else:
                    self.print_colored(f"{i}. {option}", 'GREEN')

            choice = input(f"\n{self.COLORS['CYAN']}Enter your choice (1-3): {self.COLORS['ENDC']}").strip()

            if choice == "1":
                # Sign up
                username = self.get_input("Enter username")
                password = self.get_input("Enter password")

                try:
                    user = self.tm.register_user(username, password)
                    if user:
                        self.print_colored(f"\n✓ Successfully registered user: {username}", 'GREEN')
                        self.current_user = user
                        input(f"\n{self.COLORS['CYAN']}Press Enter to continue...{self.COLORS['ENDC']}")
                        return True
                    else:
                        self.print_colored(f"\n✗ Username '{username}' already exists!", 'FAIL')
                        input(f"\n{self.COLORS['CYAN']}Press Enter to continue...{self.COLORS['ENDC']}")
                except Exception as e:
                    self.print_colored(f"\n✗ Registration failed: {str(e)}", 'FAIL')
                    input(f"\n{self.COLORS['CYAN']}Press Enter to continue...{self.COLORS['ENDC']}")

            elif choice == "2":
                # Sign in
                username = self.get_input("Enter username")
                password = self.get_input("Enter password")

                try:
                    user = self.tm.authenticate_user(username, password)
                    if user:
                        self.print_colored(f"\n✓ Welcome back, {username}!", 'GREEN')
                        self.current_user = user
                        input(f"\n{self.COLORS['CYAN']}Press Enter to continue...{self.COLORS['ENDC']}")
                        return True
                    else:
                        self.print_colored(f"\n✗ Invalid credentials for user '{username}'", 'FAIL')
                        input(f"\n{self.COLORS['CYAN']}Press Enter to continue...{self.COLORS['ENDC']}")
                except Exception as e:
                    self.print_colored(f"\n✗ Sign in failed: {str(e)}", 'FAIL')
                    input(f"\n{self.COLORS['CYAN']}Press Enter to continue...{self.COLORS['ENDC']}")

            elif choice == "3":
                self.print_colored("\nGoodbye!", 'WARNING')
                return False

            else:
                self.print_colored("\n✗ Invalid choice. Please enter 1, 2, or 3.", 'FAIL')
                input(f"\n{self.COLORS['CYAN']}Press Enter to continue...{self.COLORS['ENDC']}")

    def show_main_menu(self):
        """Display the main application menu with colors"""
        while True:
            self.clear_screen()
            self.print_header("TASK MANAGER - MAIN MENU")
            self.print_colored(f"Signed in as: {self.current_user.username if self.current_user else 'Anonymous'}", 'CYAN')

            options = [
                "Manage Projects",
                "Manage Tasks",
                "View Reports",
                "Sign Out"
            ]
            self.print_menu("Main Menu", options)

            choice = input(f"{self.COLORS['CYAN']}Enter your choice (1-4): {self.COLORS['ENDC']}").strip()

            if choice == "1":
                self.manage_projects()
            elif choice == "2":
                self.manage_tasks()
            elif choice == "3":
                self.view_reports()
            elif choice == "4":
                self.current_user = None
                self.print_colored("\n✓ Signed out successfully!", 'GREEN')
                input(f"\n{self.COLORS['CYAN']}Press Enter to continue...{self.COLORS['ENDC']}")
                return
            else:
                self.print_colored("\n✗ Invalid choice. Please enter 1, 2, 3, or 4.", 'FAIL')
                input(f"\n{self.COLORS['CYAN']}Press Enter to continue...{self.COLORS['ENDC']}")

    def manage_projects(self):
        """Project management submenu with colors"""
        while True:
            self.clear_screen()
            self.print_header("PROJECT MANAGEMENT")

            options = [
                "List Projects",
                "Create Project",
                "Select Project",
                "Back to Main Menu"
            ]
            self.print_menu("Project Management", options)

            choice = input(f"Enter your choice (1-4): ").strip()

            if choice == "1":
                self.list_projects()
            elif choice == "2":
                self.create_project()
            elif choice == "3":
                self.select_project()
            elif choice == "4":
                return
            else:
                self.print_colored("\n✗ Invalid choice. Please enter 1, 2, 3, or 4.", 'FAIL')
                input(f"\n{self.COLORS['CYAN']}Press Enter to continue...{self.COLORS['ENDC']}")

    def list_projects(self):
        """List all projects for the current user with colors"""
        self.clear_screen()
        self.print_header("YOUR PROJECTS")

        try:
            projects = self.tm.list_projects(self.current_user.id)
            if not projects:
                self.print_colored("\nNo projects found.", 'WARNING')
            else:
                self.print_colored(f"\nProjects for {self.current_user.username}:", 'CYAN')
                self.print_colored("-" * 40, 'CYAN')
                for i, project in enumerate(projects, 1):
                    self.print_colored(f"{i}. [{project.id[:8]}...] {project.name}", 'BLUE')

            input(f"\n{self.COLORS['CYAN']}Press Enter to continue...{self.COLORS['ENDC']}")
        except Exception as e:
            self.print_colored(f"\n✗ Error listing projects: {str(e)}", 'FAIL')
            input(f"\n{self.COLORS['CYAN']}Press Enter to continue...{self.COLORS['ENDC']}")

    def create_project(self):
        """Create a new project with colors"""
        self.clear_screen()
        self.print_header("CREATE NEW PROJECT")

        try:
            name = self.get_input("Enter project name")
            if name:
                project = self.tm.create_project(name, self.current_user.id)
                self.print_colored(f"\n✓ Project '{project.name}' created successfully!", 'GREEN')
            else:
                self.print_colored("\n✗ Project name cannot be empty!", 'FAIL')
        except Exception as e:
            self.print_colored(f"\n✗ Error creating project: {str(e)}", 'FAIL')

        input(f"\n{self.COLORS['CYAN']}Press Enter to continue...{self.COLORS['ENDC']}")

    def select_project(self):
        """Select an active project with colors"""
        self.clear_screen()
        self.print_header("SELECT ACTIVE PROJECT")

        try:
            projects = self.tm.list_projects(self.current_user.id)
            if not projects:
                self.print_colored("\nNo projects available. Create a project first.", 'WARNING')
            else:
                self.print_colored("\nAvailable projects:", 'CYAN')
                for i, project in enumerate(projects, 1):
                    self.print_colored(f"{i}. [{project.id[:8]}...] {project.name}", 'BLUE')

                self.print_colored(f"{len(projects) + 1}. Cancel", 'WARNING')

                choice = input(f"\n{self.COLORS['CYAN']}Enter your choice (1-{len(projects) + 1}): {self.COLORS['ENDC']}").strip()

                if choice.isdigit():
                    idx = int(choice) - 1
                    if 0 <= idx < len(projects):
                        project = projects[idx]
                        self.tm.select_project(project.id, self.current_user.id)
                        self.print_colored(f"\n✓ Active project set to '{project.name}'", 'GREEN')
                    elif idx == len(projects):
                        self.print_colored("\nSelection cancelled.", 'WARNING')
                    else:
                        self.print_colored("\n✗ Invalid choice.", 'FAIL')
                else:
                    self.print_colored("\n✗ Invalid input. Please enter a number.", 'FAIL')
        except Exception as e:
            self.print_colored(f"\n✗ Error selecting project: {str(e)}", 'FAIL')

        input(f"\n{self.COLORS['CYAN']}Press Enter to continue...{self.COLORS['ENDC']}")

    def manage_tasks(self):
        """Task management submenu with colors"""
        while True:
            self.clear_screen()
            self.print_header("TASK MANAGEMENT")

            options = [
                "List Tasks",
                "Add Task",
                "Update Task",
                "Complete Task",
                "Delete Task",
                "Back to Main Menu"
            ]
            self.print_menu("Task Management", options)

            choice = input(f"Enter your choice (1-6): ").strip()

            if choice == "1":
                self.list_tasks()
            elif choice == "2":
                self.add_task()
            elif choice == "3":
                self.update_task()
            elif choice == "4":
                self.complete_task()
            elif choice == "5":
                self.delete_task()
            elif choice == "6":
                return
            else:
                self.print_colored("\n✗ Invalid choice. Please enter 1, 2, 3, 4, 5, or 6.", 'FAIL')
                input(f"\n{self.COLORS['CYAN']}Press Enter to continue...{self.COLORS['ENDC']}")

    def list_tasks(self):
        """List tasks for the current project or all projects with colors"""
        self.clear_screen()
        self.print_header("YOUR TASKS")

        try:
            # Check if there's an active project
            context = self.tm.get_user_context(self.current_user.id)
            if context.active_project_id:
                self.print_colored(f"Showing tasks for active project: {context.active_project_id[:8]}...", 'CYAN')
                tasks = self.tm.list_tasks(self.current_user.id)
            else:
                self.print_colored("No active project selected. Showing all tasks.", 'WARNING')
                tasks = self.tm.list_tasks(self.current_user.id)

            if not tasks:
                self.print_colored("\nNo tasks found.", 'WARNING')
            else:
                for task in tasks:
                    status = "✓" if task.completed else "○"
                    color = 'GREEN' if task.completed else 'BLUE'
                    self.print_colored(f"{status} [{task.id}] {task.title}", color)
                    if task.description:
                        self.print_colored(f"    Description: {task.description}", 'CYAN')

            input(f"\n{self.COLORS['CYAN']}Press Enter to continue...{self.COLORS['ENDC']}")
        except Exception as e:
            self.print_colored(f"\n✗ Error listing tasks: {str(e)}", 'FAIL')
            input(f"\n{self.COLORS['CYAN']}Press Enter to continue...{self.COLORS['ENDC']}")

    def add_task(self):
        """Add a new task with colors"""
        self.clear_screen()
        self.print_header("ADD NEW TASK")

        try:
            title = self.get_input("Enter task title")
            if not title:
                self.print_colored("\n✗ Task title cannot be empty!", 'FAIL')
                input(f"\n{self.COLORS['CYAN']}Press Enter to continue...{self.COLORS['ENDC']}")
                return

            description = self.get_input("Enter task description (optional)")

            # Check if there's an active project
            context = self.tm.get_user_context(self.current_user.id)
            if not context.active_project_id:
                self.print_colored("\n⚠ No active project selected. Please select a project first.", 'WARNING')
                input(f"\n{self.COLORS['CYAN']}Press Enter to continue...{self.COLORS['ENDC']}")
                return

            task = self.tm.add_task(
                title=title,
                description=description,
                user_id=self.current_user.id
            )
            self.print_colored(f"\n✓ Task '{task.title}' added successfully!", 'GREEN')
        except Exception as e:
            self.print_colored(f"\n✗ Error adding task: {str(e)}", 'FAIL')

        input(f"\n{self.COLORS['CYAN']}Press Enter to continue...{self.COLORS['ENDC']}")

    def update_task(self):
        """Update an existing task with colors"""
        self.clear_screen()
        self.print_header("UPDATE TASK")

        try:
            task_id_str = self.get_input("Enter task ID to update")
            if not task_id_str.isdigit():
                self.print_colored("\n✗ Invalid task ID. Please enter a number.", 'FAIL')
                input(f"\n{self.COLORS['CYAN']}Press Enter to continue...{self.COLORS['ENDC']}")
                return

            task_id = int(task_id_str)

            title = self.get_input("Enter new title (leave blank to keep current)")
            description = self.get_input("Enter new description (leave blank to keep current)")

            # Prepare update parameters
            title = title if title else None
            description = description if description else None

            if title is None and description is None:
                self.print_colored("\n✗ No changes provided.", 'WARNING')
                input(f"\n{self.COLORS['CYAN']}Press Enter to continue...{self.COLORS['ENDC']}")
                return

            task = self.tm.update_task(
                task_id=task_id,
                user_id=self.current_user.id,
                title=title,
                description=description
            )
            self.print_colored(f"\n✓ Task {task.id} updated successfully!", 'GREEN')
        except Exception as e:
            self.print_colored(f"\n✗ Error updating task: {str(e)}", 'FAIL')

        input(f"\n{self.COLORS['CYAN']}Press Enter to continue...{self.COLORS['ENDC']}")

    def complete_task(self):
        """Mark a task as completed with colors"""
        self.clear_screen()
        self.print_header("COMPLETE TASK")

        try:
            task_id_str = self.get_input("Enter task ID to complete")
            if not task_id_str.isdigit():
                self.print_colored("\n✗ Invalid task ID. Please enter a number.", 'FAIL')
                input(f"\n{self.COLORS['CYAN']}Press Enter to continue...{self.COLORS['ENDC']}")
                return

            task_id = int(task_id_str)

            task = self.tm.complete_task(
                task_id=task_id,
                user_id=self.current_user.id
            )
            self.print_colored(f"\n✓ Task {task.id} marked as completed!", 'GREEN')
        except Exception as e:
            self.print_colored(f"\n✗ Error completing task: {str(e)}", 'FAIL')

        input(f"\n{self.COLORS['CYAN']}Press Enter to continue...{self.COLORS['ENDC']}")

    def delete_task(self):
        """Delete a task with colors"""
        self.clear_screen()
        self.print_header("DELETE TASK")

        try:
            task_id_str = self.get_input("Enter task ID to delete")
            if not task_id_str.isdigit():
                self.print_colored("\n✗ Invalid task ID. Please enter a number.", 'FAIL')
                input(f"\n{self.COLORS['CYAN']}Press Enter to continue...{self.COLORS['ENDC']}")
                return

            task_id = int(task_id_str)

            confirm = input(f"{self.COLORS['WARNING']}Are you sure you want to delete task {task_id}? (y/N): {self.COLORS['ENDC']}").strip().lower()
            if confirm == 'y':
                success = self.tm.delete_task(
                    task_id=task_id,
                    user_id=self.current_user.id
                )
                if success:
                    self.print_colored(f"\n✓ Task {task_id} deleted successfully!", 'GREEN')
                else:
                    self.print_colored(f"\n✗ Failed to delete task {task_id}.", 'FAIL')
            else:
                self.print_colored("\nDeletion cancelled.", 'WARNING')
        except Exception as e:
            self.print_colored(f"\n✗ Error deleting task: {str(e)}", 'FAIL')

        input(f"\n{self.COLORS['CYAN']}Press Enter to continue...{self.COLORS['ENDC']}")

    def view_reports(self):
        """View various reports and analytics with colors"""
        self.clear_screen()
        self.print_header("REPORTS & ANALYTICS")

        self.print_colored("Coming soon: Detailed reports and analytics", 'CYAN')
        input(f"\n{self.COLORS['CYAN']}Press Enter to continue...{self.COLORS['ENDC']}")

    def run(self):
        """Run the main application loop"""
        while True:
            if not self.current_user:
                # Need to authenticate first
                if not self.authenticate_user():
                    break  # User chose to exit
            else:
                # User is authenticated, show main menu
                self.show_main_menu()


def main():
    """Main entry point for the console UI"""
    task_manager = TaskManager()
    ui = ColoredConsoleUI(task_manager)

    print("Starting Project-Based Task Manager...")
    print("Initializing application...")

    try:
        ui.run()
    except KeyboardInterrupt:
        print(f"\n\n{ColoredConsoleUI.COLORS['WARNING']}Application interrupted by user.{ColoredConsoleUI.COLORS['ENDC']}")
    except Exception as e:
        print(f"\n{ColoredConsoleUI.COLORS['FAIL']}Application error: {str(e)}{ColoredConsoleUI.COLORS['ENDC']}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()