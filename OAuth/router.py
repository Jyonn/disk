from Base.error import Error
from Base.response import Method, response, error_response
from OAuth.views import oauth_qtb_callback


def rt_qtb_callback(request):
    """ /api/oauth/qtb/callback

    GET: 齐天簿身份认证回调函数
    """

    options = {
        Method.GET: "齐天簿身份认证回调函数"
    }

    if request.method == Method.OPTIONS:
        return response(body=options, allow=True)

    if request.method == Method.GET:
        return oauth_qtb_callback(request)
    return error_response(Error.ERROR_METHOD)
