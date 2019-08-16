from django.urls import path

from OAuth.views import OAuthView

urlpatterns = [
    path('qtb/callback', OAuthView.as_view()),
]
