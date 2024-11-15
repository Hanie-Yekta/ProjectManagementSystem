from django.shortcuts import render
from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from . import serializers
from rest_framework.permissions import IsAuthenticated


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


class UserLogoutView(APIView):
    """
    This view is used to user logout by refresh token.
    permission ->  Only authenticated users
    """

    permission_classes = (IsAuthenticated,)

    serializer_class = serializers.UserLogoutSerializer

    def post(self, request):
        """
        this method gets the refresh token and pass it to the serializer and
        if the token is valid and successfully blacklisted, logs out the user.
        """

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'detail': 'User Logged out successfully'}, status=status.HTTP_200_OK)
