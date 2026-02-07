"""
Enhanced application file with project functionality
Extends existing task management to include project context
"""

import argparse
import sys
from datetime import datetime
from typing import List, Optional
from models import Task, ProjectContext
from project_manager import ProjectManager
from storage import Storage
from datetime import datetime


class TaskManager:
    """
    Main application class that handles both legacy task operations and new project-based operations
    """

    def calculate_project_metrics(self, user_id: str, project_id: str) -> dict:
        """
        Calculate metrics for a specific project
        """
        tasks = self.storage.get_tasks_for_project(user_id, project_id)

        total_tasks = len(tasks)
        completed_tasks = len([task for task in tasks if task.completed])
        pending_tasks = total_tasks - completed_tasks

        # Calculate average time to completion if there are completed tasks
        avg_completion_time = None
        if completed_tasks > 0:
            completion_times = []
            for task in tasks:
                if task.completed and hasattr(task, 'completed_at'):
                    # Calculate time from creation to completion
                    completion_time = (task.completed_at - task.created_at).days
                    completion_times.append(completion_time)

            if completion_times:
                avg_completion_time = sum(completion_times) / len(completion_times)

        return {
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'pending_tasks': pending_tasks,
            'completion_rate': (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
            'avg_completion_time': avg_completion_time
        }

    def calculate_user_metrics(self, user_id: str) -> dict:
        """
        Calculate overall metrics for a user across all projects
        """
        all_tasks = self.storage.get_all_user_tasks(user_id)
        user_projects = self.project_manager.list_user_projects(user_id)

        total_tasks = len(all_tasks)
        completed_tasks = len([task for task in all_tasks if task.completed])
        pending_tasks = total_tasks - completed_tasks

        return {
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'pending_tasks': pending_tasks,
            'total_projects': len(user_projects),
            'completion_rate': (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        }

    def __init__(self):
        self.storage = Storage()
        self.project_manager = ProjectManager(self.storage)
        self.contexts = {}  # Track project context per user

    def get_user_context(self, user_id: str) -> ProjectContext:
        """Get or create project context for a user"""
        if user_id not in self.contexts:
            self.contexts[user_id] = ProjectContext(user_id=user_id)
        return self.contexts[user_id]

    def add_task(self, title: str, user_id: str, description: str = "", project_id: str = None) -> Task:
        """
        Enhanced task creation that associates tasks with active project
        Falls back to active project if no project is specified
        """
        # Get user context
        context = self.get_user_context(user_id)

        # Determine project ID - use provided one or active one
        final_project_id = project_id or context.active_project_id

        if not final_project_id:
            # If no project specified and no active project, raise an error
            raise ValueError("No project specified and no active project selected. Please select a project first.")

        # Get next available task ID from storage
        next_task_id = self.storage.get_next_task_id(user_id, final_project_id)

        # Create task with project association and proper ID
        task = Task(
            title=title,
            description=description,
            created_by=user_id,
            project_id=final_project_id,
            task_id=next_task_id
        )

        # Save to storage
        self.storage.save_task(task)

        print(f"Task '{title}' added with ID {task.id} to project {final_project_id}")
        return task

    def list_tasks(self, user_id: str, project_id: str = None) -> List[Task]:
        """
        Enhanced task listing that shows tasks from active project by default
        Can show tasks from specific project if specified
        """
        context = self.get_user_context(user_id)

        # Determine which project to list from
        final_project_id = project_id or context.active_project_id

        if final_project_id:
            # List tasks from specific project
            tasks = self.storage.get_tasks_for_project(user_id, final_project_id)
            print(f"\nTasks in project '{final_project_id}':")
        else:
            # List all tasks for user across all projects
            tasks = self.storage.get_all_user_tasks(user_id)
            print(f"\nAll tasks for user '{user_id}':")

        if not tasks:
            print("No tasks found.")
        else:
            for task in tasks:
                status = "X" if task.completed else "O"
                print(f"{status} [{task.id}] {task.title}")
                if task.description:
                    print(f"    Description: {task.description}")
                print(f"    Project: {task.project_id}")

        return tasks

    def update_task(self, task_id: int, user_id: str, title: str = None, description: str = None) -> Task:
        """Update task properties"""
        context = self.get_user_context(user_id)

        # For update, we need to find the task first
        # Since we don't know which project it's in, we'll search all projects for this user
        all_tasks = self.storage.get_all_user_tasks(user_id)

        target_task = None
        for task in all_tasks:
            if task.id == task_id:
                target_task = task
                break

        if not target_task:
            raise ValueError(f"Task with ID {task_id} not found for user {user_id}")

        # Update the task properties
        if title is not None:
            target_task.title = title
        if description is not None:
            target_task.description = description

        target_task.updated_at = datetime.now()

        # Save updated task
        self.storage.save_task(target_task)
        print(f"Task {task_id} updated successfully")
        return target_task

    def complete_task(self, task_id: int, user_id: str) -> Task:
        """Mark task as completed"""
        context = self.get_user_context(user_id)

        # Find the task
        all_tasks = self.storage.get_all_user_tasks(user_id)

        target_task = None
        for task in all_tasks:
            if task.id == task_id:
                target_task = task
                break

        if not target_task:
            raise ValueError(f"Task with ID {task_id} not found for user {user_id}")

        # Mark as completed
        target_task.completed = True
        target_task.updated_at = datetime.now()

        # Save updated task
        self.storage.save_task(target_task)
        print(f"Task {task_id} marked as completed")
        return target_task

    def delete_task(self, task_id: int, user_id: str) -> bool:
        """Delete a task"""
        context = self.get_user_context(user_id)

        # For now, we'll find the project that contains this task and delete it
        # Get all projects for user
        user_projects = self.project_manager.list_user_projects(user_id)

        for project in user_projects:
            project_tasks = self.storage.get_tasks_for_project(user_id, project.id)
            for task in project_tasks:
                if task.id == task_id:
                    # Delete the task
                    self.storage.delete_task(user_id, project.id, task_id)
                    print(f"Task {task_id} deleted successfully")
                    return True

        raise ValueError(f"Task with ID {task_id} not found for user {user_id}")

    # Project-related methods
    def create_project(self, name: str, user_id: str) -> Project:
        """Create a new project for a user"""
        project = self.project_manager.create_project(name, user_id)
        print(f"Project '{name}' created with ID {project.id}")
        return project

    def select_project(self, project_id: str, user_id: str) -> Project:
        """Select an active project for the user"""
        project = self.project_manager.select_project(project_id, user_id)
        context = self.get_user_context(user_id)
        context.set_active_project(project_id)
        print(f"Active project set to '{project.name}' (ID: {project_id})")
        return project

    def list_projects(self, user_id: str) -> List[Project]:
        """List all projects for a user"""
        projects = self.project_manager.list_user_projects(user_id)

        if not projects:
            print(f"No projects found for user '{user_id}'.")
        else:
            print(f"\nProjects for user '{user_id}':")
            for project in projects:
                print(f"- [{project.id}] {project.name}")

        return projects

    # Legacy methods preserved for backward compatibility
    def add_task_legacy(self, title: str, user_id: str, description: str = "") -> Task:
        """Legacy task addition that preserves Phase I task semantics"""
        # This would be used in scenarios where no project context is wanted
        # But we still need a project, so we might create a default one or require one
        context = self.get_user_context(user_id)

        if not context.active_project_id:
            raise ValueError("No active project. Please select or create a project first.")

        return self.add_task(title, user_id, description, context.active_project_id)

    def generate_report(self, user_id: str, report_type: str, project_id: str = None, output_format: str = 'text'):
        """
        Generate various types of reports and analytics
        """
        context = self.get_user_context(user_id)

        # Determine which project to generate report for
        target_project_id = project_id or context.active_project_id

        if report_type == 'summary':
            if target_project_id:
                # Summary for specific project
                project = self.storage.get_project(target_project_id)
                project_name = project.name if project else target_project_id

                print(f"\nSUMMARY REPORT for Project: {project_name} (ID: {target_project_id})")
                print("=" * 70)

                project_metrics = self.calculate_project_metrics(user_id, target_project_id)

                print(f"Total Tasks: {project_metrics['total_tasks']}")
                print(f"Completed: {project_metrics['completed_tasks']}")
                print(f"Pending: {project_metrics['pending_tasks']}")
                print(f"Completion Rate: {project_metrics['completion_rate']:.1f}%")

                if project_metrics['avg_completion_time'] is not None:
                    print(f"Avg. Completion Time: {project_metrics['avg_completion_time']:.1f} days")

            else:
                # Summary for all projects of user
                print(f"\nSUMMARY REPORT for User: {user_id}")
                print("=" * 70)

                user_metrics = self.calculate_user_metrics(user_id)

                print(f"Total Tasks: {user_metrics['total_tasks']}")
                print(f"Completed: {user_metrics['completed_tasks']}")
                print(f"Pending: {user_metrics['pending_tasks']}")
                print(f"Total Projects: {user_metrics['total_projects']}")
                print(f"Overall Completion Rate: {user_metrics['completion_rate']:.1f}%")

        elif report_type == 'detailed':
            if target_project_id:
                # Detailed report for specific project
                project = self.storage.get_project(target_project_id)
                project_name = project.name if project else target_project_id

                print(f"\nDETAILED REPORT for Project: {project_name} (ID: {target_project_id})")
                print("=" * 70)

                tasks = self.storage.get_tasks_for_project(user_id, target_project_id)

                print(f"Project Details:")
                print(f"  Name: {project_name}")
                print(f"  Created: {project.created_at.strftime('%Y-%m-%d %H:%M:%S') if project else 'N/A'}")
                print(f"  Total Tasks: {len(tasks)}")

                print(f"\nTask Breakdown:")
                completed_tasks = [t for t in tasks if t.completed]
                pending_tasks = [t for t in tasks if not t.completed]

                print(f"  Completed Tasks: {len(completed_tasks)}")
                for task in completed_tasks:
                    completion_date = getattr(task, 'completed_at', task.updated_at)
                    print(f"    - [{task.id}] {task.title} (Completed: {completion_date.strftime('%Y-%m-%d')})")

                print(f"  Pending Tasks: {len(pending_tasks)}")
                for task in pending_tasks:
                    print(f"    - [{task.id}] {task.title} (Created: {task.created_at.strftime('%Y-%m-%d')})")

            else:
                # Detailed report for all projects of user
                print(f"\nDETAILED REPORT for User: {user_id}")
                print("=" * 70)

                projects = self.project_manager.list_user_projects(user_id)

                print(f"User Details:")
                print(f"  ID: {user_id}")
                print(f"  Total Projects: {len(projects)}")

                all_tasks = self.storage.get_all_user_tasks(user_id)
                print(f"  Total Tasks Across All Projects: {len(all_tasks)}")

                print(f"\nProjects Breakdown:")
                for project in projects:
                    project_tasks = self.storage.get_tasks_for_project(user_id, project.id)
                    project_metrics = self.calculate_project_metrics(user_id, project.id)

                    print(f"  [DIR] Project: {project.name} (ID: {project.id})")
                    print(f"    Total Tasks: {project_metrics['total_tasks']}")
                    print(f"    Completed: {project_metrics['completed_tasks']}")
                    print(f"    Pending: {project_metrics['pending_tasks']}")
                    print(f"    Completion Rate: {project_metrics['completion_rate']:.1f}%")

        elif report_type == 'completion':
            if target_project_id:
                # Completion trend report for specific project
                project = self.storage.get_project(target_project_id)
                project_name = project.name if project else target_project_id

                print(f"\nCOMPLETION TREND REPORT for Project: {project_name} (ID: {target_project_id})")
                print("=" * 70)

                tasks = self.storage.get_tasks_for_project(user_id, target_project_id)

                # Count tasks by completion status
                completed_count = sum(1 for task in tasks if task.completed)
                pending_count = len(tasks) - completed_count

                print(f"Completion Statistics:")
                print(f"  Total Tasks: {len(tasks)}")
                print(f"  Completed: {completed_count}")
                print(f"  Pending: {pending_count}")
                print(f"  Completion Rate: {(completed_count / len(tasks) * 100):.1f}%" if len(tasks) > 0 else "0%")

                # Show completion timeline
                completed_tasks = [t for t in tasks if t.completed]
                if completed_tasks:
                    completed_tasks_sorted = sorted(completed_tasks, key=lambda x: x.updated_at)
                    print(f"\nCompletion Timeline:")
                    for i, task in enumerate(completed_tasks_sorted, 1):
                        print(f"  {i}. [{task.id}] {task.title} - Completed: {task.updated_at.strftime('%Y-%m-%d %H:%M:%S')}")

            else:
                # Completion trend report for all projects of user
                print(f"\nCOMPLETION TREND REPORT for User: {user_id}")
                print("=" * 70)

                all_tasks = self.storage.get_all_user_tasks(user_id)

                completed_count = sum(1 for task in all_tasks if task.completed)
                pending_count = len(all_tasks) - completed_count

                print(f"Overall Completion Statistics:")
                print(f"  Total Tasks: {len(all_tasks)}")
                print(f"  Completed: {completed_count}")
                print(f"  Pending: {pending_count}")
                print(f"  Completion Rate: {(completed_count / len(all_tasks) * 100):.1f}%" if len(all_tasks) > 0 else "0%")

        elif report_type == 'productivity':
            if target_project_id:
                # Productivity report for specific project
                project = self.storage.get_project(target_project_id)
                project_name = project.name if project else target_project_id

                print(f"\nPRODUCTIVITY REPORT for Project: {project_name} (ID: {target_project_id})")
                print("=" * 70)

                tasks = self.storage.get_tasks_for_project(user_id, target_project_id)

                # Calculate productivity metrics
                completed_tasks = [t for t in tasks if t.completed]

                if completed_tasks:
                    # Calculate average time to complete tasks
                    total_duration = 0
                    completed_count = 0
                    for task in completed_tasks:
                        duration = (task.updated_at - task.created_at).days
                        if duration >= 0:  # Only count valid durations
                            total_duration += duration
                            completed_count += 1

                    avg_completion_days = total_duration / completed_count if completed_count > 0 else 0

                    print(f"Productivity Metrics:")
                    print(f"  Total Tasks: {len(tasks)}")
                    print(f"  Completed Tasks: {len(completed_tasks)}")
                    print(f"  Average Days to Complete: {avg_completion_days:.1f} days")
                    print(f"  Tasks per Day: {len(completed_tasks) / max(avg_completion_days, 1):.1f}" if avg_completion_days > 0 else f"  Tasks per Day: 0")
                else:
                    print("No completed tasks to calculate productivity metrics.")

            else:
                # Productivity report for all projects of user
                print(f"\nPRODUCTIVITY REPORT for User: {user_id}")
                print("=" * 70)

                all_tasks = self.storage.get_all_user_tasks(user_id)
                completed_tasks = [t for t in all_tasks if t.completed]

                if completed_tasks:
                    # Calculate average time to complete tasks
                    total_duration = 0
                    completed_count = 0
                    for task in completed_tasks:
                        duration = (task.updated_at - task.created_at).days
                        if duration >= 0:  # Only count valid durations
                            total_duration += duration
                            completed_count += 1

                    avg_completion_days = total_duration / completed_count if completed_count > 0 else 0

                    print(f"Overall Productivity Metrics:")
                    print(f"  Total Tasks: {len(all_tasks)}")
                    print(f"  Completed Tasks: {len(completed_tasks)}")
                    print(f"  Average Days to Complete: {avg_completion_days:.1f} days")
                    print(f"  Tasks per Day: {len(completed_tasks) / max(avg_completion_days, 1):.1f}" if avg_completion_days > 0 else f"  Tasks per Day: 0")
                else:
                    print("No completed tasks to calculate productivity metrics.")

    def show_shortcuts(self):
        """
        Display keyboard shortcuts and available commands
        """
        print("\nKEYBOARD SHORTCUTS & COMMANDS REFERENCE")
        print("=" * 60)
        print("CLI Commands Available:")
        print()
        print("Task Management:")
        print("  add --title <title> [--description <desc>] [--user <user>] [--project <proj_id>]")
        print("      Add a new task to the specified project or active project")
        print()
        print("  list [--user <user>] [--project <proj_id>]")
        print("      List tasks in the specified project or active project")
        print()
        print("  update --id <task_id> [--title <title>] [--description <desc>] [--user <user>]")
        print("      Update an existing task")
        print()
        print("  complete --id <task_id> [--user <user>]")
        print("      Mark a task as completed")
        print()
        print("  delete --id <task_id> [--user <user>]")
        print("      Delete a task")
        print()
        print("Project Management:")
        print("  project create --name <project_name> [--user <user>]")
        print("      Create a new project")
        print()
        print("  project select --id <project_id> [--user <user>]")
        print("      Select an active project")
        print()
        print("  project list [--user <user>]")
        print("      List all projects for a user")
        print()
        print("UI Enhancement Commands:")
        print("  dashboard [--user <user>] [--project <proj_id>]")
        print("      Show project dashboard with metrics")
        print()
        print("  filter --user <user> [--project <proj_id>] [--status all|completed|pending] [--search <term>] [--sort id|title|date]")
        print("      Filter tasks by various criteria")
        print()
        print("  bulk --user <user> --operation complete|delete|update --ids <task_ids> [--project <proj_id>] [--confirm]")
        print("      Perform bulk operations on multiple tasks (use --confirm for destructive ops)")
        print()
        print("  report --user <user> --type summary|detailed|completion|productivity [--project <proj_id>] [--format text|csv]")
        print("      Generate various types of reports and analytics")
        print()
        print("Examples:")
        print("  python implementation.py add --title \"New Task\" --user john")
        print("  python implementation.py project create --name \"Work\" --user john")
        print("  python implementation.py dashboard --user john")
        print("  python implementation.py filter --user john --status completed --sort date")
        print("  python implementation.py bulk --user john --operation complete --ids 1,2,3 --confirm")
        print("  python implementation.py report --user john --type summary")

    def get_tasks_by_ids(self, user_id: str, task_ids: list) -> list:
        """
        Retrieve tasks by their IDs for the specified user
        """
        all_tasks = self.storage.get_all_user_tasks(user_id)
        return [task for task in all_tasks if task.id in task_ids]

    def bulk_operation(self, user_id: str, project_id: str = None, operation: str = 'complete', task_ids: list = [], confirm: bool = False):
        """
        Perform bulk operations on tasks
        """
        context = self.get_user_context(user_id)

        # Determine which project to operate on
        target_project_id = project_id or context.active_project_id

        # Get tasks by IDs
        tasks_to_operate = self.get_tasks_by_ids(user_id, task_ids)

        if not tasks_to_operate:
            print(f"No tasks found with IDs {task_ids} for user {user_id}")
            return []

        # Verify all tasks belong to the target project if specified
        if target_project_id:
            tasks_to_operate = [task for task in tasks_to_operate if task.project_id == target_project_id]
            if not tasks_to_operate:
                print(f"No tasks with IDs {task_ids} found in project {target_project_id}")
                return []

        print(f"Selected {len(tasks_to_operate)} task(s) for bulk operation '{operation}':")
        for task in tasks_to_operate:
            print(f"  - [{task.id}] {task.title}")

        # For destructive operations, require confirmation
        if operation in ['delete'] and not confirm:
            print(f"WARNING: This is a destructive operation. Please add --confirm flag to proceed with '{operation}'.")
            return []

        # Perform the operation
        results = []
        if operation == 'complete':
            for task in tasks_to_operate:
                task.completed = True
                task.updated_at = datetime.now()
                self.storage.save_task(task)
                results.append(task)
                print(f"[OK] Task {task.id} marked as completed")
        elif operation == 'delete':
            for task in tasks_to_operate:
                # Find the project that contains this task and delete it
                user_projects = self.project_manager.list_user_projects(user_id)
                for project in user_projects:
                    if task.project_id == project.id:
                        self.storage.delete_task(user_id, project.id, task.id)
                        results.append(task.id)  # For delete, we just return the IDs
                        print(f"[OK] Task {task.id} deleted")
                        break
        elif operation == 'update':
            # For update operation, we might want to allow setting common properties
            # For now, just update the timestamp
            for task in tasks_to_operate:
                task.updated_at = datetime.now()
                self.storage.save_task(task)
                results.append(task)
                print(f"[OK] Task {task.id} updated")
        else:
            print(f"Unknown operation: {operation}")
            return []

        print(f"Bulk operation '{operation}' completed on {len(results)} task(s).")
        return results

    def filter_tasks(self, user_id: str, project_id: str = None, status_filter: str = 'all', search_term: str = None, sort_by: str = 'id'):
        """
        Filter tasks based on criteria
        """
        context = self.get_user_context(user_id)

        # Determine which project to filter tasks from
        target_project_id = project_id or context.active_project_id

        if target_project_id:
            # Filter tasks from specific project
            tasks = self.storage.get_tasks_for_project(user_id, target_project_id)
        else:
            # Filter tasks from all projects for the user
            tasks = self.storage.get_all_user_tasks(user_id)

        # Apply status filter
        if status_filter == 'completed':
            tasks = [task for task in tasks if task.completed]
        elif status_filter == 'pending':
            tasks = [task for task in tasks if not task.completed]

        # Apply search filter
        if search_term:
            search_term_lower = search_term.lower()
            tasks = [
                task for task in tasks
                if search_term_lower in task.title.lower() or
                (task.description and search_term_lower in task.description.lower())
            ]

        # Apply sorting
        if sort_by == 'title':
            tasks = sorted(tasks, key=lambda x: x.title.lower())
        elif sort_by == 'date':
            tasks = sorted(tasks, key=lambda x: x.created_at, reverse=True)
        else:  # Sort by ID
            tasks = sorted(tasks, key=lambda x: x.id)

        # Display filtered tasks
        if target_project_id:
            project = self.storage.get_project(target_project_id)
            project_name = project.name if project else target_project_id
            print(f"\nFILTERED TASKS IN PROJECT '{project_name}' (ID: {target_project_id}):")
        else:
            print(f"\nFILTERED TASKS ACROSS ALL PROJECTS FOR USER '{user_id}':")

        print(f"Applied filters - Status: {status_filter}, Search: '{search_term or 'None'}', Sort: {sort_by}")

        if not tasks:
            print("No tasks found matching the criteria.")
        else:
            print(f"Found {len(tasks)} task(s):")
            for task in tasks:
                status = "X" if task.completed else "O"
                print(f"{status} [{task.id}] {task.title}")
                if task.description:
                    print(f"    Description: {task.description}")
                if target_project_id:
                    print(f"    Project: {target_project_id}")

        return tasks

    def dashboard(self, user_id: str, project_id: str = None):
        """
        Show dashboard with project metrics
        """
        context = self.get_user_context(user_id)

        # Determine which project to show dashboard for
        target_project_id = project_id or context.active_project_id

        if target_project_id:
            # Show dashboard for specific project
            project = self.storage.get_project(target_project_id)
            if not project:
                print(f"Project with ID {target_project_id} not found.")
                return

            print(f"\nDASHBOARD for Project: {project.name} (ID: {target_project_id})")
            print("-" * 60)

            # Get project metrics
            project_metrics = self.calculate_project_metrics(user_id, target_project_id)

            print(f"Total Tasks: {project_metrics['total_tasks']}")
            print(f"Completed: {project_metrics['completed_tasks']}")
            print(f"Pending: {project_metrics['pending_tasks']}")
            print(f"Completion Rate: {project_metrics['completion_rate']:.1f}%")

            if project_metrics['avg_completion_time'] is not None:
                print(f"Avg. Completion Time: {project_metrics['avg_completion_time']:.1f} days")

            # List recent tasks
            tasks = self.storage.get_tasks_for_project(user_id, target_project_id)
            recent_tasks = sorted(tasks, key=lambda x: x.created_at, reverse=True)[:5]  # Last 5 tasks

            if recent_tasks:
                print(f"\nRECENT TASKS:")
                for task in recent_tasks:
                    status = "[DONE]" if task.completed else "[PEND]"
                    print(f"  {status} [{task.id}] {task.title} ({task.created_at.strftime('%Y-%m-%d')})")
            else:
                print("\nNO TASKS IN THIS PROJECT YET.")

        else:
            # Show overall user dashboard
            print(f"\nOVERALL DASHBOARD for User: {user_id}")
            print("-" * 60)

            user_metrics = self.calculate_user_metrics(user_id)

            print(f"Total Tasks: {user_metrics['total_tasks']}")
            print(f"Completed: {user_metrics['completed_tasks']}")
            print(f"Pending: {user_metrics['pending_tasks']}")
            print(f"Total Projects: {user_metrics['total_projects']}")
            print(f"Overall Completion Rate: {user_metrics['completion_rate']:.1f}%")

            # List projects
            projects = self.project_manager.list_user_projects(user_id)
            if projects:
                print(f"\nPROJECTS:")
                for project in projects:
                    project_metrics = self.calculate_project_metrics(user_id, project.id)
                    print(f"  [DIR] [{project.id}] {project.name} - {project_metrics['total_tasks']} tasks ({project_metrics['completion_rate']:.1f}% complete)")

    def ensure_backward_compatibility(self):
        """Ensure Phase I-III functionality remains unchanged"""
        # All existing methods maintain their original signatures and behavior
        # where possible, but now operate within project context
        pass


def main():
    """Main CLI interface with both legacy and new project-based commands"""
    parser = argparse.ArgumentParser(description='Project-Based Task Manager')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Task commands
    add_parser = subparsers.add_parser('add', help='Add a new task')
    add_parser.add_argument('--title', required=True, help='Task title')
    add_parser.add_argument('--description', help='Task description')
    add_parser.add_argument('--user', default='default_user', help='User ID')
    add_parser.add_argument('--project', help='Project ID (optional, uses active project if not specified)')

    list_parser = subparsers.add_parser('list', help='List tasks')
    list_parser.add_argument('--user', default='default_user', help='User ID')
    list_parser.add_argument('--project', help='Project ID (optional, uses active project if not specified)')

    update_parser = subparsers.add_parser('update', help='Update a task')
    update_parser.add_argument('--id', type=int, required=True, help='Task ID')
    update_parser.add_argument('--title', help='New task title')
    update_parser.add_argument('--description', help='New task description')
    update_parser.add_argument('--user', default='default_user', help='User ID')

    complete_parser = subparsers.add_parser('complete', help='Complete a task')
    complete_parser.add_argument('--id', type=int, required=True, help='Task ID')
    complete_parser.add_argument('--user', default='default_user', help='User ID')

    delete_parser = subparsers.add_parser('delete', help='Delete a task')
    delete_parser.add_argument('--id', type=int, required=True, help='Task ID')
    delete_parser.add_argument('--user', default='default_user', help='User ID')

    # Project commands
    project_parser = subparsers.add_parser('project', help='Project management commands')
    project_subparsers = project_parser.add_subparsers(dest='project_action', help='Project actions')

    create_parser = project_subparsers.add_parser('create', help='Create a project')
    create_parser.add_argument('--name', required=True, help='Project name')
    create_parser.add_argument('--user', default='default_user', help='User ID')

    select_parser = project_subparsers.add_parser('select', help='Select a project')
    select_parser.add_argument('--id', required=True, help='Project ID')
    select_parser.add_argument('--user', default='default_user', help='User ID')

    list_proj_parser = project_subparsers.add_parser('list', help='List projects')
    list_proj_parser.add_argument('--user', default='default_user', help='User ID')

    # Dashboard command
    dashboard_parser = subparsers.add_parser('dashboard', help='Show project dashboard')
    dashboard_parser.add_argument('--user', default='default_user', help='User ID')
    dashboard_parser.add_argument('--project', help='Project ID (optional, uses active project if not specified)')

    # Filter command
    filter_parser = subparsers.add_parser('filter', help='Filter tasks by criteria')
    filter_parser.add_argument('--user', default='default_user', help='User ID')
    filter_parser.add_argument('--project', help='Project ID (optional, uses active project if not specified)')
    filter_parser.add_argument('--status', choices=['all', 'completed', 'pending'], default='all', help='Filter by task status')
    filter_parser.add_argument('--search', help='Search term to filter tasks by title or description')
    filter_parser.add_argument('--sort', choices=['id', 'title', 'date'], default='id', help='Sort results by')

    # Bulk operations command
    bulk_parser = subparsers.add_parser('bulk', help='Perform bulk operations on tasks')
    bulk_parser.add_argument('--user', default='default_user', help='User ID')
    bulk_parser.add_argument('--project', help='Project ID (optional, uses active project if not specified)')
    bulk_parser.add_argument('--operation', required=True, choices=['complete', 'delete', 'update'], help='Bulk operation to perform')
    bulk_parser.add_argument('--ids', required=True, help='Comma-separated list of task IDs to operate on')
    bulk_parser.add_argument('--confirm', action='store_true', help='Confirm the bulk operation (required for destructive operations)')

    # Report command
    report_parser = subparsers.add_parser('report', help='Generate reports and analytics')
    report_parser.add_argument('--user', default='default_user', help='User ID')
    report_parser.add_argument('--project', help='Project ID (optional, uses active project if not specified)')
    report_parser.add_argument('--type', required=True, choices=['summary', 'detailed', 'completion', 'productivity'], help='Type of report to generate')
    report_parser.add_argument('--format', choices=['text', 'csv'], default='text', help='Output format for the report')

    # Help command for shortcuts
    help_parser = subparsers.add_parser('help', help='Show help and keyboard shortcuts')
    help_parser.add_argument('--extended', action='store_true', help='Show extended help with all commands')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    task_manager = TaskManager()

    try:
        if args.command == 'add':
            task_manager.add_task(
                title=args.title,
                description=args.description or "",
                user_id=args.user,
                project_id=args.project
            )
        elif args.command == 'list':
            task_manager.list_tasks(
                user_id=args.user,
                project_id=args.project
            )
        elif args.command == 'update':
            task_manager.update_task(
                task_id=args.id,
                user_id=args.user,
                title=args.title,
                description=args.description
            )
        elif args.command == 'complete':
            task_manager.complete_task(
                task_id=args.id,
                user_id=args.user
            )
        elif args.command == 'delete':
            task_manager.delete_task(
                task_id=args.id,
                user_id=args.user
            )
        elif args.command == 'project':
            if args.project_action == 'create':
                task_manager.create_project(
                    name=args.name,
                    user_id=args.user
                )
            elif args.project_action == 'select':
                task_manager.select_project(
                    project_id=args.id,
                    user_id=args.user
                )
            elif args.project_action == 'list':
                task_manager.list_projects(
                    user_id=args.user
                )
            else:
                project_parser.print_help()
        elif args.command == 'dashboard':
            task_manager.dashboard(
                user_id=args.user,
                project_id=args.project
            )
        elif args.command == 'filter':
            task_manager.filter_tasks(
                user_id=args.user,
                project_id=args.project,
                status_filter=args.status,
                search_term=args.search,
                sort_by=args.sort
            )
        elif args.command == 'bulk':
            # Parse the task IDs from the comma-separated string
            task_ids = [int(id_str.strip()) for id_str in args.ids.split(',')]

            task_manager.bulk_operation(
                user_id=args.user,
                project_id=args.project,
                operation=args.operation,
                task_ids=task_ids,
                confirm=args.confirm
            )
        elif args.command == 'report':
            task_manager.generate_report(
                user_id=args.user,
                report_type=args.type,
                project_id=args.project,
                output_format=args.format
            )
        elif args.command == 'help':
            if args.extended:
                task_manager.show_shortcuts()
            else:
                parser.print_help()
        else:
            parser.print_help()

    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()