from rest_framework import generics, permissions
from .models import Project, Task
from . import serializers

class ProjectListCreateView(generics.ListCreateAPIView):
    """
    this view is used to listing and creating projects.
    methods -> GET: for show the list of projects
               POST: for create a new project
    permission ->  Only authenticated users
    """

    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializers.ProjectSerializer

    def get_queryset(self):
        """
        return user's projects
        """

        return Project.objects.filter(ceo=self.request.user)

    def perform_create(self, serializer):
        """
        pass the user to serializer as CEO
        save project's information
        """

        serializer.is_valid(raise_exception=True)
        serializer.save(ceo=self.request.user)


class ProjectUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    """
    this view is used to update and delete a project
    methods -> PUT, PATCH: for update the information of the project
               DELETE: for delete the project
    permission ->  Only authenticated users
    """

    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializers.ProjectSerializer
    queryset = Project

    def perform_update(self, serializer):
        """
        validate and update the project data
        """

        serializer.is_valid(raise_exception=True)
        serializer.save()

    def perform_destroy(self, instance):
        """
        delete the project
        """
        instance.delete()


class TaskListCreateView(generics.ListCreateAPIView):
    """
    his view is used to listing and creating tasks.
    methods -> GET: for show the list of tasks of specific project
               POST: for create a new task for specific project
    permission ->  Only authenticated users
    """
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializers.TaskSerializer
    lookup_field = 'project_id'

    def get_queryset(self):
        """
        return user's tasks
        """
        return Task.objects.filter(project=self.kwargs['project_id'])

    def get_serializer_context(self):
        """
        sent additional data (project data) to serializer with context to validate fields properly.
        """
        context = super().get_serializer_context()
        context['project'] = Project.objects.get(id=self.kwargs['project_id'])
        return context


    def perform_create(self, serializer):
        """
        pass the project to serializer
        save task's information
        """
        serializer.is_valid(raise_exception=True)
        project = Project.objects.get(id=self.kwargs['project_id'])
        serializer.save(project=project)


class TaskUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    """
    this view is used to update and delete a task
    methods -> PUT, PATCH: for update the information of the task
               DELETE: for delete the task
    permission ->  Only authenticated users
    """

    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializers.TaskSerializer
    queryset = Task

    def perform_update(self, serializer):
        """
        validate and update the task data
        """
        serializer.is_valid(raise_exception=True)
        serializer.save()

    def perform_destroy(self, instance):
        """
        delete the task
        """
        instance.delete()



