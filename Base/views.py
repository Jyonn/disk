from SmartDjango import E
from django.views import View


class ErrorView(View):
    @staticmethod
    def get(_):
        """GET /base/errors"""
        return E.all()
