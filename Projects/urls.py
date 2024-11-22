from django.urls import path
from . import views


app_name = 'projects'

urlpatterns = [
    path('create-list-project/', views.ProjectListCreateView.as_view(), name='create_list_project'),
    path('update-delete-project/<int:pk>/', views.ProjectUpdateDeleteView.as_view(), name='update_delete_project'),
    path('<int:project_id>/create-list-task/', views.TaskListCreateView.as_view(), name='create_list_task'),
    path('update-delete-task/<int:pk>/', views.TaskUpdateDeleteView.as_view(), name='update_delete_task'),
]