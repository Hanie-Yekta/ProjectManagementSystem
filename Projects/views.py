from rest_framework import generics, permissions, status
from .models import Project
from . import serializers
from rest_framework.response import Response

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





