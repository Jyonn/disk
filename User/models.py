""" Adel Liu 180111

用户类
"""
from SmartDjango import SmartModel, Packing, ErrorCenter, E
from django.db import models

from Base.common import qt_manager


class UserError(ErrorCenter):
    CREATE_USER = E("新建用户错误", hc=500)
    USER_NOT_FOUND = E("不存在的用户", hc=404)


UserError.register()


class User(SmartModel):
    """
    用户类
    根超级用户id=1
    """
    ROOT_ID = 1
    MAX_L = {
        'password': 32,
        'nickname': 10,
        'avatar': 1024,
        'qt_user_app_id': 16,
        'qtb_token': 256,
        'description': 20,
    }

    avatar = models.CharField(
        default=None,
        null=True,
        blank=True,
        max_length=MAX_L['avatar'],
    )

    nickname = models.CharField(
        max_length=MAX_L['nickname'],
        default=None,
        blank=True,
        null=True,
    )

    qt_user_app_id = models.CharField(
        default=None,
        max_length=MAX_L['qt_user_app_id'],
        unique=True,
    )

    qtb_token = models.CharField(
        default=None,
        max_length=MAX_L['qtb_token'],
    )

    description = models.CharField(
        max_length=MAX_L['description'],
        default=None,
        blank=True,
        null=True,
    )

    """
    查询函数
    """

    @staticmethod
    @Packing.pack
    def get_by_id(user_id):
        """根据用户ID获取用户对象"""
        try:
            o_user = User.objects.get(pk=user_id)
        except User.DoesNotExist as err:
            return UserError.USER_NOT_FOUND
        return o_user

    @staticmethod
    @Packing.pack
    def get_by_qtid(qt_user_app_id):
        """根据齐天用户-应用ID获取用户对象"""
        try:
            o_user = User.objects.get(qt_user_app_id=qt_user_app_id)
        except User.DoesNotExist as err:
            return UserError.USER_NOT_FOUND
        return o_user

    """
    字典函数
    """

    def _readable_user_id(self):
        return self.pk

    def _readable_root_res(self):
        from Resource.models import Resource
        ret = Resource.get_root_folder(self)
        if not ret.ok:
            return None
        else:
            o_res = ret.body
            return o_res.res_str_id

    def d(self):
        return self.dictor(['user_id', 'avatar', 'nickname', 'root_res'])

    """
    增删函数
    """

    @classmethod
    @Packing.pack
    def create(cls, qt_user_app_id, token):
        ret = cls.get_by_qtid(qt_user_app_id)
        if ret.ok:
            user = ret.body
            user.qtb_token = token
            user.save()
            return user
        try:
            user = cls(
                qt_user_app_id=qt_user_app_id,
                qtb_token=token,
            )
            user.save()
        except Exception as err:
            return UserError.CREATE_USER
        return user

    @Packing.pack
    def update(self):
        ret = qt_manager.get_user_info(self.qtb_token)
        if not ret.ok:
            return ret
        body = ret.body
        self.avatar = body['avatar']
        self.nickname = body['nickname']
        self.description = body['description']
        self.save()

    def remove(self):
        return self.delete()
