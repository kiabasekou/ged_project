# backend/apps/users/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet

router = DefaultRouter()
router.register(r'', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    # Les actions custom sont accessibles via :
    # GET  /users/me/
    # PATCH /users/update-profile/
    # POST /users/<id>/accept-privacy/
]