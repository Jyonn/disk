""" Adel Liu 180111

用户API处理函数
"""

from Base.decorator import require_login, require_get, require_delete, require_root
from Base.error import Error
from Base.jtoken import jwt_e
from Base.response import response, error_response

from User.models import User


def get_token_info(o_user):
    ret = jwt_e(dict(user_id=o_user.pk))
    # if ret.error is not Error.OK:
    #     return error_response(ret)
    token, dict_ = ret.body
    user_dict = o_user.to_dict()
    user_dict['token'] = token
    return user_dict


@require_get()
@require_login
def get_my_info(request):
    """ GET /api/user/

    获取我的信息
    """
    o_user = request.user
    return get_user_info(request, o_user.qt_user_app_id)


@require_get()
def get_user_info(request, qt_user_app_id):
    """ GET /api/user/@:qt_user_app_id

    获取用户信息
    """
    ret = User.get_user_by_qt_user_app_id(qt_user_app_id)
    if ret.error is not Error.OK:
        return error_response(ret)
    o_user = ret.body
    if not isinstance(o_user, User):
        return error_response(Error.STRANGE)
    ret = o_user.update()
    if ret.error is Error.REQUIRE_RELOGIN:
        return error_response(ret)
    return response(body=o_user.to_dict())


@require_delete()
@require_root
def delete_user(request, qt_user_app_id):
    """ DELETE /api/user/@:qt_user_app_id

    删除用户
    """

    ret = User.get_user_by_qt_user_app_id(qt_user_app_id)
    if ret.error is not Error.OK:
        return error_response(ret)
    o_user = ret.body
    if not isinstance(o_user, User):
        return error_response(Error.STRANGE)
    o_user.delete()
    return response()
