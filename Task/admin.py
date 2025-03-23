# Django imports
from django.contrib import admin
# Internal imports
from .models import Task

admin.site.register(Task)