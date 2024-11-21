from django.urls import path
from . import views


app_name = 'projects'

urlpatterns = [
    path('create-list-project/', views.ProjectListCreateView.as_view(), name='create_list_project'),
    path('update-delete-project/<int:pk>/', views.ProjectUpdateDeleteView.as_view(), name='update_delete_project'),
]