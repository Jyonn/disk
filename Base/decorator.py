# 171203 Adel Liu
# 弃用http.require_POST和http.require_GET
# 将require_POST和require_params合二为一
# 把最终参数字典存储在request.d中

import base64
import json
from functools import wraps

# from django.views.decorators import http
from django.db import models
from django.http import HttpRequest

# from Base.common import deprint
from Base.common import deprint
from Base.error import Error
from Base.param import Param
from Base.response import Ret, error_response

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
                # print(valid_method)
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


def field_validator(d, cls):
    field_list = getattr(cls, 'FIELD_LIST', None)
    if field_list is None:
        return Ret(Error.VALIDATION_FUNC_ERROR, append_msg='，不存在FIELD_LIST')
    _meta = getattr(cls, '_meta', None)
    if _meta is None:
        return Ret(Error.VALIDATION_FUNC_ERROR, append_msg='，不是Django的models类')
    ll = getattr(cls, 'L', None)
    if ll is None:
        return Ret(Error.VALIDATION_FUNC_ERROR, append_msg='，不存在长度字典L')

    for k in d.keys():
        if k in getattr(cls, 'FIELD_LIST'):
            if isinstance(_meta.get_field(k), models.CharField):
                if len(d[k]) > ll[k]:
                    return Ret(Error.PARAM_FORMAT_ERROR, append_msg='，%s的长度不应超过%s个字符' % (k, ll[k]))
            vf = getattr(cls, '_valid_%s' % k, None)
            if vf is not None and callable(vf):
                print('_valid_', k)
                ret = vf(d[k])
                if ret.error is not Error.OK:
                    return ret
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
            request.d = Param(request.GET)
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
            if decode:
                for k in request.POST.keys():
                    try:
                        base64.decodebytes(bytes(request.POST[k], encoding='utf8')).decode()
                    except:
                        return error_response(Error.REQUIRE_BASE64)
            ret = validate_params(r_params, request.POST)
            if ret.error is not Error.OK:
                return error_response(ret.error, append_msg=ret.append_msg)
            request.d = Param(request.POST)
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
            ret = verify_func(request)
            # deprint('decorator', ret, verify_func)
            if ret.error is not Error.OK:
                return error_response(ret.error, append_msg=ret.append_msg)
            return func(request, *args, **kwargs)
        return wrapper
    return decorator


def maybe_login_func(request):
    jwt_str = request.d.get('token')
    from Base.jtoken import jwt_d

    ret = jwt_d(jwt_str)
    if ret.error is not Error.OK:
        return Ret()
    d = ret.body
    try:
        user_id = d.user_id
        from User.models import User
        ret = User.get_user_by_id(user_id)
        if ret.error is not Error.OK:
            return Ret()
        o_user = ret.body
    except Exception as e:
        deprint(e)
        return Ret()
    request.user = o_user
    return Ret()


def require_login_func(request):
    """
    需要登录
    并根据传入的token获取user
    """
    jwt_str = getattr(request.d, 'token', None)
    if jwt_str is None:
        return Ret(Error.REQUIRE_LOGIN)
    from Base.jtoken import jwt_d

    ret = jwt_d(jwt_str)
    # deprint('jwt_d', ret.error, jwt_str)
    if ret.error is not Error.OK:
        return ret
    d = ret.body
    try:
        user_id = d["user_id"]
        from User.models import User
        ret = User.get_user_by_id(user_id)
        if ret.error is not Error.OK:
            return ret
        o_user = ret.body
    except Exception as e:
        deprint(e)
        return Ret(Error.STRANGE)
    request.user = o_user
    return Ret()

require_login = decorator_generator(require_login_func)
maybe_login = decorator_generator(maybe_login_func)
