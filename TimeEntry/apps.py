from django.apps import AppConfig


class TimeentryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'TimeEntry'

    def ready(self):
        import TimeMate.Signals.signals
