from Base.error import Error
from Base.response import error_response
from Resource.models import Resource
from Resource.views import get_my_res, upload_res_token, get_res_info, create_folder, get_visit_key, get_dl_link, \
    dlpath_callback, modify_res


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
    if request.method == "POST":
        return create_folder(request)
    if request.method == "PUT":
        return modify_res(request)

    return error_response(Error.ERROR_METHOD)


def rt_res_visit_key(request, slug):
    ret = Resource.decode_slug(slug)
    if ret.error is not Error.OK:
        return error_response(ret)
    request.resource = ret.body

    if request.method == 'GET':
        return get_visit_key(request)

    return error_response(Error.ERROR_METHOD)


def rt_res_dl(request, slug):
    ret = Resource.decode_slug(slug)
    if ret.error is not Error.OK:
        return error_response(ret)
    request.resource = ret.body

    if request.method == "GET":
        return get_dl_link(request)

    return error_response(Error.ERROR_METHOD)


def rt_dlpath_callback(request):
    if request.method == "GET":
        return dlpath_callback(request)
