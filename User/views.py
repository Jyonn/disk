from Base.decorator import require_json, require_post, require_login, require_get
from Base.error import Error
from Base.policy import get_avatar_policy
from Base.response import response, error_response
from User.models import User
from Base.qn import get_upload_token, auth_callback


@require_json
@require_post(['username', 'password'], decode=False)
@require_login
def create_user(request):
    """
    创建用户
    """
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
    """
    登录获取token
    """
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


@require_get(['filename'])
@require_login
def upload_avatar_token(request):
    """
    获取七牛上传token
    """
    filename = request.d['filename']

    o_user = request.user
    if not isinstance(o_user, User):
        return error_response(Error.STRANGE)

    import datetime
    key = 'user/%s/avatar/%s/%s' % (o_user.pk, datetime.datetime.now().timestamp(), filename)
    qn_token, key = get_upload_token(key, get_avatar_policy(o_user.pk))
    return response(body=dict(upload_token=qn_token, key=key))


@require_json
@require_post(['key', 'user_id'])
def upload_avatar_callback(request):
    ret = auth_callback(request)
    if ret.error is not Error.OK:
        return error_response(ret.error)

    key = request.d['key']
    user_id = request.d['user_id']
    ret = User.get_user_by_id(user_id)
    if ret.error is not Error.OK:
        return error_response(ret.error)
    o_user = ret.body
    if not isinstance(o_user, User):
        return error_response(Error.STRANGE)
    o_user.avatar = key
    o_user.save()
    return response(body=o_user.to_dict())
