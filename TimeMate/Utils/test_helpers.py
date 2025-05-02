def get_error_code(error):
    """
    Extracts an error code from a DRF error object or list of such objects.

    The problem:
        When handling errors in DRF responses, you may receive either
        a single ErrorDetail instance or a list of them—but downstream logic
        often just wants one canonical `code`.

    The solution:
        If `error` is a list, return the `code` of the first element.
        Otherwise, assume it's a single object and return its `code` directly.

    :param error: An error instance with a `code` attribute, or a list of such instances.
    :type error: object or list[object]
    :return: The `code` attribute of the error (or of the first error in the list).
    :rtype: Any
    """
    if isinstance(error, list):
        return error[0].code
    return error.code