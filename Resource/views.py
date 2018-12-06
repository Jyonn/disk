""" Adel Liu 180111

资源API处理函数
"""
import json

from django.http import HttpResponseRedirect
from qiniu import urlsafe_base64_decode

from Base.decorator import require_get, require_json, require_post, maybe_login, \
    require_put, require_delete, require_owner
from Base.error import Error
from Base.policy import get_res_policy, get_cover_policy
from Base.qn import QN_RES_MANAGER
from Base.response import response, error_response
from Resource.models import Resource
from User.models import User


@require_json
@require_post(['folder_name'])
@require_owner
def create_folder(request):
    """ POST /api/res/:res_str_id/folder

    上传文件夹资源
    """
    o_user = request.user

    folder_name = request.d.folder_name

    # get parent folder
    o_parent = request.resource
    if not isinstance(o_parent, Resource):
        return error_response(Error.STRANGE)

    ret = Resource.create_folder(folder_name, o_user, o_parent)
    if ret.error is not Error.OK:
        return error_response(ret)
    o_res = ret.body
    if not isinstance(o_res, Resource):
        return error_response(Error.STRANGE)
    return response(body=o_res.to_dict())


@require_json
@require_post(['link_name', 'link'])
@require_owner
def create_link(request):
    """ POST /api/res/:res_str_id/link

    上传链接资源
    """
    o_user = request.user

    link_name = request.d.link_name
    link = request.d.link

    o_parent = request.resource
    if not isinstance(o_parent, Resource):
        return error_response(Error.STRANGE)

    ret = Resource.create_link(link_name, o_user, o_parent, link)
    if ret.error is not Error.OK:
        return error_response(ret)
    o_res = ret.body
    if not isinstance(o_res, Resource):
        return error_response(Error.STRANGE)
    return response(body=o_res.to_dict())


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

    return response(o_res.to_dict_with_children())


@require_get()
@require_owner
def get_res_info_for_selector(request):
    o_res = request.resource
    if not isinstance(o_res, Resource):
        return error_response(Error.STRANGE)
    return response(o_res.to_dict_for_selector())


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
        return HttpResponseRedirect(o_res.dlpath)
    if o_res.rtype != Resource.RTYPE_FILE:
        return error_response(Error.REQUIRE_FILE)

    return HttpResponseRedirect(o_res.get_dl_url())
    # return response(body=dict(link=o_res.get_dl_url()))


@require_get([
    ('token', None, None),
    ('visit_key', None, None),
])
def deal_dl_link(request):
    """ GET /api/res/:res_str_id/dl

    获取下载资源链接
    """
    request.META['HTTP_TOKEN'] = request.d.token
    return get_dl_link(request)


@require_get()
@maybe_login
def get_res_base_info(request):
    """ GET /api/res/:res_str_id/base

    获取资源公开信息
    """
    o_user = request.user

    o_res = request.resource
    if not isinstance(o_res, Resource):
        return error_response(Error.STRANGE)

    return response(body=dict(
        info=o_res.to_base_dict(),
        readable=o_res.readable(o_user, None)
    ))


def deal_upload_dlpath(key, user_id, fsize, fname, parent_str_id, ftype):
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

    ret = Resource.get_res_by_str_id(parent_str_id)
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
@require_post(['key', 'user_id', 'fsize', 'fname', 'parent_str_id', 'ftype'])
def upload_dlpath_callback(request):
    """ POST /api/res/dlpath/callback

    七牛上传资源回调函数
    """
    ret = QN_RES_MANAGER.qiniu_auth_callback(request)
    if ret.error is not Error.OK:
        return error_response(ret)

    key = request.d.key
    user_id = request.d.user_id
    fsize = request.d.fsize
    fname = request.d.fname
    parent_str_id = request.d.parent_str_id
    ftype = request.d.ftype

    return deal_upload_dlpath(key, user_id, fsize, fname, parent_str_id, ftype)


@require_get(['upload_ret'])
def upload_dlpath_redirect(request):
    """ GET /api/res/dlpath/callback

    七牛上传资源成功后的回调函数
    """
    upload_ret = request.d.upload_ret
    upload_ret = urlsafe_base64_decode(upload_ret)
    # upload_ret = upload_ret.replace('-', '+').replace('_', '/')
    # upload_ret = base64.decodebytes(bytes(upload_ret, encoding='utf8')).decode()
    upload_ret = json.loads(upload_ret)

    key = upload_ret['key']
    user_id = upload_ret['user_id']
    fsize = upload_ret['fsize']
    fname = upload_ret['fname']
    parent_str_id = upload_ret['parent_str_id']
    ftype = upload_ret['ftype']

    return deal_upload_dlpath(key, user_id, fsize, fname, parent_str_id, ftype)


def deal_cover_dlpath(key, res_str_id):
    ret = Resource.get_res_by_str_id(res_str_id)
    if ret.error is not Error.OK:
        return error_response(ret)
    o_res = ret.body
    if not isinstance(o_res, Resource):
        return error_response(Error.STRANGE)

    ret = o_res.modify_cover(key, Resource.COVER_UPLOAD)
    if ret.error is not Error.OK:
        return error_response(ret)
    return response(o_res.to_dict())


