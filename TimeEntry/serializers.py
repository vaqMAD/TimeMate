# Django imports
from django.shortcuts import get_object_or_404
# DRF imports
from rest_framework import serializers
# Internal imports
from .models import TimeEntry
from Task.models import Task
from Task.serializers import TaskListSerializer
from TimeMate.Utils.mixins import OwnerRepresentationMixin
from .validators import validate_start_and_end_time


class TimeEntryCreateSerializer(OwnerRepresentationMixin, serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = TimeEntry
        fields = ['owner', 'task', 'start_time', 'end_time', 'created_at']
        read_only_fields = ['created_at']

    def validate(self, data):
        data = super().validate(data)

        # Get necessary values
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        # Calling custom validator
        validate_start_and_end_time(start_time, end_time)
        return data

    def validate_task(self, value):
        # Ensures Task by given UUID exists
        task = get_object_or_404(Task, pk=value.id)
        # Check is user, owner of this task
        if task.owner != self.context['request'].user:
            raise serializers.ValidationError("You do not have permission to use this task.")
        return value


# TODO [InProgress] : add `detail_url` field.
class TimeEntryListSerializer(serializers.ModelSerializer):
    task = TaskListSerializer(read_only=True)
    detail_url = serializers.HyperlinkedIdentityField(read_only=True, view_name='time_entry_detail')

    class Meta:
        model = TimeEntry
        fields = ['id', 'task', 'start_time', 'end_time', 'detail_url']


class TimeEntryDetailSerializer(OwnerRepresentationMixin, serializers.ModelSerializer):
    task = TaskListSerializer(read_only=True)

    class Meta:
        model = TimeEntry
        fields = ['id', 'task', 'start_time', 'end_time', 'owner', 'created_at']
