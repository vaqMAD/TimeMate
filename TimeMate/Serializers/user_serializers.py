from django.contrib.auth import get_user_model
from rest_framework import serializers

user = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = user
        fields = ['username', 'email']