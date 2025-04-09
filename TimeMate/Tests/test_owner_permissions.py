# Python imports
from unittest.mock import MagicMock
# Django imports
from django.test import TestCase
from django.contrib.auth import get_user_model
# DRF imports
from rest_framework.test import APIRequestFactory
from rest_framework.exceptions import PermissionDenied
# Internal imports
from TimeMate.Permissions.owner_permissions import PERMISSION_ERROR_CODE_NOT_TASK_OWNER, IsObjectOwner

User = get_user_model()


class IsObjectOwnerPermissionTests(TestCase):
    def setUp(self):
        # Request related set up
        self.factory = APIRequestFactory()
        # Permission related set up
        self.permission = IsObjectOwner()
        # Mock objects related set up
        self.dummy_object = MagicMock()
        # User objects related set up
        self.user_owner = User.objects.create_user(username='user1', password='<PASSWORD>', email='<EMAIL>')
        self.user_not_owner = User.objects.create_user(username='user2', password='<PASSWORD>', email='<EMAIL>')

    def test_permission_allows_when_user_is_owner(self):
        """
        Permissions returns True when user is owner of the object
        """
        request = self.factory.get('/')
        request.user = self.user_owner

        # Set up a mock object with the owner attribute
        self.dummy_object.owner = self.user_owner

        self.assertTrue(
            self.permission.has_object_permission(request, None, self.dummy_object),
            "Permission should allow access for the owner"
        )

    def test_permission_denies_when_user_is_not_owner(self):
        """
        Permission raises PermissionDenied when user is not the owner.
        """
        request = self.factory.get('/')
        request.user = self.user_not_owner
        self.dummy_object.owner = self.user_owner

        with self.assertRaises(PermissionDenied) as context:
            self.permission.has_object_permission(request, None, self.dummy_object)

        error_detail = context.exception.detail
        self.assertEqual(error_detail.code, PERMISSION_ERROR_CODE_NOT_TASK_OWNER)