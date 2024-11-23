from django.db.models.signals import post_save
from .models import Task, Project, SubTask
from django.utils.timezone import now


def complete_task_status(sender, instance,**kwargs):
    task = instance.task
    print(task)
    subtasks = task.sub_task.exclude(status='completed')
    print(subtasks)
    if not subtasks:
        task.status = 'completed'
        task.completion_date = now().date()
        task.save()


post_save.connect(receiver=complete_task_status,sender=SubTask)


def complete_project_status(sender, instance,**kwargs):
    project = instance.project
    tasks = project.task.exclude(status='completed')

    if not tasks:
        project.status = 'completed'
        project.completion_date = now().date()
        project.save()


post_save.connect(receiver=complete_project_status,sender=Task)