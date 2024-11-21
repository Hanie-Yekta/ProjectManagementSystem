from django.contrib import admin
from .models import Project
import admin_thumbnails


@admin_thumbnails.thumbnail('image')
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'CEO', 'image_thumbnail', 'status', 'budget')
    search_fields = ('title', 'CEO', 'category')
    list_filter = ('status',)

admin.site.register(Project, ProjectAdmin)

