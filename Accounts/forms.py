from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    """
    form for creating a user with fields -> first name, last name, phone number, gender, email, profile picture
    """

    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'phone_number', 'email', 'gender', 'image')


class CustomUserChangeForm(UserChangeForm):
    """
    form for updating user information with fields -> first name, last name, phone number, gender, email, profile picture,
    is active, is staff, is superuser
    """

    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'phone_number', 'email', 'gender', 'image', 'is_active', 'is_staff',
                  'is_superuser')
