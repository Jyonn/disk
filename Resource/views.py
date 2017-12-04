from Base.decorator import require_get, require_login
from Base.response import response


@require_get(['filename', 'parent_id', 'description', 'status'])
@require_login
def upload_res_token(request):
    return response()