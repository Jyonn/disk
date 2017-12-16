from Base.error import Error
from Base.response import error_response
from Resource.models import Resource
from Resource.views import upload_res_token, get_res_info


def rt_res_token(request):
    if request.method == "GET":
        return upload_res_token(request)
    return error_response(Error.ERROR_METHOD)


def rt_res(request, slug):
    slug_list = slug.split('-')

    ret = Resource.get_res_by_id(Resource.ROOT_ID)
    if ret.error is not Error.OK:
        return error_response(ret.error)
    o_res_parent = ret.body

    for rid in slug_list:
        ret = Resource.get_res_by_id(rid)
        if ret.error is not Error.OK:
            return error_response(ret.error)
        o_res_crt = ret.body
        if not isinstance(o_res_crt, Resource):
            return error_response(Error.STRANGE)
        if o_res_crt.parent != o_res_parent:
            return error_response(Error.ERROR_RESOURCE_RELATION)
        o_res_parent = o_res_crt

    request.resource = o_res_parent

    if request.method == "GET":
        return get_res_info(request)

    return error_response(Error.ERROR_METHOD)
