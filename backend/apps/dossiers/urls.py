# backend/apps/dossiers/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DossierViewSet

router = DefaultRouter()
router.register(r'', DossierViewSet, basename='dossier')

urlpatterns = [
    path('', include(router.urls)),
    # Actions custom :
    # POST /dossiers/<id>/cloturer/
    # POST /dossiers/<id>/archiver/
    # GET  /dossiers/<id>/folders/
    # GET  /dossiers/stats/
]