# 171203 Adel Liu
# 即将使用web前端直接上传到七牛 而无需通过服务器 减小服务器压力

import qiniu
from django.http import HttpRequest

from Base.error import Error
from Base.response import Ret
from Config.models import Config
from disk.settings import HOST, CDN_HOST

try:
    AccessKey = Config.objects.get(key='qiniu-access-key').value
    SecretKey = Config.objects.get(key='qiniu-secret-key').value
    bucket = Config.objects.get(key='qiniu-bucket').value
except:
    AccessKey = 'ACCESSKEY'
    SecretKey = 'SECRETKEY'
    bucket = 'BUCKET'

auth = qiniu.Auth(access_key=AccessKey, secret_key=SecretKey)
host = HOST
key_prefix = 'disk/'


def get_upload_token(key, policy):
    """
    获取七牛上传token
    :param policy: 上传策略
    :param key: 规定的键
    """
    key = key_prefix + key
    return auth.upload_token(bucket=bucket, key=key, expires=3600, policy=policy), key


def auth_callback(request):
    if not isinstance(request, HttpRequest):
        return Ret(Error.STRANGE)
    auth_header = request.META.get('Authorization')
    if auth_header is None:
        return Ret(Error.UNAUTH_CALLBACK)
    url = request.get_full_path()
    body = request.body
    verified = auth.verify_callback(auth_header, url, body, content_type='application/json')
    if not verified:
        return Ret(Error.UNAUTH_CALLBACK)
    return Ret(Error.OK)


def get_resource_url(key, expires=3600):
    url = '%s/%s' % (CDN_HOST, key)
    return auth.private_download_url(url, expires=expires)
