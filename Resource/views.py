""" Adel Liu 180111

资源API处理函数
"""
from SmartDjango import Analyse, P
from django.http import HttpResponseRedirect
from django.utils.crypto import get_random_string
from django.views import View

from Base.auth import Auth
from Base.policy import Policy
from Base.qn_manager import qn_res_manager, QnManager
from Resource.models import Resource, P_RNAME, P_VISIT_KEY, ResourceError, P_STATUS, P_DESC, \
    P_RIGHT_BUBBLE, P_COVER, P_COVER_TYPE, RtypeChoice, StypeChoice, CoverChoice
from User.models import User


P_RES = P('res_str_id', yield_name='res').process(Resource.get_by_id)
P_PARENT_RES = P('parent_str_id', yield_name='parent_res').process(Resource.get_by_id)
P_USER = P('user_id', yield_name='user').process(User.get_by_id)


class BaseView(View):
    @staticmethod
    @Auth.maybe_login
    @Analyse.r(q=[P_VISIT_KEY.clone().null()], a=[P_RES])
    def get(r):
        """ GET /api/res/:res_str_id

        获取资源信息
        """
        user = r.user
        res = r.d.res
        visit_key = r.d.visit_key

        if not res.readable(user, visit_key):
            return ResourceError.NOT_READABLE
        return res.d_layer()

    @staticmethod
    @Analyse.r(b=[
        P_RNAME.clone().null(),
        P_STATUS.clone().null(),
        P_DESC.clone().null(),
        P_VISIT_KEY.clone().null(),
        P_RIGHT_BUBBLE.clone().null(),
        P_PARENT_RES.clone().null()
    ], a=[P_RES])
    @Auth.require_owner
    def put(r):
        """ PUT /api/res/:slug/

        修改资源信息
        """
        user = r.user
        rname = r.d.rname
        description = r.d.description
        status = r.d.status
        visit_key = r.d.visit_key
        right_bubble = r.d.right_bubble
        parent_res = r.d.parent_res

        res = r.d.res

        if parent_res:
            if not parent_res.belong(user):
                return ResourceError.RESOURCE_NOT_BELONG
            if parent_res.rtype != RtypeChoice.FOLDER:
                return ResourceError.REQUIRE_FOLDER

            temp_res = parent_res
            while temp_res.pk != Resource.ROOT_ID:
                if temp_res.pk == res.pk:
                    return ResourceError.RESOURCE_CIRCLE
                temp_res = temp_res.parent

        res.modify_info(rname, description, status, visit_key, right_bubble, parent_res)
        return res.d()

    @staticmethod
    @Analyse.r(a=[P_RES])
    @Auth.require_owner
    def delete(r):
        """ DELETE /api/res/:slug

        删除资源
        """
        res = r.d.res

        if res.parent == Resource.ROOT_ID:
            return ResourceError.DELETE_ROOT_FOLDER

        res.remove()


class FolderView(View):
    @staticmethod
    @Analyse.r(b=[P_RNAME.clone().rename('folder_name')],
               a=[P_RES])
    @Auth.require_owner
    def post(r):
        """ POST /api/res/:res_str_id/folder

        上传文件夹资源
        """
        user = r.user
        folder_name = r.d.folder_name
        res_parent = r.d.res

        res = Resource.create_folder(folder_name, user, res_parent)
        return res.d()


class LinkView(View):
    @staticmethod
    @Analyse.r(b=[P_RNAME.clone().rename('link_name'), P('link')],
               a=[P_RES])
    @Auth.require_owner
    def post(r):
        """ POST /api/res/:res_str_id/link

        上传链接资源
        """
        user = r.user
        link_name = r.d.link_name
        link = r.d.link
        res_parent = r.d.res

        res = Resource.create_link(link_name, user, res_parent, link)
        return res.d()


class PathView(View):
    @staticmethod
    @Analyse.r(a=[P_RES])
    @Auth.require_owner
    def get(r):
        res = r.d.res
        res_path = []
        while res.pk != Resource.ROOT_ID:
            if res.res_str_id in res_path:
                return ResourceError.RESOURCE_CIRCLE
            res_path.append(res.res_str_id)
            res = res.parent
        return res_path


class SelectView(View):
    @staticmethod
    @Analyse.r(a=[P_RES])
    @Auth.require_owner
    def get(r):
        res = r.d.res
        return res.d_selector_layer()


class TokenView(View):
    @staticmethod
    @Analyse.r(q=[P_RNAME.clone().rename('filename')], a=[P_RES])
    @Auth.require_owner
    def get(r):
        """ GET /api/res/:res_str_id/token

        获取七牛上传资源token
        """
        user = r.user
        filename = r.d.filename
        filename = QnManager.encode_key(filename)
        res_parent = r.d.res

        import datetime
        crt_time = datetime.datetime.now().timestamp()
        salt = get_random_string(4)
        key = 'res/%s/%s/%s' % (salt, crt_time, filename)
        qn_token, key = qn_res_manager.get_upload_token(
            key, Policy.file(filename, user.pk, res_parent.res_str_id))
        return dict(upload_token=qn_token, key=key)

    @staticmethod
    @Analyse.r(b=[P('key'), P_USER, P('fsize'), P('fname'), P('ftype')],
               a=[P_RES])
    def post(r):
        """ POST /api/res/:res_str_id/token

        七牛上传资源回调函数
        """
        qn_res_manager.auth_callback(r)

        key = r.d.key
        user = r.d.user
        fsize = r.d.fsize
        fname = r.d.fname
        ftype = r.d.ftype
        res_parent = r.d.res

        if ftype.find('video') == 0:
            sub_type = StypeChoice.VIDEO
        elif ftype.find('image') == 0:
            sub_type = StypeChoice.IMAGE
        elif ftype.find('audio') == 0:
            sub_type = StypeChoice.MUSIC
        else:
            sub_type = StypeChoice.FILE

        if not res_parent.belong(user):
            return ResourceError.PARENT_NOT_BELONG

        decode_fname = QnManager.decode_key(fname)
        if fname != decode_fname:
            new_key = '%s/%s' % (key[:key.rfind('/')], decode_fname)
            qn_res_manager.move_res(key, new_key)
            fname = decode_fname
            key = new_key

        res = Resource.create_file(fname, user, res_parent, key, fsize, sub_type, ftype)
        return res.d_child()


