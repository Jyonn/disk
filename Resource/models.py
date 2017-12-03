from django.db import models

from Base.error import Error
from Base.response import Ret


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
    }
    RTYPE_FILE = 0
    RTYPE_FOLDER = 1
    RTYPE_TABLE = (
        (RTYPE_FILE, 'file'),
        (RTYPE_FOLDER, 'folder'),
    )
    rname = models.CharField(
        verbose_name='resource name',
        max_length=L['rname'],
    )
    rtype = models.IntegerField(
        verbose_name='file or folder',
        choices=RTYPE_TABLE,
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
        'User',
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

    @classmethod
    def create_file(cls, rname, o_user, o_parent, desc, dlpath):
        try:
            o_res = cls(
                rname=rname,
                rtype=Resource.RTYPE_FILE,
                description=desc,
                avatar=None,
                owner=o_user,
                parent=o_parent,
                dlpath=dlpath,
            )
        except:
            return Ret(Error.CREATE_FILE_ERROR)
        return Ret(Error.OK, o_res)

    @classmethod
    def create_folder(cls, rname, o_user, o_parent, desc):
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
