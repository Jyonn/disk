from django.utils.crypto import get_random_string

from Base.decorator import require_root, require_post
from Base.response import response
from Resource.models import Resource


@require_root
@require_post()
def set_unique_res_key(request):
    for o_res in Resource.objects.all():
        if not o_res.res_str_id:
            o_res.res_str_id = get_random_string(length=6)
            o_res.save()
    return response()
