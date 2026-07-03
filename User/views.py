""" Adel Liu 180111

用户API处理函数
"""
from django.views import View
from smartdjango import analyse, OK
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
        force_refresh = str(request.GET.get('refresh', '')).lower() in ('1', 'true', 'yes')
        user.refresh_profile(force=force_refresh, suppress_error=not force_refresh)
        return user.d()


class RefreshView(View):
    @Auth.require_login
    def post(self, request: Request, **kwargs):
        """ POST /api/user/refresh/

        强制刷新我的信息
        """
        user: User = request.user
        user.refresh_profile(force=True, suppress_error=False)
        return user.d()


class QitianView(View):
    @analyse.argument(UserParams.qt_user_getter)
    def get(self, request: Request, **kwargs):
        """ GET /api/user/@:qt_user_app_id

        获取用户信息
        """
        user: User = request.argument.user
        user.refresh_profile(force=False, suppress_error=True)
        return user.d()

    @analyse.argument(UserParams.qt_user_getter)
    @Auth.require_root
    def delete_user(self, request: Request, **kwargs):
        """ DELETE /api/user/@:qt_user_app_id

        删除用户
        """
        user: User = request.argument.user
        user.remove()

        return OK
