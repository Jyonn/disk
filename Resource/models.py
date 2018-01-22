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
        'visit_key': 4,
        'cover': 1024,
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
    create_time = models.DateTimeField()
    dlcount = models.IntegerField(
        verbose_name='download number',
        default=0,
    )
    FIELD_LIST = [
        'rname', 'rtype', 'rsize', 'sub_type', 'description', 'cover', 'owner',
        'parent', 'dlpath', 'status', 'visit_key', 'create_time', 'dlcount'
    ]

    @staticmethod
    def _valid_rname(rname):
        """验证rname属性"""
        invalid_chars = '\\/*:\'"|<>?'
        for char in invalid_chars:
            if char in rname:
                print(char)
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

    @classmethod
    def _validate(cls, dict_):
        """验证传入参数是否合法"""
        return field_validator(dict_, Resource)

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
            o_res = cls(
                rname=rname,
                rtype=Resource.RTYPE_FILE,
                description=None,
                cover=None,
                owner=o_user,
                parent=o_parent,
                dlpath=dlpath,
                status=Resource.STATUS_PRIVATE,
                visit_key=get_random_string(length=4),
                rsize=rsize,
                sub_type=sub_type,
                create_time=datetime.datetime.now(),
            )
            o_res.save()
        except ValueError as err:
            deprint(str(err))
            return Ret(Error.ERROR_CREATE_FILE)
        return Ret(Error.OK, o_res)

    @classmethod
    def create_folder(cls, rname, o_user, o_parent, desc):
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
            o_res = cls(
                rname=rname,
                rtype=Resource.RTYPE_FOLDER,
                sub_type=Resource.STYPE_FOLDER,
                description=desc,
                cover=None,
                owner=o_user,
                parent=o_parent,
                dlpath=None,
                status=Resource.STATUS_PRIVATE,
                visit_key=get_random_string(length=4),
                rsize=0,
                dlcount=0,
            )
            o_res.save()
        except ValueError as err:
            deprint(str(err))
            return Ret(Error.ERROR_CREATE_FOLDER)
        return Ret(Error.OK, o_res)

    @classmethod
    def create_link(cls, rname, o_user, o_parent, desc, dlpath):
        """ 创建链接对象

        :param rname: 链接名称
        :param o_user: 所属用户
        :param o_parent: 所在目录
        :param desc: 介绍说明
        :param dlpath: 链接地址
        :return: Ret对象，错误返回错误代码，成功返回链接对象
        """
        ret = cls._validate(locals())
        if ret.error is not Error.OK:
            return ret

        try:
            o_res = cls(
                rname=rname,
                rtype=Resource.RTYPE_LINK,
                sub_type=Resource.STYPE_LINK,
                description=desc,
                cover=None,
                owner=o_user,
                parent=o_parent,
                dlpath=dlpath,
                status=Resource.STATUS_PRIVATE,
                visit_key=get_random_string(length=4),
                rsize=0,
                dlcount=0,
            )
            o_res.save()
        except ValueError as err:
            deprint(str(err))
            return Ret(Error.ERROR_CREATE_LINK)
        return Ret(Error.OK, o_res)

    @staticmethod
    def get_res_by_id(res_id):
        """根据资源id获取资源对象"""
        try:
            o_res = Resource.objects.get(pk=res_id)
        except Resource.DoesNotExist as err:
            deprint(str(err))
            return Ret(Error.NOT_FOUND_RESOURCE)
        return Ret(Error.OK, o_res)

    def belong(self, o_user):
        """判断资源是否属于用户"""
        return self.owner == o_user

    def get_cover_url(self, small=True):
        """获取封面链接"""
        if self.cover is None:
            return None
        from Base.qn import get_resource_url
        key = "%s-small" % self.cover if small else self.cover
        return get_resource_url(key)

    def to_dict_for_child(self):
        """当资源作为子资源，获取简易字典"""
        return dict(
            res_id=self.pk,
            rname=self.rname,
            rtype=self.rtype,
            # description=self.description,
            cover=self.get_cover_url(),
            status=self.status,
            create_time=self.create_time.timestamp(),
            sub_type=self.sub_type,
            dlcount=self.dlcount,
        )

    def to_dict(self):
        """获取资源字典"""
        return dict(
            res_id=self.pk,
            rname=self.rname,
            rtype=self.rtype,
            rsize=self.rsize,
            sub_type=self.sub_type,
            description=self.description,
            cover=self.get_cover_url(small=False),
            owner=self.owner.to_dict(),
            parent_id=self.parent_id,
            status=self.status,
            create_time=self.create_time.timestamp(),
            dlcount=self.dlcount,
            visit_key=self.visit_key,
        )

    def get_child_res_list(self):
        """获取目录的子资源列表"""
        _res_list = Resource.objects.filter(parent=self)

        res_list = []
        for o_res in _res_list:
            res_list.append(o_res.to_dict_for_child())

        return Ret(Error.OK, res_list)

    @staticmethod
    def get_root_folder(o_user):
        """获取当前用户的根目录"""
        try:
            o_res = Resource.objects.get(owner=o_user, parent=1, rtype=Resource.RTYPE_FOLDER)
        except Resource.DoesNotExist as err:
            deprint(str(err))
            return Ret(Error.ERROR_GET_ROOT_FOLDER)
        return Ret(Error.OK, o_res)

    def readable(self, o_user, visit_key):
        """判断当前资源是否被当前用户可读"""
        if self.owner == o_user or self.status == Resource.STATUS_PUBLIC:
            return True
        if self.status == Resource.STATUS_PROTECT and self.visit_key == visit_key:
            return True
        return False

    def get_dl_url(self):
        """获取当前资源的下载链接"""
        if self.rtype != Resource.RTYPE_FILE:
            return None
        self.dlcount += 1
        self.save()
        from Base.qn import get_resource_url
        return get_resource_url(self.dlpath)

    def get_visit_key(self):
        """获取当前资源的访问密码"""
        if self.status == Resource.STATUS_PROTECT:
            return self.visit_key
        return None

    @staticmethod
    def decode_slug(slug):
        """解码slug并获取资源对象"""
        slug_list = slug.split('-')

        ret = Resource.get_res_by_id(Resource.ROOT_ID)
        if ret.error is not Error.OK:
            return ret
        o_res_parent = ret.body

        for rid in slug_list:
            try:
                rid = int(rid)
            except ValueError as err:
                deprint(str(err))
                return Ret(Error.ERROR_RESOURCE_ID)
            ret = Resource.get_res_by_id(rid)
            if ret.error is not Error.OK:
                return ret
            o_res_crt = ret.body
            if not isinstance(o_res_crt, Resource):
                return Ret(Error.STRANGE)
            if o_res_crt.parent != o_res_parent:
                return Ret(Error.ERROR_RESOURCE_RELATION)
            o_res_parent = o_res_crt
        return Ret(Error.OK, o_res_parent)

    def modify_info(self, rname, description, status, visit_key):
        """ 修改资源属性

        :param rname: 资源名称
        :param description: 资源介绍
        :param status: 资源分享类型（公开、私有、加密）
        :param visit_key: 资源加密密钥
        :return: Ret对象，错误返回错误代码，成功返回资源对象
        """
        if rname is None:
            rname = self.rname
        if description is None:
            description = self.description or ''
        if status is None:
            status = self.status
        if visit_key is None:
            visit_key = get_random_string(length=4)
        ret = self._validate(locals())
        if ret.error is not Error.OK:
            return ret
        self.rname = rname
        self.description = description
        self.status = status
        if status == Resource.STATUS_PROTECT:
            self.visit_key = visit_key
        self.save()
        return Ret()

    def modify_cover(self, cover):
        """修改资源封面"""
        ret = self._validate(locals())
        if ret.error is not Error.OK:
            return ret
        self.cover = cover
        self.save()
        return Ret()

    def delete_(self):
        # TODO: 删除资源
        pass