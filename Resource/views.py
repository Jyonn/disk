from django.http import HttpResponseRedirect
from django.utils.crypto import get_random_string
from django.views import View
from smartdjango import Validator, analyse
from smartdjango.analyse import Request

from Base.auth import Auth
from Base.policy import Policy
from Base.qn_manager import qn_res_manager, QnManager
from Resource.models import Resource, RtypeChoice, StypeChoice, CoverChoice
from Resource.params import ResourceParams
from Resource.validators import ResourceErrors
from User.models import User
from User.params import UserParams


class BaseView(View):
    @Auth.maybe_login
    @analyse.query(ResourceParams.visit_key.copy().null().default(None))
    @analyse.argument(ResourceParams.resource_getter)
    def get(self, request: Request, **kwargs):
        """ GET /api/res/:res_str_id

        获取资源信息
        """
        user = request.user
        resource: Resource = request.argument.resource
        visit_key = request.query.visit_key

        if not resource.readable(user, visit_key):
            raise ResourceErrors.NOT_READABLE
        return resource.d_layer()

    @analyse.json(
        ResourceParams.rname.copy().null().default(None),
        ResourceParams.status.copy().null().default(None),
        ResourceParams.description.copy().null().default(None),
        ResourceParams.visit_key.copy().null().default(None),
        ResourceParams.right_bubble.copy().null().default(None),
        ResourceParams.parent_getter.copy().null().default(None)
    )
    @analyse.argument(ResourceParams.resource_getter)
    @Auth.require_owner
    def put(self, request: Request, **kwargs):
        """ PUT /api/res/:slug/

        修改资源信息
        """
        user = request.user
        rname = request.json.rname
        description = request.json.description
        status = request.json.status
        visit_key = request.json.visit_key
        right_bubble = request.json.right_bubble
        parent: Resource = request.json.parent

        resource: Resource = request.argument.resource

        if parent:
            if not parent.belong(user):
                raise ResourceErrors.RESOURCE_NOT_BELONG

            if parent.rtype != RtypeChoice.FOLDER:
                raise ResourceErrors.REQUIRE_FOLDER

            temp_res = parent
            while temp_res.pk != Resource.ROOT_ID:
                if temp_res.pk == resource.pk:
                    raise ResourceErrors.RESOURCE_CIRCLE
                temp_res = temp_res.parent

        resource.modify_info(rname, description, status, visit_key, right_bubble, parent)
        return resource.d()

    @analyse.argument(ResourceParams.resource_getter)
    @Auth.require_owner
    def delete(self, request: Request, **kwargs):
        """ DELETE /api/res/:slug

        删除资源
        """
        resource: Resource = request.argument.resource

        if resource.parent == Resource.ROOT_ID:
            raise ResourceErrors.DELETE_ROOT_FOLDER

        resource.remove()


class FolderView(View):
    @analyse.json(ResourceParams.rname.copy().rename('folder_name'))
    @analyse.argument(ResourceParams.resource_getter)
    @Auth.require_owner
    def post(self, request: Request, **kwargs):
        """ POST /api/res/:res_str_id/folder

        上传文件夹资源
        """
        user = request.user
        folder_name = request.json.folder_name
        res_parent: Resource = request.argument.resource

        res = Resource.create_folder(folder_name, user, res_parent)
        return res.d()


class LinkView(View):
    @analyse.json(ResourceParams.rname.copy().rename('link_name'), 'link')
    @analyse.argument(ResourceParams.resource_getter)
    @Auth.require_owner
    def post(self, request: Request, **kwargs):
        """ POST /api/res/:res_str_id/link

        上传链接资源
        """
        user = request.user
        link_name = request.json.link_name
        link = request.json.link
        parent: Resource = request.argument.resource

        resource: Resource = Resource.create_link(link_name, user, parent, link)
        return resource.d()


class PathView(View):
    @analyse.argument(ResourceParams.resource_getter)
    @Auth.require_owner
    def get(self, request: Request, **kwargs):
        resource: Resource = request.argument.resource
        res_path = []
        while resource.pk != Resource.ROOT_ID:
            if resource.res_str_id in res_path:
                raise ResourceErrors.RESOURCE_CIRCLE
            res_path.append(resource.res_str_id)
            resource = resource.parent
        return res_path


class SelectView(View):
    @analyse.argument(ResourceParams.resource_getter)
    @Auth.require_owner
    def get(self, request: Request, **kwargs):
        resource: Resource = request.argument.resource
        return resource.d_selector_layer()


class TokenView(View):
    @analyse.query(ResourceParams.rname.copy().rename('filename'))
    @analyse.argument(ResourceParams.resource_getter)
    @Auth.require_owner
    def get(self, request: Request, **kwargs):
        """ GET /api/res/:res_str_id/token

        获取七牛上传资源token
        """
        user = request.user
        filename = request.query.filename
        filename = QnManager.encode_key(filename)
        res_parent: Resource = request.argument.resource

        import datetime
        crt_time = datetime.datetime.now().timestamp()
        salt = get_random_string(4)
        key = 'res/%s/%s/%s' % (salt, crt_time, filename)
        qn_token, key = qn_res_manager.get_upload_token(
            key, Policy.file(filename, user.pk, res_parent.res_str_id))
        return dict(upload_token=qn_token, key=key)

    @analyse.json(UserParams.user_getter, 'fsize', 'fname', 'ftype', 'key')
    @analyse.argument(ResourceParams.resource_getter)
    def post(self, request: Request, **kwargs):
        """ POST /api/res/:res_str_id/token

        七牛上传资源回调函数
        """
        qn_res_manager.auth_callback(request)

        key = request.json.key
        user: User = request.json.user
        fsize = request.json.fsize
        fname = request.json.fname
        ftype = request.json.ftype
        parent: Resource = request.argument.resource

        if ftype.find('video') == 0:
            sub_type = StypeChoice.VIDEO
        elif ftype.find('image') == 0:
            sub_type = StypeChoice.IMAGE
        elif ftype.find('audio') == 0:
            sub_type = StypeChoice.MUSIC
        else:
            sub_type = StypeChoice.FILE

        if not parent.belong(user):
            raise ResourceErrors.PARENT_NOT_BELONG

        decode_fname = QnManager.decode_key(fname)
        if fname != decode_fname:
            new_key = '%s/%s' % (key[:key.rfind('/')], decode_fname)
            qn_res_manager.move_res(key, new_key)
            fname = decode_fname
            key = new_key

        resource = Resource.create_file(fname, user, parent, key, fsize, sub_type, ftype)
        return resource.d_child()


