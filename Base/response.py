""" Adel Liu 180111

函数返回、方法返回、错误返回类
"""

import json

from django.http import HttpResponse

from Base.common import deprint
from Base.error import Error, E


class Method:
    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    DELETE = 'DELETE'
    OPTIONS = 'OPTIONS'


class Ret:
    """
    函数返回类
    """
    def __init__(self, error=Error.OK, body=None, append_msg=''):
        if not isinstance(error, E):
            body = error
            error = Error.OK
        self.error = error
        self.body = body or []
        self.append_msg = append_msg


def response(eid=Error.OK, msg="ok", body=None, allow=False):
    """
    回复HTTP请求
    """
    resp = {
        "code": eid.eid,
        "msg": msg,
        "body": body or [],
    }

    http_resp = HttpResponse(
        json.dumps(resp, ensure_ascii=False),
        status=200,
        content_type="application/json; encoding=utf-8",
    )
    if allow and isinstance(body, dict):
        allow_method_list = []
        for item in body:
            allow_method_list.append(item)
        http_resp['Allow'] = ', '.join(allow_method_list)
    return http_resp


def error_response(error_id, append_msg=""):
    """
    回复一个错误
    171216 当error_id为Ret类时，自动转换
    """
    if isinstance(error_id, Ret):
        append_msg = error_id.append_msg
        error_id = error_id.error
    if not isinstance(error_id, E):
        deprint(error_id)
        return error_response(Error.STRANGE, append_msg='error_response error_id not E')
    for error in Error.ERROR_DICT:
        if error_id == error[0]:
            return response(eid=error_id, msg=error[1] + append_msg)
    return error_response(Error.ERROR_NOT_FOUND, append_msg=str(error_id))