@require_json
@require_put(['cover', 'cover_type'])
def modify_cover(request):
    """ PUT /api/res/:res_str_id/cover

    修改封面信息
    """
    cover = request.d.cover
    cover_type = request.d.cover_type

    o_res = request.resource
    if not isinstance(o_res, Resource):
        return error_response(Error.STRANGE)

    if cover_type == Resource.COVER_UPLOAD:
        return error_response(Error.NOT_ALLOWED_COVER_UPLOAD)
    if cover_type == Resource.COVER_SELF and o_res.sub_type != Resource.STYPE_IMAGE:
        return error_response(Error.NOT_ALLOWED_COVER_SELF_OF_NOT_IMAGE)

    ret = o_res.modify_cover(cover, cover_type)
    if ret.error is not Error.OK:
        return error_response(ret)
    return response(o_res.to_dict())


@require_json
@require_post(['key', 'res_str_id'])
def upload_cover_callback(request):
    """ POST /api/res/cover/callback

    七牛上传资源封面成功后的回调函数
    """
    ret = QN_RES_MANAGER.qiniu_auth_callback(request)
    if ret.error is not Error.OK:
        return error_response(ret)

    key = request.d.key
    res_str_id = request.d.res_str_id

    return deal_cover_dlpath(key, res_str_id)


@require_get(['upload_ret'])
def upload_cover_redirect(request):
    """ GET /api/res/cover/callback

    七牛上传资源封面成功后的重定向
    """
    upload_ret = request.d.upload_ret
    upload_ret = urlsafe_base64_decode(upload_ret)
    # upload_ret = upload_ret.replace('-', '+').replace('_', '/')
    # upload_ret = base64.decodebytes(bytes(upload_ret, encoding='utf8')).decode()
    upload_ret = json.loads(upload_ret)

    key = upload_ret['key']
    res_str_id = upload_ret['res_str_id']

    return deal_cover_dlpath(key, res_str_id)


@require_json
@require_put(
    [
        ('rname', None, None),
        ('status', None, None),
        ('description', None, None),
        ('visit_key', None, None),
        ('right_bubble', None, None),
        ('parent_str_id', None, None),
    ]
)
@require_owner
def modify_res(request):
    """ PUT /api/res/:slug/

    修改资源信息
    """
    o_user = request.user
    rname = request.d.rname
    description = request.d.description
    status = request.d.status
    visit_key = request.d.visit_key
    right_bubble = request.d.right_bubble
    parent_str_id = request.d.parent_str_id

    o_res = request.resource
    if not isinstance(o_res, Resource):
        return error_response(Error.STRANGE)

    if parent_str_id:
        ret = Resource.get_res_by_str_id(parent_str_id)
        if ret.error is not Error.OK:
            return error_response(ret)
        o_parent = ret.body
        if not isinstance(o_parent, Resource):
            return error_response(Error.STRANGE)
        if not o_parent.belong(o_user):
            return error_response(Error.NOT_YOUR_RESOURCE)
        if not o_parent.rtype != Resource.RTYPE_FOLDER:
            return error_response(Error.REQUIRE_FOLDER)
    else:
        o_parent = None

    ret = o_res.modify_info(rname, description, status, visit_key, right_bubble, o_parent)
    if ret.error is not Error.OK:
        return error_response(ret)
    return response(body=o_res.to_dict())


@require_get([('filename', Resource.pub_valid_rname)])
@require_owner
def upload_res_token(request):
    """ GET /api/res/:res_str_id/token

    获取七牛上传资源token
    """
    o_user = request.user
    filename = request.d.filename

    if not isinstance(o_user, User):
        return error_response(Error.STRANGE)

    o_parent = request.resource
    if not isinstance(o_parent, Resource):
        return error_response(Error.STRANGE)

    import datetime
    crt_time = datetime.datetime.now().timestamp()
    key = 'res/%s/%s/%s' % (o_user.pk, crt_time, filename)
    qn_token, key = QN_RES_MANAGER.get_upload_token(
        key, get_res_policy(filename, o_user.pk, o_parent.res_str_id))
    return response(body=dict(upload_token=qn_token, key=key))


@require_get([('filename', Resource.pub_valid_rname)])
@require_owner
def upload_cover_token(request):
    """ GET /api/res/:res_str_id/cover

    获取七牛上传资源封面token
    """
    filename = request.d.filename

    o_res = request.resource
    if not isinstance(o_res, Resource):
        return error_response(Error.STRANGE)

    import datetime
    crt_time = datetime.datetime.now().timestamp()
    key = 'cover/%s/%s/%s' % (o_res.pk, crt_time, filename)
    qn_token, key = QN_RES_MANAGER.get_upload_token(key, get_cover_policy(o_res.res_str_id))
    return response(body=dict(upload_token=qn_token, key=key))


@require_delete()
@require_owner
def delete_res(request):
    """ DELETE /api/res/:slug

    删除资源
    """
    o_res = request.resource
    if not isinstance(o_res, Resource):
        return error_response(Error.STRANGE)

    if o_res.parent == Resource.ROOT_ID:
        return error_response(Error.ERROR_DELETE_ROOT_FOLDER)

    ret = o_res.delete_()
    if ret.error is not Error.OK:
        return error_response(ret)
    return response()


def direct_link(request):
    """ GET /l/:res_str_id

    直链解析，允许在资源ID后加扩展名
    """
    return get_dl_link(request)
