# DRF imports
from rest_framework import serializers
# Internal imports
from .models import Task
from TimeMate.Serializers.user_serializers import UserSerializer
from .validators import unique_owner_for_task_name


class TaskCreateSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Task
        fields = ['id', 'name', 'description', 'created_at', 'owner']
        read_only_fields = ['created_at']
        # Overwrite validators attribute to turn off default UniqueConstraint validator
        validators = []

    def validate(self, data):
        data = super().validate(data)
        # Calling custom validator
        unique_owner_for_task_name(data['owner'], data.get('name'))
        return data

    def to_representation(self, instance):
        """Customize the serialized representation for the Task model."""
        representation = super().to_representation(instance)
        # Return owner field as a nested serialized object, not as an ID
        representation['owner'] = UserSerializer(instance.owner).data
        return representation


class TaskDetailSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)

    class Meta:
        model = Task
        fields = ['id', 'name', 'description', 'created_at', 'owner']
        read_only_fields = ['created_at']


class TaskListSerializer(serializers.ModelSerializer):
    detail_url = serializers.HyperlinkedIdentityField(read_only=True, view_name='task_detail')

    class Meta:
        model = Task
        fields = ['name', 'id', 'detail_url']


class TaskUpdateSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Task
        fields = ['id', 'name', 'description', 'owner', 'created_at']
        read_only_fields = ['created_at']
        validators = []

    def validate_name(self, value):
        # In update operations, validate the 'name' field only if it has changed.
        if self.instance and value != self.instance.name:
            # Check correctness of the new data by unique_owner_for_task_name
            unique_owner_for_task_name(self.instance.owner, value)
        return value
