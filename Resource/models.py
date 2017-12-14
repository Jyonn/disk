from django.db import models
from django.utils.crypto import get_random_string

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
    }
    RTYPE_FILE = 0
    RTYPE_FOLDER = 1
    RTYPE_TUPLE = (
        (RTYPE_FILE, 'file'),
        (RTYPE_FOLDER, 'folder'),
    )
    STATUS_PUBLIC = 0
    STATUS_PRIVATE = 1
    STATUS_PROTECT = 2
    STATUS_TUPLE = (
        (STATUS_PUBLIC, 'public'),
        (STATUS_PRIVATE, 'private'),
        (STATUS_PROTECT, 'protect')
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
    description = models.CharField(
        verbose_name='description in Markdown',
        max_length=L['description'],
    )
    avatar = models.URLField(
        null=True,
        blank=True,
        default=None,
    )
    owner = models.ForeignKey(
        User,
    )
    parent = models.ForeignKey(
        'Resource',
        null=True,
        blank=True,
        default=0,
    )
    dlpath = models.CharField(
        verbose_name='download relative path to res.6-79.cn',
        max_length=L['dlpath'],
        default=None,
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

    def format_attr(self):
        invalid_chars = '\\/.*:\'"|<>?'
        for char in invalid_chars:
            if char in self.rname:
                return Ret(Error.INVALID_RNAME)

        if self.status not in [Resource.STATUS_PUBLIC, Resource.STATUS_PRIVATE, Resource.STATUS_PROTECT]:
            return Ret(Error.ERROR_RESOURCE_STATUS)
        return Ret(Error.OK)

    @classmethod
    def create_file(cls, rname, o_user, o_parent, dlpath, status, size):
        try:
            o_res = cls(
                rname=rname,
                rtype=Resource.RTYPE_FILE,
                description=None,
                avatar=None,
                owner=o_user,
                parent=o_parent,
                dlpath=dlpath,
                status=status,
                visit_key=get_random_string(length=4),
                rsize=size,
            )
            ret = o_res.format_attr()
            if ret.error is not Error.OK:
                return ret
            o_res.save()
        except:
            return Ret(Error.CREATE_FILE_ERROR)
        return Ret(Error.OK, o_res)

    @classmethod
    def create_folder(cls, rname, o_user, o_parent, desc, status):
        if not isinstance(o_parent, Resource):
            return Ret(Error.STRANGE)
        if o_parent.rtype == Resource.RTYPE_FILE:
            return Ret(Error.ERROR_FILE_PARENT)
        try:
            o_res = cls(
                rname=rname,
                rtype=Resource.RTYPE_FOLDER,
                description=desc,
                avatar=None,
                owner=o_user,
                parent=o_parent,
                dlpath=None,
                status=status,
                visit_key=get_random_string(length=4),
                rsize=0,
            )
            ret = o_res.format_attr()
            if ret.error is not Error.OK:
                return ret
            o_res.save()
        except:
            return Ret(Error.CREATE_FOLDER_ERROR)
        return Ret(Error.OK, o_res)

    @staticmethod
    def get_res_by_id(res_id):
        try:
            o_res = Resource.objects.get(pk=res_id)
        except:
            return Ret(Error.NOT_FOUND_RESOURCE)
        return Ret(Error.OK, o_res)

    def belong(self, o_user):
        if not isinstance(o_user, User):
            return Ret(Error.STRANGE)
        return Ret(Error.OK, self.parent == o_user)

    def to_dict(self):
        return dict(
            rname=self.rname,
            rtype=self.rtype,
            description=self.description,
            avatar=self.avatar,
            owner=self.owner.to_dict(),
            parent_id=self.parent_id,
            status=self.status,
        )

    def get_child_res_list(self):
        _res_list = Resource.objects.filter(parent=self)

        res_list = [self.to_dict()]
        for o_res in _res_list:
            res_list.append(o_res.to_dict())

        return Ret(Error.OK, res_list)

    @staticmethod
    def get_root_folder(o_user):
        try:
            o_res = Resource.objects.get(owner=o_user, parent=1, rtype=Resource.RTYPE_FOLDER)
        except:
            return Ret(Error.ERROR_GET_ROOT_FOLDER)
        return Ret(Error.OK, o_res)

    def readable(self, o_user, visit_key):
        if self.owner == o_user or self.status == Resource.STATUS_PUBLIC:
            return True
        if self.status == Resource.STATUS_PROTECT and self.visit_key == visit_key:
            return True
        return False

    def get_dl_url(self):
        if self.rtype != Resource.RTYPE_FILE:
            return None
        from Base.qn import get_resource_url
        return get_resource_url(self.dlpath)

    def change_visit_key(self):
        self.visit_key = get_random_string(length=4)
        self.save()

    def change_info(self, rname, status, desc):
        self.rname = rname
        self.status = status
        self.description = desc
        ret = Resource.format_attr(self)
        if ret.error is not Error.OK:
            return ret
        self.change_visit_key()
        self.save()
        return Ret()
