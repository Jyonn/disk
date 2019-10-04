from SmartDjango import ErrorCenter
from django.views import View


class ErrorView(View):
    @staticmethod
    def get(_):
        """GET /base/errors"""
        return ErrorCenter.all()