class CoverView(View):
    @analyse.query(ResourceParams.rname.copy().rename('filename'))
    @analyse.argument(ResourceParams.resource_getter)
    @Auth.require_owner
    def get(self, request: Request, **kwargs):
        """ GET /api/res/:res_str_id/cover

        获取七牛上传资源封面token
        """
        filename = request.query.filename
        filename = QnManager.encode_key(filename)
        resource: Resource = request.argument.resource

        import datetime
        crt_time = datetime.datetime.now().timestamp()
        salt = get_random_string(4)
        key = 'cover/%s/%s/%s' % (salt, crt_time, filename)
        qn_token, key = qn_res_manager.get_upload_token(key, Policy.cover(resource.res_str_id))
        return dict(upload_token=qn_token, key=key)

    @analyse.json('key')
    @analyse.argument(ResourceParams.resource_getter)
    def post(self, request):
        """ POST /api/res/:res_str_id/cover

        七牛上传资源封面成功后的回调函数
        """
        qn_res_manager.auth_callback(request)

        key = request.json.key
        resource: Resource = request.argument.resource

        resource.modify_cover(key, CoverChoice.UPLOAD)
        return resource.d()

    @analyse.json(ResourceParams.cover, ResourceParams.cover_type)
    @analyse.argument(ResourceParams.resource_getter)
    @Auth.require_owner
    def put(self, request: Request, **kwargs):
        """ PUT /api/res/:res_str_id/cover

        修改封面信息
        """
        cover = request.json.cover
        cover_type = request.json.cover_type

        resource: Resource = request.argument.resource
        user = request.user

        if cover_type == CoverChoice.UPLOAD:
            raise ResourceErrors.NOT_ALLOWED_COVER_UPLOAD
        if cover_type == CoverChoice.SELF and resource.sub_type != StypeChoice.IMAGE:
            raise ResourceErrors.NOT_ALLOWED_COVER_SELF_OF_NOT_IMAGE
        if cover_type == CoverChoice.RESOURCE:
            resource_chain = [cover]
            next_str_id = cover
            while True:
                next_res = Resource.get_by_id(next_str_id)
                if next_res.res_str_id == resource.res_str_id:
                    raise ResourceErrors.RESOURCE_CIRCLE
                if not next_res.belong(user):
                    raise ResourceErrors.RESOURCE_NOT_BELONG
                if next_res.cover_type == CoverChoice.RESOURCE:
                    next_str_id = next_res.cover
                elif next_res.cover_type == CoverChoice.PARENT:
                    next_str_id = next_res.parent.res_str_id
                else:
                    break
                if next_str_id in resource_chain:
                    raise ResourceErrors.RESOURCE_CIRCLE
                resource_chain.append(next_str_id)

        resource.modify_cover(cover, cover_type)
        return resource.d()


class BaseInfoView(View):
    @analyse.argument(ResourceParams.resource_getter)
    @Auth.maybe_login
    def get(self, request, **kwargs):
        """ GET /api/res/:res_str_id/base

        获取资源公开信息
        """
        user = request.user  # type: User
        resource: Resource = request.argument.resource

        return dict(
            info=resource.d_base(),
            readable=resource.readable(user, None)
        )


class DownloadView(View):
    @staticmethod
    @Auth.maybe_login
    def get_dl_link(request: Request, visit_key):
        user = request.user

        resource: Resource = request.data.resource
        if not resource.readable(user, visit_key):
            raise ResourceErrors.NOT_READABLE

        if resource.rtype == RtypeChoice.FOLDER:
            raise ResourceErrors.REQUIRE_FILE

        dl_url = resource.get_dl_url()
        return HttpResponseRedirect(dl_url)

    @analyse.query(
        Validator('token', '登录口令').null().default(None),
        ResourceParams.visit_key.copy().null().default(None)
    )
    @analyse.argument(ResourceParams.resource_getter)
    def get(self, request: Request, **kwargs):
        """ GET /api/res/:res_str_id/dl

        获取下载资源链接
        """
        request.META['HTTP_TOKEN'] = request.query.token

        visit_key = request.query.visit_key
        return DownloadView.get_dl_link(request, visit_key)


class ShortLinkView(View):
    @analyse.query(ResourceParams.visit_key.copy().null().default(None))
    @analyse.argument(ResourceParams.shortlink_resource_getter)
    def get(self, request: Request, **kwargs):
        """ /s/:res_str_id

        GET: direct_link, 直链分享解析
        """
        visit_key = request.query.visit_key
        return DownloadView.get_dl_link(request, visit_key)
