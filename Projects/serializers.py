from rest_framework import serializers
from Accounts.models import CustomUser
from .models import Project, Task, SubTask
from Accounts.serializers import UserProfileDetailSerializer


class ProjectSerializer(serializers.ModelSerializer):
    """
    serialize data for project model.
    include validation on start date and end date and budget fields.
    """

    experts = serializers.ListField(child=serializers.EmailField(), write_only=True, required=False)
    experts_details = UserProfileDetailSerializer(source='experts', many=True, read_only=True)
    ceo = UserProfileDetailSerializer(read_only=True)

    class Meta:
        model = Project
        fields = ('pk', 'title', 'ceo', 'experts', 'experts_details', 'description', 'image', 'category', 'start_date',
                  'end_date', 'status', 'budget', 'initial_budget')
        extra_kwargs = {'description': {'required': False},
                        'budget': {'required': True},
                        'initial_budget': {'read_only': True},}

    def validate(self, attrs):
        """
        override this method to validate start date and end date -> start date must before end date
        Once the date value is set, these fields cannot be changed
        budget cannot be 0.
        """

        start_date = attrs.get('start_date')
        end_date = attrs.get('end_date')
        budget = attrs.get('budget')

        if self.instance:
            if start_date and self.instance.start_date and start_date != self.instance.start_date:
                raise serializers.ValidationError({'start_date': "You can't change start date field!"})
            if end_date and self.instance.end_date and end_date != self.instance.end_date:
                raise serializers.ValidationError({'end_date': "You can't change end date field!"})

        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError({'Error': "start date cannot be greater than end date."})

        if budget == 0:
            raise serializers.ValidationError({'Error': "budget cannot be 0."})

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
        override this method to handle update project operation
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


class TaskSerializer(serializers.ModelSerializer):
    """
    serialize data for task model.
    include validation on start date, end date, manager and budget fields.
    """
    experts = serializers.ListField(child=serializers.EmailField(), write_only=True, required=False)
    experts_details = UserProfileDetailSerializer(source='experts', many=True, read_only=True)
    project = ProjectSerializer(read_only=True)
    manager = serializers.EmailField(write_only=True, required=True)
    manager_details = UserProfileDetailSerializer(source='manager', read_only=True)

    class Meta:
        model = Task
        fields = ('pk', 'title', 'project', 'manager', 'manager_details','experts', 'experts_details', 'description',
                  'image', 'category', 'start_date', 'end_date', 'status', 'budget')
        extra_kwargs = {'description': {'required': False},
                        'budget':{'required':True}}


    def validate(self, attrs):
        """
        override this method to validate start date and end date -> the parent project must have dates value.
                                                                    start date must before end date
                                                                    task's start date must be before project's start date.
                                                                    task's end date must be before project's end date.
        Once the date value is set, these fields cannot be changed.
        and validate manager field -> can not be changed
        the total budget of a project's tasks cannot be greater than the project's budget.
        budget cannot be 0.
        """

        start_date = attrs.get('start_date')
        end_date = attrs.get('end_date')
        manager = attrs.get('manager')
        budget = attrs.get('budget')

        if self.instance:
            project = self.instance.project
            if project.start_date and project.end_date:
                if start_date and self.instance.start_date:
                    raise serializers.ValidationError({'start_date': "You can't change start date field!"})

                if end_date and self.instance.end_date:
                    raise serializers.ValidationError({'end_date': "You can't change end date field!"})
            else:
                raise serializers.ValidationError({'Error': "You Cannot set task's start date or end date "
                                                            "because the parent project's dates aren't set."})

            if manager:
                raise serializers.ValidationError({'manager': "You can't change manager field!"})
        else:
            project = self.context['project']

        if project.start_date and project.end_date:
            if start_date and end_date:
                if start_date > end_date:
                    raise serializers.ValidationError({'Error': "start date cannot be greater than end date."})

                if start_date < project.start_date:

                    raise serializers.ValidationError(f"Task's start date must be after {project.start_date}")

                if end_date > project.end_date:
                    raise serializers.ValidationError(f"Task's end date must be before {project.end_date}")
        else:
            raise serializers.ValidationError({'Error': "You Cannot set task's start date or end date "
                                                        "because the parent project's dates aren't set."})

        if budget == 0:
            raise serializers.ValidationError({'Error': "budget cannot be 0."})

        all_tasks = project.task.all()
        total_tasks_budget = 0

        for task in all_tasks:
            total_tasks_budget += task.budget

        if total_tasks_budget + budget > project.budget:
            raise serializers.ValidationError({'Error': "your project doesn't have enough budget to add this task."})

        return attrs

    def create(self, validated_data):
        """
        override this method to handle expert users and link them to the task record
        the expert email that has been sent must exist in CustomUser model
        also manager email must exist in CustomUser model
        and if it has been sent create a record in task model.
        """

        experts_email = validated_data.pop('experts', [])
        manager_email = validated_data.pop('manager')
        exist_experts = []


        if experts_email:
            for expert in experts_email:
                user = CustomUser.objects.filter(email=expert).first()
                if user:
                    exist_experts.append(user)
                else:
                    raise serializers.ValidationError({'Error': f'User with email {expert} not found.'})

        manager = CustomUser.objects.filter(email=manager_email).first()

        if manager:
            task = Task.objects.create(manager=manager, **validated_data)

            if exist_experts:
                task.experts.set(exist_experts)
                task.save()
            return task
        else:
            raise serializers.ValidationError({'Error': f'Manager with email {manager_email} not found.'})


    def update(self, instance, validated_data):
        """
        override this method to handle update task operation
        handle new experts that user entered
        new expert must exist in CustomUser model and not be duplicated in task record
        """

        update_experts = validated_data.pop('experts', [])

        exist_experts = []
        for p_expert in instance.experts.all():
            exist_experts.append(p_expert.email)

        new_experts = []
        if update_experts:
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



