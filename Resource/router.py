from Base.error import Error
from Base.response import error_response
from Resource.views import upload_res_token


def rt_res_token(request):
    if request.method == "GET":
        return upload_res_token(request)
    return error_response(Error.ERROR_METHOD)