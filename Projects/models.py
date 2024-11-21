from django.db import models
from Accounts.models import CustomUser
from django.core.exceptions import ValidationError


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
    budget = models.PositiveBigIntegerField(null=True, blank=True)


    def __str__(self):
        return self.title


    def clean(self):
        """
        override this method to ensure that start date must before end date.
        """

        super().clean()
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError("start date cannot be greater than end date.")