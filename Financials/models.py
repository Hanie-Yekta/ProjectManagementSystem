from django.db import models
from Accounts.models import CustomUser
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils.timezone import now


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
    create_date = models.DateField(auto_now_add=True)
    update_date = models.DateField(null=True, blank=True)
    payment_date = models.DateField(null=True, blank=True)
    status = models.CharField(choices=STATUS_CHOICES, default='in_progress', max_length=11)
    payment_method = models.CharField(choices=PAYMENT_METHOD_CHOICES, max_length=11)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """
        Override this method to update update date field.
        """
        if self.pk:
            previous_obj = FinancialOutcomeRecord.objects.get(pk=self.pk)
            if previous_obj.status != self.status:
                self.update_date = now().date()

        super().save(*args, **kwargs)


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

    def complete_cash_payment(self):
        """
        complete cash payment with change two fields -> status=done
                                                   payment_date = the date of the day that method called
        """
        self.status = 'done'
        self.payment_date = now().date()
        self.save()

    def cancel_cash_payment(self):
        """
        cancel cash payment with change the status field -> status=canceled
        """
        self.status = 'canceled'
        self.save()


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

    @property
    def cancel_check_payment(self):
        """
        check if the check date and check number has values and status is none ->
                if the check date is in the past -> status = 'canceled'
        else -> don't change the status value
        """
        if self.check_date and self.check_number and self.status is None:
            if self.check_date < now().date():
                return 'canceled'
        return self.status


    def complete_check_payment(self):
        """
        complete check payment base on check date  and check number fields ->
                    if both fields have values and if the check date is equal to today's date -> status=done
                                                                                        return string with value = true
                                                    else return string with value = false2
                    else return string with value = false1
        """
        if self.check_date and self.check_number:
            if self.check_date == now().date():
                self.status = 'done'
                self.save()
                return 'True'
            return 'False2'
        return 'False1'


    def save(self, *args, **kwargs):
        """
        Override this method to update status value.
        """
        self.status = self.cancel_check_payment
        super().save(*args, **kwargs)




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


    def complete_installment_schedule(self):
        """
        complete installment schedule base on date field ->
                    if date field has value and if its value is today or in future -> status=paid
                                                                                   return string with value = true
                                                else return string with value = false2
                    else return string with value = false1
        """
        if self.date:
            if self.date >= now().date():
                self.installment_status = 'paid'
                self.save()
                return 'True'
            return 'False2'
        return 'False1'


    @property
    def cancel_installment_schedule_payment(self):
        """
        check if the date has value and status is in progress ->
                if the date is in past -> status = 'canceled'
        else -> don't change status value
        """
        if self.date and self.installment_status == 'in_progress':
            if self.date < now().date():
                return 'canceled'
        return self.installment_status


    def save(self, *args, **kwargs):
        """
        Override this method to update status value.
        """
        self.installment_status = self.cancel_installment_schedule_payment
        super().save(*args, **kwargs)



class FinancialIncomeRecord(models.Model):
    """
    financial income model stores user financial income information.
    user can enter -> title, description, amount, source, related project
    """
    INCOME_SOURCE_CHOICES = (
        ('investment', 'Investment'),
        ('grant', 'Grant'),
        ('other', 'Other')
    )

    title = models.CharField(max_length=256)
    description = models.TextField(blank=True, null=True)
    amount = models.PositiveBigIntegerField()
    source = models.CharField(max_length=50, choices=INCOME_SOURCE_CHOICES)
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_finance_income')
    project = models.ForeignKey('Projects.Project', on_delete=models.CASCADE, related_name='project')
    create_date = models.DateField(auto_now_add=True)

    def str(self):
        return self.title