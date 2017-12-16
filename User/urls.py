# from django.conf.urls import url
from django.urls import path

from User.router import rt_user, rt_user_token, rt_user_avatar, rt_user_id
from User.views import avatar_callback

urlpatterns = [
    path('', rt_user),
    path('<int:user_id>', rt_user_id),
    path('token', rt_user_token),
    path('avatar', rt_user_avatar),
    path('avatar/callback', avatar_callback)
]
