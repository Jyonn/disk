""" Adel Liu 180111

资源API路由
"""
from django.views.decorators.gzip import gzip_page

from Base.error import Error
from Base.response import error_response, response, Method
from Resource.models import Resource
from Resource.views import upload_res_token, get_res_info, create_folder, \
    upload_dlpath_redirect, modify_res, create_link, upload_cover_token, upload_cover_redirect, \
    upload_dlpath_callback, upload_cover_callback, delete_res, deal_dl_link, get_res_base_info, \
    direct_link


# @gzip_page
# def rt_res(request):
#     """ /api/res
#
#     GET:    get_my_res, 获取我的资源根目录
#     """
#     options = {
#         Method.GET: "获取我的资源根目录"
#     }
#     if request.method == Method.OPTIONS:
#         return response(body=options, allow=True)
#
#     if request.method == Method.GET:
#         return get_my_res(request)
#
#     return error_response(Error.ERROR_METHOD)


@gzip_page
def rt_res_token(request, parent_str_id):
    """ /api/res/token

    GET:    upload_res_token, 获取资源上传
    """
    options = {
        Method.GET: "获取资源上传",
    }
    if request.method == Method.OPTIONS:
        return response(body=options, allow=True)

    if request.method == Method.GET:
        return upload_res_token(request, parent_str_id)
    return error_response(Error.ERROR_METHOD)


@gzip_page
def rt_res_slug(request, slug):
    """ /api/res/:slug/

    GET:    get_res_info, 获取资源信息
    PUT:    modify_res, 修改资源信息
    DELETE: delete_res, 删除资源
    """
    options = {
        Method.GET: "获取资源信息",
        Method.PUT: "修改资源信息",
        Method.DELETE: "删除资源"
    }
    if request.method == Method.OPTIONS:
        return response(body=options, allow=True)

    ret = Resource.decode_slug(slug)
    if ret.error is not Error.OK:
        return error_response(ret)
    request.resource = ret.body

    if request.method == Method.GET:
        return get_res_info(request)
    if request.method == Method.PUT:
        return modify_res(request)
    if request.method == Method.DELETE:
        return delete_res(request)
    return error_response(Error.ERROR_METHOD)


@gzip_page
def rt_res_folder(request, res_str_id):
    """ /api/res/:res_str_id/folder

    POST:   create_folder, 上传文件夹资源
    """
    options = {
        Method.POST: "上传文件夹资源",
    }
    if request.method == Method.OPTIONS:
        return response(body=options, allow=True)

    if request.method == Method.POST:
        return create_folder(request, res_str_id)
    return error_response(Error.ERROR_METHOD)


@gzip_page
def rt_res_link(request, res_str_id):
    """ /api/res/:res_str_id/link

    POST:   create_link, 上传链接资源
    """
    options = {
        Method.POST: "上传链接资源",
    }
    if request.method == Method.OPTIONS:
        return response(body=options, allow=True)

    if request.method == Method.POST:
        return create_link(request, res_str_id)
    return error_response(Error.ERROR_METHOD)


@gzip_page
def rt_res_slug_dl(request, slug):
    """ /api/res/:slug/dl

    GET:    get_dl_link, 获取资源下载链接
    """
    options = {
        Method.GET: "获取资源下载链接",
    }
    if request.method == Method.OPTIONS:
        return response(body=options, allow=True)

    ret = Resource.decode_slug(slug)
    if ret.error is not Error.OK:
        return error_response(ret)
    request.resource = ret.body

    if request.method == Method.GET:
        return deal_dl_link(request)
    return error_response(Error.ERROR_METHOD)


@gzip_page
def rt_res_slug_base(request, slug):
    """ /api/res/:slug/base

    GET:    get_status, 获取资源公开信息
    """
    options = {
        Method.GET: "获取资源公开信息",
    }
    if request.method == Method.OPTIONS:
        return response(body=options, allow=True)

    ret = Resource.decode_slug(slug)
    if ret.error is not Error.OK:
        return error_response(ret)
    request.resource = ret.body

    if request.method == Method.GET:
        return get_res_base_info(request)
    return error_response(Error.ERROR_METHOD)


@gzip_page
def rt_res_cover(request, res_str_id):
    """ /api/res/:res_str_id/cover

    GET:    upload_cover_token, 获取七牛上传资源封面token
    """
    options = {
            Method.GET: "获取七牛上传资源封面token",
    }
    if request.method == Method.OPTIONS:
        return response(body=options, allow=True)

    if request.method == Method.GET:
        return upload_cover_token(request, res_str_id)
    return error_response(Error.ERROR_METHOD)


@gzip_page
def rt_dlpath_callback(request):
    """ /api/res/dlpath/callback

    # GET:    upload_dlpath_redirect, 七牛上传资源成功后的回调函数（303重定向）
    POST:   upload_dlpath_callback, 七牛上传资源成功后的回调函数
    """
    # if request.method == Method.GET:
    #     return upload_dlpath_redirect(request)
    options = {
        Method.POST: "七牛上传资源成功后的回调函数",
    }
    if request.method == Method.OPTIONS:
        return response(body=options, allow=True)

    if request.method == Method.POST:
        return upload_dlpath_callback(request)
    return error_response(Error.ERROR_METHOD)


@gzip_page
def rt_cover_callback(request):
    """ /api/res/cover/callback

    # GET:    upload_cover_redirect, 七牛上传资源封面成功后的回调函数（303重定向）
    POST:   upload_cover_callback, 七牛上传资源封面成功后的回调函数
    """
    # if request.method == Method.GET:
    #     return upload_cover_redirect(request)
    options = {
        Method.POST: "七牛上传资源封面成功后的回调函数",
    }
    if request.method == Method.OPTIONS:
        return response(body=options, allow=True)

    if request.method == Method.POST:
        # print(request.body)
        return upload_cover_callback(request)
    return error_response(Error.ERROR_METHOD)


def rt_direct_link(request, res_str_id):
    """ /s/:res_str_id

    GET: direct_link, 直链分享解析
    """

    options = {
        Method.GET: "直链分享解析",
    }
    if request.method == Method.OPTIONS:
        return response(body=options, allow=True)

    find_dot = res_str_id.find('.')
    if find_dot != -1:
        res_str_id = res_str_id[:find_dot]
    ret = Resource.get_res_by_str_id(res_str_id)
    if ret.error is not Error.OK:
        return error_response(ret)

    request.resource = ret.body
    if request.method == Method.GET:
        return direct_link(request)
    return error_response(Error.ERROR_METHOD)