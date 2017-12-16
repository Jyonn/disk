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
    parent = models.ForeignKey(
        'User',
        null=True,
        blank=True,
    )
    avatar = models.URLField(
        default=None,
        null=True,
        blank=True,
        verbose_name='暂时不用'
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
        valid_chars = '^[A-Za-z0-9_]{3,32}$'
        if re.match(valid_chars, username) is None:
            return Ret(Error.INVALID_USERNAME)
        return Ret()

    @staticmethod
    def _valid_password(password):
        valid_chars = '^[A-Za-z0-9!@#$%^&*()_+-=,.?;:]{6,16}$'
        if re.match(valid_chars, password) is None:
            return Ret(Error.INVALID_PASSWORD)
        return Ret()

    @classmethod
    def _validate(cls, d):
        return field_validator(d, cls)

    @classmethod
    def create(cls, username, password, nickname, o_parent):
        ret = cls._validate(locals())
        if ret.error is not Error.OK:
            return ret
        if not isinstance(o_parent, User):
            return Ret(Error.STRANGE)
        if not o_parent.grant:
            return Ret(Error.REQUIRE_GRANT)
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
                nickname=nickname,
            )
            o_user.save()
        except Exception as e:
            deprint(e)
            return Ret(Error.ERROR_CREATE_USER)
        return Ret(Error.OK, o_user)

    @staticmethod
    def _hash(s):
        import hashlib
        md5 = hashlib.md5()
        md5.update(s.encode())
        return md5.hexdigest()

    @staticmethod
    def get_user_by_username(username):
        try:
            o_user = User.objects.get(username=username)
        except:
            return Ret(Error.NOT_FOUND_USER)
        return Ret(Error.OK, o_user)

    @staticmethod
    def get_user_by_id(user_id):
        try:
            o_user = User.objects.get(pk=user_id)
        except:
            return Ret(Error.NOT_FOUND_USER)
        return Ret(Error.OK, o_user)

    def to_dict(self):
        return dict(
            user_id=self.pk,
            username=self.username,
            avatar=self.get_avatar_url(),
        )

    @staticmethod
    def authenticate(username, password):
        ret = User._validate(locals())
        if ret.error is not Error.OK:
            return ret
        deprint('success valid')
        try:
            o_user = User.objects.get(username=username)
        except Exception as e:
            deprint(str(e))
            return Ret(Error.NOT_FOUND_USER)
        if User._hash(password) == o_user.password:
            return Ret(Error.OK, o_user)
        return Ret(Error.ERROR_PASSWORD)

    def get_avatar_url(self):
        if self.avatar is None:
            return None
        from Base.qn import get_resource_url
        return get_resource_url(self.avatar)

    def modify_avatar(self, avatar_key):
        self.avatar = avatar_key
        self.save()