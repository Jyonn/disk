from SmartDjango import Packing, ErrorCenter
from django.views import View


class ErrorView(View):
    @staticmethod
    @Packing.http_pack
    def get(r):
        """GET /base/errors"""
        return ErrorCenter.all()
