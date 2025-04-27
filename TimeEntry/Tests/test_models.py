# Django imports
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.utils import IntegrityError
from django.test import TestCase
# Internal imports
from Task.models import Task
from TimeEntry.models import TimeEntry

User = get_user_model()


class TimeEntryModelTests(TestCase):
    def setUp(self):
        # Set up user objects for testing.
        self.user = User.objects.create_user(username='testuser', email='<EMAIL>', password='<PASSWORD>')

        # Create a task assigned to the owner.
        self.task = Task.objects.create(name='Test Task', owner=self.user)
        # Create a time entry assigned to the owner.
        self.time_entry = TimeEntry.objects.create(
            task=self.task,
            owner=self.user,
            start_time=timezone.now(),
            end_time=timezone.now() + timezone.timedelta(hours=1)
        )

    def test_time_entry_creation(self):
        """Ensure a TimeEntry object is created successfully."""
        self.assertEqual(self.time_entry.task, self.task)
        self.assertEqual(self.time_entry.owner, self.user)
        self.assertEqual(str(self.time_entry),
                         f"TimeEntry for {self.task.name} ({self.time_entry.start_time} - {self.time_entry.end_time})")

    def test_time_entry_constraint_end_time_must_be_after_start_time(self):
        """Validate `end_time` must be after `start_time`."""
        with self.assertRaises(IntegrityError):
            TimeEntry.objects.create(
                task=self.task,
                owner=self.user,
                start_time=timezone.now() + timezone.timedelta(hours=1),
                end_time=timezone.now()
            )
