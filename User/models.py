""" Adel Liu 180111

用户类
"""
from django.db import models

from Base.common import deprint
from Base.decorator import field_validator
from Base.error import Error
from Base.response import Ret


class User(models.Model):
    """
    用户类
    根超级用户id=1
    """
    ROOT_ID = 1
    L = {
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
        max_length=L['avatar'],
    )
    nickname = models.CharField(
        max_length=L['nickname'],
        default=None,
        blank=True,
        null=True,
    )
    qt_user_app_id = models.CharField(
        default=None,
        max_length=L['qt_user_app_id'],
    )
    qtb_token = models.CharField(
        default=None,
        max_length=L['qtb_token'],
    )
    description = models.CharField(
        max_length=L['description'],
        default=None,
        blank=True,
        null=True,
    )
    FIELD_LIST = ['avatar', 'nickname', 'qt_user_app_id', 'description']

    @classmethod
    def _validate(cls, dict_):
        """验证传入参数是否合法"""
        return field_validator(dict_, cls)

    @staticmethod
    def _hash(s):
        from Base.common import md5
        return md5(s)

    @staticmethod
    def get_user_by_id(user_id):
        """根据用户ID获取用户对象"""
        try:
            o_user = User.objects.get(pk=user_id)
        except User.DoesNotExist as err:
            deprint(str(err))
            return Ret(Error.NOT_FOUND_USER)
        return Ret(o_user)

    @staticmethod
    def get_user_by_qt_user_app_id(qt_user_app_id):
        """根据齐天用户-应用ID获取用户对象"""
        try:
            o_user = User.objects.get(qt_user_app_id=qt_user_app_id)
        except User.DoesNotExist as err:
            deprint(str(err))
            return Ret(Error.NOT_FOUND_USER)
        return Ret(o_user)

    def to_dict(self):
        """把用户对象转换为字典"""
        from Resource.models import Resource
        ret = Resource.get_root_folder(self)
        if ret.error is not Error.OK:
            root_res = None
        else:
            o_res = ret.body
            if not isinstance(o_res, Resource):
                root_res = None
            else:
                root_res = o_res.res_str_id
        return dict(
            user_id=self.pk,
            avatar=self.avatar,
            nickname=self.nickname,
            root_res=root_res
        )

    @classmethod
    def create(cls, qt_user_app_id, token):
        ret = cls.get_user_by_qt_user_app_id(qt_user_app_id)
        if ret.error is Error.OK:
            o_user = ret.body
            return Ret(o_user)
        try:
            o_user = cls(
                qt_user_app_id=qt_user_app_id,
                qtb_token=token,
            )
            o_user.save()
        except Exception as err:
            deprint(str(err))
            return Ret(Error.ERROR_CREATE_USER)
        return Ret(o_user)

    def update(self):
        from Base.qtb import update_user_info
        ret = update_user_info(self.qtb_token)
        if ret.error is not Error.OK:
            return ret
        body = ret.body
        self.avatar = body['avatar']
        self.nickname = body['nickname']
        self.description = body['description']
        self.save()
        return Ret()
