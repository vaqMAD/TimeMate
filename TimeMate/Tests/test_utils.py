# Python imports
import unittest
from collections import namedtuple

from rest_framework.exceptions import ErrorDetail

# Internal imports
from TimeMate.Utils.test_helpers import get_error_code

# Create simple object, to simulate error
error_detail = namedtuple('error_detail', ['code'])


class TestUtils(unittest.TestCase):
    def test_get_error_code_single_error(self):
        error = error_detail(code='error_code')
        result = get_error_code(error)
        self.assertEqual(result, 'error_code')

    def test_get_error_code_multiple_errors(self):
        # Prepare a list of error objects, function should return the code of first element.
        error_list = [error_detail(code='error_code1'), error_detail(code='error_code2')]
        result = get_error_code(error_list)
        self.assertEqual(result, 'error_code1')
