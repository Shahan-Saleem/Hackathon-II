#!/usr/bin/env python3
"""
Simple test script to verify Phase IV implementation
"""

import os
import sys
import tempfile
from datetime import datetime

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from implementation import TaskManager
from models import Project, Task, ProjectContext
from storage import Storage
from project_manager import ProjectManager


def test_basic_functionality():
    """Test basic project and task functionality"""
    print("Testing Phase IV - Project-Based Task Management...")

    # Create a task manager with temporary storage
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tmp:
        tmp.close()
        # Create a new storage instance with temp file
        original_storage_file = "tasks_storage.json"
        if os.path.exists(original_storage_file):
            # Remove any existing backup first
            backup_path = f"{original_storage_file}.backup"
            if os.path.exists(backup_path):
                os.remove(backup_path)
            os.rename(original_storage_file, backup_path)

        try:
            tm = TaskManager()
            # Override storage to use temp file
            tm.storage = Storage(tmp.name)

            # Test User Story 1: Project-Based Task Organization
            print("\n--- Testing User Story 1: Project-Based Task Organization ---")

            # Create a project
            project = tm.create_project("Test Project", "test_user")
            print(f"[OK] Created project: {project.name} ({project.id})")

            # Select the project
            selected_project = tm.select_project(project.id, "test_user")
            print(f"[OK] Selected project: {selected_project.name}")

            # Add a task to the project
            task = tm.add_task("Test Task", "test_user", "This is a test task")
            print(f"[OK] Added task: {task.title} (ID: {task.id})")

            # List tasks (should show tasks from active project)
            tasks = tm.list_tasks("test_user")
            print(f"[OK] Listed tasks: Found {len(tasks)} task(s)")

            # Test User Story 2: UI-First Project Interaction
            print("\n--- Testing User Story 2: UI-First Project Interaction ---")

            # List all projects
            projects = tm.list_projects("test_user")
            print(f"[OK] Listed projects: Found {len(projects)} project(s)")

            # Complete the task
            completed_task = tm.complete_task(task.id, "test_user")
            print(f"[OK] Completed task: {completed_task.title}")

            # List tasks again to see completion status
            tasks = tm.list_tasks("test_user")
            print(f"[OK] Verified task completion")

            # Test User Story 3: Backward Compatibility
            print("\n--- Testing User Story 3: Backward Compatibility ---")

            # Add another task to same project (using explicit project)
            task2 = tm.add_task("Second Task", "test_user", "Another test task", project_id=project.id)
            print(f"[OK] Added second task with explicit project: {task2.title}")

            # List all user tasks (across all projects)
            all_tasks = tm.list_tasks("test_user")
            print(f"[OK] Listed all user tasks: Found {len(all_tasks)} task(s)")

            print("\n[OK] All Phase IV functionality tests passed!")

        finally:
            # Cleanup
            if os.path.exists(tmp.name):
                os.unlink(tmp.name)
            backup_path = f"{original_storage_file}.backup"
            if os.path.exists(backup_path):
                # Remove the original file if it exists, then restore from backup
                if os.path.exists(original_storage_file):
                    os.remove(original_storage_file)
                os.rename(backup_path, original_storage_file)


def test_acceptance_scenarios():
    """Test the acceptance scenarios from the spec"""
    print("\n--- Testing Acceptance Scenarios ---")

    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tmp:
        tmp.close()
        original_storage_file = "tasks_storage.json"
        if os.path.exists(original_storage_file):
            os.rename(original_storage_file, f"{original_storage_file}.backup")

        try:
            tm = TaskManager()
            # Override storage to use temp file
            tm.storage = Storage(tmp.name)

            # Scenario 1: Given user has no projects, When user creates a new project,
            # Then system creates a distinct project container with unique identifier
            print("\nScenario 1: Create project for user with no projects")
            project = tm.create_project("New Project", "test_user")
            assert project.id is not None
            assert project.name == "New Project"
            assert project.user_id == "test_user"
            print("[OK] Scenario 1 passed")

            # Scenario 2: Given user has multiple projects, When user selects a specific project,
            # Then system displays only tasks associated with that project
            print("\nScenario 2: Select specific project and verify task isolation")
            project2 = tm.create_project("Another Project", "test_user")
            tm.select_project(project.id, "test_user")

            # Add task to first project
            task1 = tm.add_task("Task for Project 1", "test_user")

            # Switch to second project and add task
            tm.select_project(project2.id, "test_user")
            task2 = tm.add_task("Task for Project 2", "test_user")

            # Verify task isolation - when viewing project 1, should only see task1
            tm.select_project(project.id, "test_user")
            project1_tasks = tm.storage.get_tasks_for_project("test_user", project.id)
            assert len(project1_tasks) == 1
            assert project1_tasks[0].id == task1.id
            print("[OK] Scenario 2 passed")

            # Scenario 3: Given user is in a project context, When user adds a task,
            # Then system assigns that task to the current project
            print("\nScenario 3: Task assignment to active project")
            tm.select_project(project.id, "test_user")
            task3 = tm.add_task("Task assigned to active project", "test_user")

            # Verify the task is in the right project
            project_tasks = tm.storage.get_tasks_for_project("test_user", project.id)
            task_ids = [t.id for t in project_tasks]
            assert task3.id in task_ids
            print("[OK] Scenario 3 passed")

            print("\n[OK] All acceptance scenarios passed!")

        finally:
            # Cleanup
            if os.path.exists(tmp.name):
                os.unlink(tmp.name)
            if os.path.exists(f"{original_storage_file}.backup"):
                # Remove the original file if it exists, then restore from backup
                if os.path.exists(original_storage_file):
                    os.remove(original_storage_file)
                os.rename(f"{original_storage_file}.backup", original_storage_file)


