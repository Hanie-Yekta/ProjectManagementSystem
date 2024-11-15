from django.shortcuts import render
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework import permissions

from . import serializers
from .models import CustomUser


class UserRegistrationView(generics.CreateAPIView):
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

    permission_classes = (permissions.IsAuthenticated,)

    serializer_class = serializers.UserLogoutSerializer

    def post(self, request):
        """
        this method gets the refresh token and pass it to the serializer and
        if the token is valid and successfully blacklisted, logs out the user.
        """

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(data={'detail': 'User Logged out successfully'}, status=status.HTTP_200_OK)


class UserProfileDetailUpdateView(APIView):
    """
    This view is used to view and update user information
    permission ->  Only authenticated users
    """

    permission_classes = (permissions.IsAuthenticated,)

    serializer_class = serializers.UserProfileDetailSerializer

    def get(self, request, *args, **kwargs):
        """
        this method gets the authenticated user's email and retrieve another information from database
        and passes it to serializer
        """

        user = CustomUser.objects.get(email=request.user.email)
        user_ser_data = self.serializer_class(instance=user)

        return Response(data={'user_information': user_ser_data.data}, status=status.HTTP_200_OK)


    def put(self, request, *args, **kwargs):
        """
        this method gets the authenticated user's email and retrieve another information from database
        with new changes that provided by user and passes it to serializer
        if the data is valid, save them into database and show new information.
        """

        user = CustomUser.objects.get(email=request.user.email)
        user_ser_data = self.serializer_class(instance=user, data=request.data, partial=True)

        if user_ser_data.is_valid(raise_exception=True):
            user_ser_data.save()
            return Response(data={'detail': 'user information updated!',
                                  'user_information': user_ser_data.data}, status=status.HTTP_200_OK)



