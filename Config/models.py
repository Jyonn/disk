""" Adel Liu 180111

系统配置类
"""
from SmartDjango import models, E


@E.register(id_processor=E.idp_cls_prefix())
class ConfigError:
    CREATE = E("更新配置错误", hc=500)
    NOT_FOUND = E("不存在的配置", hc=404)


class Config(models.Model):
    """
    系统配置，如七牛密钥等
    """
    key = models.CharField(
        max_length=255,
        unique=True,
    )
    value = models.CharField(
        max_length=255,
    )

    @classmethod
    def get_config_by_key(cls, key):
        try:
            config = cls.objects.get(key=key)
        except cls.DoesNotExist as err:
            raise ConfigError.CONFIG_NOT_FOUND(debug_message=err)

        return config

    @classmethod
    def get_value_by_key(cls, key, default=None):
        try:
            config = cls.get_config_by_key(key)
            return config.value
        except Exception:
            return default

    @classmethod
    def update_value(cls, key, value):
        try:
            config = cls.get_config_by_key(key)
            config.value = value
            config.save()
        except E as e:
            if e.eis(ConfigError.CONFIG_NOT_FOUND):
                try:
                    config = cls(
                        key=key,
                        value=value,
                    )
                    config.save()
                except Exception:
                    raise ConfigError.CREATE_CONFIG
            else:
                raise ConfigError.CREATE_CONFIG


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

    MAX_IMAGE_SIZE = 'max-image-size'
    MAX_FILE_SIZE = 'max-file-size'


CI = ConfigInstance
