from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework.response import Response

from .models import FinancialOutcomeRecord, CashPaymentRecord, CheckPaymentRecord, InstallmentPaymentRecord, \
    InstallmentSchedule, FinancialIncomeRecord
from . import serializers
from Projects.models import Project



class FinancialOutcomeListCreateView(generics.ListCreateAPIView):
    """
    this view is used to listing and creating financial outcome records.
    methods -> GET: for show the list of financial outcome records
               POST: for create a new financial outcome record
    permission ->  Only authenticated users
    """
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializers.FinancialOutcomeSerializer

    def get_queryset(self):
        """
        return user's financial outcome records.
        """
        return FinancialOutcomeRecord.objects.filter(created_by=self.request.user)

    def get_serializer_context(self):
        """
        sent additional data (object_id, model name) to serializer with context to validate fields properly.
        """
        context = super().get_serializer_context()

        context['object_id'] = self.kwargs['object_id']
        context['model'] = self.kwargs['model']

        return context

    def perform_create(self, serializer):
        """
        pass the user to serializer as creator of financial outcome record.
        save financial outcome record's information
        """
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=self.request.user)


class FinancialOutcomeUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    """
    this view is used to update and delete a financial outcome record.
    methods -> PUT, PATCH: for update the information of the financial outcome record
                DELETE: for delete the financial outcome record
    permission ->  Only authenticated users
    """
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializers.FinancialOutcomeSerializer
    queryset = FinancialOutcomeRecord

    def perform_update(self, serializer):
        """
        validate and update the financial outcome record data
        """
        serializer.is_valid(raise_exception=True)
        serializer.save()

    def perform_destroy(self, instance):
        """
        delete the financial outcome record
        """
        instance.delete()


class PaymentMethodUpdateView(generics.RetrieveUpdateAPIView):
    """
    this view is used to update a payment method instance of financial outcome record.
    methods -> PUT, PATCH: for update the information of the payment method
    permission ->  Only authenticated users
    """
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        """
        retrieves the payment method instance based on the associated financial outcome record.
        """
        financial_obj = FinancialOutcomeRecord.objects.get(id=self.kwargs['financial_id'])

        if financial_obj.payment_method == 'cash':
            return CashPaymentRecord.objects.get(financial_outcome=financial_obj)
        elif financial_obj.payment_method == 'check':
            return CheckPaymentRecord.objects.get(financial_outcome=financial_obj)
        elif financial_obj.payment_method == 'installment':
            return InstallmentPaymentRecord.objects.get(financial_outcome=financial_obj)

    def get_serializer_class(self):
        """
        selects the appropriate serializer based on the payment method.
        """
        financial_obj = FinancialOutcomeRecord.objects.get(id=self.kwargs['financial_id'])

        if financial_obj.payment_method == 'cash':
            return serializers.CashPaymentSerializer
        elif financial_obj.payment_method == 'check':
            return serializers.CheckPaymentSerializer
        elif financial_obj.payment_method == 'installment':
            return serializers.InstallmentPaymentSerializer

    def get_serializer_context(self):
        """
        sent additional data (payment_method) to serializer with context to validate fields properly.
        """
        context = super().get_serializer_context()
        context['payment_method'] = self.get_object()
        return context

    def perform_update(self, serializer):
        """
        validate and update the payment method instance data
        """
        serializer.is_valid(raise_exception=True)
        serializer.save()


class InstallmentScheduleListView(generics.ListAPIView):
    """
    this view is used to listing installment schedules for a specific installment payment.
    methods -> GET: for show the list of installment schedules
    permission ->  Only authenticated users
    """
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializers.InstallmentScheduleSerializer

    def get_queryset(self):
        """
        return installment payment's installment schedule records
        """
        installment_obj = InstallmentPaymentRecord.objects.get(id=self.kwargs['installment_id'])
        return InstallmentSchedule.objects.filter(installment_id=installment_obj)


class InstallmentScheduleUpdateView(generics.RetrieveUpdateAPIView):
    """
    this view is used to update an installment schedule instance.
    methods -> PUT, PATCH: for update the information of the installment schedule record
    permission ->  Only authenticated users
    """
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializers.InstallmentScheduleSerializer
    queryset = InstallmentSchedule

    def perform_update(self, serializer):
        """
        validate and update the installment schedule record data
        """
        serializer.is_valid(raise_exception=True)
        serializer.save()


