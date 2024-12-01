from rest_framework import permissions
from django.shortcuts import get_object_or_404
from Projects.models import Project, Task


class CanUpdateDeleteProject(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.ceo == request.user


class CanCreateSeeTask(permissions.BasePermission):
    def has_permission(self, request, view):
        project = get_object_or_404(Project, pk=view.kwargs['project_id'])
        return request.user == project.ceo


class CanUpdateDeleteTask(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method == "DELETE":
            return obj.project.ceo == request.user
        else:
            return request.user == obj.project.ceo or request.user == obj.manager


class CanCreateSeeSubTask(permissions.BasePermission):
    def has_permission(self, request, view):
        task = get_object_or_404(Task, pk=view.kwargs['task_id'])
        return request.user == task.project.ceo or request.user == task.manager


class CanUpdateDeleteSubTask(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method == "DELETE":
            return obj.task.project.ceo == request.user or request.user == obj.task.manager
        else:
            print(request.user)
            return request.user == obj.task.project.ceo or request.user == obj.task.manager or request.user == obj.manager
