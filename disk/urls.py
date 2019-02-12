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
from django.http import HttpResponseRedirect
from django.urls import path, include

from Resource.router import rt_direct_link


# def page_not_found(request):
#     return HttpResponseRedirect('https://github.com/lqj679ssn/disk')


urlpatterns = [
    path('api/', include('disk.api_urls')),
    path('s/<str:res_str_id>/', rt_direct_link),
    path('s/<str:res_str_id>/<str:_>', rt_direct_link),
    path('s/<str:res_str_id>', rt_direct_link),
]

# handler404 = page_not_found
# handler500 = page_not_found
