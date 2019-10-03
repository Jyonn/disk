from SmartDjango import Excp, Analyse, Param
from django.views import View

from Base.auth import Auth
from Base.common import qt_manager
from Resource.models import Resource, ResourceError
from User.models import User


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


class OAuthView(View):
    @staticmethod
    @Excp.handle
    @Analyse.r(q=[Param('code', '齐天簿授权码')])
    def get(r):
        code = r.d.code

        body = qt_manager.get_token(code)

        token = body['token']
        qt_user_app_id = body['user_app_id']

        user = User.create(qt_user_app_id, token)

        try:
            Resource.get_root_folder(user)
        except Excp as ret:
            if ret.erroris(ResourceError.GET_ROOT_FOLDER):
                root = Resource.get_by_pk(Resource.ROOT_ID)

                Resource.create_folder(
                    user.qt_user_app_id,
                    user,
                    root,
                    ROOT_DESC
                )

        user.update()
        return Auth.get_login_token(user)
