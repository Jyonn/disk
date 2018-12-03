""" Adel Liu 180111

资源类和方法
"""
import datetime

from django.db import models
from django.utils.crypto import get_random_string

from Base.common import deprint
from Base.decorator import field_validator
from Base.error import Error
from Base.response import Ret
from User.models import User


class Resource(models.Model):
    """
    资源类
    根资源文件夹id=1
    一旦新增用户，就在根目录创建一个属于新增用户的文件夹
    """
    ROOT_ID = 1
    L = {
        'rname': 256,
        'description': 1024,
        'manager': 255,
        'dlpath': 1024,
        'visit_key': 16,
        'cover': 1024,
        'res_str_id': 6,
    }
    RTYPE_FILE = 0
    RTYPE_FOLDER = 1
    RTYPE_LINK = 2
    RTYPE_TUPLE = (
        (RTYPE_FILE, 'file'),
        (RTYPE_FOLDER, 'folder'),
        (RTYPE_LINK, 'link'),
    )
    STATUS_PUBLIC = 0
    STATUS_PRIVATE = 1
    STATUS_PROTECT = 2
    STATUS_TUPLE = (
        (STATUS_PUBLIC, 'public'),
        (STATUS_PRIVATE, 'private'),
        (STATUS_PROTECT, 'protect')
    )
    STYPE_FOLDER = 0
    STYPE_IMAGE = 1
    STYPE_VIDEO = 2
    STYPE_MUSIC = 3
    STYPE_FILE = 4
    STYPE_LINK = 5
    SUB_TYPE_TUPLE = (
        (STYPE_FOLDER, 'folder'),
        (STYPE_IMAGE, 'image'),
        (STYPE_VIDEO, 'video'),
        (STYPE_MUSIC, 'music'),
        (STYPE_FILE, 'normal file'),
        (STYPE_LINK, 'link'),
    )
    COVER_RANDOM = 0
    COVER_UPLOAD = 1
    COVER_PARENT = 2
    COVER_OUTLNK = 3
    COVER_TYPE_TUPLE = (
        (COVER_RANDOM, 'random cover'),
        (COVER_UPLOAD, 'upload cover'),
        (COVER_PARENT, 'same as parent'),
        (COVER_OUTLNK, 'use outsize link'),
    )
    rname = models.CharField(
        verbose_name='resource name',
        max_length=L['rname'],
    )
    rtype = models.IntegerField(
        verbose_name='file or folder',
        choices=RTYPE_TUPLE,
    )
    rsize = models.IntegerField(
        default=0,
    )
    sub_type = models.IntegerField(
        verbose_name='sub type',
        choices=SUB_TYPE_TUPLE,
        default=STYPE_FOLDER,
    )
    description = models.CharField(
        verbose_name='description in Markdown',
        max_length=L['description'],
        null=True,
        blank=True,
        default=None,
    )
    cover = models.CharField(
        null=True,
        blank=True,
        default=None,
        max_length=L['cover']
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
        max_length=L['dlpath'],
        default=None,
        null=True,
        blank=True,
    )
    status = models.IntegerField(
        choices=STATUS_TUPLE,
        verbose_name='加密状态 0公开 1仅自己可见 2需要密码',
        default=STATUS_PUBLIC,
    )
    visit_key = models.CharField(
        max_length=L['visit_key'],
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
        max_length=L['res_str_id'],
        unique=True,
    )
    right_bubble = models.NullBooleanField(
        verbose_name='读取权限向上冒泡',
        default=True,
    )
    cover_type = models.IntegerField(
        choices=COVER_TYPE_TUPLE,
        verbose_name='封面类型 0 上传图片 1 与父资源相同 2 与指定资源相同 3 外部URI链接',
        default=COVER_RANDOM,
        null=0,
        blank=0,
    )

    FIELD_LIST = [
        'rname', 'rtype', 'rsize', 'sub_type', 'description', 'cover', 'owner',
        'parent', 'dlpath', 'status', 'visit_key', 'create_time', 'dlcount',
        'res_str_id', 'right_bubble', 'cover_type',
    ]

    @classmethod
    def get_unique_res_str_id(cls):
        while True:
            res_str_id = get_random_string(length=cls.L['res_str_id'])
            ret = cls.get_res_by_str_id(res_str_id)
            if ret.error == Error.NOT_FOUND_RESOURCE:
                return res_str_id
            deprint('generate res_str_id: %s, conflict.' % res_str_id)

    @staticmethod
    def _valid_rname(rname):
        """验证rname属性"""
        invalid_chars = '\\/*:\'"|<>?'
        for char in invalid_chars:
            if char in rname:
                # print(char)
                return Ret(Error.INVALID_RNAME)
        return Ret()

    @staticmethod
    def pub_valid_rname(rname):
        """验证rname属性"""
        return Resource._valid_rname(rname)

    @staticmethod
    def _valid_o_parent(o_parent):
        """验证o_parent属性"""
        if not isinstance(o_parent, Resource):
            return Ret(Error.STRANGE)
        if o_parent.rtype != Resource.RTYPE_FOLDER:
            return Ret(Error.ERROR_FILE_PARENT)
        return Ret()

    @staticmethod
    def _valid_visit_key(visit_key):
        if len(visit_key) < 3:
            return Ret(Error.VISIT_KEY_LEN)
        return Ret()

    @classmethod
    def _validate(cls, dict_):
        """验证传入参数是否合法"""
        return field_validator(dict_, Resource)

    @classmethod
    def create_abstract(cls, rname, rtype, desc, o_user, o_parent, dlpath, rsize, sub_type):
        crt_time = datetime.datetime.now()
        return cls(
            rname=rname,
            rtype=rtype,
            description=desc,
            cover=None,
            cover_type=cls.COVER_RANDOM,
            owner=o_user,
            parent=o_parent,
            dlpath=dlpath,
            status=cls.STATUS_PRIVATE,
            visit_key=get_random_string(length=4),
            create_time=crt_time,
            vk_change_time=crt_time.timestamp(),
            rsize=rsize,
            sub_type=sub_type,
            res_str_id=cls.get_unique_res_str_id(),
            dlcount=0,
            right_bubble=True,
        )

    @classmethod
    def create_file(cls, rname, o_user, o_parent, dlpath, rsize, sub_type):
        """ 创建文件对象

        :param rname: 文件名
        :param o_user: 所属用户
        :param o_parent: 所属目录
        :param dlpath: 七牛存储的key
        :param rsize: 文件大小
        :param sub_type: 文件分类
        :return: Ret对象，错误返回错误代码，成功返回文件对象
        """
        ret = cls._validate(locals())
        if ret.error is not Error.OK:
            return ret

        try:
            o_res = cls.create_abstract(
                rname=rname,
                rtype=cls.RTYPE_FILE,
                desc=None,
                o_user=o_user,
                o_parent=o_parent,
                dlpath=dlpath,
                rsize=rsize,
                sub_type=sub_type,
            )
            o_res.save()
        except ValueError as err:
            deprint(str(err))
            return Ret(Error.ERROR_CREATE_FILE)
        return Ret(o_res)

    @classmethod
    def create_folder(cls, rname, o_user, o_parent, desc=None):
        """ 创建文件夹对象

        :param rname: 文件夹名
        :param o_user: 所属用户
        :param o_parent: 所属目录
        :param desc: 描述说明
        :return: Ret对象，错误返回错误代码，成功返回文件夹对象
        """
        ret = cls._validate(locals())
        if ret.error is not Error.OK:
            return ret

        try:
            o_res = cls.create_abstract(
                rname=rname,
                rtype=cls.RTYPE_FOLDER,
                desc=desc,
                o_user=o_user,
                o_parent=o_parent,
                dlpath=None,
                rsize=0,
                sub_type=cls.STYPE_FOLDER,
            )
            o_res.save()
        except ValueError as err:
            deprint(str(err))
            return Ret(Error.ERROR_CREATE_FOLDER)
        return Ret(o_res)

    @classmethod
    def create_link(cls, rname, o_user, o_parent, dlpath):
        """ 创建链接对象

        :param rname: 链接名称
        :param o_user: 所属用户
        :param o_parent: 所在目录
        :param dlpath: 链接地址
        :return: Ret对象，错误返回错误代码，成功返回链接对象
        """
        ret = cls._validate(locals())
        if ret.error is not Error.OK:
            return ret

        try:
            o_res = cls.create_abstract(
                rname=rname,
                rtype=cls.RTYPE_LINK,
                desc=None,
                o_user=o_user,
                o_parent=o_parent,
                dlpath=dlpath,
                rsize=0,
                sub_type=cls.STYPE_LINK,
            )
            o_res.save()
        except ValueError as err:
            deprint(str(err))
            return Ret(Error.ERROR_CREATE_LINK)
        return Ret(o_res)

    @classmethod
    def get_res_by_str_id(cls, res_str_id):
        try:
            o_res = cls.objects.get(res_str_id=res_str_id)
        except cls.DoesNotExist as err:
            deprint(str(err))
            return Ret(Error.NOT_FOUND_RESOURCE)
        return Ret(o_res)

    @classmethod
    def get_res_by_id(cls, res_id):
        """根据资源id获取资源对象"""
        try:
            o_res = cls.objects.get(pk=res_id)
        except cls.DoesNotExist as err:
            deprint(str(err))
            return Ret(Error.NOT_FOUND_RESOURCE)
        return Ret(o_res)

    def belong(self, o_user):
        """判断资源是否属于用户"""
        return self.owner == o_user

    def get_cover_urls(self):
        """获取封面链接"""
        o_res = self
        cover = None
        while o_res.pk != Resource.ROOT_ID:
            if o_res.cover_type == Resource.COVER_PARENT:
                o_res = o_res.parent
            else:
                cover = o_res.cover
                break
        if cover is None:
            return None, None
        if o_res.cover_type == Resource.COVER_UPLOAD:
            from Base.qn import QN_RES_MANAGER
            return (QN_RES_MANAGER.get_resource_url(cover),
                    QN_RES_MANAGER.get_resource_url("%s-small" % cover))
        else:
            return cover, cover

    def to_dict_for_child(self):
        """当资源作为子资源，获取简易字典"""
        cover_urls = self.get_cover_urls()
        return dict(
            res_str_id=self.res_str_id,
            rname=self.rname,
            rtype=self.rtype,
            # description=self.description,
            # cover=cover_urls[0],
            cover_small=cover_urls[1],
            status=self.status,
            create_time=self.create_time.timestamp(),
            sub_type=self.sub_type,
            dlcount=self.dlcount,
            # right_bubble=self.right_bubble,
        )

    def to_dict(self, o_user=None):
        """获取资源字典"""
        cover_urls = self.get_cover_urls()
        return dict(
            res_str_id=self.res_str_id,
            rname=self.rname,
            rtype=self.rtype,
            rsize=self.rsize,
            sub_type=self.sub_type,
            description=self.description,
            cover=cover_urls[0],
            cover_small=cover_urls[1],
            cover_type=self.cover_type,
            owner=self.owner.to_dict(),
            parent_str_id=self.parent.res_str_id,
            status=self.status,
            create_time=self.create_time.timestamp(),
            dlcount=self.dlcount,
            visit_key=self.visit_key if self.status == Resource.STATUS_PROTECT else None,
            is_home=self.parent_id == Resource.ROOT_ID,
            right_bubble=self.right_bubble,
            secure_env=self.secure_env()
        )

    def to_base_dict(self):
        """获取资源最基本信息"""
        cover_urls = self.get_cover_urls()
        return dict(
            cover=cover_urls[0],
            cover_small=cover_urls[1],
            status=self.status,
            is_home=self.parent_id == Resource.ROOT_ID,
            owner=self.owner.to_dict(),
            create_time=self.create_time.timestamp(),
            right_bubble=self.right_bubble,
        )

    def get_child_res_list(self):
        """获取目录的子资源列表"""
        _res_list = Resource.objects.filter(parent=self)

        res_list = []
        for o_res in _res_list:
            res_list.append(o_res.to_dict_for_child())
        return Ret(res_list)

    @staticmethod
    def get_root_folder(o_user):
        """获取当前用户的根目录"""
        try:
            o_res = Resource.objects.get(owner=o_user, parent=1, rtype=Resource.RTYPE_FOLDER)
        except Resource.DoesNotExist as err:
            deprint(str(err))
            return Ret(Error.ERROR_GET_ROOT_FOLDER)
        return Ret(o_res)

    def secure_env(self):
        if self.pk == Resource.ROOT_ID or \
                not self.right_bubble or \
                self.status == Resource.STATUS_PUBLIC:
            return True
        o_res = self.parent
        while o_res.pk != Resource.ROOT_ID:
            if o_res.status == Resource.STATUS_PUBLIC:
                return o_res.rname
            if not o_res.right_bubble:
                break
            o_res = o_res.parent
        return True

    def readable(self, o_user, visit_key):
        """判断当前资源是否被当前用户可读"""
        o_res = self
        while o_res.pk != Resource.ROOT_ID:
            if o_res.owner == o_user or o_res.status == Resource.STATUS_PUBLIC:
                return True
            if o_res.status == Resource.STATUS_PROTECT and o_res.visit_key == visit_key:
                UserRight.update(o_user, o_res)
                return True
            if o_res.status == Resource.STATUS_PROTECT and UserRight.verify(o_user, o_res):
                return True
            if not o_res.right_bubble:
                break
            o_res = o_res.parent
            visit_key = None
        return False

    def get_dl_url(self):
        """获取当前资源的下载链接"""
        if self.rtype != Resource.RTYPE_FILE:
            return None
        self.dlcount += 1
        self.save()
        from Base.qn import QN_RES_MANAGER
        return QN_RES_MANAGER.get_resource_url(self.dlpath)

    def get_visit_key(self):
        """获取当前资源的访问密码"""
        if self.status == Resource.STATUS_PROTECT:
            return self.visit_key
        return None

    def modify_rname(self, rname):
        key = self.dlpath
        new_key = '%s/%s' % (key[:key.rfind('/')], rname)
        from Base.qn import QN_RES_MANAGER
        ret = QN_RES_MANAGER.move_res(key, new_key)
        if ret.error is not Error.OK:
            return ret
        self.rname = rname
        self.dlpath = new_key
        self.save()
        return Ret()

    def modify_info(self, rname, description, status, visit_key, right_bubble, o_parent):
        """ 修改资源属性

        :param rname: 资源名称
        :param description: 资源介绍
        :param status: 资源分享类型（公开、私有、加密）
        :param visit_key: 资源加密密钥
        :param right_bubble: 资源读取权限是否向上查询
        :param o_parent: 移动后的新父目录
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
        if o_parent is None:
            o_parent = self.parent

        ret = self._validate(locals())
        if ret.error is not Error.OK:
            return ret
        if self.rname != rname:
            if self.rtype == Resource.RTYPE_FILE:
                ret = self.modify_rname(rname)
                if ret.error is not Error.OK:
                    return ret
            else:
                self.rname = rname
        # self.rname = rname
        self.description = description
        self.status = status
        self.right_bubble = right_bubble
        self.parent = o_parent
        if status == Resource.STATUS_PROTECT:
            if self.visit_key != visit_key:
                self.visit_key = visit_key
                self.vk_change_time = datetime.datetime.now().timestamp()
        self.save()
        return Ret()

    def modify_cover(self, cover, cover_type):
        """修改资源封面"""
        ret = self._validate(locals())
        if ret.error is not Error.OK:
            return ret
        from Base.qn import QN_RES_MANAGER
        if self.cover_type == self.COVER_UPLOAD:
            ret = QN_RES_MANAGER.delete_res(self.cover)
            if ret.error is not Error.OK:
                return ret
        self.cover = cover
        self.cover_type = cover_type
        self.save()
        return Ret(self)

    def is_empty(self):
        """ 资源是否为空（针对文件夹资源） """
        res_list = Resource.objects.filter(parent=self)
        if res_list:
            return False
        return True

    def delete_(self):
        """ 删除资源 """
        if self.rtype == Resource.RTYPE_FOLDER:
            if not self.is_empty():
                return Ret(Error.REQUIRE_EMPTY_FOLDER)
        from Base.qn import QN_RES_MANAGER
        if self.cover:
            ret = QN_RES_MANAGER.delete_res(self.cover)
            if ret.error is not Error.OK:
                return ret
            self.cover = None
            self.save()
        if self.rtype == Resource.RTYPE_FILE:
            ret = QN_RES_MANAGER.delete_res(self.dlpath)
            if ret.error is not Error.OK:
                return ret
        self.delete()
        return Ret()


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
    def update(cls, o_user, o_res):
        if not isinstance(o_user, User):
            return Ret(Error.STRANGE)
        if not isinstance(o_res, Resource):
            return Ret(Error.STRANGE)
        ret = cls.get_right(o_user, o_res)
        if ret.error is Error.OK:
            o_right = ret.body
            if not isinstance(o_right, UserRight):
                return Ret(Error.STRANGE)
            o_right.verify_time = datetime.datetime.now().timestamp()
            o_right.save()
            return Ret(o_right)
        try:
            o_right = cls(
                user=o_user,
                res=o_res,
                verify_time=datetime.datetime.now().timestamp()
            )
            o_right.save()
        except ValueError as err:
            deprint(str(err))
            return Ret(Error.ERROR_CREATE_RIGHT)
        return Ret(o_right)

    @classmethod
    def get_right(cls, o_user, o_res):
        try:
            o_right = cls.objects.get(user=o_user, res=o_res)
        except cls.DoesNotExist:
            return Ret(Error.NOT_FOUND_RIGHT)
        return Ret(o_right)

    @classmethod
    def verify(cls, o_user, o_res):
        if not isinstance(o_res, Resource):
            return False
        if not isinstance(o_user, User):
            return False
        ret = cls.get_right(o_user, o_res)
        if ret.error is not Error.OK:
            return False
        o_right = ret.body
        if not isinstance(o_right, UserRight):
            return False
        if o_right.verify_time > o_res.vk_change_time:
            return True
        else:
            o_right.delete()
            return False
