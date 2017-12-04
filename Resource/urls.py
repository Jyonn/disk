from django.conf.urls import url

from Resource.router import rt_res_token

urlpatterns = [
    url(r'^token$', rt_res_token),
]