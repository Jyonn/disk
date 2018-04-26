""" Adel Liu 180111

用户API路由
"""
from django.views.decorators.gzip import gzip_page

from Base.error import Error
from Base.response import error_response, response, Method
from User.views import get_user_info, delete_user, get_my_info


@gzip_page
def rt_user(request):
    """ /api/user/

    GET:    get_my_info, 获取我的信息
    POST:   create_user, 创建用户
    # PUT:    modify_user, 修改用户信息
    """
    options = {
        Method.GET: "获取我的信息",
        Method.POST: "创建用户",
        # Method.PUT: "修改用户信息",
    }
    if request.method == Method.OPTIONS:
        return response(body=options, allow=True)

    if request.method == Method.GET:
        return get_my_info(request)
    return error_response(Error.ERROR_METHOD)

@gzip_page
def rt_qt_user_app_id(request, qt_user_app_id):
    """ /api/user/@:username

    GET:    get_user_info, 获取用户信息
    DELETE: delete_user, 删除用户
    """
    options = {
        Method.GET: "获取用户信息",
        Method.DELETE: "删除用户",
    }
    if request.method == Method.OPTIONS:
        return response(body=options, allow=True)

    if request.method == Method.GET:
        return get_user_info(request, qt_user_app_id)
    if request.method == Method.DELETE:
        return delete_user(request, qt_user_app_id)
    return error_response(Error.ERROR_METHOD)
