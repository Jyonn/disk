""" Adel Liu 180111

资源类和方法
"""
import datetime

from SmartDjango import models, E, BaseError
from django.utils.crypto import get_random_string
from pigmento import pnt

from User.models import User


@E.register(id_processor=E.idp_cls_prefix())
class ResourceError:
    PARENT_NOT_BELONG = E("无法在他人目录下存储", hc=403)
    NOT_ALLOWED_COVER_SELF_OF_NOT_IMAGE = E("不允许非图片资源设置封面为自身", hc=403)
    NOT_ALLOWED_COVER_UPLOAD = E("不允许封面类型直接修改为本地上传类型", hc=403)

    DELETE_ROOT_FOLDER = E("无法删除用户根目录", hc=403)
    RESOURCE_CIRCLE = E("不允许资源关系成环", hc=403)

    REQUIRE_FOLDER = E("目标需要为目录资源", hc=403)
    REQUIRE_FILE = E("目标需要为文件资源", hc=403)

    NOT_READABLE = E("没有读取权限", hc=403)
    RIGHT_NOT_FOUND = E("不存在的读取权限", hc=404)
    CREATE_RIGHT = E("存储读取权限错误", hc=500)
    REQUIRE_EMPTY_FOLDER = E("非空目录无法删除", hc=403)
    GET_ROOT_FOLDER = E("无法获得根目录", hc=500)
    CREATE_LINK = E("存储链接错误", hc=500)
    CREATE_FOLDER = E("存储目录错误", hc=500)
    CREATE_FILE = E("存储文件错误", hc=500)
    FILE_PARENT = E("文件资源不能成为父目录", hc=403)
    RESOURCE_NOT_BELONG = E("没有权限", hc=403)
    RESOURCE_NOT_FOUND = E("不存在的资源", hc=404)
    INVALID_RNAME = E("不合法的资源名称", hc=400)


class RtypeChoice(models.cenum.CREnum):
    FILE = 0
    FOLDER = 1
    LINK = 2
    

class StatusChoice(models.cenum.CREnum):
    PUBLIC = 0
    PRIVATE = 1
    PROTECT = 2


class StypeChoice(models.cenum.CREnum):
    FOLDER = 0
    IMAGE = 1
    VIDEO = 2
    MUSIC = 3
    FILE = 4
    LINK = 5


class CoverChoice(models.cenum.CREnum):
    RANDOM = 0
    UPLOAD = 1
    PARENT = 2
    OUTLNK = 3
    SELF = 4
    RESOURCE = 5


