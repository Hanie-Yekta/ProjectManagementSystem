from django.contrib.auth.models import BaseUserManager


class CustomUserManager(BaseUserManager):
    """
    this class manage creation of users for Custom User model
    handles 2 types of users: normal user, superuser
    """

    def create_user(self, phone_number, email, password=None, **extra_fields):
        """
        this method create normal user instance.
        get phone number, email, password and other information
        """

        if not phone_number:
            raise ValueError('User must have phone number')

        if not email:
            raise ValueError('User must have email')

        user = self.model(phone_number=phone_number, email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, email, password=None, **extra_fields):
        """
        this method create superuser instance.
        get phone number, email, password and other information
        set permission information -> is staff status, is superuser status
        and passes them to normal user creation method
        """

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(phone_number, email, password, **extra_fields)
