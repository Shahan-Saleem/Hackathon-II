#!/usr/bin/env python3
"""
Setup script for the Project-Based Task Management Application
Creates necessary directories and initializes the application
"""

import os
import sys
from pathlib import Path

def create_directory_structure():
    """Create the required directory structure"""
    directories = [
        "data",  # For storing application data
        "logs",  # For logging
        "docs",  # For documentation
        "tests",  # For test files
    ]

    for directory in directories:
        path = Path(directory)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            print(f"Created directory: {path.absolute()}")

def create_config_files():
    """Create configuration files"""
    config_content = '''{
    "storage": {
        "file": "tasks_storage.json",
        "backup_enabled": true,
        "backup_location": "data/backups/"
    },
    "security": {
        "password_min_length": 6,
        "session_timeout_minutes": 30
    },
    "ui": {
        "theme": "default",
        "color_scheme": "standard"
    }
}'''

    config_path = Path("config.json")
    if not config_path.exists():
        with open(config_path, 'w') as f:
            f.write(config_content)
        print(f"Created config file: {config_path.absolute()}")

def create_readme():
    """Create a README file"""
    readme_content = '''# Project-Based Task Management Application

This is a complete, runnable task management application implementing Phases 1-5 of the specification.

## Features

- **Phase 1**: Core task logic
- **Phase 2**: UI-first console interaction
- **Phase 3**: Persistent storage
- **Phase 4**: Project-based isolation
- **Phase 5**: Determinism & enforcement

## Authentication

- User registration and login
- Session-based user flow
- Isolated projects and tasks per user

## Project Structure

- Users -> Projects -> Tasks hierarchy
- Task IDs are unique per project
- Persistent file-based storage
- Deterministic behavior
- No cross-project or cross-user access

## Getting Started

1. Run the application: `python main.py`
2. Sign up for a new account or sign in
3. Create a project
4. Add tasks to your project
5. Manage your tasks

## Running from Command Line

You can also use the CLI directly:
- `python app.py auth signup --username myuser --password mypass`
- `python app.py project create --name "My Project" --user <user_id>`
- `python app.py add --title "My Task" --user <user_id>`

## Files

- `main.py`: Main entry point
- `app.py`: Core application logic
- `ui.py`: Console UI implementation
- `tasks_storage.json`: Default storage file
- `config.json`: Configuration file

## Quality

- Python 3.x compatible
- Clean modular code
- Docstrings on all public functions
- Error handling
'''

    readme_path = Path("README.md")
    with open(readme_path, 'w') as f:
        f.write(readme_content)
    print(f"Created README: {readme_path.absolute()}")

def create_requirements():
    """Create requirements file"""
    requirements_content = '''# No external dependencies required
# This application uses only Python standard library
'''

    req_path = Path("requirements.txt")
    with open(req_path, 'w') as f:
        f.write(requirements_content)
    print(f"Created requirements file: {req_path.absolute()}")

def create_gitignore():
    """Create .gitignore file"""
    gitignore_content = '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
logs/

# Data
data/
*.json
*.db

# Backup files
*~
'''

    gitignore_path = Path(".gitignore")
    with open(gitignore_path, 'w') as f:
        f.write(gitignore_content)
    print(f"Created .gitignore: {gitignore_path.absolute()}")

def main():
    """Main setup function"""
    print("Setting up Project-Based Task Management Application...")

    try:
        create_directory_structure()
        create_config_files()
        create_readme()
        create_requirements()
        create_gitignore()

        print("")
        print("Setup complete!")
        print("")
        print("To run the application:")
        print("  python main.py")
        print("")
        print("Or use the CLI directly:")
        print("  python app.py --help")

    except Exception as e:
        print(f"Setup failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()