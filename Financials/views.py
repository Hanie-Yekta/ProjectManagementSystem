from rest_framework import generics, permissions

from .models import FinancialOutcomeRecord, CashPaymentRecord, CheckPaymentRecord, InstallmentPaymentRecord, \
    InstallmentSchedule
from . import serializers


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