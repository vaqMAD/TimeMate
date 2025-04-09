# Validators error codes
VALIDATION_ERROR_CODE_INVALID_TIME_RANGE = "invalid_time_range"
# Drf imports
from rest_framework.exceptions import ValidationError


def validate_start_and_end_time(start_time, end_time):
    """
    Check if end_time is greater than start_time
    """
    if end_time < start_time or end_time == start_time:
        raise ValidationError(
            f"End time {end_time}, must be greater than start time {start_time}",
            code=VALIDATION_ERROR_CODE_INVALID_TIME_RANGE
        )
