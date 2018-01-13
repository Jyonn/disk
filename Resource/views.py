""" Adel Liu 180111

资源API处理函数
"""
import base64
import json

from Base.decorator import require_get, require_login, require_json, require_post, maybe_login, \
    require_put
from Base.error import Error
from Base.policy import get_res_policy, get_cover_policy
from Base.qn import get_upload_token, qiniu_auth_callback
from Base.response import response, error_response
from Resource.models import Resource
from User.models import User


@require_json
@require_post(['folder_name', 'description'])
@require_login
def create_folder(request, res_id):
    """ POST /api/res/:res_id/folder

    上传文件夹资源
    """
    o_user = request.user

    folder_name = request.d.folder_name
    desc = request.d.description

    # get parent folder
    ret = Resource.get_res_by_id(res_id)
    o_parent = ret.body

    if not o_parent.belong(o_user):
        return error_response(Error.PARENT_NOT_BELONG)

    ret = Resource.create_folder(folder_name, o_user, o_parent, desc)
    if ret.error is not Error.OK:
        return error_response(ret)
    o_res = ret.body
    if not isinstance(o_res, Resource):
        return error_response(Error.STRANGE)
    return response(body=o_res.to_dict())


@require_json
@require_post(['link_name', 'description', 'link'])
@require_login
def create_link(request, res_id):
    """ POST /api/res/:res_id/link

    上传链接资源
    """
    o_user = request.user

    link_name = request.d.link_name
    desc = request.d.description
    link = request.d.link

    ret = Resource.get_res_by_id(res_id)
    if ret.error is not Error.OK:
        return error_response(ret)
    o_parent = ret.body

    if not o_parent.belong(o_user):
        return error_response(Error.PARENT_NOT_BELONG)

    ret = Resource.create_link(link_name, o_user, o_parent, desc, link)
    if ret.error is not Error.OK:
        return error_response(ret)
    o_res = ret.body
    if not isinstance(o_res, Resource):
        return error_response(Error.STRANGE)
    return response(body=o_res.to_dict())


@require_get()
@require_login
def get_my_res(request):
    """ GET /api/res/

    获取我的资源根目录
    """
    o_user = request.user
    ret = Resource.get_root_folder(o_user)
    if ret.error is not Error.OK:
        return error_response(ret)
    o_res = ret.body
    if not isinstance(o_res, Resource):
        return error_response(Error.STRANGE)
    request.resource = o_res
    return get_res_info(request)


@require_get([('visit_key', None, None)])
@maybe_login
def get_res_info(request):
    """ GET /api/res/:slug

    获取资源信息
    """
    o_user = request.user
    o_res = request.resource
    visit_key = request.d.visit_key

    if not isinstance(o_res, Resource):
        return error_response(Error.STRANGE)

    if not o_res.readable(o_user, visit_key):
        return error_response(Error.NOT_READABLE)

    ret = o_res.get_child_res_list()
    if ret.error is not Error.OK:
        return error_response(ret)
    res_list = ret.body
    return response(body=dict(info=o_res.to_dict(), child_list=res_list))


@require_get()
@require_login
def get_visit_key(request, res_id):
    """ GET /api/res/:res_id/vk

    获取加密密钥
    """
    o_user = request.user

    ret = Resource.get_res_by_id(res_id)
    if ret.error is not Error.OK:
        return error_response(ret)
    o_res = ret.body

    if not isinstance(o_res, Resource):
        return error_response(Error.STRANGE)

    if not o_res.belong(o_user):
        return error_response(Error.NOT_READABLE)
    return response(body=dict(visit_key=o_res.get_visit_key(), status=o_res.status))


@require_get([('visit_key', None, None)])
@maybe_login
def get_dl_link(request):
    """ GET /api/res/:slug/dl

    获取资源下载链接
    """
    o_user = request.user
    visit_key = request.d.visit_key

    o_res = request.resource
    if not isinstance(o_res, Resource):
        return error_response(Error.STRANGE)

    if not o_res.readable(o_user, visit_key):
        return error_response(Error.NOT_READABLE)

    if o_res.rtype == Resource.RTYPE_LINK:
        return response(body=dict(link=o_res.dlpath))
    if o_res.rtype != Resource.RTYPE_FILE:
        return error_response(Error.REQUIRE_FILE)

    return response(body=dict(link=o_res.get_dl_url()))


def deal_upload_dlpath(key, user_id, fsize, fname, parent_id, ftype):
    if ftype.find('video') == 0:
        sub_type = Resource.STYPE_VIDEO
    elif ftype.find('image') == 0:
        sub_type = Resource.STYPE_IMAGE
    elif ftype.find('audio') == 0:
        sub_type = Resource.STYPE_MUSIC
    else:
        sub_type = Resource.STYPE_FILE

    ret = User.get_user_by_id(user_id)
    if ret.error is not Error.OK:
        return error_response(ret)
    o_user = ret.body
    if not isinstance(o_user, User):
        return error_response(Error.STRANGE)

    ret = Resource.get_res_by_id(parent_id)
    if ret.error is not Error.OK:
        return error_response(ret)
    o_parent = ret.body
    if not isinstance(o_parent, Resource):
        return error_response(Error.STRANGE)

    if not o_parent.belong(o_user):
        return error_response(Error.PARENT_NOT_BELONG)

    ret = Resource.create_file(fname, o_user, o_parent, key, fsize, sub_type)
    if ret.error is not Error.OK:
        return error_response(ret)
    o_res = ret.body
    if not isinstance(o_res, Resource):
        return error_response(Error.STRANGE)
    return response(body=o_res.to_dict())


