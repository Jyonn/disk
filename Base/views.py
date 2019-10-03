from SmartDjango import Excp, ErrorCenter
from django.views import View


class ErrorView(View):
    @staticmethod
    @Excp.handle
    def get(r):
        """GET /base/errors"""
        return ErrorCenter.all()
