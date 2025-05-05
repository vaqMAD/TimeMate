# Python imports
import os
from datetime import timedelta
# Django imports
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.authtoken.models import Token
# Internal imports
from Task.models import Task
from TimeEntry.models import TimeEntry

User = get_user_model()

SUPERUSER_ENV_VARS = {
    'username': 'DJANGO_SUPERUSER_USERNAME',
    'email':    'DJANGO_SUPERUSER_EMAIL',
    'password': 'DJANGO_SUPERUSER_PASSWORD',
    'token':    'DJANGO_SUPERUSER_TOKEN',
}

DEMO_TASKS = [
    {
        'name': 'API Design',
        'description': 'Design API endpoints and schema.',
    },
    {
        'name': 'Serializer Implementation',
        'description': 'Implement DRF serializers for Task and TimeEntry.',
    },
    {
        'name': 'Unit Testing',
        'description': 'Write unit tests for all key logic.',
    },
]
NUM_DEMO_TASKS = 20           # Number of demo tasks to generate
ENTRIES_PER_TASK = 5          # Number of time entries per task
SEED_WINDOW_DAYS = 7          # Seed entries within the last week
TIME_ENTRY_DURATION_HOURS = 1 # Duration of each entry in hours

class Command(BaseCommand):
    help = 'Seed the database with demo data for TimeMate.'
    def handle(self, *args, **options):
        """
        Entry point for seeding demo data:
        1. Create superuser if not exists.
        2. Create or update token for API access.
        3. Seed a configurable number of tasks.
        4. Seed multiple non-overlapping time entries per task within the last week.
        """
        self.stdout.write('Starting demo data seeding...')
        superuser = self._create_superuser()
        token = self._create_token(superuser)
        self.stdout.write(f'API Token: {token.key}')

        tasks = self._seed_tasks(superuser)
        self._seed_time_entries(superuser, tasks)
        self.stdout.write(self.style.SUCCESS('Demo data successfully seeded.'))

    def _create_superuser(self) -> User:
        """
        Create a Django superuser using environment variables.
        Returns the created or existing superuser instance.
        """
        username = os.getenv(SUPERUSER_ENV_VARS['username'])
        email = os.getenv(SUPERUSER_ENV_VARS['email'])
        password = os.getenv(SUPERUSER_ENV_VARS['password'])

        if not username or not email or not password:
            raise ValueError(
                'Superuser credentials must be set in environment variables.'
            )

        user_qs = User.objects.filter(username=username)
        if user_qs.exists():
            self.stdout.write('Superuser already exists.')
            return user_qs.first()

        self.stdout.write('Creating superuser...')
        return User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
        )
    def _create_token(self, user: User) -> Token:
        """
        Create or update an auth token for the given user.
        Token value is read from an environment variable, allowing manual configuration.
        """
        token_key = os.getenv(SUPERUSER_ENV_VARS['token'])
        if not token_key:
            raise ValueError('API token must be set in environment variable DEMO_API_TOKEN')

        token, created = Token.objects.update_or_create(
            user=user,
            defaults={'key': token_key}
        )
        status = 'Created' if created else 'Updated'
        self.stdout.write(f'Token for user "{user.username}": {status}')
        return token

    def _seed_tasks(self, owner: User) -> list:
        """
        Seed the Task model with a sequence of demo tasks.
        Returns a list of created or existing Task instances.
        """
        tasks = []
        for i in range(1, NUM_DEMO_TASKS + 1):
            name = f'Demo Task {i}'
            description = f'Description for demo task {i}.'
            task, created = Task.objects.get_or_create(
                name=name,
                defaults={
                    'description': description,
                    'owner': owner,
                }
            )
            status = 'Created' if created else 'Exists'
            self.stdout.write(f'Task "{task.name}": {status}')
            tasks.append(task)
        return tasks

    def _seed_time_entries(self, owner: User, tasks: list) -> None:
        """
        Seed the TimeEntry model for each Task with multiple entries.
        Entries are non-overlapping and distributed over the last week.
        """
        now = timezone.now()
        start_window = now - timedelta(days=SEED_WINDOW_DAYS)
        duration = timedelta(hours=TIME_ENTRY_DURATION_HOURS)

        for task in tasks:
            for entry_index in range(ENTRIES_PER_TASK):
                # Calculate sequential, non-overlapping intervals
                entry_start = start_window + entry_index * duration
                entry_end = entry_start + duration

                entry, created = TimeEntry.objects.get_or_create(
                    task=task,
                    owner=owner,
                    start_time=entry_start,
                    defaults={
                        'end_time': entry_end,
                    }
                )
                status = 'Created' if created else 'Exists'
                self.stdout.write(
                    f'TimeEntry [{entry.start_time} - {entry_end}]  \n'  +
                    f'for task "{task.name}": {status}'
                )
