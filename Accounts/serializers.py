from rest_framework import serializers
from .models import CustomUser
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password


def clean_email(value):
    """
    check if the email is unique, if it's not(already exists in the database, raise an error)
    """

    if CustomUser.objects.filter(email=value).exists():
        raise serializers.ValidationError('Email already exists. try another one!')


def clean_phone_number(value):
    """
    check if the phone number is 11 digits and unique, if it's not(already exists in the database, raise an error)
    """

    if len(value) < 11:
        raise serializers.ValidationError('Phone number must be 11 digits')

    if CustomUser.objects.filter(phone_number=value).exists():
        raise serializers.ValidationError('Phone number already exists. try another one!')


class UserRegisterSerializer(serializers.ModelSerializer):
    """
    serialize data for registering a new user.
    include validation on email and phone number fields and hashes the password.
    """

    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'phone_number', 'email', 'gender', 'image', 'password')
        extra_kwargs = {'password': {'write_only': True,
                                     'validators': (validate_password,)},
                        'email': {'validators': (clean_email,)},
                        'phone_number': {'validators': (clean_phone_number,)}, }

    def create(self, validated_data):
        """
        override this method to hash the password and then create user in database.
        """

        password = validated_data.get('password')
        validated_data['password'] = make_password(password)
        return super().create(validated_data)