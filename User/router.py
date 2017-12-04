from Base.error import Error
from Base.response import error_response
from User.views import create_user, auth_token, upload_avatar_token, upload_avatar_callback


def rt_user(request):
    if request.method == "POST":
        return create_user(request)
    return error_response(Error.ERROR_METHOD)


def rt_user_token(request):
    if request.method == "POST":
        return auth_token(request)
    return error_response(Error.ERROR_METHOD)


def rt_user_avatar(request):
    if request.method == "GET":
        return upload_avatar_token(request)
    if request.method == "POST":
        return upload_avatar_callback(request)
    return error_response(Error.ERROR_METHOD)
