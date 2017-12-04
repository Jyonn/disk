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

    @classmethod
    def create_file(cls, rname, o_user, o_parent, desc, dlpath, status):
        if status not in [Resource.STATUS_PUBLIC, Resource.STATUS_PRIVATE, Resource.STATUS_PROTECT]:
            return Ret(Error.ERROR_RESOURCE_STATUS)
        try:
            o_res = cls(
                rname=rname,
                rtype=Resource.RTYPE_FILE,
                description=desc,
                avatar=None,
                owner=o_user,
                parent=o_parent,
                dlpath=dlpath,
                status=status,
                visit_key=get_random_string(length=4)
            )
        except:
            return Ret(Error.CREATE_FILE_ERROR)
        return Ret(Error.OK, o_res)

    @classmethod
    def create_folder(cls, rname, o_user, o_parent, desc):
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
            )
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
        # if self.rtype == self.RTYPE_FILE:
        #     return Ret(Error.ERROR_FILE_PARENT)
        # if self.owner == o_user or self.status == self.STATUS_PUBLIC or \
        #         (self.status == self.STATUS_PROTECT and self.visit_key == visit_key):
        _res_list = Resource.objects.filter(parent=self)
        # else:
        #     return Ret(Error.ERROR_REACH_PRIVATE)

        res_list = [self.to_dict()]
        for o_res in _res_list:
            res_list.append(o_res.to_dict())

        return Ret(Error.OK, res_list)

