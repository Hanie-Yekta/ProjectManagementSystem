from django.db.models.signals import post_save
from .models import InstallmentSchedule, InstallmentPaymentRecord, CheckPaymentRecord, CashPaymentRecord


def complete_installment_payment_status(sender, instance,**kwargs):
    """
    this method gets the parent installment of installment_schedule that has been changed in database.
    and retrieves all the parent installment's installment_schedule that are not paid,
    if there is not any -> change the installment status = done
    if there is any installment_schedule with canceled status -> change the installment status = canceled
    """

    installment_obj = instance.installment_id
    installment_schedules = installment_obj.installments_schedule.all()

    unpaid_schedules = []
    canceled_schedules = []

    for schedule in installment_schedules:
        if schedule.installment_status != 'paid':
            unpaid_schedules.append(schedule)

            if schedule.installment_status == 'canceled':
                canceled_schedules.append(schedule)

    if canceled_schedules:
        installment_obj.status = 'canceled'
        installment_obj.save()

    elif not unpaid_schedules:
        installment_obj.status = 'done'
        installment_obj.save()


post_save.connect(receiver=complete_installment_payment_status, sender=InstallmentSchedule)




def complete_financial_outcome_status(sender, instance,**kwargs):
    """
    this method gets the parent financial outcome of instance (installment, cash, check) that has been changed in database.
    if the instance status = done -> change the financial outcome status = paid
    if the instance status = canceled -> change the financial outcome status = canceled
    else -> the financial outcome status = in_progress
    """

    if isinstance(instance, InstallmentPaymentRecord):
        instance_obj = instance.financial_outcome
    elif isinstance(instance, CheckPaymentRecord):
        instance_obj = instance.financial_outcome
    elif isinstance(instance, CashPaymentRecord):
        instance_obj = instance.financial_outcome
    else:
        return

    if instance.status == 'done':
        instance_obj.status = 'paid'

    elif instance.status == 'canceled':
        instance_obj.status = 'canceled'

    else:
        instance_obj.status = 'in_progress'

    instance_obj.save()


post_save.connect(receiver=complete_financial_outcome_status, sender=InstallmentPaymentRecord)
post_save.connect(receiver=complete_financial_outcome_status, sender=CheckPaymentRecord)
post_save.connect(receiver=complete_financial_outcome_status, sender=CashPaymentRecord)