class CoverView(View):
    @staticmethod
    @Analyse.r(q=[P_RNAME.clone().rename('filename')], a=[P_RES])
    @Auth.require_owner
    def get(r):
        """ GET /api/res/:res_str_id/cover

        获取七牛上传资源封面token
        """
        filename = r.d.filename
        filename = QnManager.encode_key(filename)
        res = r.d.res

        import datetime
        crt_time = datetime.datetime.now().timestamp()
        salt = get_random_string(4)
        key = 'cover/%s/%s/%s' % (salt, crt_time, filename)
        qn_token, key = qn_res_manager.get_upload_token(key, Policy.cover(res.res_str_id))
        return dict(upload_token=qn_token, key=key)

    @staticmethod
    @Analyse.r(b=[P('key')], a=[P_RES])
    def post(r):
        """ POST /api/res/:res_str_id/cover

        七牛上传资源封面成功后的回调函数
        """
        qn_res_manager.auth_callback(r)

        key = r.d.key
        res = r.d.res  # type: Resource

        res.modify_cover(key, CoverChoice.UPLOAD)
        return res.d()

    @staticmethod
    @Analyse.r(b=[P_COVER, P_COVER_TYPE], a=[P_RES])
    @Auth.require_owner
    def put(r):
        """ PUT /api/res/:res_str_id/cover

        修改封面信息
        """
        cover = r.d.cover
        cover_type = r.d.cover_type

        res = r.d.res
        user = r.user

        if cover_type == CoverChoice.UPLOAD:
            return ResourceError.NOT_ALLOWED_COVER_UPLOAD
        if cover_type == CoverChoice.SELF and res.sub_type != StypeChoice.IMAGE:
            return ResourceError.NOT_ALLOWED_COVER_SELF_OF_NOT_IMAGE
        if cover_type == CoverChoice.RESOURCE:
            resource_chain = [cover]
            next_str_id = cover
            while True:
                next_res = Resource.get_by_id(next_str_id)
                if next_res.res_str_id == res.res_str_id:
                    return ResourceError.RESOURCE_CIRCLE
                if not next_res.belong(user):
                    return ResourceError.RESOURCE_NOT_BELONG
                if next_res.cover_type == CoverChoice.RESOURCE:
                    next_str_id = next_res.cover
                elif next_res.cover_type == CoverChoice.PARENT:
                    next_str_id = next_res.parent.res_str_id
                else:
                    break
                if next_str_id in resource_chain:
                    return ResourceError.RESOURCE_CIRCLE
                resource_chain.append(next_str_id)

        res.modify_cover(cover, cover_type)
        return res.d()


class BaseInfoView(View):
    @staticmethod
    @Analyse.r(a=[P_RES])
    @Auth.maybe_login
    def get(r):
        """ GET /api/res/:res_str_id/base

        获取资源公开信息
        """
        user = r.user  # type: User
        res = r.d.res  # type: Resource

        return dict(
            info=res.d_base(),
            readable=res.readable(user, None)
        )


class DownloadView(View):
    @staticmethod
    @Auth.maybe_login
    def get_dl_link(r, visit_key):
        user = r.user

        res = r.d.res  # type: Resource
        if not res.readable(user, visit_key):
            return ResourceError.NOT_READABLE

        if res.rtype == RtypeChoice.FOLDER:
            return ResourceError.REQUIRE_FILE

        return HttpResponseRedirect(res.get_dl_url())

    @staticmethod
    @Analyse.r(q=[P('token', '登录口令').null(), P_VISIT_KEY.clone().null()], a=[P_RES])
    def get(r):
        """ GET /api/res/:res_str_id/dl

        获取下载资源链接
        """
        r.META['HTTP_TOKEN'] = r.d.token

        visit_key = r.d.visit_key
        return DownloadView.get_dl_link(r, visit_key)


def remove_dot(res_str_id):
    find_dot = res_str_id.find('.')
    if find_dot != -1:
        res_str_id = res_str_id[:find_dot]
    return res_str_id


class ShortLinkView(View):
    P_SL_RES_ID = P_RES.clone().process(remove_dot, begin=True)

    @staticmethod
    @Analyse.r(q=[P_VISIT_KEY.clone().null()], a=[P_SL_RES_ID])
    def get(r):
        """ /s/:res_str_id

        GET: direct_link, 直链分享解析
        """
        visit_key = r.d.visit_key
        return DownloadView.get_dl_link(r, visit_key)
