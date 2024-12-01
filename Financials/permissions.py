from rest_framework import permissions
from django.shortcuts import get_object_or_404
from Financials.models import FinancialOutcomeRecord, InstallmentPaymentRecord
from Projects.models import Project, Task, SubTask


class IsOwnerFinancialOutcome(permissions.BasePermission):
    """
    custom permission to create or view financial outcome records
    method -> GET, POST -> if record related to project: project CEO
                           if the record related to task: task manager, project CEO
                           if the record related to subtask: subtask manager, task manager, project CEO
    """
    def has_permission(self, request, view):
        object_id = view.kwargs.get('object_id')
        model = view.kwargs.get('model')

        if model.lower() == 'project':
            record = get_object_or_404(Project, pk=object_id)
            return request.user == record.ceo

        elif model.lower() == 'task':
            record = get_object_or_404(Task, pk=object_id)
            return request.user == record.manager or request.user == record.project.ceo

        elif model.lower() == 'subtask':
            record = get_object_or_404(SubTask, pk=object_id)
            return request.user == record.manager or request.user == record.task.manager or request.user == record.task.project.ceo


class CanUpdateDeleteFinancial(permissions.BasePermission):
    """
    custom permission to update or delete the financial outcome record.
    method -> PUT, PATCH, DELETE -> if record related to project: project CEO
                                    if the record related to task: task manager, project CEO
                                    if the record related to subtask: subtask manager, task manager, project CEO
    """
    def has_object_permission(self, request, view, obj):

        if obj.content_type.model == 'project':
            return request.user == obj.content_object.ceo

        elif obj.content_type.model == 'task':
            return request.user == obj.content_object.manager or request.user == obj.content_object.project.ceo

        elif obj.content_type.model == 'subtask':
            return request.user == obj.content_object.manager or request.user == obj.content_object.task.manager or request.user == obj.content_object.ceo


class CanUpdateDeletePaymentMethod(permissions.BasePermission):
    """
    custom permission to update or delete the payment method.
    by financial id that fetched from url, access the financial related model, then access the ceo or manager
    method -> PUT, PATCH, DELETE -> if record related to project: project CEO
                                    if the record related to task: task manager, project CEO
                                    if the record related to subtask: subtask manager, task manager, project CEO
    """
    def has_object_permission(self, request, view, obj):
        financial_obj = get_object_or_404(FinancialOutcomeRecord, id=obj.financial_outcome)

        if financial_obj.content_type.model == 'project':
            return request.user == financial_obj.content_object.ceo

        elif financial_obj.content_type.model == 'task':
            return request.user == financial_obj.content_object.manager or request.user == financial_obj.content_object.project.ceo

        elif financial_obj.content_type.model == 'subtask':
            return request.user == financial_obj.content_object.manager or request.user == financial_obj.content_object.task.manager or request.user == financial_obj.content_object.ceo


class CanSeeInstallmentSchedule(permissions.BasePermission):
    """
    custom permission to see installment schedule record.
    by installment id that fetched from url, access the financial related model, then access the ceo or manager
    method -> GET -> if record related to project: project CEO
                     if the record related to task: task manager, project CEO
                     if the record related to subtask: subtask manager, task manager, project CEO
    """
    def has_permission(self, request, view):
        installment_obj = get_object_or_404(InstallmentPaymentRecord, id=view.kwargs.get('installment_id'))
        model_name = installment_obj.financial_outcome.content_object.model

        if model_name == 'project':
            return request.user == installment_obj.financial_outcome.content_object.ceo

        elif model_name == 'task':
            return request.user == installment_obj.financial_outcome.content_object.manager or request.user == installment_obj.financial_outcome.content_object.project.ceo

        elif model_name == 'subtask':
            return request.user == installment_obj.financial_outcome.content_object.manager or request.user == installment_obj.financial_outcome.content_object.task.manager or request.user == installment_obj.financial_outcome.content_object.ceo


class CanUpdateInstallmentSchedule(permissions.BasePermission):
    """
    custom permission to update the installment schedule record.
    method -> PUT, PATCH -> if record related to project: project CEO
                            if the record related to task: task manager, project CEO
                            if the record related to subtask: subtask manager, task manager, project CEO
    """
    def has_object_permission(self, request, view, obj):
        model_name = obj.installment_id.financial_outcome.content_object.model

        if model_name == 'project':
            return request.user == obj.installment_id.financial_outcome.content_object.ceo

        elif model_name == 'task':
            return request.user == obj.installment_id.financial_outcome.content_object.manager or request.user == obj.installment_id.financial_outcome.content_object.project.ceo

        elif model_name == 'subtask':
            return request.user == obj.installment_id.financial_outcome.content_object.manager or request.user == obj.installment_id.financial_outcome.content_object.task.manager or request.user == obj.installment_id.financial_outcome.content_object.ceo


class CanUpdateStatusPaymentMethod(permissions.BasePermission):
    """
    custom permission to update the payment method status.
    method POST -> if record related to project: project CEO
                   if the record related to task: task manager, project CEO
                   if the record related to subtask: subtask manager, task manager, project CEO
    """
    def has_object_permission(self, request, view, obj):
        model_name = obj.financial_outcome.content_object.model
        if model_name == 'project':
            return request.user == obj.financial_outcome.content_object.ceo

        elif model_name == 'task':
            return request.user == obj.financial_outcome.content_object.manager or request.user == obj.financial_outcome.content_object.project.ceo

        elif model_name == 'subtask':
            return request.user == obj.financial_outcome.content_object.manager or request.user == obj.financial_outcome.content_object.task.manager or request.user == obj.financial_outcome.content_object.ceo


class IsOwnerFinancialIncome(permissions.BasePermission):
    """
    custom permission to create or view financial income records.
    by project id that fetched from url, access the project CEO
    method -> GET, POST: project CEO
    """
    def has_permission(self, request, view):
        project_obj = get_object_or_404(Project, id=view.kwargs.get('project_id'))
        return request.user == project_obj.ceo


class CanUpdateDeleteFinancialIncome(permissions.BasePermission):
    """
     custom permission to update or delete financial income records.
     method -> PUT, PATCH, DELETE: project CEO
     """
    def has_object_permission(self, request, view, obj):
        return request.user == obj.project.ceo
