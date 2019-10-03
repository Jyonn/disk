""" Adel Liu 180111

用户API处理函数
"""
from SmartDjango import Excp, Analyse, P
from django.views import View

from Base.auth import Auth

from User.models import User

P_QITIAN_USER = P('qt_user_app_id').process(P.Processor(User.get_by_qtid, yield_name='user'))


class BaseView(View):
    @staticmethod
    @Excp.handle
    @Auth.require_login
    def get(r):
        """ GET /api/user/

        获取我的信息
        """
        user = r.user
        user.update()
        return user.d()


class QitianView(View):
    @staticmethod
    @Excp.handle
    @Analyse.r(a=[P_QITIAN_USER])
    def get(r, qt_user_app_id):
        """ GET /api/user/@:qt_user_app_id

        获取用户信息
        """
        user = r.d.user
        user.update()
        return user.d()

    @staticmethod
    @Excp.handle
    @Analyse.r(a=[P_QITIAN_USER])
    @Auth.require_root
    def delete_user(r, qt_user_app_id):
        """ DELETE /api/user/@:qt_user_app_id

        删除用户
        """
        user = r.d.user
        user.remove()
