from django.db.models.signals import post_save
from .models import Task, Project, SubTask
from django.utils.timezone import now


def complete_task_status(sender, instance,**kwargs):
    """
    this method gets the parent task of subtask that has been changed in database.
    and retrieves all the parent task's subtasks that are not completed, if there is not any
    -> change the task status = completed
    """
    task = instance.task
    subtasks = task.sub_task.exclude(status='completed')

    if not subtasks:
        task.status = 'completed'
        task.completion_date = now().date()
        task.save()


post_save.connect(receiver=complete_task_status,sender=SubTask)



def complete_project_status(sender, instance,**kwargs):
    """
    this method gets the parent project of task that has been changed in database.
    and retrieves all the parent project's tasks that are not completed, if there is not any
    -> change the project status = completed
    """
    project = instance.project
    tasks = project.task.exclude(status='completed')

    if not tasks:
        project.status = 'completed'
        project.completion_date = now().date()
        project.save()


post_save.connect(receiver=complete_project_status,sender=Task)