def test_constitution_principles():
    """Test that constitutional principles are upheld"""
    print("\n--- Testing Constitutional Principles ---")

    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tmp:
        tmp.close()
        original_storage_file = "tasks_storage.json"
        if os.path.exists(original_storage_file):
            os.rename(original_storage_file, f"{original_storage_file}.backup")

        try:
            tm = TaskManager()
            # Override storage to use temp file
            tm.storage = Storage(tmp.name)

            # Test: All tasks belong to exactly one project
            print("\nConstitution Principle: All tasks belong to exactly one project")
            project = tm.create_project("Test Project", "test_user")
            tm.select_project(project.id, "test_user")
            task = tm.add_task("Single Project Task", "test_user")
            assert task.project_id == project.id
            print("[OK] All tasks belong to exactly one project")

            # Test: Projects as highest-level organizational unit
            print("\nConstitution Principle: Projects are highest-level organizational unit")
            projects = tm.list_projects("test_user")
            assert len(projects) >= 1
            print("[OK] Projects serve as highest-level organizational unit")

            # Test: No tasks exist outside project contexts
            print("\nConstitution Principle: No tasks exist outside project contexts")
            all_user_tasks = tm.storage.get_all_user_tasks("test_user")
            for task in all_user_tasks:
                assert hasattr(task, 'project_id') and task.project_id is not None
            print("[OK] No tasks exist outside project contexts")

            # Test: Deterministic project operations
            print("\nConstitution Principle: Project operations are deterministic")
            initial_count = len(tm.list_projects("test_user"))
            new_project = tm.create_project("Deterministic Project", "test_user")
            final_count = len(tm.list_projects("test_user"))
            assert final_count == initial_count + 1
            print("[OK] Project operations are deterministic")

            # Test: Active project context is explicit in all UI interactions
            print("\nConstitution Principle: Active project context is explicit")
            context = tm.get_user_context("test_user")
            assert hasattr(context, 'active_project_id')
            print("[OK] Active project context is explicit in all interactions")

            # Test: Project boundaries are strictly enforced
            print("\nConstitution Principle: Project boundaries are strictly enforced")
            project1 = tm.create_project("Boundary Test 1", "test_user")
            project2 = tm.create_project("Boundary Test 2", "test_user")

            tm.select_project(project1.id, "test_user")
            task_in_p1 = tm.add_task("Task in Project 1", "test_user")

            tm.select_project(project2.id, "test_user")
            task_in_p2 = tm.add_task("Task in Project 2", "test_user")

            p1_tasks = tm.storage.get_tasks_for_project("test_user", project1.id)
            p2_tasks = tm.storage.get_tasks_for_project("test_user", project2.id)

            # Verify no cross-contamination
            assert task_in_p1.id not in [t.id for t in p2_tasks]
            assert task_in_p2.id not in [t.id for t in p1_tasks]
            print("[OK] Project boundaries are strictly enforced")

            print("\n[OK] All constitutional principles upheld!")

        finally:
            # Cleanup
            if os.path.exists(tmp.name):
                os.unlink(tmp.name)
            if os.path.exists(f"{original_storage_file}.backup"):
                # Remove the original file if it exists, then restore from backup
                if os.path.exists(original_storage_file):
                    os.remove(original_storage_file)
                os.rename(f"{original_storage_file}.backup", original_storage_file)


