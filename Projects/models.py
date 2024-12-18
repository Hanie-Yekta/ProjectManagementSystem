from django.db import models
from Accounts.models import CustomUser
from django.core.exceptions import ValidationError
from django.utils.timezone import now
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from Financials.models import FinancialOutcomeRecord


class Project(models.Model):
    """
    project model stores user projects information.
    user can enter -> title, experts, description, category, budget, start and end date of project
    """

    STATUS_OPTIONS = (
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    )

    CATEGORY_OPTIONS = (
        ('red', 'Technical'),
        ('green', 'Design'),
        ('blue', 'Research'),
        ('purple', 'Business'),
        ('pink', 'Education'),
        ('yellow', 'Other'),
    )
    title = models.CharField(max_length=100)
    ceo = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='project_ceo')
    experts = models.ManyToManyField(CustomUser, related_name='project_experts')
    description = models.TextField()
    image = models.ImageField(upload_to='projects/project/', default='projects/default/project_d.png')
    category = models.CharField(choices=CATEGORY_OPTIONS, max_length=6)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(choices=STATUS_OPTIONS, max_length=11, default='not_started')
    initial_budget = models.PositiveBigIntegerField(null=True, blank=True)
    budget = models.PositiveBigIntegerField(null=True, blank=True)
    is_overdue = models.BooleanField(default=False)
    completion_date = models.DateField(null=True, blank=True)
    financial_object_type = GenericRelation(FinancialOutcomeRecord, related_name='project')

    def __str__(self):
        return self.title

    def clean(self):
        """
        override this method to ensure that start date must before end date.
        the budget cannot be 0.
        """

        super().clean()
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError("start date cannot be greater than end date.")

        if self.budget == 0:
            raise ValidationError("budget cannot be 0.")

    @property
    def change_overdue(self):
        """
        check if the end date has value and status is not completed ->
                if the end date is overdue ->
                        overdue field = True
        else -> overdue field = False
        """
        if self.end_date and self.status != 'completed':
            if self.end_date < now().date():
                return True
        return False

    @property
    def change_status(self):
        """
        check if the start date has value and status is not started ->
                if the start date is overdue ->
                        status = 'in_progress'
        else -> don't change status value
        """
        if self.start_date and self.status == 'not_started':
            if self.start_date < now().date():
                return 'in_progress'
        return self.status

    def complete_project(self):
        """
        complete project with change two fields -> status=completed
                                                   completion_date = the date of the day that method called
        """
        self.status = 'completed'
        self.completion_date = now().date()
        self.save()

    @property
    def generate_budget_report(self):
        """
        generate a report if the status is not 'in_progress'.
        checks if the initial budget was accurate or not (or checks if we need financial income or not).
        """
        if self.status != 'in_progress':
            if self.budget > self.initial_budget:
                return 'exceeded'

            elif self.budget == self.initial_budget:
                return 'accurate'

    @property
    def generate_financial_outcome_report(self):
        """
        generate a report if the status is not 'in_progress'.
        gets all the financial outcome record for the project and adds their price together
        checks if the spent amount is different from the budget or not.
        """
        if self.status != 'in_progress':
            financial_objs = FinancialOutcomeRecord.objects.filter(content_type=ContentType.objects.get_for_model(self),
                                                                   object_id=self.pk,
                                                                   status='paid')
            total_price = 0
            if financial_objs:

                for financial_obj in financial_objs:
                    total_price += financial_obj.price

            if self.budget < total_price:
                return 'exceeded'

            elif self.budget > total_price:
                return 'under'

            elif self.budget == total_price:
                return 'accurate'


    @property
    def generate_completion_date_report(self):
        """
        generate a report if the status is not 'in_progress'.
        checks if the chosen end date is accurate or not.
        """
        if self.status == 'completed':
            if self.completion_date < self.end_date:
               return 'advance'
            elif self.completion_date > self.end_date:
                return 'delay'
            elif self.completion_date == self.end_date:
                return 'on schedule'


    def save(self, *args, **kwargs):
        """
        Override this method to update overdue and status value.
        if an instance is about to be created -> initial_budget = budget
        """
        self.is_overdue = self.change_overdue
        self.status = self.change_status

        if not self.pk:
            self.initial_budget = self.budget

        super().save(*args, **kwargs)


    @property
    def content_id(self):
        """
        return the contentType id for the project model instance.
        """
        c = ContentType.objects.get_for_model(self)
        return c.id



