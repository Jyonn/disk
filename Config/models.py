from django.db import models


class Config(models.Model):
    L = {
        'key': 512,
        'value': 1024,
    }
    key = models.CharField(
        max_length=L['key'],
    )
    value = models.CharField(
        max_length=L['value'],
    )