# Python imports
from collections import OrderedDict
# DRF imports
from rest_framework import serializers
# Internal imports
from .models import TimeEntry
from Task.models import Task
from Task.serializers import TaskListSerializer
from TimeMate.Utils.mixins import OwnerRepresentationMixin
from .validators import validate_start_and_end_time
from Task.validators import validate_task_ownership


class TimeEntryBaseSerializer(serializers.ModelSerializer):
    detail_url = serializers.HyperlinkedIdentityField(read_only=True, view_name='time_entry_detail')

    class Meta:
        model = TimeEntry
        fields = ['id', 'start_time', 'end_time', 'duration', 'detail_url']


class TimeEntryCreateSerializer(OwnerRepresentationMixin, serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = TimeEntry
        fields = ['owner', 'task', 'start_time', 'end_time']

    def validate(self, data):
        data = super().validate(data)

        # Get necessary values
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        # Calling custom validator
        if start_time and end_time:
            validate_start_and_end_time(start_time, end_time)
        return data

    def validate_task(self, value):
        return validate_task_ownership(value, self.context['request'].user)


class TimeEntryListSerializer(TimeEntryBaseSerializer):
    task = TaskListSerializer(read_only=True)

    class Meta(TimeEntryBaseSerializer.Meta):
        fields = ['id', 'task', 'start_time', 'end_time', 'duration', 'detail_url']


class TimeEntryDetailSerializer(OwnerRepresentationMixin, serializers.ModelSerializer):
    task = TaskListSerializer(read_only=True)

    class Meta(TimeEntryBaseSerializer.Meta):
        fields = ['id', 'task', 'start_time', 'end_time', 'duration', 'owner', 'created_at']


class TimeEntryUpdateSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = TimeEntry
        fields = ['id', 'task', 'start_time', 'end_time', 'duration', 'owner']

    def validate(self, data):
        data = super().validate(data)
        # Get necessary values
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        # Calling custom validator
        if start_time and end_time:
            validate_start_and_end_time(start_time, end_time)
        return data

    def validate_task(self, value):
        return validate_task_ownership(value, self.context['request'].user)


class TaskWithTimeEntriesSerializer(serializers.ModelSerializer):
    entries = TimeEntryBaseSerializer(
        source='time_entries',
        many=True,
        read_only=True
    )
    detail_url = serializers.HyperlinkedIdentityField(
        read_only=True,
        view_name='task_detail'
    )

    class Meta:
        model = Task
        fields = ['id', 'name', 'detail_url', 'entries']


class TimeEntryByDayListSerializer(serializers.ListSerializer):
    def to_representation(self, data):

        flat = super().to_representation(data)
        grouped = OrderedDict()
        for item in flat:
            # Return the day in the format YYYY-MM-DD (first 10 ISO-8601 characters).
            day = item['end_time'][:10]
            grouped.setdefault(day, []).append(item)
        return [
            {
                'day': day,
                'entries': entries
            }
            for day, entries in grouped.items()
        ]

class TimeEntryByDaySerializer(TimeEntryBaseSerializer):
    task = TaskListSerializer(read_only=True)
    class Meta(TimeEntryBaseSerializer.Meta):
        list_serializer_class = TimeEntryByDayListSerializer
        fields = TimeEntryBaseSerializer.Meta.fields + ['task']