@require_json
@require_post(['key', 'user_id', 'fsize', 'fname', 'parent_id', 'ftype'])
def upload_dlpath_callback(request):
    """ POST /api/res/dlpath/callback

    七牛上传资源回调函数
    """
    ret = qiniu_auth_callback(request)
    if ret.error is not Error.OK:
        return error_response(ret)

    key = request.d.key
    user_id = request.d.user_id
    fsize = request.d.fsize
    fname = request.d.fname
    parent_id = request.d.parent_id
    ftype = request.d.ftype

    return deal_upload_dlpath(key, user_id, fsize, fname, parent_id, ftype)


@require_get(['upload_ret'])
def upload_dlpath_redirect(request):
    """ GET /api/res/dlpath/callback

    七牛上传资源成功后的回调函数
    """
    upload_ret = request.d.upload_ret
    upload_ret = upload_ret.replace('-', '+').replace('_', '/')
    upload_ret = base64.decodebytes(bytes(upload_ret, encoding='utf8')).decode()
    upload_ret = json.loads(upload_ret)

    key = upload_ret['key']
    user_id = upload_ret['user_id']
    fsize = upload_ret['fsize']
    fname = upload_ret['fname']
    parent_id = upload_ret['parent_id']
    ftype = upload_ret['ftype']

    return deal_upload_dlpath(key, user_id, fsize, fname, parent_id, ftype)


def deal_cover_dlpath(key, res_id):
    ret = Resource.get_res_by_id(res_id)
    if ret.error is not Error.OK:
        return error_response(ret)
    o_res = ret.body
    if not isinstance(o_res, Resource):
        return error_response(Error.STRANGE)

    o_res.modify_cover(key)
    return response(body=o_res.to_dict())


@require_json
@require_post(['key', 'res_id'])
def upload_cover_callback(request):
    """ POST /api/res/cover/callback

    七牛上传资源封面成功后的回调函数
    """
    print(request.body)
    ret = qiniu_auth_callback(request)
    if ret.error is not Error.OK:
        return error_response(ret)

    key = request.d.key
    res_id = request.d.res_id

    return deal_cover_dlpath(key, res_id)


@require_get(['upload_ret'])
def upload_cover_redirect(request):
    """ GET /api/res/cover/callback

    七牛上传资源封面成功后的重定向
    """
    upload_ret = request.d.upload_ret
    upload_ret = upload_ret.replace('-', '+').replace('_', '/')
    upload_ret = base64.decodebytes(bytes(upload_ret, encoding='utf8')).decode()
    upload_ret = json.loads(upload_ret)

    key = upload_ret['key']
    res_id = upload_ret['res_id']

    return deal_cover_dlpath(key, res_id)


@require_json
@require_put(
    [
        ('rname', None, None),
        ('status', None, None),
        ('description', None, None),
        ('visit_key', None, None)
    ]
)
@require_login
def modify_res(request):
    """ PUT /api/res/:slug/

    修改资源信息
    """
    o_user = request.user
    rname = request.d.rname
    description = request.d.description
    status = request.d.status
    visit_key = request.d.visit_key

    o_res = request.resource
    if not isinstance(o_res, Resource):
        return error_response(Error.STRANGE)
    if not o_res.belong(o_user):
        return error_response(Error.NOT_WRITEABLE)
    ret = o_res.modify_info(rname, description, status, visit_key)
    if ret.error is not Error.OK:
        return error_response(ret)
    return response(body=o_res.to_dict())


@require_get([('filename', Resource.pub_valid_rname)])
@require_login
def upload_res_token(request, parent_id):
    """ GET /api/res/:res_id/token

    获取七牛上传资源token
    """
    o_user = request.user
    filename = request.d.filename

    if not isinstance(o_user, User):
        return error_response(Error.STRANGE)

    ret = Resource.get_res_by_id(parent_id)
    if ret.error is not Error.OK:
        return error_response(ret)
    o_parent = ret.body
    if not isinstance(o_parent, Resource):
        return error_response(Error.STRANGE)

    if not o_parent.belong(o_user):
        return error_response(Error.PARENT_NOT_BELONG)

    import datetime
    crt_time = datetime.datetime.now().timestamp()
    key = 'res/%s/%s/%s' % (o_user.pk, crt_time, filename)
    qn_token, key = get_upload_token(key, get_res_policy(o_user.pk, o_parent.pk))
    return response(body=dict(upload_token=qn_token, key=key))


@require_get([('filename', Resource.pub_valid_rname)])
@require_login
def upload_cover_token(request, res_id):
    """ GET /api/res/:res_id/cover

    获取七牛上传资源封面token
    """
    o_user = request.user
    filename = request.d.filename

    if not isinstance(o_user, User):
        return error_response(Error.STRANGE)

    ret = Resource.get_res_by_id(res_id)
    if ret.error is not Error.OK:
        return error_response(ret)
    o_res = ret.body
    if not isinstance(o_res, Resource):
        return error_response(Error.STRANGE)

    if not o_res.belong(o_user):
        return error_response(Error.NOT_WRITEABLE)

    import datetime
    crt_time = datetime.datetime.now().timestamp()
    key = 'cover/%s/%s/%s' % (o_res.pk, crt_time, filename)
    qn_token, key = get_upload_token(key, get_cover_policy(o_res.pk))
    return response(body=dict(upload_token=qn_token, key=key))
