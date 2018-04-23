from Base.decorator import require_get
from Base.error import Error
from Base.qtb import get_qtb_user_token
from Base.response import error_response, response
from User.models import User


@require_get(['code'])
def oauth_qtb_callback(request):
    code = request.d.code

    ret = get_qtb_user_token(code)
    if ret.error is not Error.OK:
        print("why")
        return error_response(ret)
    print("success")
    body = ret.body
    token = body['token']
    qt_user_app_id = body['user_app_id']

    ret = User.create(qt_user_app_id, token)
    if ret.error is not Error.OK:
        return error_response(ret)
    o_user = ret.body
    if not isinstance(o_user, User):
        return error_response(Error.STRANGE)

    ret = o_user.update()
    if ret.error is not Error.OK:
        return error_response(ret)
    return response(body=o_user.to_dict())
