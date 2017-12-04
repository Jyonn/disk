from django.conf.urls import url, include

urlpatterns = [
    url(r'^user/', include('User.urls')),
    # url(r'^resource/', include('Resource.urls')),
]