""" Adel Liu 180111

用户类
"""
import re

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
        'username': 32,
        'password': 32,
        'nickname': 10,
        'avatar': 1024,
    }
    email = models.EmailField(
        null=True,
        blank=True,
        default=None,
        verbose_name='暂时不用'
    )
    username = models.CharField(
        max_length=L['username'],
        unique=True,
    )
    password = models.CharField(
        max_length=L['password'],
    )
    pwd_change_time = models.FloatField(
        null=True,
        blank=True,
        default=0,
    )
    parent = models.ForeignKey(
        'User',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    avatar = models.CharField(
        default=None,
        null=True,
        blank=True,
        max_length=L['avatar'],
    )
    grant = models.BooleanField(
        verbose_name='是否有权限新增用户',
        default=False,
    )
    nickname = models.CharField(
        max_length=L['nickname'],
        default=None,
    )
    FIELD_LIST = ['email', 'username', 'password', 'parent', 'avatar', 'grant', 'nickname']

    @staticmethod
    def _valid_username(username):
        """验证用户名合法"""
        valid_chars = '^[A-Za-z0-9_]{3,32}$'
        if re.match(valid_chars, username) is None:
            return Ret(Error.INVALID_USERNAME)
        return Ret()

    @staticmethod
    def _valid_password(password):
        """验证密码合法"""
        valid_chars = '^[A-Za-z0-9!@#$%^&*()_+-=,.?;:]{6,16}$'
        if re.match(valid_chars, password) is None:
            return Ret(Error.INVALID_PASSWORD)
        return Ret()

    @staticmethod
    def _valid_o_parent(o_parent):
        """验证o_parent合法"""
        if not isinstance(o_parent, User):
            return Ret(Error.STRANGE)
        if not o_parent.grant:
            return Ret(Error.REQUIRE_GRANT)
        return Ret()

    @classmethod
    def _validate(cls, dict_):
        """验证传入参数是否合法"""
        return field_validator(dict_, cls)

    @classmethod
    def create(cls, username, password, o_parent):
        """ 创建用户

        :param username: 用户名
        :param password: 密码
        :param o_parent: 父用户
        :return: Ret对象，错误返回错误代码，成功返回用户对象
        """
        ret = cls._validate(locals())
        if ret.error is not Error.OK:
            return ret

        hash_password = User._hash(password)
        ret = User.get_user_by_username(username)
        if ret.error is Error.OK:
            return Ret(Error.USERNAME_EXIST)
        try:
            o_user = cls(
                username=username,
                password=hash_password,
                email=None,
                parent=o_parent,
                avatar=None,
                grant=False,
                nickname='',
            )
            o_user.save()
        except ValueError as err:
            deprint(str(err))
            return Ret(Error.ERROR_CREATE_USER)
        return Ret(o_user)

    def change_password(self, password, old_password):
        """修改密码"""
        ret = self._validate(locals())
        if ret.error is not Error.OK:
            return ret
        if self.password != User._hash(old_password):
            return Ret(Error.ERROR_PASSWORD)
        hash_password = User._hash(password)
        self.password = hash_password
        import datetime
        self.pwd_change_time = datetime.datetime.now().timestamp()
        self.save()
        return Ret()

    @staticmethod
    def _hash(s):
        from Base.common import md5
        return md5(s)

    @staticmethod
    def get_user_by_username(username):
        """根据用户名获取用户对象"""
        try:
            o_user = User.objects.get(username=username)
        except User.DoesNotExist as err:
            deprint(str(err))
            return Ret(Error.NOT_FOUND_USER)
        return Ret(o_user)

    @staticmethod
    def get_user_by_id(user_id):
        """根据用户ID获取用户对象"""
        try:
            o_user = User.objects.get(pk=user_id)
        except User.DoesNotExist as err:
            deprint(str(err))
            return Ret(Error.NOT_FOUND_USER)
        return Ret(o_user)

    def to_dict(self):
        """把用户对象转换为字典"""
        return dict(
            user_id=self.pk,
            username=self.username,
            avatar=self.get_avatar_url(),
            nickname=self.nickname,
        )

    def to_base_dict(self):
        """基本字典信息"""
        return dict(
            nickname=self.username[:-3]+'***',
            avatar=self.get_avatar_url(),
        )

    @staticmethod
    def authenticate(username, password):
        """验证用户名和密码是否匹配"""
        ret = User._validate(locals())
        if ret.error is not Error.OK:
            return ret
        try:
            o_user = User.objects.get(username=username)
        except User.DoesNotExist as err:
            deprint(str(err))
            return Ret(Error.NOT_FOUND_USER)
        if User._hash(password) == o_user.password:
            return Ret(o_user)
        return Ret(Error.ERROR_PASSWORD)

    def get_avatar_url(self, small=True):
        """获取用户头像地址"""
        if self.avatar is None:
            return None
        from Base.qn import get_resource_url
        key = "%s-small" % self.avatar if small else self.avatar
        return get_resource_url(key)

    def modify_avatar(self, avatar):
        """修改用户头像"""
        ret = self._validate(locals())
        if ret.error is not Error.OK:
            return ret
        self.avatar = avatar
        self.save()
        return Ret()

    def modify_info(self, nickname):
        """修改用户信息"""
        if nickname is None:
            nickname = self.nickname
        ret = self._validate(locals())
        if ret.error is not Error.OK:
            return ret
        # if nickname is not None:
        self.nickname = nickname
        self.save()
        return Ret()
