""" Adel Liu 180111

资源API路由
"""
from Base.error import Error
from Base.response import error_response
from Resource.models import Resource
from Resource.views import get_my_res, upload_res_token, get_res_info, create_folder, \
    get_visit_key, get_dl_link, dlpath_callback, modify_res, create_link, \
    upload_cover_token, cover_callback


def rt_res(request):
    """ /api/res

    GET:    get_my_res, 获取我的资源根目录
    """
    if request.method == "GET":
        return get_my_res(request)
    return error_response(Error.ERROR_METHOD)


def rt_res_token(request, parent_id):
    """ /api/res/token

    GET:    upload_res_token, 获取资源上传
    """
    if request.method == "GET":
        return upload_res_token(request, parent_id)
    return error_response(Error.ERROR_METHOD)


def rt_res_slug(request, slug):
    """ /api/res/:slug/

    GET:    get_res_info, 获取资源信息
    PUT:    modify_res, 修改资源信息
    """
    ret = Resource.decode_slug(slug)
    if ret.error is not Error.OK:
        return error_response(ret)
    request.resource = ret.body

    if request.method == "GET":
        return get_res_info(request)
    if request.method == "PUT":
        return modify_res(request)

    return error_response(Error.ERROR_METHOD)


def rt_res_folder(request, res_id):
    """ /api/res/:res_id/folder

    POST:   create_folder, 上传文件夹资源
    """
    if request.method == "POST":
        return create_folder(request, res_id)

    return error_response(Error.ERROR_METHOD)


def rt_res_link(request, res_id):
    """ /api/res/:res_id/link

    POST:   create_link, 上传链接资源
    """
    if request.method == "POST":
        return create_link(request, res_id)

    return error_response(Error.ERROR_METHOD)


def rt_res_vk(request, res_id):
    """ /api/res/:res_id/vk

    GET:    get_visit_key, 获取加密密钥
    """
    if request.method == 'GET':
        return get_visit_key(request, res_id)

    return error_response(Error.ERROR_METHOD)


def rt_res_slug_dl(request, slug):
    """ /api/res/:slug/dl

    GET:    get_dl_link, 获取资源下载链接
    """
    ret = Resource.decode_slug(slug)
    if ret.error is not Error.OK:
        return error_response(ret)
    request.resource = ret.body

    if request.method == "GET":
        return get_dl_link(request)

    return error_response(Error.ERROR_METHOD)


def rt_res_cover(request, res_id):
    """ /api/res/:res_id/cover

    GET:    upload_cover_token, 获取七牛上传资源封面token
    """
    if request.method == "GET":
        return upload_cover_token(request, res_id)
    return error_response(Error.ERROR_METHOD)


def rt_dlpath_callback(request):
    """ /api/res/dlpath/callback

    GET:    dlpath_callback, 七牛上传资源成功后的回调函数
    """
    if request.method == "GET":
        return dlpath_callback(request)
    return error_response(Error.ERROR_METHOD)


def rt_cover_callback(request):
    """ /api/res/cover/callback

    GET:    cover_callback, 七牛上传资源封面成功后的回调函数
    """
    if request.method == "GET":
        return cover_callback(request)
    return error_response(Error.ERROR_METHOD)
