from django.db import models
from Accounts.models import CustomUser
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class FinancialOutcomeRecord(models.Model):
    """
    financial outcome model stores user financial outcome information.
    user can enter -> title, description, price, payment method
    """

    STATUS_CHOICES = (
        ('paid', 'Paid'),
        ('in_progress', 'In Progress'),
        ('canceled', 'Canceled'),
    )

    PAYMENT_METHOD_CHOICES = (
        ('cash', 'Cash'),
        ('check', 'Check'),
        ('installment', 'Installment'),
    )

    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_finance')
    title = models.CharField(max_length=100)
    description = models.TextField()
    price = models.PositiveBigIntegerField()
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(null=True, blank=True)
    payment_date = models.DateField(null=True, blank=True)
    status = models.CharField(choices=STATUS_CHOICES, default='in_progress', max_length=11)
    payment_method = models.CharField(choices=PAYMENT_METHOD_CHOICES, max_length=11)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return self.title


class CashPaymentRecord(models.Model):
    """
    this model stores cash payment information that associated to a financial outcome instance.
    """

    PAYMENT_CHOICES = (
        ('done', 'Done'),
        ('canceled', 'Canceled')
    )

    payment_date = models.DateField(null=True, blank=True)
    status = models.CharField(choices=PAYMENT_CHOICES, max_length=8, blank=True)
    update_date = models.DateField(auto_now=True)
    financial_outcome = models.ForeignKey(FinancialOutcomeRecord, on_delete=models.CASCADE, related_name='cash_payment')

    def __str__(self):
        return self.financial_outcome.title


class CheckPaymentRecord(models.Model):
    """
    this model stores check payment information that associated to a financial outcome instance.
    user can enter -> check date, check number
    """

    PAYMENT_CHOICES = (
        ('done', 'Done'),
        ('canceled', 'Canceled')
    )

    check_date = models.DateField(null=True, blank=True)
    check_number = models.CharField(max_length=16, null=True, blank=True)
    status = models.CharField(choices=PAYMENT_CHOICES, max_length=8, blank=True)
    update_date = models.DateField(auto_now=True)
    financial_outcome = models.ForeignKey(FinancialOutcomeRecord, on_delete=models.CASCADE,
                                          related_name='check_payment')

    def __str__(self):
        return self.financial_outcome.title


class InstallmentPaymentRecord(models.Model):
    """
    this model stores cash payment information that associated to a financial outcome instance.
    user can enter -> count of installments
    """

    PAYMENT_CHOICES = (
        ('done', 'Done'),
        ('canceled', 'Canceled')
    )

    count_installments = models.PositiveIntegerField(blank=True, null=True)
    status = models.CharField(choices=PAYMENT_CHOICES, max_length=8, blank=True)
    update_date = models.DateField(auto_now=True)
    financial_outcome = models.ForeignKey(FinancialOutcomeRecord, on_delete=models.CASCADE,
                                          related_name='installment_payment')

    def __str__(self):
        return self.financial_outcome.title


class InstallmentSchedule(models.Model):
    """
    This model stores information related to an instance of the 'InstallmentPaymentRecord' model.
    Records are created in this model based on the specified number in the 'count_installments' field.
    user can enter -> date
    """

    PAYMENT_CHOICES = (
        ('paid', 'Paid'),
        ('in_progress', 'In Progress'),
        ('canceled', 'Canceled')
    )

    date = models.DateField(blank=True, null=True)
    installment_status = models.CharField(choices=PAYMENT_CHOICES, max_length=11, default='in_progress')
    installment_id = models.ForeignKey(InstallmentPaymentRecord, on_delete=models.CASCADE,
                                       related_name='installments_schedule')

    def __str__(self):
        return self.installment_id.financial_outcome.title
