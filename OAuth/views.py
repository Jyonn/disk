from Base.decorator import require_get
from Base.error import Error
from Base.qtb import get_qtb_user_token
from Base.response import error_response, response
from Resource.models import Resource
from User.models import User
from User.views import get_token_info


@require_get(['code'])
def oauth_qtb_callback(request):
    code = request.d.code

    ret = get_qtb_user_token(code)
    if ret.error is not Error.OK:
        return error_response(ret)
    body = ret.body
    token = body['token']
    qt_user_app_id = body['user_app_id']

    ret = User.create(qt_user_app_id, token)
    if ret.error is not Error.OK:
        return error_response(ret)
    o_user = ret.body
    if not isinstance(o_user, User):
        return error_response(Error.STRANGE)

    ret = Resource.get_root_folder(o_user)
    if ret.error is Error.ERROR_GET_ROOT_FOLDER:
        ret = Resource.get_res_by_id(Resource.ROOT_ID)
        if ret.error is not Error.OK:
            return error_response(ret)
        o_root = ret.body

        ret = Resource.create_folder(
            o_user.qt_user_app_id,
            o_user,
            o_root,
            '# 我的浑天匣'
        )
        if ret.error is not Error.OK:
            return error_response(ret)

    ret = o_user.update()
    if ret.error is not Error.OK:
        return error_response(ret)
    return response(body=get_token_info(o_user))
