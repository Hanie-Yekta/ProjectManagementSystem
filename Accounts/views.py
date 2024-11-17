from django.shortcuts import render
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework import permissions
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.urls import reverse

from . import serializers
from .models import CustomUser
from django.conf import settings


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


class UserPasswordResetView(generics.GenericAPIView):
    """
    This view handles user password reset request
    """

    serializer_class = serializers.UserPasswordResetSerializer

    def post(self, request):
        """
        this method gets the user's email and passes it to serializer
        if the data is valid, retrieve user from database and create token and uid for it.
        create an url and send it via email that user can set new password.
        """

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        user = CustomUser.objects.get(email=email)

        if user:
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_url = request.build_absolute_uri(
                reverse(viewname='accounts:password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
            )
            send_mail(subject='Password Reset Request of Project Manager',
                      message=f'Click the link below to reset your password: {reset_url}',
                      from_email=f'{settings.DEFAULT_FROM_EMAIL}',
                      recipient_list=[user.email],
                      fail_silently=False, )
        return Response(data={'detail': 'Password reset link has been sent'}, status=status.HTTP_200_OK)



class UserPasswordResetConfirmView(generics.GenericAPIView):
    """
    This view handles the confirmation step for user password reset.
    """

    serializer_class = serializers.UserPasswordResetConfirmSerializer

    def post(self, request, uidb64=None, token=None, *args, **kwargs):
        """
        gets uid and token from url and retrieve user from database with it.
        if token provided for user, passes data to the serializer and update the password in database.
        """

        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = CustomUser.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            user = None
        if user and default_token_generator.check_token(user, token):
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(user)
            return Response({"detail": 'Password have been reset with new password'})
        else:
            return Response({"detail": 'Password have been reset'})