class Task(models.Model):
    """
    task model stores user task information.
    user can enter -> title, experts, description, category, budget, start and end date of task
    """

    STATUS_OPTIONS = (
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    )

    CATEGORY_OPTIONS = (
        ('red', 'Technical'),
        ('green', 'Design'),
        ('blue', 'Research'),
        ('purple', 'Business'),
        ('pink', 'Education'),
        ('yellow', 'Other'),
    )
    title = models.CharField(max_length=100)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='task')
    manager = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='task_manager')
    experts = models.ManyToManyField(CustomUser, related_name='task_experts')
    description = models.TextField()
    image = models.ImageField(upload_to='projects/task/', default='projects/default/task_d.png')
    category = models.CharField(choices=CATEGORY_OPTIONS, max_length=6)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(choices=STATUS_OPTIONS, max_length=11, default='not_started')
    budget = models.PositiveBigIntegerField(null=True, blank=True)
    is_overdue = models.BooleanField(default=False)
    completion_date = models.DateField(null=True, blank=True)
    financial_object_type = GenericRelation(FinancialOutcomeRecord, related_name='task')

    def __str__(self):
        return self.title


    def clean(self):
        """
        override this method to ensure that -> the parent project must have dates value.
                                               start date must be before end date.
                                               task's start date must be before project's start date.
                                               task's end date must be before project's end date.
                                               the total budget of a project's tasks cannot be greater than
                                                    the project's budget.
                                               the budget cannot be 0.
        """

        super().clean()
        if self.project.start_date and self.project.end_date:
            if self.start_date and self.end_date:
                if self.start_date > self.end_date:
                    raise ValidationError("start date cannot be greater than end date.")

                if self.start_date < self.project.start_date:
                    raise ValidationError("Task's start date must be after Project's start date.")

                if self.end_date > self.project.end_date:
                    raise ValidationError("Task's end date must be before Project's end date.")
        else:
            raise ValidationError("You Cannot set task's start date or end date "
                                  "because the parent project's dates aren't set.")

        if self.budget == 0:
            raise ValidationError("budget cannot be 0.")

        if self.project.budget:
            all_tasks = self.project.task.exclude(id=self.id)
            total_tasks_budget = all_tasks.aggregate(total_price=models.Sum('budget'))['total_price'] or 0

            if total_tasks_budget + self.budget > self.project.budget:
                raise ValidationError("your project doesn't have enough budget to add this task.")


    @property
    def change_overdue(self):
        """
        check if the end date has value and status is not completed ->
                if the end date is overdue ->
                        overdue field = True
        else -> overdue field = False
        """
        if self.end_date and self.status != 'completed':
            if self.end_date < now().date():
                return True
        return False


    @property
    def change_status(self):
        """
        check if the start date has value and status is not started ->
                if the start date is overdue ->
                        status = 'in_progress'
        else -> don't change status value
        """
        if self.start_date and self.status == 'not_started':
            if self.start_date < now().date():
                return 'in_progress'
        return self.status


    def complete_task(self):
        """
        complete task with change two fields -> status=completed
                                                completion_date = the date of the day that method called
        """
        self.status = 'completed'
        self.completion_date = now().date()
        self.save()

    @property
    def generate_completion_date_report(self):
        """
        generate a report if the status is not 'in_progress'.
        checks if the chosen end date is accurate or not.
        """
        if self.status == 'completed':
            if self.completion_date < self.end_date:
                return 'advance'
            elif self.completion_date > self.end_date:
                return 'delay'
            elif self.completion_date == self.end_date:
                return 'on schedule'

    @property
    def generate_financial_outcome_report(self):
        """
        generate a report if the status is not 'in_progress'.
        gets all the financial outcome record for the task and adds their price together
        checks if the spent amount is different from the budget or not.
        """
        if self.status != 'in_progress':
            financial_objs = FinancialOutcomeRecord.objects.filter(content_type=ContentType.objects.get_for_model(self),
                                                                   object_id=self.pk,
                                                                   status='paid')
            total_price = 0
            if financial_objs:

                for financial_obj in financial_objs:
                    total_price += financial_obj.price

            if self.budget < total_price:
                return 'exceeded'
            elif self.budget > total_price:
                return 'under'
            elif self.budget == total_price:
                return 'accurate'


    def save(self, *args, **kwargs):
        """
        Override this method to update overdue and status value.
        """
        self.is_overdue = self.change_overdue
        self.status = self.change_status

        super().save(*args, **kwargs)


    @property
    def content_id(self):
        """
        return the contentType id for the task model instance.
        """
        c = ContentType.objects.get_for_model(self)
        return c.id


