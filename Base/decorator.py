# 171203 Adel Liu
# 弃用http.require_POST和http.require_GET
# 将require_POST和require_params合二为一
# 把最终参数字典存储在request.d中

import base64
from functools import wraps

# from django.views.decorators import http

from Base.common import deprint
from Base.response import *

# require_post = http.require_POST
# require_get = http.require_GET


def require_get(r_params=list()):
    """
    需要获取的参数是否在request.GET中存在
    并把结果保存到request.params中
    """
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            if request.method != "GET":
                return error_response(Error.ERROR_METHOD)
            for require_param in r_params:
                if require_param not in request.GET:
                    return error_response(Error.REQUIRE_PARAM, append_msg=require_param)
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
            if request.method != "POST":
                return error_response(Error.ERROR_METHOD)
            for r_param in r_params:
                if r_param in request.POST:
                    if decode:
                        x = request.POST[r_param]
                        try:
                            c = base64.decodebytes(bytes(x, encoding='utf8')).decode()
                        except:
                            return error_response(Error.REQUIRE_BASE64)
                        request.POST[r_param] = c
                else:
                    return error_response(Error.REQUIRE_PARAM, append_msg=r_param)
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
    # return load_session(request, 'user', once_delete=False) is not None

require_login = decorator_generator(require_login_func)