class Resource(models.Model):
    """
    资源类
    根资源文件夹id=1
    一旦新增用户，就在根目录创建一个属于新增用户的文件夹
    """
    ROOT_ID = 1

    rname = models.CharField(
        verbose_name='resource name',
        max_length=256,
    )
    rtype = models.IntegerField(
        verbose_name='file or folder',
        choices=RtypeChoice.list(),
    )
    rsize = models.IntegerField(
        default=0,
    )
    sub_type = models.IntegerField(
        verbose_name='sub type',
        choices=StypeChoice.list(),
        default=StypeChoice.FOLDER.value,
    )
    mime = models.CharField(
        verbose_name='资源类型',
        null=True,
        default=True,
        max_length=100,
    )
    description = models.TextField(
        verbose_name='description in Markdown',
        null=True,
        blank=True,
        default=None,
    )
    cover = models.CharField(
        null=True,
        blank=True,
        default=None,
        max_length=1024,
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    parent = models.ForeignKey(
        'Resource',
        null=True,
        blank=True,
        default=0,
        on_delete=models.CASCADE,
    )
    dlpath = models.CharField(
        verbose_name='download relative path to res.6-79.cn',
        max_length=1024,
        default=None,
        null=True,
        blank=True,
    )
    status = models.IntegerField(
        choices=StatusChoice.list(),
        verbose_name='加密状态 0公开 1仅自己可见 2需要密码',
        default=StatusChoice.PUBLIC.value,
    )
    visit_key = models.CharField(
        max_length=16,
        min_length=3,
        verbose_name='当status为2时有效',
    )
    vk_change_time = models.FloatField(
        null=True,
        blank=True,
        default=0,
    )
    create_time = models.DateTimeField()
    dlcount = models.IntegerField(
        verbose_name='download number',
        default=0,
    )
    res_str_id = models.CharField(
        verbose_name='唯一随机资源ID，弃用res_id',
        default=None,
        null=True,
        blank=True,
        max_length=6,
        unique=True,
    )
    right_bubble = models.NullBooleanField(
        verbose_name='读取权限向上冒泡',
        default=True,
    )
    cover_type = models.IntegerField(
        choices=CoverChoice.list(),
        verbose_name='封面类型 0 上传图片 1 与父资源相同 2 与指定资源相同 3 外部URI链接',
        default=CoverChoice.RANDOM.value,
        null=0,
        blank=0,
    )

    @classmethod
    def get_unique_id(cls):
        while True:
            res_str_id = get_random_string(length=6)
            try:
                cls.get_by_id(res_str_id)
            except E as ret:
                if ret.eis(ResourceError.RESOURCE_NOT_FOUND):
                    return res_str_id

    @staticmethod
    def _valid_rname(rname):
        """验证rname属性"""
        invalid_chars = '\\/*:\'"|<>?'
        for char in invalid_chars:
            if char in rname:
                raise ResourceError.INVALID_RNAME

    @staticmethod
    def _valid_res_parent(parent):
        """验证parent属性"""
        if not isinstance(parent, Resource):
            raise BaseError.STRANGE
        if parent.rtype != RtypeChoice.FOLDER.value:
            raise ResourceError.FILE_PARENT

    @classmethod
    def create_abstract(cls, rname, rtype, desc, user, parent, dlpath, rsize, sub_type, mime):
        crt_time = datetime.datetime.now()

        return cls(
            rname=rname,
            rtype=rtype,
            mime=mime,
            description=desc,
            cover=None,
            cover_type=CoverChoice.SELF.value if sub_type == StypeChoice.IMAGE.value else CoverChoice.RANDOM.value,
            owner=user,
            parent=parent,
            dlpath=dlpath,
            status=StatusChoice.PRIVATE.value,
            visit_key=get_random_string(length=4),
            create_time=crt_time,
            vk_change_time=crt_time.timestamp(),
            rsize=rsize,
            sub_type=sub_type,
            res_str_id=cls.get_unique_id(),
            dlcount=0,
            right_bubble=True,
        )

    @classmethod
    def create_file(cls, rname, user, res_parent, dlpath, rsize, sub_type, mime):
        """ 创建文件对象

        :param mime: 七牛返回的资源类型
        :param rname: 文件名
        :param user: 所属用户
        :param res_parent: 所属目录
        :param dlpath: 七牛存储的key
        :param rsize: 文件大小
        :param sub_type: 文件分类
        :return: Ret对象，错误返回错误代码，成功返回文件对象
        """
        try:
            res = cls.create_abstract(
                rname=rname,
                rtype=RtypeChoice.FILE.value,
                desc=None,
                user=user,
                parent=res_parent,
                dlpath=dlpath,
                rsize=rsize,
                sub_type=sub_type,
                mime=mime,
            )
            res.save()
        except Exception:
            raise ResourceError.CREATE_FILE
        return res

    @classmethod
    def create_folder(cls, rname, user, res_parent, desc=None):
        """ 创建文件夹对象

        :param rname: 文件夹名
        :param user: 所属用户
        :param res_parent: 所属目录
        :param desc: 描述说明
        :return: Ret对象，错误返回错误代码，成功返回文件夹对象
        """
        try:
            res = cls.create_abstract(
                rname=rname,
                rtype=RtypeChoice.FOLDER.value,
                desc=desc,
                user=user,
                parent=res_parent,
                dlpath=None,
                rsize=0,
                sub_type=StypeChoice.FOLDER.value,
                mime=None,
            )
            res.save()
        except Exception:
            raise ResourceError.CREATE_FOLDER
        return res

    @classmethod
    def create_link(cls, rname, user, res_parent, dlpath):
        """ 创建链接对象

        :param rname: 链接名称
        :param user: 所属用户
        :param res_parent: 所在目录
        :param dlpath: 链接地址
        :return: Ret对象，错误返回错误代码，成功返回链接对象
        """
        try:
            res = cls.create_abstract(
                rname=rname,
                rtype=RtypeChoice.LINK.value,
                desc=None,
                user=user,
                parent=res_parent,
                dlpath=dlpath,
                rsize=0,
                sub_type=StypeChoice.LINK.value,
                mime=None,
            )
            res.save()
        except Exception as e:
            raise ResourceError.CREATE_LINK
        return res

    """
    查询方法
    """

    @classmethod
    def get_by_id(cls, res_str_id):
        try:
            res = cls.objects.get(res_str_id=res_str_id)
        except cls.DoesNotExist:
            raise ResourceError.RESOURCE_NOT_FOUND
        return res

    @classmethod
    def get_by_pk(cls, res_id):
        """根据资源id获取资源对象"""
        try:
            res = cls.objects.get(pk=res_id)
        except cls.DoesNotExist:
            raise ResourceError.RESOURCE_NOT_FOUND
        return res

    def belong(self, user):
        """判断资源是否属于用户"""
        return self.owner.pk == user.pk

    def is_home(self):
        return self.parent.pk == Resource.ROOT_ID

    def get_cover_urls(self):
        """获取封面链接"""
        res = self
        cover = None
        while res.pk != Resource.ROOT_ID:
            if res.cover_type == CoverChoice.PARENT.value:
                res = res.parent
            elif res.cover_type == CoverChoice.RESOURCE.value:
                try:
                    res = Resource.get_by_id(res.cover)
                except E:
                    return None, None
                if not res.belong(self.owner):
                    return None, None
            else:
                cover = res.cover
                break
        if res.cover_type == CoverChoice.SELF.value:
            if res.sub_type == StypeChoice.IMAGE.value:
                from Base.qn_manager import qn_res_manager
                return (qn_res_manager.get_resource_url(res.dlpath),
                        qn_res_manager.get_resource_url("%s-small" % res.dlpath))
        if cover is None:
            return None, None
        if res.cover_type == CoverChoice.UPLOAD.value:
            from Base.qn_manager import qn_res_manager
            return (qn_res_manager.get_resource_url(cover),
                    qn_res_manager.get_resource_url("%s-small" % cover))
        else:
            return cover, cover

    """
    字典方法
    """

    def _readable_owner(self):
        return self.owner.d()

    def _readable_create_time(self):
        return self.create_time.timestamp()

    def _readable_visit_key(self):
        return self.visit_key if self.status == StatusChoice.PROTECT.value else None

    def _readable_is_home(self):
        return self.is_home()

    def _readable_secure_env(self):
        if self.pk == Resource.ROOT_ID or \
                not self.right_bubble or \
                self.status == StatusChoice.PUBLIC.value:
            return True
        res = self.parent
        while res.pk != Resource.ROOT_ID:
            if res.status == StatusChoice.PUBLIC.value:
                return res.rname
            if not res.right_bubble:
                break
            res = res.parent
        return True

    def _readable_raw_cover(self):
        return self.cover

    def _readable_parent_str_id(self):
        return self.parent.res_str_id

    def d(self):
        dict_ = self.dictify('res_str_id', 'rname', 'rtype', 'rsize', 'sub_type', 'description',
                             'cover_type', 'owner', 'parent_str_id', 'status', 'create_time',
                             'dlcount', 'visit_key', 'is_home', 'right_bubble', 'secure_env',
                             'raw_cover')
        cover_urls = self.get_cover_urls()
        dict_.update(dict(
            cover=cover_urls[0],
            cover_small=cover_urls[1],
        ))
        return dict_

    def d_base(self):
        dict_ = self.dictify('status', 'is_home', 'owner', 'create_time', 'right_bubble')
        cover_urls = self.get_cover_urls()
        dict_.update(dict(
            cover=cover_urls[0],
            cover_small=cover_urls[1],
        ))
        return dict_

    def d_child(self):
        dict_ = self.dictify('res_str_id', 'rname', 'rtype', 'status', 'create_time', 'sub_type', 'dlcount')
        cover_urls = self.get_cover_urls()
        dict_.update(dict(
            cover_small=cover_urls[1],
        ))
        return dict_

    def d_layer(self):
        child_list = Resource.objects.filter(parent=self).dict(Resource.d_child)
        return dict(
            info=self.d(),
            child_list=child_list,
        )

    def d_child_selector(self):
        return self.dictify('res_str_id', 'rname', 'rtype', 'sub_type')

    def d_selector_layer(self):
        child_list = Resource.objects.filter(parent=self).dict(Resource.d_child_selector)
        info = self.dictify('is_home', 'res_str_id', 'rname', 'parent_str_id')
        return dict(
            info=info,
            child_list=child_list,
        )

    """
    查询方法
    """

    @classmethod
    def get_root_folder(cls, user):
        """获取当前用户的根目录"""
        try:
            res = cls.objects.get(owner=user, parent=1, rtype=RtypeChoice.FOLDER.value)
        except cls.DoesNotExist:
            raise ResourceError.GET_ROOT_FOLDER
        return res

    def readable(self, user, visit_key):
        """判断当前资源是否被当前用户可读"""
        res = self
        while res.pk != Resource.ROOT_ID:
            if res.owner == user or res.status == StatusChoice.PUBLIC.value:
                return True
            if res.status == StatusChoice.PROTECT.value and res.visit_key == visit_key:
                if user:
                    UserRight.update(user, res)
                return True
            if res.status == StatusChoice.PROTECT.value and UserRight.verify(user, res):
                return True
            if not res.right_bubble:
                break
            res = res.parent
            visit_key = None
        return False

    def get_dl_url(self):
        """获取当前资源的下载链接"""
        self.dlcount += 1
        self.save()
        if self.rtype == RtypeChoice.LINK.value:
            return self.dlpath
        from Base.qn_manager import qn_res_manager
        return qn_res_manager.get_resource_url(self.dlpath)

    def get_visit_key(self):
        """获取当前资源的访问密码"""
        if self.status == StatusChoice.PROTECT.value:
            return self.visit_key
        return None

    """
    修改方法
    """

    def modify_rname(self, rname):
        key = self.dlpath
        new_key = '%s/%s' % (key[:key.rfind('/')], rname)
        from Base.qn_manager import qn_res_manager
        qn_res_manager.move_res(key, new_key)
        self.rname = rname
        self.dlpath = new_key
        self.save()

    def modify_info(self, rname, description, status, visit_key, right_bubble, parent):
        """ 修改资源属性

        :param rname: 资源名称
        :param description: 资源介绍
        :param status: 资源分享类型（公开、私有、加密）
        :param visit_key: 资源加密密钥
        :param right_bubble: 资源读取权限是否向上查询
        :param parent: 移动后的新父目录
        :return: Ret对象，错误返回错误代码，成功返回资源对象
        """
        if rname is None:
            rname = self.rname
        if description is None:
            description = self.description or ''
        if status is None:
            status = self.status
        if visit_key is None:
            visit_key = self.visit_key
        if right_bubble is None:
            right_bubble = self.right_bubble
        if parent is None:
            parent = self.parent

        if self.rname != rname:
            if self.rtype == RtypeChoice.FILE.value:
                self.modify_rname(rname)
            else:
                self.rname = rname
        self.description = description
        self.status = status
        self.right_bubble = right_bubble
        self.parent = parent
        if status == StatusChoice.PROTECT.value:
            if self.visit_key != visit_key:
                self.visit_key = visit_key
                self.vk_change_time = datetime.datetime.now().timestamp()
        self.save()

    def modify_cover(self, cover, cover_type):
        """修改资源封面"""
        from Base.qn_manager import qn_res_manager
        if self.cover_type == CoverChoice.UPLOAD.value:
            try:
                qn_res_manager.delete_res(self.cover)
            except:
                pass
        self.cover = cover
        self.cover_type = cover_type
        self.save()
        return self

    def is_empty(self):
        """ 资源是否为空（针对文件夹资源） """
        res_list = Resource.objects.filter(parent=self)
        if res_list:
            return False
        return True

    def remove(self):
        """ 删除资源 """
        if self.rtype == RtypeChoice.FOLDER.value:
            if not self.is_empty():
                raise ResourceError.REQUIRE_EMPTY_FOLDER
        from Base.qn_manager import qn_res_manager
        if self.cover and self.cover_type == CoverChoice.UPLOAD.value:
            qn_res_manager.delete_res(self.cover)
            self.cover = None
            self.save()
        if self.rtype == RtypeChoice.FILE.value:
            qn_res_manager.delete_res(self.dlpath)
        self.delete()


class UserRight(models.Model):
    """
    用户可读资源权限表（记录加密资源可读性）
    """
    user = models.ForeignKey(
        'User.User',
        on_delete=models.CASCADE,
    )
    res = models.ForeignKey(
        'Resource.Resource',
        on_delete=models.CASCADE,
    )
    verify_time = models.FloatField(
        default=0,
    )

    @classmethod
    def update(cls, user: User, res: Resource):
        try:
            right = cls.get_right(user, res)
            right.verify_time = datetime.datetime.now().timestamp()
            right.save()
        except E as e:
            if e.eis(ResourceError.RESOURCE_NOT_FOUND):
                try:
                    right = cls(
                        user=user,
                        res=res,
                        verify_time=datetime.datetime.now().timestamp()
                    )
                    right.save()
                except Exception:
                    raise ResourceError.CREATE_RIGHT
            else:
                return e
        return right

    @classmethod
    def get_right(cls, user, res):
        try:
            right = cls.objects.get(user=user, res=res)
        except cls.DoesNotExist:
            raise ResourceError.RIGHT_NOT_FOUND
        return right

    @classmethod
    def verify(cls, user: User, res: Resource):
        if not user:
            return False
        try:
            right = cls.get_right(user, res)
        except E:
            return False
        if right.verify_time > res.vk_change_time:
            return True
        else:
            right.delete()
            return False


P_RNAME, P_VISIT_KEY, P_STATUS, P_DESC, P_RIGHT_BUBBLE, P_COVER, P_COVER_TYPE = Resource.get_params(
        'rname', 'visit_key', 'status', 'description', 'right_bubble', 'cover', 'cover_type')
