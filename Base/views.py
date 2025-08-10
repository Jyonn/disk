from django.views import View
from smartdjango import Error
from smartdjango.analyse import Request


class ErrorView(View):
    def get(self, request: Request):
        """GET /base/errors"""
        return Error.all()
