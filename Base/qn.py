# 171203 Adel Liu
# 即将使用web前端直接上传到七牛 而无需通过服务器 减小服务器压力

import qiniu

from Config.models import Config
from disk.settings import HOST

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


def get_upload_token(key):
    """
    获取七牛上传token
    :param key: 规定的键
    """
    policy = {
        'insertOnly': 1,
        'callbackUrl': "%s/qiniu/callback" % host,
        'callbackBody': {
            'key': '$(key)',
            'hash': '$(etag)',
            'w': '$(imageInfo.width)',
        },
        'callbackBodyType': 'application/json',
    }
    return auth.upload_token(bucket=bucket, key=key_prefix+key, expires=3600, policy=policy)
