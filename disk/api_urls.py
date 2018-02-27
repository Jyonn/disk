""" Adel Liu 180111

api子路由
"""
from django.urls import path, include

urlpatterns = [
    path('user/', include('User.urls')),
    path('res/', include('Resource.urls')),
    path('base/', include('Base.urls')),
]
