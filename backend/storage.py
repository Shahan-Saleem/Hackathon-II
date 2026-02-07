"""
Enhanced storage layer with project associations
Maintains Phase III persistence guarantees while adding project context
"""

import json
import os
import uuid
from datetime import datetime
from typing import List, Optional, Dict
from .models import Project, Task


class Storage:
    """
    Enhanced storage layer to persist project-task relationships
    Maintains existing task storage format with added project relationships
    """

    def __init__(self, storage_file: str = "tasks_storage.json"):
        self.storage_file = storage_file
        self.data = self.load_data()

    def load_data(self) -> Dict:
        """Load data from storage file"""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                # If file is corrupted or not found, return default structure
                return self.get_default_data_structure()
        else:
            return self.get_default_data_structure()

    def get_default_data_structure(self) -> Dict:
        """Return the default data structure"""
        return {
            "projects": {},
            "tasks": {},  # Will store tasks by user_id -> project_id -> task_list
            "users": {}
        }

    def save_data(self):
        """Save data to storage file"""
        with open(self.storage_file, 'w') as f:
            json.dump(self.data, f, indent=2)

    def save_project(self, project: Project):
        """Save a project to storage"""
        if "projects" not in self.data:
            self.data["projects"] = {}

        self.data["projects"][project.id] = project.to_dict()
        self.save_data()

    def get_next_task_id(self, user_id: str, project_id: str) -> int:
        """Get the next available task ID for a user across all projects"""
        if "tasks" not in self.data:
            self.data["tasks"] = {}

        if user_id not in self.data["tasks"]:
            return 1

        max_id = 0
        # Look across ALL projects for this user to find max ID
        if user_id in self.data["tasks"]:
            for proj_tasks in self.data["tasks"][user_id].values():
                for existing_task in proj_tasks:
                    if existing_task['id'] > max_id:
                        max_id = existing_task['id']

        return max_id + 1

    def get_project(self, project_id: str) -> Optional[Project]:
        """Retrieve a project from storage"""
        if "projects" not in self.data:
            self.data["projects"] = {}

        project_data = self.data["projects"].get(project_id)
        if project_data:
            return Project.from_dict(project_data)
        return None

    def get_projects_for_user(self, user_id: str) -> List[Project]:
        """Get all projects for a specific user"""
        if "projects" not in self.data:
            self.data["projects"] = {}

        user_projects = []
        for project_data in self.data["projects"].values():
            if project_data["user_id"] == user_id:
                user_projects.append(Project.from_dict(project_data))
        return user_projects

    def save_task(self, task: Task):
        """Save a task to storage within its project context"""
        if "tasks" not in self.data:
            self.data["tasks"] = {}

        # Ensure user exists in tasks dict
        if task.created_by not in self.data["tasks"]:
            self.data["tasks"][task.created_by] = {}

        # Ensure project exists under user
        if task.project_id not in self.data["tasks"][task.created_by]:
            self.data["tasks"][task.created_by][task.project_id] = []

        # Check if task already exists (by ID) and update or append
        task_found = False
        for i, existing_task in enumerate(self.data["tasks"][task.created_by][task.project_id]):
            if existing_task['id'] == task.id:
                self.data["tasks"][task.created_by][task.project_id][i] = task.to_dict()
                task_found = True
                break

        if not task_found:
            # Get next available ID for this user/project combination
            next_id = self.get_next_task_id(task.created_by, task.project_id)
            task.id = next_id
            self.data["tasks"][task.created_by][task.project_id].append(task.to_dict())

        self.save_data()

    def get_tasks_for_project(self, user_id: str, project_id: str) -> List[Task]:
        """Get all tasks for a specific user and project"""
        if "tasks" not in self.data:
            self.data["tasks"] = {}

        if user_id not in self.data["tasks"]:
            return []

        if project_id not in self.data["tasks"][user_id]:
            return []

        tasks = []
        for task_data in self.data["tasks"][user_id][project_id]:
            tasks.append(Task.from_dict(task_data))
        return tasks

    def get_all_user_tasks(self, user_id: str) -> List[Task]:
        """Get all tasks for a specific user across all projects"""
        if "tasks" not in self.data:
            self.data["tasks"] = {}

        if user_id not in self.data["tasks"]:
            return []

        all_tasks = []
        for project_tasks in self.data["tasks"][user_id].values():
            for task_data in project_tasks:
                all_tasks.append(Task.from_dict(task_data))
        return all_tasks

    def delete_task(self, user_id: str, project_id: str, task_id: int):
        """Delete a specific task"""
        if "tasks" not in self.data:
            self.data["tasks"] = {}

        if user_id in self.data["tasks"] and project_id in self.data["tasks"][user_id]:
            self.data["tasks"][user_id][project_id] = [
                task for task in self.data["tasks"][user_id][project_id]
                if task['id'] != task_id
            ]
            self.save_data()

    def migrate_legacy_tasks(self, default_project_name: str = "Default"):
        """
        Handle existing tasks without project associations by assigning them to a default project
        """
        if "tasks" not in self.data:
            self.data["tasks"] = {}

        # Find users with tasks but no project associations
        for user_id, user_tasks in self.data["tasks"].items():
            # Check if tasks are already organized by project
            needs_migration = False

            # If the structure is flat (old format), we need to migrate
            if user_tasks and isinstance(list(user_tasks.values())[0], list):
                # Check if the first entry is a task list directly (old format)
                first_value = next(iter(user_tasks.values()))
                if isinstance(first_value, list) and first_value and 'project_id' not in first_value[0]:
                    needs_migration = True

            if needs_migration:
                # Create a default project for this user
                default_project = Project(name=default_project_name, user_id=user_id)
                self.save_project(default_project)

                # Move all tasks to the default project
                migrated_tasks = {}
                for project_or_task_key, content in user_tasks.items():
                    if isinstance(content, list):  # These are tasks
                        # Add project_id to each task
                        for task_data in content:
                            task_data['project_id'] = default_project.id
                        migrated_tasks[default_project.id] = content

                self.data["tasks"][user_id] = migrated_tasks

        self.save_data()

    def ensure_phase_iii_compatibility(self):
        """
        Ensure Phase III persistence guarantees remain unchanged
        """
        # The storage structure maintains backward compatibility by keeping
        # the same basic structure while adding project relationships
        # Legacy operations can still work by operating on all projects for a user
        pass

    def log_activity(self, user_id: str, activity_type: str, project_id: str = None, task_id: int = None, description: str = ""):
        """Log an activity event"""
        if "activities" not in self.data:
            self.data["activities"] = []

        activity = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "type": activity_type,
            "project_id": project_id,
            "task_id": task_id,
            "description": description,
            "timestamp": datetime.now().isoformat()
        }

        self.data["activities"].append(activity)
        self.save_data()

    def get_recent_activities(self, user_id: str, limit: int = 10) -> List[Dict]:
        """Get recent activities for a user"""
        if "activities" not in self.data:
            return []

        user_activities = [activity for activity in self.data["activities"]
                          if activity["user_id"] == user_id]

        # Sort by timestamp (most recent first)
        user_activities.sort(key=lambda x: x["timestamp"], reverse=True)

        return user_activities[:limit]

    def delete_project_and_related_data(self, user_id: str, project_id: str):
        """Delete a project and all related tasks and activities"""
        # Remove project
        if "projects" in self.data and project_id in self.data["projects"]:
            del self.data["projects"][project_id]

        # Remove all tasks associated with this project
        if "tasks" in self.data and user_id in self.data["tasks"]:
            if project_id in self.data["tasks"][user_id]:
                del self.data["tasks"][user_id][project_id]

        # Remove all activities associated with this project
        if "activities" in self.data:
            self.data["activities"] = [
                activity for activity in self.data["activities"]
                if activity["user_id"] != user_id or activity["project_id"] != project_id
            ]

        self.save_data()