from rest_framework import serializers
from abc import ABC
from django.contrib.contenttypes.models import ContentType
from django.utils.timezone import now

from .models import FinancialOutcomeRecord, CashPaymentRecord, InstallmentPaymentRecord, CheckPaymentRecord, \
    InstallmentSchedule, FinancialIncomeRecord
from Projects.models import Project, Task, SubTask
from Projects.serializers import ProjectSerializer, TaskSerializer, SubTaskSerializer
from Accounts.serializers import UserProfileDetailSerializer


class FinancialRecordRelationFieldSerializer(serializers.RelatedField, ABC):
    """
    Serializes the given related object(Project, Task, SubTask) into its serialized data by its serializers
    """
    def to_representation(self, value):
        """
        pass the value to related object
        if object is not among them raise an error.
        """
        if isinstance(value, Project):
            serializer = ProjectSerializer(value)
        elif isinstance(value, Task):
            serializer = TaskSerializer(value)
        elif isinstance(value, SubTask):
            serializer = SubTaskSerializer(value)
        else:
            raise serializers.ValidationError({'Error': 'not excepted model'})
        return serializer.data


class FinancialOutcomeSerializer(serializers.ModelSerializer):
    """
    serialize data for financial outcome model.
    include validation on payment method field.
    """
    content_object = FinancialRecordRelationFieldSerializer(read_only=True)
    created_by = UserProfileDetailSerializer(read_only=True)

    class Meta:
        model = FinancialOutcomeRecord
        fields = ('id', 'created_by', 'title', 'description', 'price', 'payment_method', 'content_type', 'object_id',
                  'content_object')
        extra_kwargs = {'content_type': {'read_only': True},
                        'object_id': {'read_only': True},
                        'content_object': {'read_only': True}}

    def validate(self, attrs):
        """
        override this method to validate payment method:
        Once the payment method value is set, this field cannot be changed
        """
        if self.instance:
            if attrs.get('payment_method'):
                raise serializers.ValidationError({'Error': 'This field cannot be change.'})

        return attrs


    def create(self, validated_data):
        """
        override this method to handle generic foreignkey relation and link it to the proper model
        (fill its fields by given values)
        base on payment method field, create an instance in proper model (cash, check, installment)
        """
        model_name = self.context.get('model')
        try:
            content_type = ContentType.objects.get(model=model_name.lower())
        except ContentType.DoesNotExist:
            raise serializers.ValidationError({'Error': f'model {model_name} is not valid'})

        validated_data['object_id'] = self.context.get('object_id')
        validated_data['content_type'] = content_type

        financial_record = FinancialOutcomeRecord.objects.create(**validated_data)

        if financial_record.payment_method == 'cash':
            CashPaymentRecord.objects.create(financial_outcome=financial_record)
        elif financial_record.payment_method == 'check':
            CheckPaymentRecord.objects.create(financial_outcome=financial_record)
        elif financial_record.payment_method == 'installment':
            InstallmentPaymentRecord.objects.create(financial_outcome=financial_record)

        return financial_record


class CashPaymentSerializer(serializers.ModelSerializer):
    """
    serialize data for cash payment model.
    include validation on payment date field.
    """
    financial_outcome = FinancialOutcomeSerializer(read_only=True)

    class Meta:
        model = CashPaymentRecord
        fields = ('id', 'payment_date', 'financial_outcome')

    def validate(self, attrs):
        """
        override this method to validate payment date -> date must be in today or in future
                                                        if the field is empty -> required
        Once the payment date value is set, this field cannot be changed
        """
        if self.instance:
            payment_date = attrs.get('payment_date')
            cash_obj = self.context['payment_method']

            if payment_date:
                if cash_obj.payment_date:
                    raise serializers.ValidationError({'Error': 'Payment date cannot be change'})

                elif payment_date < now().date():
                    raise serializers.ValidationError({'Error': 'The payment date must be today or in future!'})

            elif payment_date is None and cash_obj.payment_date is None:
                raise serializers.ValidationError({'Error': 'You must enter a payment date!'})

        return attrs


