import requests

from Base.common import deprint
from Base.error import Error
from Base.response import Ret

QTB_OAUTH_MS = 'http://oauth:5000'


def get_qtb_user_token(code):
    uri = QTB_OAUTH_MS + '/token'
    req = requests.post(uri, json=dict(
        code=code,
    ), timeout=3)
    if req.status_code != requests.codes.ok:
        return Ret(Error.QTB_AUTH_FAIL)
    try:
        res = req.json()
    except Exception as err:
        deprint(str(err))
        return Ret(Error.QTB_AUTH_FAIL)

    if res['code'] != Error.OK.eid:
        return Ret(Error.EMPTY, append_msg=res['msg'])
    return Ret(res['body'])


def update_user_info(token):
    uri = QTB_OAUTH_MS + '/info'
    req = requests.get(uri, headers=dict(
        token=token,
    ), timeout=3)
    if req.status_code != requests.codes.ok:
        return Ret(Error.QTB_GET_INFO_FAIL)

    try:
        res = req.json()
    except Exception as err:
        deprint(str(err))
        return Ret(Error.QTB_GET_INFO_FAIL)

    if res['code'] != Error.OK.eid:
        return Ret(Error.EMPTY, append_msg=res['msg'])

    return Ret(res['body'])
