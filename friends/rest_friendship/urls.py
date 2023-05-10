from django.urls import include
from django.urls import path
from rest_framework import routers

from . import views

v1_router = routers.DefaultRouter()
v1_router.register('friends', views.FriendViewSet, 'friend')

urlpatterns = [
    path('', include(v1_router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
]
