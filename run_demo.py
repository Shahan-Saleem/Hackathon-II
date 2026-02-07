#!/usr/bin/env python3
"""
Demo script to showcase the Project-Based Task Management Application features
"""

import os
import sys
from app import TaskManager, User

def demo_features():
    """Demonstrate the key features of the application"""
    print("[APP] Project-Based Task Management Application Demo")
    print("="*50)

    # Initialize the task manager
    tm = TaskManager()
    print("[OK] TaskManager initialized")

    # Demo user authentication
    print("\n[SEC] DEMO: User Authentication")
    print("-"*30)

    # Register a demo user
    try:
        user = tm.register_user("demo_user_" + str(hash("demo"))[-4:], "demo_password")
        if user:
            print(f"[OK] User '{user.username}' registered with ID: {user.id}")
        else:
            print("[INFO] User already exists, authenticating instead...")
            user = tm.authenticate_user("demo_user_" + str(hash("demo"))[-4:], "demo_password")
            if not user:
                print("[ERR] Could not authenticate existing user")
                return
            print(f"[OK] Existing user authenticated: {user.username}")
    except:
        # Fallback to a different username if there's an issue
        import uuid
        username = "demo_user_" + str(uuid.uuid4())[:8]
        user = tm.register_user(username, "demo_password")
        if user:
            print(f"[OK] User '{user.username}' registered with ID: {user.id}")
        else:
            print("[ERR] User registration failed")
            return

    # Authenticate the user
    authenticated_user = tm.authenticate_user("demo_user", "demo_password")
    if authenticated_user:
        print(f"[OK] User '{authenticated_user.username}' authenticated")
    else:
        print("[ERR] User authentication failed")
        return

    # Demo project management
    print("\n[PROJ] DEMO: Project Management")
    print("-"*30)

    # Create a project
    project = tm.create_project("Demo Project", user.id)
    print(f"[OK] Project '{project.name}' created with ID: {project.id}")

    # Select the project as active
    selected_project = tm.select_project(project.id, user.id)
    print(f"[OK] Project '{selected_project.name}' selected as active")

    # Demo task management
    print("\n[TASK] DEMO: Task Management")
    print("-"*30)

    # Add a task to the project
    task = tm.add_task(
        title="Demo Task",
        description="This is a demonstration task",
        user_id=user.id,
        project_id=project.id
    )
    print(f"[OK] Task '{task.title}' added with ID: {task.id}")

    # List tasks
    tasks = tm.list_tasks(user.id, project.id)
    print(f"[OK] Found {len(tasks)} task(s) in project")

    # Update the task
    updated_task = tm.update_task(
        task_id=task.id,
        user_id=user.id,
        title="Updated Demo Task",
        description="This is an updated demonstration task"
    )
    print(f"[OK] Task updated to '{updated_task.title}'")

    # Complete the task
    completed_task = tm.complete_task(task.id, user.id)
    print(f"[OK] Task '{completed_task.title}' marked as completed")

    # List projects
    projects = tm.list_projects(user.id)
    print(f"[OK] User has {len(projects)} project(s)")

    print("\n[SUCCESS] Demo completed successfully!")
    print("\n[INFO] To use the full application:")
    print("   python main.py")
    print("\nThe application features:")
    print("   • User authentication (signup/signin)")
    print("   • Project-based task organization")
    print("   • Colorful console UI")
    print("   • Persistent storage")
    print("   • Cross-platform compatibility")

if __name__ == "__main__":
    demo_features()