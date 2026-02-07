"""
Data models for Project and enhanced Task entities
"""

import uuid
from datetime import datetime
from typing import Optional


class Project:
    """
    Project entity representing an organizational container that holds tasks
    """

    def __init__(self, name: str, user_id: str, project_id: Optional[str] = None, description: str = ""):
        self.id = project_id if project_id else str(uuid.uuid4())
        self.name = name
        self.description = description
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.user_id = user_id

    def to_dict(self):
        """Convert project to dictionary representation"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'user_id': self.user_id
        }

    @classmethod
    def from_dict(cls, data):
        """Create Project instance from dictionary representation"""
        project = cls(
            name=data['name'],
            user_id=data['user_id'],
            project_id=data['id'],
            description=data.get('description', '')
        )
        project.created_at = datetime.fromisoformat(data['created_at'])
        project.updated_at = datetime.fromisoformat(data['updated_at'])
        return project


class Task:
    """
    Enhanced Task entity with project association
    Maintains all existing properties while adding project_id
    """

    def __init__(self, title: str, created_by: str, project_id: str,
                 description: Optional[str] = "", completed: bool = False,
                 task_id: Optional[int] = None, created_at: Optional[datetime] = None,
                 updated_at: Optional[datetime] = None):
        self.id = task_id if task_id else self._generate_id()  # Sequential ID per user
        self.title = title
        self.description = description
        self.completed = completed
        self.created_by = created_by
        self.project_id = project_id  # NEW: Reference to Project entity
        self.created_at = created_at if created_at else datetime.now()
        self.updated_at = updated_at if updated_at else datetime.now()

    def _generate_id(self) -> int:
        """Generate a unique ID for the task (placeholder - will be handled by storage layer)"""
        # This will be replaced by the storage layer which handles sequential IDs per user
        return 0  # Placeholder - actual ID will be assigned by storage

    def to_dict(self):
        """Convert task to dictionary representation"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'completed': self.completed,
            'created_by': self.created_by,
            'project_id': self.project_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data):
        """Create Task instance from dictionary representation"""
        task = cls(
            title=data['title'],
            description=data.get('description', ''),
            completed=data.get('completed', False),
            created_by=data['created_by'],
            project_id=data['project_id'],
            task_id=data['id']
        )
        task.created_at = datetime.fromisoformat(data['created_at'])
        task.updated_at = datetime.fromisoformat(data['updated_at'])
        return task


class ProjectContext:
    """
    Project Context Manager to track active project context
    """

    def __init__(self, user_id: str, active_project_id: Optional[str] = None):
        self.user_id = user_id
        self.active_project_id = active_project_id

    def set_active_project(self, project_id: str):
        """Set the active project for the current user session"""
        self.active_project_id = project_id
        self.updated_at = datetime.now()

    def get_active_project(self) -> Optional[str]:
        """Get the active project ID for the current user session"""
        return self.active_project_id

    def clear_active_project(self):
        """Clear the active project context"""
        self.active_project_id = None