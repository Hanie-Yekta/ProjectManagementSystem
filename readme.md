# Project Name
Project Management System

<br>

## Description
This is a project management system built with Django and Django REST Framework (DRF).<br>
The system helps teams organize tasks, track project progress, and work together.
features include task assignment, progress tracking, team collaboration and manage budgets and expenses.

<br>

## Features
### 1. User Management
+ Registration and Login:<br>
Users can register and log in to access their profiles.<br>
Authentication is managed using JWT tokens.


+ User Roles:<br>
Role-based access control to ensure users have access only to the features relevant to their roles.


### 2. Project and Task and Sub-task Management
+ Create Projects:<br>
Users can create multiple projects.<br>
Projects, tasks, sub-tasks include details like name, description, budget, timeline,...
Each project can have multiple tasks and each task can have multiple sub-tasks.


+ Manage Team Members:<br>
Assign team members to projects with specific roles (Manager, experts).<br>
Roles determine the level of access and permissions within the project.

  
+ Track Progress:<br>
Update the status of project and tasks and sub-tasks (In Progress, Completed, Canceled).<br>
Visualize the progress of tasks and projects against the defined timeline.


+ Define Deadlines:<br>
Assign start and end dates for projects, tasks, and sub-tasks.


### 3. Financial Management
+ Track Expenses:<br>
Log incoming and outgoing expenses to Projects, tasks, sub-tasks.<br>
View expense reports for each section.

<br>

## Team Members
+ <a href="https://github.com/Hanie-Yekta">Hanie Yekta</a>

<br>


## Technology Stack
+ Backend: Django, Django REST Framework
+ Database: Postgresql
+ Authentication: JWT

<br>

## Installation
1. **Clone the repository**:
```
git clone https://github.com/Hanie-Yekta/BootCamp_FinalProject.git
```

<br>

2. **Create a virtual environment**

<br>

3. **Install the dependencies**
```
pip install -r requirements.txt
```

<br>

4. **Apply migrations**:
```
python manage.py migrate
```

<br>

5. **Create a superuser**:
```
python manage.py createsuperuser
```

<br>

6. **Run**:
```
python manage.py runserver
```
