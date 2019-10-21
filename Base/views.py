import qiniu
from SmartDjango import ErrorJar
from django.views import View

from Base.qn_manager import qn_auth, RES_BUCKET, key_prefix
from Resource.models import Resource


class ErrorView(View):
    @staticmethod
    def get(_):
        """GET /base/errors"""
        return ErrorJar.all()


class CleanerView(View):
    @staticmethod
    def get(_):
        resources = Resource.objects.all()

        manager = qiniu.BucketManager(qn_auth)
        ret, eof, info = manager.list(RES_BUCKET, key_prefix)
        if ret.get('items'):
            items = ret['items']
            items = list(map(lambda x: dict(k=x['key'], m=x['mimeType']), items))
            dict_ = dict()
            for item in items:
                dict_[item['k']] = dict(m=item['m'])

            for resource in resources:
                resource.mime = None
                if resource.rtype == Resource.RTYPE_FILE:
                    if resource.dlpath in dict_:
                        resource.mime = dict_[resource.dlpath]['m']
                        del dict_[resource.dlpath]
                resource.save()

            for k in dict_:
                manager.delete(RES_BUCKET, k)
