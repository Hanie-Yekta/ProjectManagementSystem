from django.contrib import admin
from .models import Project, Task
import admin_thumbnails


@admin_thumbnails.thumbnail('image')
class ProjectAdmin(admin.ModelAdmin):
    """
    manage project instances in admin panel.
    Provides additional display, filtering, and searching options
    search by -> title, CEO, category
    filter by -> status
    """

    list_display = ('title', 'ceo', 'image_thumbnail', 'status', 'budget')
    search_fields = ('title', 'ceo', 'category')
    list_filter = ('status',)

admin.site.register(Project, ProjectAdmin)



@admin_thumbnails.thumbnail('image')
class TaskAdmin(admin.ModelAdmin):
    """
    manage task instances in admin panel.
    Provides additional display, filtering, and searching options
    search by -> title, manager, category
    filter by -> status
    """

    list_display = ('title', 'manager', 'project__ceo', 'project__title', 'image_thumbnail', 'status', 'budget')
    search_fields = ('title', 'manager', 'category')
    list_filter = ('status',)

admin.site.register(Task, TaskAdmin)