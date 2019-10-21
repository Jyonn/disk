from SmartDjango import ErrorJar
from django.views import View


class ErrorView(View):
    @staticmethod
    def get(_):
        """GET /base/errors"""
        return ErrorJar.all()
