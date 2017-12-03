# from Base.common import get_user_from_session, save_user_to_session, logout_user_from_session
from Base.decorator import require_json, require_post, require_login, require_get
from Base.error import Error
from Base.response import response, error_response
from User.models import User
from Base.qn import get_upload_token


@require_json
@require_post(['username', 'password'], decode=False)
@require_login
def create_user(request):
    username = request.d['username']
    password = request.d['password']

    # ret = get_user_from_session(request)
    # if ret.error is not Error.OK:
    #     return error_response(ret.error)
    # o_parent = ret.body
    o_parent = request.user
    if not isinstance(o_parent, User):
        return error_response(Error.STRANGE)

    ret = User.create(username, password, o_parent)
    if ret.error is not Error.OK:
        return error_response(ret.error)
    o_user = ret.body
    if not isinstance(o_user, User):
        return error_response(Error.STRANGE)

    return response(body=o_user.to_dict())


@require_json
@require_post(['username', 'password'], decode=False)
def auth_token(request):
    username = request.d['username']
    password = request.d['password']

    ret = User.authenticate(username, password)
    if ret.error != Error.OK:
        return error_response(ret.error)
    o_user = ret.body
    if not isinstance(o_user, User):
        return error_response(Error.STRANGE)

    # save_user_to_session(request, o_user)
    from Base.jtoken import jwt_e
    ret = jwt_e(o_user.to_dict())
    if ret.error is not Error.OK:
        return error_response(ret.error)
    token, d = ret.body
    d['token'] = token

    return response(body=d)


@require_get
@require_login
def upload_avatar_token(request):
    o_user = request.user
    if not isinstance(o_user, User):
        return error_response(Error.STRANGE)

    key = 'user/avatar/%s' % o_user.pk
    qn_token = get_upload_token(key)
    return response(body=dict(upload_token=qn_token))