class CompleteCashPaymentMethodView(APIView):
    """
    this view is used to change the status of chash payment record
    permission ->  Only authenticated users
    """
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        """
        this method retrieves cash payment instance and change its status to done.
        """
        cash = get_object_or_404(CashPaymentRecord, id=kwargs['pk'])
        cash.complete_cash_payment()
        return Response(data={'detail': 'cash payment operation completed successfully'}, status=status.HTTP_200_OK)


class CancelCashPaymentMethodView(APIView):
    """
    this view is used to change the status of chash payment record.
    permission ->  Only authenticated users
    """
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        """
        this method retrieves cash payment instance and change its status to cancel.
        """
        cash = get_object_or_404(CashPaymentRecord, id=kwargs['pk'])
        cash.cancel_cash_payment()
        return Response(data={'detail': 'cash payment operation canceled'}, status=status.HTTP_200_OK)


class CompleteCheckPaymentMethodView(APIView):
    """
    this view is used to change the status of check payment record.
    permission ->  Only authenticated users
    """
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        """
        this method retrieves the check payment instance and changes its status to done.
        based on returned string, display a proper message
        """
        check = get_object_or_404(CheckPaymentRecord, id=kwargs['pk'])

        if check.status != 'canceled':
            flag = check.complete_check_payment()
            if flag == 'True':
                return Response(data={'detail': 'check payment operation completed successfully'},
                                status=status.HTTP_200_OK)
            elif flag == 'False1':
                return Response(data={'Error': 'You must fill check number and check date first!'},
                                status=status.HTTP_400_BAD_REQUEST)
            elif flag == 'False2':
                return Response(data={'Error': 'The check date is not today'},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(data={'Error': 'this check already canceled!'},
                            status=status.HTTP_400_BAD_REQUEST)


class CompleteInstallmentSchedulePaymentMethodView(APIView):
    """
    this view is used to change the status of installment schedule record.
    permission ->  Only authenticated users
    """
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        """
        this method retrieves the installment schedule instance and changes its status to paid.
        based on returned string, display a proper message
        """
        installment = get_object_or_404(InstallmentSchedule, id=kwargs['pk'])
        if installment.installment_status == 'in_progress':
            flag = installment.complete_installment_schedule()
            if flag == 'True':
                return Response(data={'detail': 'install schedule payment operation completed successfully'},
                                status=status.HTTP_200_OK)
            elif flag == 'False2':
                return Response(data={'Error': "The installment payment due date has passed."},
                                status=status.HTTP_400_BAD_REQUEST)
            elif flag == 'False1':
                return Response(data={'Error': 'You must fill installment date field first!'},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(data={'Error': '"The payment status has already been determined."'},
                            status=status.HTTP_400_BAD_REQUEST)


class FinancialIncomeListCreateView(generics.ListCreateAPIView):
    """
    this view is used to listing and creating financial income records.
    methods -> GET: for show the list of financial income records
               POST: for create a new financial income record
    permission ->  Only authenticated users
    """
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializers.FinancialIncomeSerializer

    def get_queryset(self):
        """
        return user's financial income records.
        """
        return FinancialIncomeRecord.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        """
        pass the user to serializer as creator of financial income record.
        save financial income record's information
        """
        serializer.is_valid(raise_exception=True)
        project = get_object_or_404(Project, id=self.kwargs['project_id'])
        serializer.save(owner=self.request.user, project=project)


class FinancialIncomeUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    """
    this view is used to update and delete a financial income record.
    methods -> PUT, PATCH: for update the information of the financial income record
                DELETE: for delete the financial income record
    permission ->  Only authenticated users
    """
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializers.FinancialIncomeSerializer
    queryset = FinancialIncomeRecord

    def perform_update(self, serializer):
        """
        validate and update the financial income record data
        """
        serializer.is_valid(raise_exception=True)
        serializer.save()

    def perform_destroy(self, instance):
        """
        delete the financial income record
        """
        instance.delete()