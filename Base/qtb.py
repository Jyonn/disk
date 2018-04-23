import requests

from Base.common import deprint
from Base.error import Error
from Base.response import Ret
from Config.models import Config

QTB_HOST = 'https://sso.6-79.cn'

QTB_APP_ID = Config.get_value_by_key('qtb-app-id', 'DEFAULT-QTB-APP-ID').body
QTB_APP_SECRET = Config.get_value_by_key('qtb-app-secret', 'DEFAULT-QTB-APP-SECRET').body


def get_qtb_user_token(code):
    get_user_token_uri = '%s/api/oauth/token' % QTB_HOST
    req = requests.post(get_user_token_uri, json=dict(
        code=code,
        app_secret=QTB_APP_SECRET,
    ), timeout=3)
    if req.status_code != requests.codes.ok:
        return Ret(Error.QTB_AUTH_FAIL)
    try:
        res = req.json()
    except Exception as err:
        deprint(str(err))
        return Ret(Error.QTB_AUTH_FAIL)

    if res['code'] != Error.OK.eid:
        return Ret(Error.QTB_AUTH_FAIL, append_msg='，%s' % res['msg'])
    return Ret(res['body'])


def update_user_info(token):
    update_info_uri = '%s/api/user/' % QTB_HOST
    req = requests.get(update_info_uri, headers=dict(
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
        return Ret(Error.QTB_GET_INFO_FAIL, append_msg='，%s' % res['msg'])

    return Ret(res['body'])
