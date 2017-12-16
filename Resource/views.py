from Base.decorator import require_get, require_login, require_json, require_post, maybe_login
from Base.error import Error
from Base.policy import get_file_policy
from Base.qn import get_upload_token, auth_callback
from Base.response import response, error_response
from Resource.models import Resource
from User.models import User


@require_json
@require_post(['folder_name', 'parent_id', 'description', 'status'])
@require_login
def create_folder(request):
    o_user = request.user

    folder_name = request.d.folder_name
    parent_id = request.d.parent_id
    desc = request.d.description
    status = request.d.status

    if status not in [Resource.STATUS_PUBLIC, Resource.STATUS_PRIVATE, Resource.STATUS_PROTECT]:
        return error_response(Error.ERROR_RESOURCE_STATUS)

    # get parent folder
    ret = Resource.get_res_by_id(parent_id)
    if ret.error is not Error.OK:
        return error_response(ret.error)
    o_parent = ret.body
    if not isinstance(o_parent, Resource):
        return error_response(Error.STRANGE)

    if not o_parent.belong(o_user):
        return error_response(Error.PARENT_NOT_BELONG)
    if o_parent.rtype != Resource.RTYPE_FOLDER:
        return error_response(Error.ERROR_FILE_PARENT)

    ret = Resource.create_folder(folder_name, o_user, o_parent, desc, status)
    if ret.error is not Error.OK:
        return error_response(ret.error)
    o_res = ret.body
    if not isinstance(o_res, Resource):
        return error_response(Error.STRANGE)
    return response(body=o_res.to_dict())


@require_get()
@require_login
def get_root_res(request):
    o_user = request.user

    ret = Resource.get_root_folder(o_user)
    if ret.error is not Error.OK:
        return error_response(ret.error)
    o_root = ret.body
    if not isinstance(o_root, Resource):
        return error_response(Error.STRANGE)

    ret = o_root.get_child_res_list()
    if ret.error is not Error.OK:
        return error_response(ret.error)
    res_list = ret.body
    return response(body=res_list)


@require_get(['parent_id', 'visit_key'])
@maybe_login
def get_child_res_list(request):
    o_user = request.user
    parent_id = request.d.parent_id
    visit_key = request.d.visit_key

    ret = Resource.get_res_by_id(parent_id)
    if ret.error is not Error.OK:
        return error_response(ret.error)
    o_parent = ret.body
    if not isinstance(o_parent, Resource):
        return error_response(Error.STRANGE)

    if not o_parent.readable(o_user, visit_key):
        return error_response(Error.NOT_READABLE)

    ret = o_parent.get_child_res_list()
    if ret.error is not Error.OK:
        return error_response(ret.error)
    res_list = ret.body
    return response(body=dict(info=o_parent.to_dict(), child_list=res_list))


@require_get(['filename', 'parent_id', 'description', 'status'])
@require_login
def upload_res_token(request):
    o_user = request.user
    parent_id = request.d.parent_id
    status = request.d.status
    filename = request.d.filename

    if not isinstance(o_user, User):
        return error_response(Error.STRANGE)

    ret = Resource.get_res_by_id(parent_id)
    if ret.error is not Error.OK:
        return error_response(ret.error)
    o_parent = ret.body
    if not isinstance(o_parent, Resource):
        return error_response(Error.STRANGE)

    if not o_parent.belong(o_user):
        return error_response(Error.PARENT_NOT_BELONG)

    if status not in [Resource.STATUS_PUBLIC, Resource.STATUS_PRIVATE, Resource.STATUS_PROTECT]:
        return error_response(Error.ERROR_RESOURCE_STATUS)

    import datetime
    policy = get_file_policy(o_user.pk, o_parent.pk, status)
    key = 'res/%s/%s/%s' % (o_user.pk, datetime.datetime.now().timestamp(), filename)
    qn_token, key = get_upload_token(key, policy)
    return response(body=dict(upload_token=qn_token, key=key))


@require_json
@require_post(['key', 'user_id', 'fsize', 'fname', 'parent_id', 'status'])
def upload_res_callback(request):
    ret = auth_callback(request)
    if ret.error is not Error.OK:
        return error_response(ret.error)

    key = request.d.key
    user_id = request.d.user_id
    fsize = request.d.fsize
    fname = request.d.fname
    parent_id = request.d.parent_id
    status = request.d.status

    # get user by id
    ret = User.get_user_by_id(user_id)
    if ret.error is not Error.OK:
        return error_response(ret.error)
    o_user = ret.body
    if not isinstance(o_user, User):
        return error_response(Error.STRANGE)

    # get parent by id
    ret = Resource.get_res_by_id(parent_id)
    if ret.error is not Error.OK:
        return error_response(ret.error)
    o_parent = ret.body
    if not isinstance(o_parent, Resource):
        return error_response(Error.STRANGE)

    ret = Resource.create_file(fname, o_user, o_parent, key, status, fsize)
    if ret.error is not Error.OK:
        return error_response(ret.error)
    o_res = ret.body
    if not isinstance(o_res, Resource):
        return error_response(Error.STRANGE)

    return response(body=o_res.to_dict())


@require_get(['res_id'])
@require_login
def get_visit_key(request):
    o_user = request.user
    res_id = request.d.res_id

    ret = Resource.get_res_by_id(res_id)
    if ret.error is not Error.OK:
        return error_response(ret.error)
    o_res = ret.body
    if not isinstance(o_res, Resource):
        return error_response(Error.STRANGE)

    if not o_res.belong(o_user):
        return error_response(Error.NOT_READABLE)
    visit_key = o_res.visit_key if o_res.status == Resource.STATUS_PROTECT else None
    return response(body=dict(status=o_res.status, visit_key=visit_key))


@require_get(['res_id', 'visit_key'])
@maybe_login
def get_dl_link(request):
    o_user = request.user
    res_id = request.d['res_id']
    visit_key = request.d['visit_key']

    ret = Resource.get_res_by_id(res_id)
    if ret.error is not Error.OK:
        return error_response(ret.error)
    o_res = ret.body
    if not isinstance(o_res, Resource):
        return error_response(Error.STRANGE)

    if not o_res.readable(o_user, visit_key):
        return error_response(Error.NOT_READABLE)

    if o_res.rtype != Resource.RTYPE_FILE:
        return error_response(Error.REQUIRE_FILE)

    return response(body=dict(link=o_res.get_dl_url()))
