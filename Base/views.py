from Base.error import Error
from Base.response import response


def get_error_dict(request):
    return response(body=Error.get_error_dict())
