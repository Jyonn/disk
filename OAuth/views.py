from Base.decorator import require_get
from Base.error import Error
from Base.qtb import get_qtb_user_token
from Base.response import error_response, response
from Resource.models import Resource
from User.models import User
from User.views import get_token_info


ROOT_DESC = '''
# 我的盒子简介

## “介绍”使用介绍

### 1. 点击右上角的铅笔按钮修改介绍

- 进入编辑状态后，需要点击“修改”，才能更新介绍内容

### 2. 介绍内容支持以Markdown格式编辑

> 所有行前的特殊符号都需要加上空格后才能接正文

- 行前`#`符号表示层级标题，`#`越多表示层级越深
- 行前`-`/`*`符号表示列举
- 行前`>`符号表示引用
- 跳转页面可以使用`[跳转](页面链接)`的格式，例如：[更多Markdown格式](http://www.markdown.cn/)
'''


@require_get(['code'])
def oauth_qtb_callback(request):
    code = request.d.code

    ret = get_qtb_user_token(code)
    if ret.error is not Error.OK:
        return error_response(ret)
    body = ret.body
    token = body['token']
    qt_user_app_id = body['user_app_id']

    ret = User.create(qt_user_app_id, token)
    if ret.error is not Error.OK:
        return error_response(ret)
    o_user = ret.body
    if not isinstance(o_user, User):
        return error_response(Error.STRANGE)

    ret = Resource.get_root_folder(o_user)
    if ret.error is Error.ERROR_GET_ROOT_FOLDER:
        ret = Resource.get_res_by_id(Resource.ROOT_ID)
        if ret.error is not Error.OK:
            return error_response(ret)
        o_root = ret.body

        ret = Resource.create_folder(
            o_user.qt_user_app_id,
            o_user,
            o_root,
            ROOT_DESC
        )
        if ret.error is not Error.OK:
            return error_response(ret)

    ret = o_user.update()
    if ret.error is not Error.OK:
        return error_response(ret)
    return response(body=get_token_info(o_user))
