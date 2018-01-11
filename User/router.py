from Base.error import Error
from Base.response import error_response
from User.views import create_user, auth_token, upload_avatar_token, upload_avatar_callback, get_user_info, delete_user, \
    modify_user, get_my_info


def rt_user(request):
    if request.method == "GET":
        return get_my_info(request)
    if request.method == "POST":
        return create_user(request)
    if request.method == "PUT":
        return modify_user(request)
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


def rt_username(request, username):
    if request.method == "GET":
        return get_user_info(request, username)
    if request.method == "DELETE":
        return delete_user(request, username)
    return error_response(Error.ERROR_METHOD)
