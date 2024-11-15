from rest_framework import serializers
from .models import CustomUser
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.tokens import RefreshToken


def clean_email(value):
    """
    check if the email is unique, if it's not(already exists in the database, raise an error)
    """

    if CustomUser.objects.filter(email=value).exists():
        raise serializers.ValidationError({'Error': 'Email already exists. try another one!'})


def clean_phone_number(value):
    """
    check if the phone number is 11 digits and unique, if it's not(already exists in the database, raise an error)
    """

    if len(value) < 11:
        raise serializers.ValidationError('Phone number must be 11 digits')

    if CustomUser.objects.filter(phone_number=value).exists():
        raise serializers.ValidationError({'Error': 'Phone number already exists. try another one!'})


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




class UserLogoutSerializer(serializers.Serializer):
    """
    serializes data for logging out a user.
    includes validation for refresh token.
    """

    refresh = serializers.CharField(required=True)

    def validate(self, attrs):
        """
        override this method to validates and blacklists the refresh token.
        """

        try:
            token = RefreshToken(attrs.get('refresh'))
            token.blacklist()
        except Exception as e:
            raise serializers.ValidationError({'Error': "Invalid token or token already blacklisted"})

        return attrs



class UserProfileDetailSerializer(serializers.ModelSerializer):
    """
    serializes data for viewing and updating user information.
    phone number and email cannot be changed by user.
    """

    class Meta:
        model = CustomUser
        fields = ('id', 'first_name', 'last_name', 'phone_number', 'email', 'gender', 'image')
        extra_kwargs = {'phone_number': {'read_only': True},
                        'email': {'read_only': True}}