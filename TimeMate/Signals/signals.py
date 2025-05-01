# Django imports
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
# Internal imports
from TimeEntry.models import TimeEntry
from Task.models import Task


def invalidate_user_list(user_id):
    pattern = f"*:user={user_id}:*"
    cache.delete_pattern(pattern)

@receiver([post_save, post_delete], sender=TimeEntry)
def on_time_entry_change(sender, instance, **kwargs):
    invalidate_user_list(instance.owner.id)

@receiver([post_save, post_delete], sender=Task)
def on_task_change(sender, instance, **kwargs):
    invalidate_user_list(instance.owner.id)
