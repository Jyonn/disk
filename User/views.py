""" Adel Liu 180111

用户API处理函数
"""
import json

from qiniu import urlsafe_base64_decode

from Base.common import deprint
from Base.decorator import require_json, require_post, require_login, require_get, require_delete, \
    require_put
from Base.error import Error
from Base.jtoken import jwt_e
from Base.policy import get_avatar_policy
from Base.qn import get_upload_token, qiniu_auth_callback
from Base.response import response, error_response
from Config.models import Config

from Resource.models import Resource
from User.models import User


def get_token_info(o_user):
    ret = jwt_e(dict(user_id=o_user.pk))
    if ret.error is not Error.OK:
        return error_response(ret)
    token, dict_ = ret.body
    dict_['token'] = token
    dict_['avatar'] = o_user.get_avatar_url()
    return dict_


@require_get()
@require_login
def get_my_info(request):
    """ GET /api/user/

    获取我的信息
    """
    o_user = request.user
    return get_user_info(request, o_user.username)


@require_get()
def get_user_info(request, username):
    """ GET /api/user/@:username

    获取用户信息
    """
    ret = User.get_user_by_username(username)
    if ret.error is not Error.OK:
        return error_response(ret)
    o_user = ret.body
    if not isinstance(o_user, User):
        return error_response(Error.STRANGE)
    return response(body=o_user.to_dict())


@require_delete()
@require_login
def delete_user(request, username):
    """ DELETE /api/user/@:username

    删除用户
    """
    o_parent = request.user
    if not isinstance(o_parent, User):
        return error_response(Error.STRANGE)

    ret = User.get_user_by_username(username)
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
@require_post(['username', 'password', 'beta_code'])
# @require_login
def create_user(request):
    """ POST /api/user/

    创建用户
    """
    username = request.d.username
    password = request.d.password
    beta_code = request.d.beta_code

    try:
        excepted_bc = Config.objects.get('beta-code').value
    except Exception as err:
        deprint(str(err))
        excepted_bc = 'EXCEPTED_BC'

    if beta_code != excepted_bc:
        return error_response(Error.BETA_CODE_ERROR)

    # o_parent = request.user
    # if not isinstance(o_parent, User):
    #     return error_response(Error.STRANGE)
    ret = User.get_user_by_id(User.ROOT_ID)
    if ret.error is not Error.OK:
        return error_response(ret)
    o_parent = ret.body
    if not isinstance(o_parent, User):
        return error_response(Error.STRANGE)

    ret = User.create(username, password, o_parent)
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
        o_user.username,
        o_user,
        o_root,
        '# %s的盒子' % o_user.username
    )
    if ret.error is not Error.OK:
        return error_response(ret)

    # ret = jwt_e(o_user.to_dict())
    # if ret.error is not Error.OK:
    #     return error_response(ret)
    # token, dict_ = ret.body
    # dict_['token'] = token
    #
    # return response(body=o_user.to_dict())
    return response(body=get_token_info(o_user))


@require_json
@require_post(['username', 'password'])
def auth_token(request):
    """ GET /api/user/token

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

    # ret = jwt_e(dict(user_id=o_user.pk))
    # if ret.error is not Error.OK:
    #     return error_response(ret)
    # token, dict_ = ret.body
    # dict_['token'] = token
    # dict_['avatar'] = o_user.get_avatar_url()
    #
    # return response(body=dict_)
    return response(body=get_token_info(o_user))


@require_get([('filename', Resource.pub_valid_rname)])
@require_login
def upload_avatar_token(request):
    """ GET /api/user/avatar

    获取七牛上传token
    """
    o_user = request.user
    filename = request.d.filename

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
    """ POST /api/user/avatar/callback

    七牛上传用户头像回调函数
    """
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
def upload_avatar_redirect(request):
    """ GET /api/user/avatar/callback

    七牛上传用户头像303重定向
    """
    upload_ret = request.d.upload_ret
    upload_ret = urlsafe_base64_decode(upload_ret)
    # upload_ret = upload_ret.replace('-', '+').replace('_', '/')
    # upload_ret = base64.decodebytes(bytes(upload_ret, encoding='utf8')).decode()
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
@require_put(
    [
        ('password', None, None),
        ('old_password', None, None),
        ('nickname', None, None)
    ]
)
@require_login
def modify_user(request):
    """ PUT /api/user/

    修改用户信息
    """
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