class CheckPaymentSerializer(serializers.ModelSerializer):
    """
    serialize data for check payment model.
    include validation on check date and check number fields.
    """
    financial_outcome = FinancialOutcomeSerializer(read_only=True)

    class Meta:
        model = CheckPaymentRecord
        fields = ('id', 'check_date', 'check_number', 'financial_outcome')


    def validate(self, attrs):
        """
        override this method to validate check date -> date must be in today or in future
                                                        if the field is empty -> required
                                validate check number -> it must have 16 digits
                                                         if the field is empty -> required
        Once these two field values set, values cannot be changed
        """
        if self.instance:
            check_date = attrs.get('check_date')
            check_number = attrs.get('check_number')
            check_obj = self.context['payment_method']

            if check_date:
                if check_obj.check_date:
                    raise serializers.ValidationError({'Error': "You can't change check date field!"})

                elif check_date < now().date():
                    raise serializers.ValidationError({'Error': 'The check date must be today or in future!'})

            elif check_date is None and check_obj.check_date is None:
                raise serializers.ValidationError({'Error': 'You must enter a check date!'})

            if check_number:
                if check_obj.check_number:
                    raise serializers.ValidationError({'Error': "You can't change check number field!"})

                elif len(check_number)<16:
                    raise serializers.ValidationError({'Error': 'The check number must have 16 digits'})

            elif check_number is None and check_obj.check_number is None:
                raise serializers.ValidationError({'Error': 'You must enter a check number!'})

        return attrs



class InstallmentPaymentSerializer(serializers.ModelSerializer):
    """
    serialize data for installment payment model.
    include validation on count of installments field.
    """
    financial_outcome = FinancialOutcomeSerializer(read_only=True)

    class Meta:
        model = InstallmentPaymentRecord
        fields = ('id', 'count_installments', 'financial_outcome')

    def validate(self, attrs):
        """
        override this method to validate count installment -> count should be 4 or less
                                                        if the field is empty -> required
        Once count installment field value sets, it cannot be changed
        """
        if self.instance:
            count_installments = attrs.get('count_installments')
            installment_obj = self.context['payment_method']

            if count_installments:
                if installment_obj.count_installments:
                    raise serializers.ValidationError({'Error': 'You cant change count installments!'})

                elif count_installments > 4:
                    raise serializers.ValidationError({'Error': 'The count installments must be less than 4'})

            elif count_installments in None and installment_obj.count_installments is None:
                raise serializers.ValidationError({'Error': 'You must enter a count installments!'})

        return attrs

    def update(self, instance, validated_data):
        """
        override this method to handle update installment payment operation
        creates records in the installment schedule model based on the count installments field.
        """
        obj = super().update(instance, validated_data)

        for i in range(instance.count_installments):
            InstallmentSchedule.objects.create(installment_id=instance)

        return obj


class InstallmentScheduleSerializer(serializers.ModelSerializer):
    """
    serialize data for installment schedule model.
    include validation on date field.
    """
    class Meta:
        model = InstallmentSchedule
        fields = ('id', 'date', 'installment_status', 'installment_id')
        extra_kwargs = {'installment_id': {'read_only': True},
                        'installment_status': {'read_only': True}}

    def validate(self, attrs):
        """
        override this method to validate date -> date must be in today or in future
                                                if the field is empty -> required
        Once these two field values set, values cannot be changed
        """
        if self.instance:
            date = attrs.get('date')
            if date:
                if self.instance.date is not None:
                    raise serializers.ValidationError({'Error': 'You cant change date of installment!'})

                elif date < now().date():
                    raise serializers.ValidationError({'Error': 'The installment date must be today or in future!'})

            elif date in None and self.instance.date is None:
                raise serializers.ValidationError({'Error': 'You must enter date of installment!'})

        return attrs

    def update(self, instance, validated_data):
        """
        override this method to handle update installment schedule operation
        retrieves all installment schedules related to specific installment.
        check -> input date is not duplicate and doesn't have same month with another instance.
        """
        date = validated_data.get('date')
        installment_obj = self.instance.installment_id
        installment_schedule_objs = InstallmentSchedule.objects.filter(installment_id=installment_obj)

        for schedule_obj in installment_schedule_objs:
            if schedule_obj.date is not None:
                if schedule_obj.date == date:
                    raise serializers.ValidationError({'Error': 'This date is picked by another installment!'})

                elif schedule_obj.date.month == date.month:
                    raise serializers.ValidationError({'Error': "You can't set two installments in one month!"})


        return super().update(instance, validated_data)


class FinancialIncomeSerializer(serializers.ModelSerializer):
    """
    serialize data for financial income model.
    include validation on amount field.
    """
    owner = UserProfileDetailSerializer(read_only=True)
    project = ProjectSerializer(read_only=True)

    class Meta:
        model = FinancialIncomeRecord
        fields = ('id', 'title', 'description', 'amount', 'source', 'owner', 'project')

    def validate(self, attrs):
        if self.instance:
            amount = attrs.get('amount')
            if self.instance.amount and amount and self.instance.amount != amount:
                raise serializers.ValidationError({'Error': "You cant change financial income's amount"})
        return attrs