class SubTaskSerializer(serializers.ModelSerializer):
    """
    serialize data for subtask model.
    include validation on start date, end date, manager and budget fields.
    """
    experts = serializers.ListField(child=serializers.EmailField(), write_only=True, required=False)
    experts_details = UserProfileDetailSerializer(source='experts', many=True, read_only=True)
    task = TaskSerializer(read_only=True)
    manager = serializers.EmailField(write_only=True, required=True)
    manager_details = UserProfileDetailSerializer(source='manager', read_only=True)

    class Meta:
        model = SubTask
        fields = ('pk', 'title', 'task', 'manager', 'manager_details', 'experts', 'experts_details', 'description',
                  'image', 'category', 'start_date', 'end_date', 'status', 'budget')
        extra_kwargs = {'description': {'required': False},
                        'budget': {'required': True},}


    def validate(self, attrs):
        """
        override this method to validate start date and end date -> the parent task must have dates value.
                                                                    start date must before end date
                                                                    subtask's start date must be before task's start date.
                                                                    subtask's end date must be before task's end date.
        Once the date value is set, these fields cannot be changed.
        and validate manager field -> can not be changed
        the total budget of a task's subtasks cannot be greater than the task's budget.
        budget cannot be 0.
        """

        start_date = attrs.get('start_date')
        end_date = attrs.get('end_date')
        manager = attrs.get('manager')
        budget = attrs.get('budget')

        if self.instance:
            task = self.instance.task
            if task.start_date and task.end_date:
                if start_date and self.instance.start_date:
                    raise serializers.ValidationError({'start_date': "You can't change start date field!"})

                if end_date and self.instance.end_date:
                    raise serializers.ValidationError({'end_date': "You can't change end date field!"})
            else:
                raise serializers.ValidationError({'Error':"You Cannot set subtask's start date or end date "
                                                           "because the parent task's dates aren't set."})

            if manager:
                raise serializers.ValidationError({'manager': "You can't change manager field!"})
        else:
            task = self.context['task']


        if task.start_date and task.end_date:
            if start_date and end_date:
                if start_date > end_date:
                    raise serializers.ValidationError({'Error': "start date cannot be greater than end date."})

                if start_date < task.start_date:
                    raise serializers.ValidationError(f"Task's start date must be after {task.start_date}")

                if end_date > task.end_date:
                    raise serializers.ValidationError(f"Task's end date must be before {task.end_date}")
        else:
            raise serializers.ValidationError({'Error': "You Cannot set subtask's start date or end date "
                                                        "because the parent task's dates aren't set."})


        if budget == 0:
            raise serializers.ValidationError({'Error': "budget cannot be 0."})

        all_subtasks = task.sub_task.all()
        total_subtasks_budget = 0

        for subtask in all_subtasks:
            total_subtasks_budget += subtask.budget

        if total_subtasks_budget + budget > task.budget:
            raise serializers.ValidationError({'Error': "your task doesn't have enough budget to add this subtask."})

        return attrs

    def create(self, validated_data):
        """
        override this method to handle expert users and link them to the subtask record
        the expert email that has been sent must exist in CustomUser model
        also manager email must exist in CustomUser model
        and if it has been sent create a record in task model.
        """

        experts_email = validated_data.pop('experts', [])
        manager_email = validated_data.pop('manager')
        exist_experts = []

        if experts_email:
            for expert in experts_email:
                user = CustomUser.objects.filter(email=expert).first()
                if user:
                    exist_experts.append(user)
                else:
                    raise serializers.ValidationError({'Error': f'User with email {expert} not found.'})

        manager = CustomUser.objects.filter(email=manager_email).first()

        if manager:
            subtask = SubTask.objects.create(manager=manager, **validated_data)

            if exist_experts:
                subtask.experts.set(exist_experts)
                subtask.save()
            return subtask
        else:
            raise serializers.ValidationError({'Error': f'Manager with email {manager_email} not found.'})


    def update(self, instance, validated_data):
        """
        override this method to handle update subtask operation
        handle new experts that user entered
        new expert must exist in CustomUser model and not be duplicated in subtask record
        """

        update_experts = validated_data.pop('experts', [])

        exist_experts = []
        for p_expert in instance.experts.all():
            exist_experts.append(p_expert.email)


        new_experts = []
        if update_experts:
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


