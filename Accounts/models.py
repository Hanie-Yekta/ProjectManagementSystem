from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from .managers import CustomUserManager


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model stores user information of system.
    user can enter -> first name, last name, phone number, email, gender, profile image
    user identify by phone number -> must be unique
    and also has email that use for some operations -> must be unique
    """

    GENDER_OPTIONS = [
        ('female', 'Female'),
        ('male', 'Male'),
    ]
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=11, unique=True)
    email = models.EmailField(unique=True)
    gender = models.CharField(choices=GENDER_OPTIONS, max_length=6)
    image = models.ImageField(default='accounts/profile/default/default_profile_picture.jpg',
                              upload_to='accounts/profile')
    created_at = models.DateTimeField(auto_now_add=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['email']

    objects = CustomUserManager()

    def __str__(self):
        return f'{self.first_name} {self.last_name}'
