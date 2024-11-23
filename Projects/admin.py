from django.contrib import admin
from .models import Project, Task, SubTask
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
    search_fields = ('title', 'manager', 'category', 'project__title')
    list_filter = ('status',)

admin.site.register(Task, TaskAdmin)


@admin_thumbnails.thumbnail('image')
class SubTaskAdmin(admin.ModelAdmin):
    """
    manage subtask instances in admin panel.
    Provides additional display, filtering, and searching options
    search by -> title, manager, category
    filter by -> status
    """

    list_display = ('title', 'manager', 'task__project__ceo', 'task__title', 'task__project__title', 'image_thumbnail', 'status', 'budget')
    search_fields = ('title', 'manager', 'category', 'task__title')
    list_filter = ('status',)

admin.site.register(SubTask, SubTaskAdmin)