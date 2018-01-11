from Base.error import Error
from Base.response import error_response
from Resource.models import Resource
from Resource.views import get_my_res, upload_res_token, get_res_info, create_folder, get_visit_key, get_dl_link, \
    dlpath_callback, modify_res, create_link, upload_cover_token, cover_callback


def rt_res(request):
    if request.method == "GET":
        return get_my_res(request)


def rt_res_token(request):
    if request.method == "GET":
        return upload_res_token(request)
    return error_response(Error.ERROR_METHOD)


def rt_res_slug(request, slug):
    ret = Resource.decode_slug(slug)
    if ret.error is not Error.OK:
        return error_response(ret)
    request.resource = ret.body

    if request.method == "GET":
        return get_res_info(request)
    if request.method == "PUT":
        return modify_res(request)

    return error_response(Error.ERROR_METHOD)


def rt_res_slug_folder(request, slug):
    ret = Resource.decode_slug(slug)
    if ret.error is not Error.OK:
        return error_response(ret)
    request.resource = ret.body

    if request.method == "POST":
        return create_folder(request)

    return error_response(Error.ERROR_METHOD)


def rt_res_slug_link(request, slug):
    ret = Resource.decode_slug(slug)
    if ret.error is not Error.OK:
        return error_response(ret)
    request.resource = ret.body

    if request.method == "POST":
        return create_link(request)

    return error_response(Error.ERROR_METHOD)


def rt_res_slug_vk(request, slug):
    ret = Resource.decode_slug(slug)
    if ret.error is not Error.OK:
        return error_response(ret)
    request.resource = ret.body

    if request.method == 'GET':
        return get_visit_key(request)

    return error_response(Error.ERROR_METHOD)


def rt_res_slug_dl(request, slug):
    ret = Resource.decode_slug(slug)
    if ret.error is not Error.OK:
        return error_response(ret)
    request.resource = ret.body

    if request.method == "GET":
        return get_dl_link(request)

    return error_response(Error.ERROR_METHOD)


def rt_res_slug_cover(request, slug):
    ret = Resource.decode_slug(slug)
    if ret.error is not Error.OK:
        return error_response(ret)
    request.resource = ret.body

    if request.method == "GET":
        return upload_cover_token(request)
    return error_response(Error.ERROR_METHOD)


def rt_dlpath_callback(request):
    if request.method == "GET":
        return dlpath_callback(request)
    return error_response(Error.ERROR_METHOD)


def rt_cover_callback(request):
    if request.method == "GET":
        return cover_callback(request)
    return error_response(Error.ERROR_METHOD)
