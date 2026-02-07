#!/usr/bin/env python3
"""
Basic functionality test for the Project-Based Task Management Application
Verifies that all core components are working correctly
"""
import os
import sys
import json
from app import TaskManager, User, Project, Task


def test_basic_functionality():
    """Test basic functionality of the application"""
    print("Testing Project-Based Task Management Application...")

    # Create a new task manager instance
    tm = TaskManager("test_storage.json")

    print("TaskManager initialized")

    # Test user registration
    print("\nTesting user registration...")
    user = tm.register_user("testuser", "testpass")
    if user:
        print(f"User '{user.username}' registered with ID: {user.id}")
        current_user_id = user.id
    else:
        print("User registration failed")
        return False

    # Test project creation
    print("\nTesting project creation...")
    try:
        project = tm.create_project("Test Project", current_user_id)
        print(f"Project '{project.name}' created with ID: {project.id}")
        project_id = project.id
    except Exception as e:
        print(f"Project creation failed: {str(e)}")
        return False

    # Test project selection
    print("\nTesting project selection...")
    try:
        selected_project = tm.select_project(project_id, current_user_id)
        print(f"Project '{selected_project.name}' selected")
    except Exception as e:
        print(f"Project selection failed: {str(e)}")
        return False

    # Test task creation
    print("\nTesting task creation...")
    try:
        task = tm.add_task("Test Task", current_user_id, "This is a test task", project_id)
        print(f"Task '{task.title}' created with ID: {task.id}")
        task_id = task.id
    except Exception as e:
        print(f"Task creation failed: {str(e)}")
        return False

    # Test task listing
    print("\nTesting task listing...")
    try:
        tasks = tm.list_tasks(current_user_id)
        print(f"Found {len(tasks)} task(s)")
    except Exception as e:
        print(f"Task listing failed: {str(e)}")
        return False

    # Test task completion
    print("\nTesting task completion...")
    try:
        completed_task = tm.complete_task(task_id, current_user_id)
        print(f"Task {completed_task.id} marked as completed")
    except Exception as e:
        print(f"Task completion failed: {str(e)}")
        return False

    # Test task update
    print("\nTesting task update...")
    try:
        updated_task = tm.update_task(task_id, current_user_id, title="Updated Test Task")
        print(f"Task {updated_task.id} updated to '{updated_task.title}'")
    except Exception as e:
        print(f"Task update failed: {str(e)}")
        return False

    # Test project listing
    print("\nTesting project listing...")
    try:
        projects = tm.list_projects(current_user_id)
        print(f"Found {len(projects)} project(s)")
    except Exception as e:
        print(f"Project listing failed: {str(e)}")
        return False

    # Test storage persistence
    print("\nTesting storage persistence...")
    if os.path.exists("test_storage.json"):
        with open("test_storage.json", 'r') as f:
            data = json.load(f)

        if "users" in data and "projects" in data and "tasks" in data:
            print("Storage file created with proper structure")

            # Check if our user, project, and task exist
            user_exists = any(u.get("username") == "testuser" for u in data["users"].values())
            project_exists = project_id in data["projects"]
            task_exists = (
                current_user_id in data["tasks"] and
                project_id in data["tasks"][current_user_id] and
                any(t["id"] == task_id for t in data["tasks"][current_user_id][project_id])
            )

            if user_exists and project_exists and task_exists:
                print("All created entities persisted to storage")
            else:
                print("Some entities not found in storage")
                return False
        else:
            print("Storage file has incorrect structure")
            return False
    else:
        print("Storage file not created")
        return False

    print("\nAll tests passed! Application is working correctly.")

    # Clean up test file
    if os.path.exists("test_storage.json"):
        os.remove("test_storage.json")
        print("Test storage file cleaned up")

    return True


def main():
    """Main test function"""
    print("Running basic functionality test...")
    print("=" * 60)

    success = test_basic_functionality()

    print("=" * 60)
    if success:
        print("All tests PASSED - Application is ready!")
        return 0
    else:
        print("Some tests FAILED - Please check the implementation")
        return 1


if __name__ == "__main__":
    sys.exit(main())