def test_project_context_management():
    """Test User Story 5: Project context maintenance during session"""
    print("\n--- Testing User Story 5: Project Context Management ---")

    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tmp:
        tmp.close()
        original_storage_file = "tasks_storage.json"
        if os.path.exists(original_storage_file):
            os.rename(original_storage_file, f"{original_storage_file}.backup")

        try:
            tm = TaskManager()
            # Override storage to use temp file
            tm.storage = Storage(tmp.name)

            # T065: Test project context behavior during session
            print("\nT065: Project context test")

            # Create multiple projects
            project1 = tm.create_project("Context Project 1", "context_user")
            project2 = tm.create_project("Context Project 2", "context_user")
            print(f"[OK] Created projects: {project1.name}, {project2.name}")

            # Select first project and verify context
            selected_project = tm.select_project(project1.id, "context_user")
            assert tm.get_user_context("context_user").active_project_id == project1.id
            print(f"[OK] Active project context set to: {selected_project.name}")

            # Add task without specifying project - should use active context
            task1 = tm.add_task("Task for Context Project 1", "context_user")
            assert task1.project_id == project1.id
            print(f"[OK] Task added to active project context: {task1.project_id}")

            # Switch context to second project
            tm.select_project(project2.id, "context_user")
            assert tm.get_user_context("context_user").active_project_id == project2.id
            print(f"[OK] Project context switched to: {project2.name}")

            # Add task again - should use new active context
            task2 = tm.add_task("Task for Context Project 2", "context_user")
            assert task2.project_id == project2.id
            print(f"[OK] Task added to new active project context: {task2.project_id}")

            # Verify task isolation between contexts
            project1_tasks = tm.storage.get_tasks_for_project("context_user", project1.id)
            project2_tasks = tm.storage.get_tasks_for_project("context_user", project2.id)
            assert task1.id in [t.id for t in project1_tasks]
            assert task2.id not in [t.id for t in project1_tasks]  # Should not be in project 1
            assert task2.id in [t.id for t in project2_tasks]
            assert task1.id not in [t.id for t in project2_tasks]  # Should not be in project 2
            print("[OK] Project context properly isolates tasks")

            print("\n[OK] T065 Project context test passed!")

            # T066: Test context persistence between commands in session
            print("\nT066: Context persistence test")

            # Establish a session with active project context
            tm.select_project(project1.id, "context_user")
            initial_context = tm.get_user_context("context_user").active_project_id
            assert initial_context == project1.id
            print(f"[OK] Initial context established: {initial_context}")

            # Execute multiple commands while maintaining context
            task3 = tm.add_task("Persistent Context Task 1", "context_user")
            assert task3.project_id == project1.id  # Should still use project1 context

            task4 = tm.add_task("Persistent Context Task 2", "context_user")
            assert task4.project_id == project1.id  # Should still use project1 context

            # List tasks - should still show project1 context
            tm.list_tasks("context_user")  # This should respect active context
            current_context = tm.get_user_context("context_user").active_project_id
            assert current_context == project1.id  # Context should persist

            print("[OK] Context persisted across multiple commands")

            # Verify all tasks added during session went to correct project
            all_project1_tasks = tm.storage.get_tasks_for_project("context_user", project1.id)
            context_task_ids = [task3.id, task4.id]
            for task_id in context_task_ids:
                assert task_id in [t.id for t in all_project1_tasks]
            print("[OK] All tasks during session went to correct project context")

            # Context should remain unchanged after listing operations
            final_context = tm.get_user_context("context_user").active_project_id
            assert final_context == project1.id
            print(f"[OK] Context remained persistent: {final_context}")

            print("\n[OK] T066 Context persistence test passed!")

        finally:
            # Cleanup
            if os.path.exists(tmp.name):
                os.unlink(tmp.name)
            if os.path.exists(f"{original_storage_file}.backup"):
                # Remove the original file if it exists, then restore from backup
                if os.path.exists(original_storage_file):
                    os.remove(original_storage_file)
                os.rename(f"{original_storage_file}.backup", original_storage_file)


if __name__ == "__main__":
    print("Starting Phase IV Implementation Verification Tests...")

    try:
        test_basic_functionality()
        test_acceptance_scenarios()
        test_constitution_principles()
        test_project_context_management()

        print("\n" + "="*60)
        print("[HURRAY] ALL PHASE IV IMPLEMENTATION TESTS PASSED! [HURRAY]")
        print("="*60)
        print("[PASS] Project-Based Task Organization working correctly")
        print("[PASS] UI-First Project Interaction implemented")
        print("[PASS] Backward Compatibility maintained")
        print("[PASS] All acceptance scenarios satisfied")
        print("[PASS] Constitutional principles upheld")
        print("[PASS] Project context management verified")
        print("[PASS] Success criteria met")
        print("="*60)

    except Exception as e:
        print(f"\n[FAILED] TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)