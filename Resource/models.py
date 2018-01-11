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
    create_time = models.DateTimeField(
        auto_created=True,
        auto_now=True,
    )
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
        invalid_chars = '\\/*:\'"|<>?'
        for char in invalid_chars:
            if char in rname:
                print(char)
                return Ret(Error.INVALID_RNAME)
        return Ret()

    @staticmethod
    def _valid_o_parent(o_parent):
        if not isinstance(o_parent, Resource):
            return Ret(Error.STRANGE)
        if o_parent.rtype != Resource.RTYPE_FOLDER:
            return Ret(Error.ERROR_FILE_PARENT)
        return Ret()

    @classmethod
    def _validate(cls, d):
        return field_validator(d, Resource)

    @classmethod
    def create_file(cls, rname, o_user, o_parent, dlpath, status, rsize, sub_type):
        print(locals())
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
                status=status,
                visit_key=get_random_string(length=4),
                rsize=rsize,
                sub_type=sub_type,
            )
            o_res.save()
        except Exception as e:
            deprint(str(e))
            return Ret(Error.CREATE_FILE_ERROR)
        return Ret(Error.OK, o_res)

    @classmethod
    def create_folder(cls, rname, o_user, o_parent, desc, status):
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
                status=status,
                visit_key=get_random_string(length=4),
                rsize=0,
                dlcount=0,
            )
            o_res.save()
        except Exception as e:
            deprint(str(e))
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
        # if not isinstance(o_user, User):
        #     return Ret(Error.STRANGE)
        return self.owner == o_user

    def get_cover_url(self):
        if self.cover is None:
            return None
        from Base.qn import get_resource_url
        return get_resource_url(self.cover)

    def to_dict_for_child(self):
        return dict(
            res_id=self.pk,
            rname=self.rname,
            rtype=self.rtype,
            # description=self.description,
            cover=self.get_cover_url(),
            status=self.status,
            create_time=self.create_time.timestamp(),
        )

    def to_dict(self):
        return dict(
            res_id=self.pk,
            rname=self.rname,
            rtype=self.rtype,
            sub_type=self.sub_type,
            description=self.description,
            cover=self.get_cover_url(),
            owner=self.owner.to_dict(),
            parent_id=self.parent_id,
            status=self.status,
            create_time=self.create_time.timestamp(),
        )

    def get_child_res_list(self):
        _res_list = Resource.objects.filter(parent=self)

        res_list = []
        for o_res in _res_list:
            res_list.append(o_res.to_dict_for_child())

        return Ret(Error.OK, res_list)

    @staticmethod
    def get_root_folder(o_user):
        try:
            o_res = Resource.objects.get(owner=o_user, parent=1, rtype=Resource.RTYPE_FOLDER)
        except Exception as e:
            deprint(str(e))
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
        self.dlcount += 1
        self.save()
        from Base.qn import get_resource_url
        return get_resource_url(self.dlpath)

    def get_visit_key(self):
        if self.status == Resource.STATUS_PROTECT:
            return self.visit_key
        return None

    def change_visit_key(self):
        self.visit_key = get_random_string(length=4)
        self.save()

    @staticmethod
    def decode_slug(slug):
        slug_list = slug.split('-')

        ret = Resource.get_res_by_id(Resource.ROOT_ID)
        if ret.error is not Error.OK:
            return ret
        o_res_parent = ret.body

        for rid in slug_list:
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

    def modify_info(self, rname, description, status):
        if rname is None:
            rname = self.rname
        if description is None:
            description = self.description
        if status is None:
            status = self.status
        ret = self._validate(locals())
        if ret.error is not Error.OK:
            return ret
        self.rname = rname
        self.description = description
        if self.status != status:
            self.change_visit_key()
            self.status = status
        self.save()
        return Ret()
