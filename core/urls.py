from django.urls import path
from . import views


urlpatterns = [
    path('getrequest', views.iclock_getrequest, name='iclock_getrequest'),
    path('cdata', views.iclock_cdata, name='iclock_cdata'),
]
