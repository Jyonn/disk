"""disk URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.urls import path, include
from django.shortcuts import render

from Base.decorator import require_get
from Base.qn import get_resource_url
from Base.response import response


def index(request):
    """上传测试"""
    return render(request, 'upload.html')


# @require_get(['key'])
# def dl(request):
#     """URL测试"""
#     return response(body=get_resource_url(request.d.key))


urlpatterns = [
    path('api/', include('disk.api_urls')),
    path('upload', index),
    # path('dl', dl),
]
