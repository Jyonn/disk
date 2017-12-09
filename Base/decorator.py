# 171203 Adel Liu
# 弃用http.require_POST和http.require_GET
# 将require_POST和require_params合二为一
# 把最终参数字典存储在request.d中

import base64
from functools import wraps

# from django.views.decorators import http
from django.http import HttpRequest

from Base.common import deprint
from Base.response import *

# require_post = http.require_POST
# require_get = http.require_GET


def validate_params(r_params, g_params):
    """
    [('a', '[a-z]+'), 'b', ('c', valid_c)]
    """

    import re
    for r_param in r_params:
        if isinstance(r_param, str):
            raw_param = r_param
        elif isinstance(r_param, tuple):
            if len(r_param) == 0:
                continue
            raw_param = r_param[0]
        else:
            continue
        if raw_param not in g_params:
            return Ret(Error.REQUIRE_PARAM, append_msg=raw_param)
        if isinstance(r_param, tuple):
            v = g_params[raw_param]
            for valid_method in r_param[1:]:
                print(valid_method)
                if isinstance(valid_method, str):
                    if re.match(valid_method, v) is None:
                        return Ret(Error.PARAM_FORMAT_ERROR, append_msg=raw_param)
                elif callable(valid_method):
                    try:
                        ret = valid_method(v)
                        if ret.error is not Error.OK:
                            return Ret(ret.error)
                    except:
                        return Ret(Error.VALIDATION_FUNC_ERROR)
    return Ret()


def require_get(r_params=list()):
    """
    需要获取的参数是否在request.GET中存在
    并把结果保存到request.params中
    """
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            if not isinstance(request, HttpRequest):
                return error_response(Error.STRANGE)
            if request.method != "GET":
                return error_response(Error.ERROR_METHOD)
            # for require_param in r_params:
            #     if require_param not in request.GET:
            #         return error_response(Error.REQUIRE_PARAM, append_msg=require_param)
            ret = validate_params(r_params, request.GET)
            if ret.error is not Error.OK:
                return error_response(ret.error, append_msg=ret.append_msg)
            request.d = request.GET
            return func(request, *args, **kwargs)
        return wrapper
    return decorator


def require_post(r_params=list(), decode=True):
    """
    需要获取的参数是否在request.POST中存在
    并把结果保存到request.params中
    """
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            if not isinstance(request, HttpRequest):
                return error_response(Error.STRANGE)
            if request.method != "POST":
                return error_response(Error.ERROR_METHOD)
            # for r_param in r_params:
            #     if r_param in request.POST:
            #         if decode:
            #             x = request.POST[r_param]
            #             try:
            #                 c = base64.decodebytes(bytes(x, encoding='utf8')).decode()
            #             except:
            #                 return error_response(Error.REQUIRE_BASE64)
            #             request.POST[r_param] = c
            #     else:
            #         return error_response(Error.REQUIRE_PARAM, append_msg=r_param)
            #     request.d = request.POST
            if decode:
                for k in request.POST.keys():
                    try:
                        c = base64.decodebytes(bytes(request.POST[k], encoding='utf8')).decode()
                    except:
                        return error_response(Error.REQUIRE_BASE64)
            ret = validate_params(r_params, request.POST)
            if ret.error is not Error.OK:
                return error_response(ret.error, append_msg=ret.append_msg)
            request.d = request.POST
            return func(request, *args, **kwargs)
        return wrapper
    return decorator


def require_json(func):
    """
    把request.body的内容反序列化为json
    """
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if request.body:
            try:
                request.POST = json.loads(request.body.decode())
            except:
                pass
            return func(request, *args, **kwargs)
        else:
            return error_response(Error.REQUIRE_JSON)
    return wrapper


# def logging(func):
#     @wraps(func)
#     def wrapper(*args, **kwargs):
#         deprint('BGN -- ', func.__name__)
#         rtn = func(*args, **kwargs)
#         deprint('END --', func.__name__)
#         return rtn
#     return wrapper


def decorator_generator(verify_func):
    """
    装饰器生成器
    """

    def decorator(func):
        def wrapper(request, *args, **kwargs):
            error_id = verify_func(request)
            if error_id is not Error.OK:
                return error_response(error_id)
            return func(request, *args, **kwargs)
        return wrapper
    return decorator


def maybe_login_func(request):
    jwt_str = request.d.get('token')
    from Base.jtoken import jwt_d

    ret = jwt_d(jwt_str)
    if ret.error is not Error.OK:
        return Error.OK
    d = ret.body
    try:
        user_id = d['user_id']
        from User.models import User
        ret = User.get_user_by_id(user_id)
        if ret.error is not Error.OK:
            return Error.Ok
        o_user = ret.body
    except Exception as e:
        deprint(e)
        return Error.OK
    request.user = o_user
    return Error.OK


def require_login_func(request):
    """
    需要登录
    并根据传入的token获取user
    """
    jwt_str = request.d.get('token')
    from Base.jtoken import jwt_d

    ret = jwt_d(jwt_str)
    if ret.error is not Error.OK:
        return ret.error
    d = ret.body
    try:
        user_id = d['user_id']
        from User.models import User
        ret = User.get_user_by_id(user_id)
        if ret.error is not Error.OK:
            return ret.error
        o_user = ret.body
    except Exception as e:
        deprint(e)
        return Error.STRANGE
    request.user = o_user
    return Error.OK

require_login = decorator_generator(require_login_func)
maybe_login = decorator_generator(maybe_login_func)
