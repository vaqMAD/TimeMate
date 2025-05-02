# Python imports
from datetime import datetime, timedelta
# Django imports
from django.test import TestCase
# DRF imports
from rest_framework.exceptions import ValidationError
# Internal imports
from TimeMate.Utils.test_helpers import get_error_code
from TimeEntry.validators import VALIDATION_ERROR_CODE_INVALID_TIME_RANGE
from TimeEntry.validators import validate_start_and_end_time


class ValidateStartAndEndTimeTest(TestCase):
    def setUp(self):
        self.start_time = datetime.now()
        self.end_time = self.start_time + timedelta(hours=1)

    def test_valid_time_range(self):
        try:
            validate_start_and_end_time(self.start_time, self.end_time)
        except ValidationError:
            self.fail("validate_start_and_end_time() raised ValidationError unexpectedly for a valid time range")

    def test_invalid_start_time(self):
        invalid_end_time = self.start_time - timedelta(hours=1)
        with self.assertRaises(ValidationError) as context:
            validate_start_and_end_time(self.start_time, invalid_end_time)

        errors = context.exception.detail
        self.assertEqual(get_error_code(errors), VALIDATION_ERROR_CODE_INVALID_TIME_RANGE)

    def test_equal_start_and_end_time(self):
        self.end_time = self.start_time
        with self.assertRaises(ValidationError) as context:
            validate_start_and_end_time(self.start_time, self.end_time)

        errors = context.exception.detail
        self.assertEqual(get_error_code(errors), VALIDATION_ERROR_CODE_INVALID_TIME_RANGE)