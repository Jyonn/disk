from django.conf.urls import url

from User.router import rt_user, rt_user_token

urlpatterns = [
    url(r'^$', rt_user),
    url(r'^token$', rt_user_token),
]