""" Adel Liu 180111

用户API处理函数
"""
from SmartDjango import Packing, Analyse, Param
from django.views import View

from Base.auth import Auth

from User.models import User

P_QITIAN_USER_ID = Param('qt_user_app_id', yield_name='user').process(User.get_by_qtid)


class BaseView(View):
    @staticmethod
    @Packing.http_pack
    @Auth.require_login
    def get(r):
        """ GET /api/user/

        获取我的信息
        """
        user = r.user
        ret = user.update()
        if not ret.ok:
            return ret
        return user.d()


class QitianView(View):
    @staticmethod
    @Packing.http_pack
    @Analyse.r(a=[P_QITIAN_USER_ID])
    def get(r, qt_user_app_id):
        """ GET /api/user/@:qt_user_app_id

        获取用户信息
        """
        user = r.d.user

        ret = user.update()
        if not ret.ok:
            return ret
        return user.d()

    @staticmethod
    @Packing.http_pack
    @Analyse.r(a=[P_QITIAN_USER_ID])
    @Auth.require_root
    def delete_user(r, qt_user_app_id):
        """ DELETE /api/user/@:qt_user_app_id

        删除用户
        """
        user = r.d.user
        user.remove()
