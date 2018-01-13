"""171203 Adel Liu

即将使用web前端直接上传到七牛 而无需通过服务器 减小服务器压力
"""
import qiniu
from django.http import HttpRequest

from Base.common import deprint
from Base.error import Error
from Base.response import Ret
from Config.models import Config
from disk.settings import HOST, CDN_HOST

try:
    ACCESS_KEY = Config.objects.get(key='qiniu-access-key').value
    SECRET_KEY = Config.objects.get(key='qiniu-secret-key').value
    BUCKET = Config.objects.get(key='qiniu-bucket').value
except Exception as err:
    deprint(str(err))
    ACCESS_KEY = 'ACCESSKEY'
    SECRET_KEY = 'SECRETKEY'
    BUCKET = 'BUCKET'

_AUTH = qiniu.Auth(access_key=ACCESS_KEY, secret_key=SECRET_KEY)
_HOST = HOST
_KEY_PREFIX = 'disk/'


def get_upload_token(key, policy):
    """
    获取七牛上传token
    :param policy: 上传策略
    :param key: 规定的键
    """
    key = _KEY_PREFIX + key
    return _AUTH.upload_token(bucket=BUCKET, key=key, expires=3600, policy=policy), key


def qiniu_auth_callback(request):
    """七牛callback认证校验"""
    if not isinstance(request, HttpRequest):
        return Ret(Error.STRANGE)
    auth_header = request.META.get('HTTP_AUTHORIZATION')
    print('auth', auth_header)
    if auth_header is None:
        return Ret(Error.UNAUTH_CALLBACK)
    url = request.get_full_path()
    body = request.body
    verified = _AUTH.verify_callback(auth_header, url, body, content_type='application/json')
    if not verified:
        return Ret(Error.UNAUTH_CALLBACK)
    return Ret(Error.OK)


def get_resource_url(key, expires=3600):
    """获取临时资源链接"""
    url = '%s/%s' % (CDN_HOST, key)
    return _AUTH.private_download_url(url, expires=expires)
