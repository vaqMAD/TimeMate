# Python imports
from unittest.mock import patch
from types import SimpleNamespace
# Django imports
from django.test import SimpleTestCase
# DRF imports
from rest_framework import serializers
# Internal imports
from TimeMate.Utils.mixins import OwnerRepresentationMixin

# Dummy serializer
class DummyBaseSerializer(serializers.Serializer):
    def to_representation(self, instance):
        # Returns a dictionary containing the attributes of the instance (without additional logic)
        return instance.__dict__.copy()

class DummySerializer(OwnerRepresentationMixin, DummyBaseSerializer):
    pass

class OwnerRepresentationMixinTests(SimpleTestCase):
    def test_to_representation_without_owner(self):
        dummy_instance = SimpleNamespace(id=1, name='Test')
        serializer = DummySerializer(dummy_instance)
        representation = serializer.to_representation(dummy_instance)


        self.assertNotIn('owner', representation)
        self.assertEqual(representation, {'id': 1, 'name': 'Test'})

    @patch('TimeMate.Utils.mixins.UserSerializer')
    def test_to_representation_with_owner(self, mock_user_serializer):
        dummy_owner = SimpleNamespace(id=2, username="dummyuser")
        dummy_instance = SimpleNamespace(id=1, name="Test Task", owner=dummy_owner)

        mock_user_serializer.return_value.data = {'username': dummy_owner.username}

        serializer = DummySerializer(dummy_instance)
        representation = serializer.to_representation(dummy_instance)

        self.assertIn('owner', representation)
        self.assertEqual(representation['owner'], {'username': dummy_owner.username})
        mock_user_serializer.assert_called_once_with(dummy_owner)