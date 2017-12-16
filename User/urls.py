from django.conf.urls import url

from User.router import rt_user, rt_user_token, rt_user_avatar
from User.views import avatar_callback

urlpatterns = [
    url(r'^$', rt_user),
    url(r'^token$', rt_user_token),
    url(r'^avatar$', rt_user_avatar),
    url(r'^avatar/callback$', avatar_callback)
]