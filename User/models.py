""" Adel Liu 180111

用户类
"""
from diq import Dictify
from django.db import models
from smartdjango import Error

from Base.common import qt_manager
from User.validators import UserValidator, UserErrors


class User(models.Model, Dictify):
    vldt = UserValidator

    ROOT_ID = 1

    avatar = models.CharField(
        default=None,
        null=True,
        blank=True,
        max_length=vldt.MAX_AVATAR_LENGTH,
    )

    nickname = models.CharField(
        max_length=vldt.MAX_NICKNAME_LENGTH,
        default=None,
        blank=True,
        null=True,
    )

    qt_user_app_id = models.CharField(
        default=None,
        max_length=vldt.MAX_QT_USER_APP_ID_LENGTH,
        unique=True,
    )

    qtb_token = models.CharField(
        default=None,
        max_length=vldt.MAX_QTB_TOKEN_LENGTH,
    )

    description = models.CharField(
        max_length=vldt.MAX_DESCRIPTION_LENGTH,
        default=None,
        blank=True,
        null=True,
    )

    """
    查询函数
    """

    @staticmethod
    def get_by_id(user_id):
        """根据用户ID获取用户对象"""
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            raise UserErrors.USER_NOT_FOUND
        return user

    @staticmethod
    def get_by_qtid(qt_user_app_id):
        """根据齐天用户-应用ID获取用户对象"""
        try:
            user = User.objects.get(qt_user_app_id=qt_user_app_id)
        except User.DoesNotExist:
            raise UserErrors.USER_NOT_FOUND
        return user

    """
    字典函数
    """

    def _dictify_user_id(self):
        return self.pk

    def _dictify_root_res(self):
        from Resource.models import Resource
        try:
            res = Resource.get_root_folder(self)
            return res.res_str_id
        except Exception:
            return None

    def d(self):
        return self.dictify('user_id', 'avatar', 'nickname', 'root_res')

    """
    增删函数
    """

    @classmethod
    def create(cls, qt_user_app_id, token):
        try:
            user = cls.get_by_qtid(qt_user_app_id)
            user.qtb_token = token
            user.save()
        except Error as e:
            if e == UserErrors.USER_NOT_FOUND:
                try:
                    user = cls(
                        qt_user_app_id=qt_user_app_id,
                        qtb_token=token,
                    )
                    user.save()
                except Exception:
                    return UserErrors.CREATE_USER
            else:
                return e
        return user

    def update(self):
        body = qt_manager.get_user_info(self.qtb_token)
        self.avatar = body['avatar']
        self.nickname = body['nickname']
        self.description = body['description']
        self.save()

    def remove(self):
        return self.delete()
