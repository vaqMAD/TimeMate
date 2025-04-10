def get_error_code(error):
    if isinstance(error, list):
        return error[0].code
    return error.code