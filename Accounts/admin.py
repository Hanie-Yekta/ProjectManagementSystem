from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser
import admin_thumbnails


@admin_thumbnails.thumbnail('image')
class CustomUserAdmin(UserAdmin):
    """
    manage user instances in admin panel.
    get 2 forms for create and update user instance.
    with thumbnail show a preview for profile image.
    search by -> phone number, email
    filter by -> is staff status
    sort by -> phone number, email
    """

    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    list_display = ('first_name', 'last_name', 'phone_number', 'email', 'image_thumbnail', 'is_staff', 'is_superuser')
    list_filter = ('is_staff',)
    readonly_fields = ('created_at',)

    fieldsets = ((None, {'fields': (('first_name', 'last_name'), 'phone_number', 'email', 'image')}),
                 ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
                 ('Important dates', {'fields': ('last_login', 'created_at')}),)

    add_fieldsets = (
        (None,
         {'fields': ('first_name', 'last_name', 'email', 'phone_number', 'gender', 'image', 'password1', 'password2',
                     'is_staff', 'is_superuser')}),
    )

    search_fields = ('phone_number', 'email')
    ordering = ('phone_number', 'email')


admin.site.register(CustomUser, CustomUserAdmin)
