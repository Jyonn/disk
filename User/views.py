""" Adel Liu 180111

用户API处理函数
"""
from django.views import View
from smartdjango import analyse
from smartdjango.analyse import Request

from Base.auth import Auth

from User.models import User
from User.params import UserParams


class BaseView(View):
    @Auth.require_login
    def get(self, request: Request, **kwargs):
        """ GET /api/user/

        获取我的信息
        """
        user: User = request.user
        user.update()
        return user.d()


class QitianView(View):
    @analyse.argument(UserParams.qt_user_getter)
    def get(self, request: Request, **kwargs):
        """ GET /api/user/@:qt_user_app_id

        获取用户信息
        """
        user: User = request.argument.user
        user.update()
        return user.d()

    @analyse.argument(UserParams.qt_user_getter)
    @Auth.require_root
    def delete_user(self, request: Request, **kwargs):
        """ DELETE /api/user/@:qt_user_app_id

        删除用户
        """
        user: User = request.argument.user
        user.remove()
