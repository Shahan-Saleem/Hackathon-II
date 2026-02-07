document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const navLinks = document.querySelectorAll('.nav-link');
    const views = document.querySelectorAll('.view');
    const signoutBtn = document.getElementById('signout-btn');
    const usernameDisplay = document.getElementById('username-display');
    const messageDiv = document.getElementById('message');
    const projectSelect = document.getElementById('project-select');
    const taskProjectSelect = document.getElementById('task-project');
    const createProjectBtn = document.getElementById('create-project-btn');
    const createTaskBtn = document.getElementById('create-task-btn');
    const createProjectModal = document.getElementById('create-project-modal');
    const createTaskModal = document.getElementById('create-task-modal');
    const closeModals = document.querySelectorAll('.close');
    const createProjectForm = document.getElementById('create-project-form');
    const createTaskForm = document.getElementById('create-task-form');

    // Current user data
    let currentUser = null;
    let currentView = 'dashboard';

    // Initialize the app
    initializeApp();

    async function initializeApp() {
        try {
            // Check if user is authenticated
            const response = await fetch('/api/auth/me');
            const data = await response.json();

            if (!response.ok) {
                // Redirect to login if not authenticated
                window.location.href = '/';
                return;
            }

            currentUser = data.user;
            usernameDisplay.textContent = currentUser.username;

            // Load initial data
            loadDashboardData();
            loadProjects();

            // Set up event listeners
            setupEventListeners();
        } catch (error) {
            showMessage('Failed to load user data', 'error');
            window.location.href = '/';
        }
    }

    function setupEventListeners() {
        // Navigation
        navLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                const viewId = this.id.replace('-link', '-view');
                switchView(viewId);
            });
        });

        // Sign out
        signoutBtn.addEventListener('click', signOut);

        // Modals
        createProjectBtn.addEventListener('click', () => showModal(createProjectModal));
        createTaskBtn.addEventListener('click', () => showModal(createTaskModal));

        closeModals.forEach(close => {
            close.addEventListener('click', () => hideModal(close.closest('.modal')));
        });

        // Close modal when clicking outside
        window.addEventListener('click', function(e) {
            if (e.target.classList.contains('modal')) {
                hideModal(e.target);
            }
        });

        // Form submissions
        createProjectForm.addEventListener('submit', createProject);
        createTaskForm.addEventListener('submit', createTask);

        // Project selection
        projectSelect.addEventListener('change', loadTasks);
    }

    function switchView(viewId) {
        // Hide all views
        views.forEach(view => view.classList.remove('active'));

        // Remove active class from all nav links
        navLinks.forEach(link => link.classList.remove('active'));

        // Show selected view
        document.getElementById(viewId).classList.add('active');

        // Activate corresponding nav link
        document.getElementById(viewId.replace('-view', '-link')).classList.add('active');

        currentView = viewId.replace('-view', '');

        // Load data for the view
        if (viewId === 'dashboard-view') {
            loadDashboardData();
        } else if (viewId === 'projects-view') {
            loadProjects();
        } else if (viewId === 'tasks-view') {
            loadProjectsForTaskForm();
            loadTasks();
        }
    }

    async function loadDashboardData() {
        try {
            const projectsResponse = await fetch('/api/projects');
            const projectsData = await projectsResponse.json();

            if (projectsResponse.ok) {
                document.getElementById('total-projects').textContent = projectsData.projects.length;

                // Count total and completed tasks
                let totalTasks = 0;
                let completedTasks = 0;

                for (const project of projectsData.projects) {
                    const tasksResponse = await fetch(`/api/tasks?project_id=${project.id}`);
                    const tasksData = await tasksResponse.json();

                    if (tasksResponse.ok) {
                        totalTasks += tasksData.tasks.length;
                        completedTasks += tasksData.tasks.filter(task => task.completed).length;
                    }
                }

                document.getElementById('total-tasks').textContent = totalTasks;
                document.getElementById('completed-tasks').textContent = completedTasks;
            }

            // Load recent activities
            loadRecentActivities();
        } catch (error) {
            showMessage('Failed to load dashboard data', 'error');
        }
    }

    async function loadRecentActivities() {
        try {
            const response = await fetch('/api/recent-activities');
            const data = await response.json();

            if (response.ok) {
                const activitiesList = document.getElementById('recent-activity-list');
                activitiesList.innerHTML = '';

                if (data.activities.length === 0) {
                    activitiesList.innerHTML = '<p>No recent activities.</p>';
                    return;
                }

                data.activities.forEach(activity => {
                    const activityElement = createActivityElement(activity);
                    activitiesList.appendChild(activityElement);
                });
            } else {
                console.error('Failed to load recent activities:', data.error);
            }
        } catch (error) {
            console.error('Error loading recent activities:', error);
        }
    }

    function createActivityElement(activity) {
        const div = document.createElement('div');
        div.className = 'activity-item';

        // Format the timestamp
        const date = new Date(activity.timestamp);
        const formattedDate = date.toLocaleString();

        div.innerHTML = `
            <div class="activity-content">
                <p>${activity.description}</p>
                <small class="activity-timestamp">${formattedDate}</small>
            </div>
        `;
        return div;
    }

    async function loadProjects() {
        try {
            const response = await fetch('/api/projects');
            const data = await response.json();

            if (response.ok) {
                const projectsList = document.getElementById('projects-list');
                projectsList.innerHTML = '';

                if (data.projects.length === 0) {
                    projectsList.innerHTML = '<p>No projects found. Create your first project!</p>';
                    return;
                }

                data.projects.forEach(project => {
                    const projectCard = createProjectCard(project);
                    projectsList.appendChild(projectCard);
                });
            } else {
                showMessage(data.error || 'Failed to load projects', 'error');
            }
        } catch (error) {
            showMessage('Failed to load projects', 'error');
        }
    }

    function createProjectCard(project) {
        const div = document.createElement('div');
        div.className = 'project-card';
        div.innerHTML = `
            <h3>${project.name}</h3>
            <p>Created: ${new Date(project.created_at).toLocaleDateString()}</p>
            <div class="project-actions">
                <button class="btn btn-primary" onclick="selectProject('${project.id}')">Select</button>
                <button class="btn btn-secondary" onclick="loadProjectTasks('${project.id}')">View Tasks</button>
            </div>
        `;
        return div;
    }

    async function loadProjectsForTaskForm() {
        try {
            const response = await fetch('/api/projects');
            const data = await response.json();

            if (response.ok) {
                // Clear existing options except the first one
                while (taskProjectSelect.children.length > 1) {
                    taskProjectSelect.removeChild(taskProjectSelect.lastChild);
                }

                // Add projects to the select dropdown
                data.projects.forEach(project => {
                    const option = document.createElement('option');
                    option.value = project.id;
                    option.textContent = project.name;
                    taskProjectSelect.appendChild(option);
                });

                // Also populate the main project select
                while (projectSelect.children.length > 1) {
                    projectSelect.removeChild(projectSelect.lastChild);
                }

                data.projects.forEach(project => {
                    const option = document.createElement('option');
                    option.value = project.id;
                    option.textContent = project.name;
                    projectSelect.appendChild(option);
                });
            }
        } catch (error) {
            showMessage('Failed to load projects for task form', 'error');
        }
    }

    async function loadTasks() {
        try {
            const projectId = projectSelect.value;

            let response;
            let data;

            if (projectId) {
                // Use the project-specific endpoint
                response = await fetch(`/api/projects/${projectId}/tasks`);
                data = await response.json();
            } else {
                // Load all tasks for the user
                response = await fetch('/api/tasks');
                data = await response.json();
            }

            if (response.ok) {
                const tasksList = document.getElementById('tasks-list');
                tasksList.innerHTML = '';

                if (data.tasks.length === 0) {
                    tasksList.innerHTML = '<p>No tasks found. Add your first task!</p>';
                    return;
                }

                data.tasks.forEach(task => {
                    const taskItem = createTaskItem(task);
                    tasksList.appendChild(taskItem);
                });
            } else {
                showMessage(data.error || 'Failed to load tasks', 'error');
            }
        } catch (error) {
            showMessage('Failed to load tasks', 'error');
        }
    }

    function createTaskItem(task) {
        const div = document.createElement('div');
        div.className = 'task-item';
        div.innerHTML = `
            <div class="task-info">
                <div class="task-title">${task.title}</div>
                <div class="task-description">${task.description || ''}</div>
                <div class="task-meta">
                    <span class="task-status ${task.completed ? 'status-completed' : 'status-pending'}">
                        ${task.completed ? 'Completed' : 'Pending'}
                    </span>
                    | Created: ${new Date(task.created_at).toLocaleDateString()}
                </div>
            </div>
            <div class="task-actions">
                <input type="checkbox" class="task-checkbox" ${task.completed ? 'checked' : ''} onchange="toggleTaskCompletion(${task.id}, this.checked)">
                <button class="btn btn-warning" onclick="editTask(${task.id})">Edit</button>
                <button class="btn btn-danger" onclick="deleteTask(${task.id})">Delete</button>
            </div>
        `;
        return div;
    }

    async function createProject(e) {
        e.preventDefault();
        const formData = new FormData(createProjectForm);
        const projectName = formData.get('name');

        try {
            showLoading(true);
            const response = await fetch('/api/projects', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ name: projectName })
            });

            const data = await response.json();

            if (response.ok) {
                showMessage('Project created successfully!', 'success');
                hideModal(createProjectModal);
                createProjectForm.reset();
                loadProjects();

                // Also reload projects in task form
                loadProjectsForTaskForm();
            } else {
                showMessage(data.error || 'Failed to create project', 'error');
            }
        } catch (error) {
            showMessage('Network error. Please try again.', 'error');
        } finally {
            showLoading(false);
        }
    }

    async function createTask(e) {
        e.preventDefault();
        const formData = new FormData(createTaskForm);
        const taskData = {
            title: formData.get('title'),
            description: formData.get('description'),
            project_id: formData.get('project_id')
        };

        try {
            showLoading(true);

            // Use the project-specific endpoint if a project is selected
            let url = '/api/tasks';
            if (taskData.project_id) {
                url = `/api/projects/${taskData.project_id}/tasks`;
            }

            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(taskData)
            });

            const data = await response.json();

            if (response.ok) {
                showMessage('Task created successfully!', 'success');
                hideModal(createTaskModal);
                createTaskForm.reset();

                // Reload tasks if on tasks view
                if (currentView === 'tasks') {
                    loadTasks();
                }

                // Also reload dashboard if on dashboard view to update stats
                if (currentView === 'dashboard') {
                    loadDashboardData();
                }
            } else {
                showMessage(data.error || 'Failed to create task', 'error');
            }
        } catch (error) {
            showMessage('Network error. Please try again.', 'error');
        } finally {
            showLoading(false);
        }
    }

    async function toggleTaskCompletion(taskId, completed) {
        try {
            // We need to get the task first to determine which project it belongs to
            const tasksResponse = await fetch('/api/tasks');
            const tasksData = await tasksResponse.json();

            if (!tasksResponse.ok) {
                showMessage('Failed to get task details', 'error');
                return;
            }

            // Find the task to get its project ID
            let projectOfTask = null;
            for (const task of tasksData.tasks) {
                if (task.id === taskId) {
                    projectOfTask = task.project_id;
                    break;
                }
            }

            if (!projectOfTask) {
                showMessage('Task not found', 'error');
                return;
            }

            const response = await fetch(`/api/projects/${projectOfTask}/tasks/${taskId}/toggle`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            const data = await response.json();

            if (response.ok) {
                showMessage(`Task ${completed ? 'completed' : 'reopened'} successfully!`, 'success');

                // Reload tasks if on tasks view
                if (currentView === 'tasks') {
                    loadTasks();
                }

                // Reload dashboard if on dashboard
                if (currentView === 'dashboard') {
                    loadDashboardData();
                }
            } else {
                showMessage(data.error || 'Failed to update task', 'error');
            }
        } catch (error) {
            showMessage('Network error. Please try again.', 'error');
        }
    }

    async function deleteTask(taskId) {
        if (!confirm('Are you sure you want to delete this task?')) {
            return;
        }

        try {
            // Get all tasks to find which project this task belongs to
            const tasksResponse = await fetch('/api/tasks');
            const tasksData = await tasksResponse.json();

            if (!tasksResponse.ok) {
                showMessage('Failed to get task details', 'error');
                return;
            }

            // Find the task to get its project ID
            let projectOfTask = null;
            for (const task of tasksData.tasks) {
                if (task.id === taskId) {
                    projectOfTask = task.project_id;
                    break;
                }
            }

            if (!projectOfTask) {
                showMessage('Task not found', 'error');
                return;
            }

            const response = await fetch(`/api/tasks/${taskId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            const data = await response.json();

            if (response.ok) {
                showMessage('Task deleted successfully!', 'success');

                // Reload tasks if on tasks view
                if (currentView === 'tasks') {
                    loadTasks();
                }

                // Reload dashboard if on dashboard
                if (currentView === 'dashboard') {
                    loadDashboardData();
                }
            } else {
                showMessage(data.error || 'Failed to delete task', 'error');
            }
        } catch (error) {
            showMessage('Network error. Please try again.', 'error');
        }
    }

    async function selectProject(projectId) {
        try {
            const response = await fetch(`/api/projects/${projectId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            const data = await response.json();

            if (response.ok) {
                showMessage('Project selected successfully!', 'success');

                // Update the project selector
                projectSelect.value = projectId;

                // If we're on the tasks view, load the tasks for this project
                if (currentView === 'tasks') {
                    loadTasks();
                }
            } else {
                showMessage(data.error || 'Failed to select project', 'error');
            }
        } catch (error) {
            showMessage('Network error. Please try again.', 'error');
        }
    }

    function loadProjectTasks(projectId) {
        projectSelect.value = projectId;
        switchView('tasks-view');
    }

    async function signOut() {
        try {
            await fetch('/api/auth/signout', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            window.location.href = '/';
        } catch (error) {
            showMessage('Failed to sign out. Redirecting anyway...', 'info');
            window.location.href = '/';
        }
    }

    function showModal(modal) {
        modal.classList.remove('hidden');
    }

    function hideModal(modal) {
        modal.classList.add('hidden');
    }

    function showMessage(text, type) {
        messageDiv.textContent = text;
        messageDiv.className = `message ${type}`;
        messageDiv.classList.remove('hidden');

        setTimeout(() => {
            messageDiv.classList.add('hidden');
        }, 5000);
    }

    function showLoading(show) {
        const buttons = document.querySelectorAll('button[type="submit"]');
        buttons.forEach(button => {
            if (show) {
                button.disabled = true;
            } else {
                button.disabled = false;
            }
        });
    }

    // Expose functions to global scope for inline event handlers
    window.selectProject = selectProject;
    window.loadProjectTasks = loadProjectTasks;
    window.toggleTaskCompletion = toggleTaskCompletion;
    window.deleteTask = deleteTask;
    window.editTask = function(taskId) {
        showMessage('Edit functionality would be implemented here', 'info');
    };
});