from rest_framework import permissions
from .models import Project, Task, SubTask


class CanSeeOrChange(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user

        if request.method in permissions.SAFE_METHODS:
            if isinstance(obj, Project):
                experts = obj.experts.all()
                if user == obj.ceo or user in experts:
                    return True
            elif isinstance(obj, Task):
                experts = obj.experts.all()
                print(experts)
                if user == obj.manager or user in experts or user == obj.project.ceo:
                    return True
            elif isinstance(obj, SubTask):
                experts = obj.experts.all()
                if user == obj.manager or user in experts or user == obj.task.project.ceo:
                    return True

        else:
            if isinstance(obj, Project):
                return user == obj.ceo

            elif isinstance(obj, Task):
                if user == obj.manager or user==obj.project.ceo:
                    return True

            elif isinstance(obj, SubTask):
                if user == obj.manager or user==obj.task.project.ceo:
                    return True

        return False

# class CanSeeTask(permissions.BasePermission):
#     def has_permission(self, request, view):
#         if request.method in permissions.SAFE_METHODS:
#             return request.user
#
#
# class CanUpdateTask(permissions.BasePermission):
#     def has_object_permission(self, request, view, obj):
#         user = request.user
#
#         if request.method in permissions.SAFE_METHODS:
#             experts = obj.experts.all()
#             print(experts)
#             if user == obj.manager or user == obj.project.ceo or user in experts:
#                 return True
#
#         elif request.method in ['POST']:
#             if user == obj.manager or user == obj.project.ceo:
#                 return True