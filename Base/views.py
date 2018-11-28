from Base.error import ERROR_DICT
from Base.response import response


def get_error_dict(request):
    return response(body=ERROR_DICT)
