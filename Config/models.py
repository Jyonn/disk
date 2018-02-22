""" Adel Liu 180111

系统配置类
"""
from django.db import models

from Base.common import deprint
from Base.error import Error
from Base.response import Ret


class Config(models.Model):
    """
    系统配置，如七牛密钥等
    """
    L = {
        'key': 512,
        'value': 1024,
    }
    key = models.CharField(
        max_length=L['key'],
        unique=True,
    )
    value = models.CharField(
        max_length=L['value'],
    )

    @classmethod
    def get_config_by_key(cls, key):
        try:
            o_config = cls.objects.get(key=key)
        except ValueError as err:
            deprint(str(err))
            return Ret(Error.NOT_FOUND_CONFIG)
        return Ret(o_config)
