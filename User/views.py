import base64
import json

from Base.decorator import require_json, require_post, require_login, require_get, require_delete, \
    require_put
from Base.error import Error
from Base.jtoken import jwt_e
from Base.policy import get_avatar_policy
from Base.response import response, error_response
from Resource.models import Resource
from User.models import User
from Base.qn import get_upload_token, qiniu_auth_callback


@require_get()
@require_login
def get_my_info(request):
    o_user = request.user
    return get_user_info(request, o_user.pk)


@require_get()
def get_user_info(request, user_id):
    ret = User.get_user_by_id(user_id)
    if ret.error is not Error.OK:
        return error_response(ret)
    o_user = ret.body
    if not isinstance(o_user, User):
        return error_response(Error.STRANGE)
    return response(body=o_user.to_dict())


@require_delete()
@require_login
def delete_user(request, user_id):
    o_parent = request.user
    if not isinstance(o_parent, User):
        return error_response(Error.STRANGE)

    ret = User.get_user_by_id(user_id)
    if ret.error is not Error.OK:
        return error_response(ret)
    o_user = ret.body
    if not isinstance(o_user, User):
        return error_response(Error.STRANGE)
    if o_user.parent != o_parent or o_parent.pk == User.ROOT_ID:
        return error_response(Error.REQUIRE_FATHER_OR_ROOT_DELETE)
    o_user.delete()
    return response()


@require_json
@require_post(['username', 'password', 'nickname'], decode=False)
@require_login
def create_user(request):
    """
    创建用户
    """
    username = request.d.username
    password = request.d.password
    nickname = request.d.nickname

    o_parent = request.user
    if not isinstance(o_parent, User):
        return error_response(Error.STRANGE)

    ret = User.create(username, password, nickname, o_parent)
    if ret.error is not Error.OK:
        return error_response(ret)
    o_user = ret.body
    if not isinstance(o_user, User):
        return error_response(Error.STRANGE)

    ret = Resource.get_res_by_id(Resource.ROOT_ID)
    if ret.error is not Error.OK:
        return error_response(ret)
    o_root = ret.body

    ret = Resource.create_folder(
        o_user.username, o_user, o_root, '# %s Disk Home' % o_user.username, Resource.STATUS_PUBLIC)
    if ret.error is not Error.OK:
        return error_response(ret)

    ret = jwt_e(o_user.to_dict())
    if ret.error is not Error.OK:
        return error_response(ret)
    token, d = ret.body
    d['token'] = token

    return response(body=o_user.to_dict())


@require_json
@require_post(['username', 'password'], decode=False)
def auth_token(request):
    """
    登录获取token
    """
    username = request.d.username
    password = request.d.password

    ret = User.authenticate(username, password)
    if ret.error != Error.OK:
        return error_response(ret)
    o_user = ret.body
    if not isinstance(o_user, User):
        return error_response(Error.STRANGE)

    # save_user_to_session(request, o_user)
    from Base.jtoken import jwt_e
    ret = jwt_e(o_user.to_dict())
    if ret.error is not Error.OK:
        return error_response(ret)
    token, d = ret.body
    d['token'] = token

    return response(body=d)


@require_get([('filename', '^[^\\/?:*<>|]+$')])
@require_login
def upload_avatar_token(request):
    """
    获取七牛上传token
    """
    filename = request.d.filename

    o_user = request.user
    if not isinstance(o_user, User):
        return error_response(Error.STRANGE)

    import datetime
    crt_time = datetime.datetime.now().timestamp()
    key = 'user/%s/avatar/%s/%s' % (o_user.pk, crt_time, filename)
    qn_token, key = get_upload_token(key, get_avatar_policy(o_user.pk))
    return response(body=dict(upload_token=qn_token, key=key))


@require_json
@require_post(['key', 'user_id'])
def upload_avatar_callback(request):
    ret = qiniu_auth_callback(request)
    if ret.error is not Error.OK:
        return error_response(ret)

    key = request.d.key
    user_id = request.d.user_id
    ret = User.get_user_by_id(user_id)
    if ret.error is not Error.OK:
        return error_response(ret)
    o_user = ret.body
    if not isinstance(o_user, User):
        return error_response(Error.STRANGE)
    o_user.modify_avatar(key)
    return response(body=o_user.to_dict())


@require_get(['upload_ret'])
def avatar_callback(request):
    upload_ret = request.d.upload_ret
    # print(upload_ret)
    upload_ret = upload_ret.replace('-', '+').replace('_', '/')
    # print(upload_ret)
    upload_ret = base64.decodebytes(bytes(upload_ret, encoding='utf8')).decode()
    # print(upload_ret)
    upload_ret = json.loads(upload_ret)
    # print(upload_ret)
    key = upload_ret['key']
    user_id = upload_ret['user_id']

    ret = User.get_user_by_id(user_id)
    if ret.error is not Error.OK:
        return error_response(ret)
    o_user = ret.body
    if not isinstance(o_user, User):
        return error_response(Error.STRANGE)
    o_user.modify_avatar(key)
    return response(body=o_user.to_dict())


@require_json
@require_put([('password', None, None), ('old_password', None, None), ('nickname', None, None)], decode=False)
@require_login
def modify_user(request):
    o_user = request.user
    if not isinstance(o_user, User):
        return error_response(Error.STRANGE)

    password = request.d.password
    nickname = request.d.nickname
    old_password = request.d.old_password
    if password is not None:
        ret = o_user.change_password(password, old_password)
        if ret.error is not Error.OK:
            return error_response(ret)
    o_user.modify_info(nickname)
    return response(body=o_user.to_dict())