class SubTask(models.Model):
    """
    subtask model stores user subtask information.
    user can enter -> title, experts, description, category, budget, start and end date of task
    """

    STATUS_OPTIONS = (
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    )

    CATEGORY_OPTIONS = (
        ('red', 'Technical'),
        ('green', 'Design'),
        ('blue', 'Research'),
        ('purple', 'Business'),
        ('pink', 'Education'),
        ('yellow', 'Other'),
    )
    title = models.CharField(max_length=100)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='sub_task')
    manager = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='subtask_manager')
    experts = models.ManyToManyField(CustomUser, related_name='subtask_experts')
    description = models.TextField()
    image = models.ImageField(upload_to='projects/subtask/', default='projects/default/subtask_d.png')
    category = models.CharField(choices=CATEGORY_OPTIONS, max_length=6)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(choices=STATUS_OPTIONS, max_length=11, default='not_started')
    budget = models.PositiveBigIntegerField(null=True, blank=True)
    is_overdue = models.BooleanField(default=False)
    completion_date = models.DateField(null=True, blank=True)
    financial_object_type = GenericRelation(FinancialOutcomeRecord, related_name='subtask')

    def __str__(self):
        return self.title


    def clean(self):
        """
        override this method to ensure that -> the parent task must have dates value
                                                start date must be before end date.
                                               subtask's start date must be before task's start date.
                                               subtask's end date must be before task's end date.
                                               the total budget of a task's subtasks cannot be greater than
                                                    the task's budget.
                                               the budget cannot be 0.
        """

        super().clean()
        if self.task.start_date and self.task.end_date:
            if self.start_date and self.end_date:
                if self.start_date > self.end_date:
                    raise ValidationError("start date cannot be greater than end date.")

                if self.start_date < self.task.start_date:
                    raise ValidationError("Subtask's start date must be after Task's start date.")

                if self.end_date > self.task.end_date:
                    raise ValidationError("Subtask's end date must be before Task's end date.")
        else:
            raise ValidationError("You Cannot set subtask's start date or end date "
                                  "because the parent task's dates aren't set.")

        if self.budget == 0:
            raise ValidationError("budget cannot be 0.")

        if self.task.budget:
            all_subtasks = self.task.sub_task.exclude(id=self.id)
            total_subtasks_budget = all_subtasks.aggregate(total_price=models.Sum('budget'))['total_price'] or 0

            if total_subtasks_budget + self.budget > self.task.budget:
                raise ValidationError("your task doesn't have enough budget to add this subtask.")


    @property
    def change_overdue(self):
        """
        check if the end date has value and status is not completed ->
                if the end date is overdue ->
                        overdue field = True
        else -> overdue field = False
        """
        if self.end_date and self.status != 'completed':
            if self.end_date < now().date():
                return True
        return False


    @property
    def change_status(self):
        """
        check if the start date has value and status is not started ->
                if the start date is overdue ->
                        status = 'in_progress'
        else -> don't change status value
        """
        if self.start_date and self.status == 'not_started':
            if self.start_date < now().date():
                return 'in_progress'
        return self.status


    def complete_subtask(self):
        """
        complete subtask with change two fields -> status=completed
                                                   completion_date = the date of the day that method called
        """
        self.status = 'completed'
        self.completion_date = now().date()
        self.save()

    @property
    def generate_completion_date_report(self):
        """
        generate a report if the status is not 'in_progress'.
        checks if the chosen end date is accurate or not.
        """
        if self.status == 'completed':
            if self.completion_date < self.end_date:
                return 'ahead'
            elif self.completion_date > self.end_date:
                return 'delay'
            elif self.completion_date == self.end_date:
                return 'on schedule'


    @property
    def generate_financial_outcome_report(self):
        """
        generate a report if the status is not 'in_progress'.
        gets all the financial outcome record for the subtask and adds their price together
        checks if the spent amount is different from the budget or not.
        """
        if self.status != 'in_progress':
            financial_objs = FinancialOutcomeRecord.objects.filter(content_type=ContentType.objects.get_for_model(self),
                                                                   object_id=self.pk,
                                                                   status='paid')
            total_price = 0
            if financial_objs:

                for financial_obj in financial_objs:
                    total_price += financial_obj.price

            if self.budget < total_price:
                return 'exceeded'
            elif self.budget > total_price:
                return 'under'
            elif self.budget == total_price:
                return 'accurate'


    def save(self, *args, **kwargs):
        """
        Override this method to update overdue and status value.
        """
        self.is_overdue = self.change_overdue
        self.status = self.change_status

        super().save(*args, **kwargs)


    @property
    def content_id(self):
        """
        return the contentType id for the subtask model instance.
        """
        c = ContentType.objects.get_for_model(self)
        return c.id




