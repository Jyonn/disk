""" Adel Liu 180111

资源API路由
"""
from django.views.decorators.gzip import gzip_page

from Base.error import Error
from Base.response import error_response, response, Method
from Resource.models import Resource
from Resource.views import upload_res_token, get_res_info, create_folder, modify_res, \
    create_link, upload_cover_token, upload_dlpath_callback, upload_cover_callback, \
    delete_res, deal_dl_link, get_res_base_info, direct_link, modify_cover


@gzip_page
def rt_dlpath_callback(request):
    """ /api/res/dlpath/callback

    POST:   upload_dlpath_callback, 七牛上传资源成功后的回调函数
    """
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

    POST:   upload_cover_callback, 七牛上传资源封面成功后的回调函数
    """
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


SUFFIX_DICT = {
    'token': {
        Method.GET: {
            'desc': "获取资源上传",
            'func': upload_res_token,
        }
    },
    'cover': {
        Method.GET: {
            'desc': "获取七牛上传资源封面token",
            'func': upload_cover_token,
        },
        Method.PUT: {
            'desc': "修改封面信息",
            'func': modify_cover,
        },
    },
    'folder': {
        Method.POST: {
            'desc': "上传文件夹资源",
            'func': create_folder,
        }
    },
    'link': {
        Method.POST: {
            'desc': "上传链接资源",
            'func': create_link,
        }
    },
    'base': {
        Method.GET: {
            'desc': "获取资源公开信息",
            'func': get_res_base_info,
        }
    },
    'dl': {
        Method.GET: {
            'desc': "获取资源下载链接",
            'func': deal_dl_link,
        }
    },
    None: {
        Method.GET: {
            'desc': "获取资源信息",
            'func': get_res_info,
        },
        Method.PUT: {
            'desc': "修改资源信息",
            'func': modify_res,
        },
        Method.DELETE: {
            'desc': "删除资源",
            'func': delete_res,
        }
    }
}


@gzip_page
def rt_res(request, res_str_id, suffix=None):
    if suffix not in SUFFIX_DICT:
        return error_response(Error.UNREACHABLE_API)

    ret = Resource.get_res_by_str_id(res_str_id)
    if ret.error is not Error.OK:
        return error_response(ret)
    request.resource = ret.body

    options = SUFFIX_DICT[suffix]
    format_options = {}
    for method in options:
        format_options[method] = options[method]['desc']
    if request.method == Method.OPTIONS:
        return response(body=format_options, allow=True)

    if request.method in options:
        return SUFFIX_DICT[suffix][request.method]['func'](request)

    return error_response(Error.ERROR_METHOD)
