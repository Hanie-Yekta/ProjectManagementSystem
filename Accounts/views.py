from django.shortcuts import render
from rest_framework.generics import CreateAPIView
from . import serializers


class UserRegistrationView(CreateAPIView):
    """
    This view is used to register a new user.
    it gets the information and pass it to the serializer and
    if the data is valid, create a user in CustomUser model with them
    """

    serializer_class = serializers.UserRegisterSerializer

    def perform_create(self, serializer):
        """
        save the user instance in the database after validating data
        """

        serializer.save()
