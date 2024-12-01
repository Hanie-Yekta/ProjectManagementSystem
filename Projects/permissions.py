from rest_framework import permissions
from django.shortcuts import get_object_or_404
from Projects.models import Project, Task


class CanUpdateDeleteProject(permissions.BasePermission):
    """
    custom permission to allow only the project CEO to update or delete the project.
    if method -> GET: project CEO, experts
                other: project CEO
    """
    def has_object_permission(self, request, view, obj):
        if request.method == "GET":
            experts = obj.experts.filter(id=request.user.id)
            return obj.ceo == request.user or experts.exists()
        else:
            return obj.ceo == request.user


class CanCreateSeeTask(permissions.BasePermission):
    """
    custom permission to allow the project CEO to create or view tasks within the project.
    by project id that fetched from url, access the project CEO
    method -> GET, POST: project CEO
    """
    def has_permission(self, request, view):
        project = get_object_or_404(Project, pk=view.kwargs['project_id'])
        return request.user == project.ceo


class CanUpdateDeleteTask(permissions.BasePermission):
    """
    custom permission to update or delete the task.
    if method -> GET: project CEO, experts, task manager
                 DELETE: project CEO
                 other: project CEO, task manager
    """
    def has_object_permission(self, request, view, obj):
        if request.method == "DELETE":
            return obj.project.ceo == request.user

        elif request.method == "GET":
            experts = obj.experts.filter(id=request.user.id)
            return request.user == obj.project.ceo or request.user == obj.manager or experts.exists()

        else:
            return request.user == obj.project.ceo or request.user == obj.manager


class CanCreateSeeSubTask(permissions.BasePermission):
    """
    custom permission to create or view subtasks within the task.
    by task id that fetched from url, access the task manager and project CEO
    method -> GET, POST: task manager, project CEO
    """
    def has_permission(self, request, view):
        task = get_object_or_404(Task, pk=view.kwargs['task_id'])
        return request.user == task.project.ceo or request.user == task.manager


class CanUpdateDeleteSubTask(permissions.BasePermission):
    """
    custom permission to update or delete the subtask.
    if method -> GET: project CEO, experts, task manager
                 DELETE: project CEO, task manager
                 other: project CEO, task manager, subtask manager
    """
    def has_object_permission(self, request, view, obj):
        if request.method == "DELETE":
            return obj.task.project.ceo == request.user or request.user == obj.task.manager
        elif request.method == "GET":
            experts = obj.experts.filter(id=request.user.id)
            return request.user == obj.task.project.ceo or request.user == obj.task.manager or request.user == obj.manager or experts.exists()
        else:
            return request.user == obj.task.project.ceo or request.user == obj.task.manager or request.user == obj.manager
