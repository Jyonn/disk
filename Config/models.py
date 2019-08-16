""" Adel Liu 180111

系统配置类
"""
from SmartDjango import SmartModel, ErrorCenter, E, Packing
from django.db import models


class ConfigError(ErrorCenter):
    CREATE_CONFIG = E("更新配置错误", hc=500)
    CONFIG_NOT_FOUND = E("不存在的配置", hc=404)


ConfigError.register()


class Config(SmartModel):
    """
    系统配置，如七牛密钥等
    """
    L = {
        'key': 255,
        'value': 255,
    }
    key = models.CharField(
        max_length=L['key'],
        unique=True,
    )
    value = models.CharField(
        max_length=L['value'],
    )

    @classmethod
    @Packing.pack
    def get_config_by_key(cls, key):
        ret = cls.validator(locals())
        if not ret.ok:
            return ret

        try:
            o_config = cls.objects.get(key=key)
        except cls.DoesNotExist as err:
            return ConfigError.CONFIG_NOT_FOUND

        return o_config

    @classmethod
    def get_value_by_key(cls, key, default=None):
        try:
            ret = cls.get_config_by_key(key)
            if not ret.ok:
                return default
            return ret.body.value
        except Exception as err:
            return default

    @classmethod
    @Packing.pack
    def update_value(cls, key, value):
        ret = cls.validator(locals())
        if not ret.ok:
            return ret

        ret = cls.get_config_by_key(key)
        if ret.ok:
            o_config = ret.body
            o_config.value = value
            o_config.save()
        else:
            try:
                o_config = cls(
                    key=key,
                    value=value,
                )
                o_config.save()
            except Exception as err:
                return ConfigError.CREATE_CONFIG


class ConfigInstance:
    JWT_ENCODE_ALGO = 'jwt-encode-algo'
    PROJECT_SECRET_KEY = 'project-secret-key'

    HOST = 'host'

    QITIAN_APP_ID = 'qt-app-id'
    QITIAN_APP_SECRET = 'qt-app-secret'
    ADMIN_QITIAN = 'admin-qitian'

    QINIU_ACCESS_KEY = 'qiniu-access-key'
    QINIU_SECRET_KEY = 'qiniu-secret-key'

    RES_BUCKET = 'qiniu-res-bucket'
    PUBLIC_BUCKET = 'qiniu-public-bucket'

    RES_CDN_HOST = 'res-cdn-host'
    PUBLIC_CDN_HOST = 'public-cdn-host'


CI = ConfigInstance
