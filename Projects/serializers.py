from rest_framework import serializers
from Accounts.models import CustomUser
from .models import Project
from Accounts.serializers import UserProfileDetailSerializer


class ProjectSerializer(serializers.ModelSerializer):
    """
    serialize data for project model.
    include validation on email and phone number fields and hashes the password.
    """

    experts = serializers.ListField(child=serializers.EmailField(), write_only=True, required=False)
    experts_details = UserProfileDetailSerializer(source='experts', many=True, read_only=True)
    ceo = UserProfileDetailSerializer(read_only=True)

    class Meta:
        model = Project
        fields = ('pk', 'title', 'ceo', 'experts', 'experts_details', 'description', 'image', 'category', 'start_date',
                  'end_date', 'status', 'budget')
        extra_kwargs = {'ceo': {'read_only': True},
                        'title': {'required': False},
                        'description': {'required': False},
                        'category': {'required': False},
                        }

    def validate(self, attrs):
        """
        override this method to validate start date and end date -> start date must before end date
        Once the date value is set, these fields cannot be changed
        """

        start_date = attrs.get('start_date')
        end_date = attrs.get('end_date')

        if self.instance:
            if start_date and self.instance.start_date and start_date != self.instance.start_date:
                raise serializers.ValidationError({'start_date': "You can't change start date field!"})
            if end_date and self.instance.end_date and end_date != self.instance.end_date:
                raise serializers.ValidationError({'end_date': "You can't change end date field!"})

        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError({'Error': "start date cannot be greater than end date."})

        return attrs

    def create(self, validated_data):
        """
        override this method to handle expert users and link them to the project record
        the expert email that has been sent must exist in CustomUser model
        """

        experts_email = validated_data.pop('experts', [])
        exist_experts = []

        if experts_email:
            for expert in experts_email:
                user = CustomUser.objects.filter(email=expert).first()
                if user:
                    exist_experts.append(user)
                else:
                    raise serializers.ValidationError({'Error': f'User with email {expert} not found.'})

        project = Project.objects.create(**validated_data)

        if exist_experts:
            project.experts.set(exist_experts)
            project.save()

        return project

    def update(self, instance, validated_data):
        """
        override this method to handle update project
        handle new experts that user entered
        new expert must exist in CustomUser model and not be duplicated in project record
        """

        update_experts = validated_data.pop('experts', [])

        exist_experts = []
        for p_expert in instance.experts.all():
            exist_experts.append(p_expert.email)

        new_experts = []
        if update_experts and exist_experts:
            for expert in update_experts:
                if expert in exist_experts:
                    raise serializers.ValidationError({'Error': f'User with email {expert} is already exits.'})
                else:
                    user = CustomUser.objects.filter(email=expert).first()
                    if user:
                        new_experts.append(user)
                    else:
                        raise serializers.ValidationError({'Error': f'User with email {expert} not found.'})

        if new_experts:
            instance.experts.add(*new_experts)

        return super().update(instance, validated_data)
