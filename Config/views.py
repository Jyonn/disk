from Base.decorator import require_get
from Base.qn import get_upload_token
from Base.response import response


@require_get
def up_token(request):
    return response(body=dict(token=get_upload_token('test')))
