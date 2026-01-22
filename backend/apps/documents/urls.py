# backend/apps/documents/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FolderViewSet, DocumentViewSet

router = DefaultRouter()
router.register(r'folders', FolderViewSet, basename='folder')
router.register(r'documents', DocumentViewSet, basename='document')

urlpatterns = [
    path('', include(router.urls)),
    # Actions importantes :
    # GET  /documents/<id>/download/
    # POST /documents/<id>/nouvelle-version/
    # GET  /documents/<id>/versions/
]