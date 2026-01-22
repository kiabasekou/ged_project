# backend/apps/clients/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ClientViewSet

router = DefaultRouter()
router.register(r'', ClientViewSet, basename='client')

urlpatterns = [
    path('', include(router.urls)),
    # Actions supplémentaires :
    # POST   /clients/<id>/grant-consent/
    # GET    /clients/stats/
]