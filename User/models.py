""" Adel Liu 180111

用户类
"""
from SmartDjango import models, Excp, ErrorCenter, E

from Base.common import qt_manager


class UserError(ErrorCenter):
    CREATE_USER = E("新建用户错误", hc=500)
    USER_NOT_FOUND = E("不存在的用户", hc=404)


UserError.register()


class User(models.Model):
    """
    用户类
    根超级用户id=1
    """
    ROOT_ID = 1

    avatar = models.CharField(
        default=None,
        null=True,
        blank=True,
        max_length=1024,
    )

    nickname = models.CharField(
        max_length=10,
        default=None,
        blank=True,
        null=True,
    )

    qt_user_app_id = models.CharField(
        default=None,
        max_length=16,
        unique=True,
    )

    qtb_token = models.CharField(
        default=None,
        max_length=256,
    )

    description = models.CharField(
        max_length=20,
        default=None,
        blank=True,
        null=True,
    )

    """
    查询函数
    """

    @staticmethod
    @Excp.pack
    def get_by_id(user_id):
        """根据用户ID获取用户对象"""
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist as err:
            return UserError.USER_NOT_FOUND
        return user

    @staticmethod
    @Excp.pack
    def get_by_qtid(qt_user_app_id):
        """根据齐天用户-应用ID获取用户对象"""
        try:
            user = User.objects.get(qt_user_app_id=qt_user_app_id)
        except User.DoesNotExist as err:
            return UserError.USER_NOT_FOUND
        return user

    """
    字典函数
    """

    def _readable_user_id(self):
        return self.pk

    def _readable_root_res(self):
        from Resource.models import Resource
        try:
            res = Resource.get_root_folder(self)
            return res.res_str_id
        except Exception:
            return None

    def d(self):
        return self.dictor(['user_id', 'avatar', 'nickname', 'root_res'])

    """
    增删函数
    """

    @classmethod
    @Excp.pack
    def create(cls, qt_user_app_id, token):
        try:
            user = cls.get_by_qtid(qt_user_app_id)
            user.qtb_token = token
            user.save()
        except Excp as ret:
            if ret.eis(UserError.USER_NOT_FOUND):
                try:
                    user = cls(
                        qt_user_app_id=qt_user_app_id,
                        qtb_token=token,
                    )
                    user.save()
                except Exception as err:
                    return UserError.CREATE_USER
            else:
                return ret
        return user

    @Excp.pack
    def update(self):
        body = qt_manager.get_user_info(self.qtb_token)
        self.avatar = body['avatar']
        self.nickname = body['nickname']
        self.description = body['description']
        self.save()

    def remove(self):
        return self.delete()
