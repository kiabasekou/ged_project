# backend/backend/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    # ------------------------------------------------------------------
    # Administration Django (personnalisée avec ton titre Cabinet Kiaba)
    # ------------------------------------------------------------------
    path('admin/', admin.site.urls),

    # ------------------------------------------------------------------
    # Authentification JWT (SimpleJWT)
    # ------------------------------------------------------------------
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    # ------------------------------------------------------------------
    # API Métier — Modules du cabinet
    # ------------------------------------------------------------------
    path('api/users/', include('apps.users.urls')),
    path('api/clients/', include('apps.clients.urls')),
    path('api/dossiers/', include('apps.dossiers.urls')),
    path('api/documents/', include('apps.documents.urls')),
    path('api/agenda/', include('apps.agenda.urls')),
    path('api/audit/', include('apps.audit.urls')),  # Réservé aux admins

    # ------------------------------------------------------------------
    # Page d'accueil simple (optionnel : pour accès direct /)
    # ------------------------------------------------------------------
    # path('', TemplateView.as_view(template_name='home.html'), name='home'),
]

# ------------------------------------------------------------------
# Service des fichiers statiques et médias
# En développement ET en déploiement on-premise (petit serveur local)
# En production derrière Nginx, tu désactiveras cela.
# ------------------------------------------------------------------
if settings.DEBUG or getattr(settings, 'DJANGO_ENV', None) == 'deployment':
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# ------------------------------------------------------------------
# Sécurité supplémentaire en production (optionnel mais recommandé)
# ------------------------------------------------------------------
if not settings.DEBUG:
    # Redirection HTTP → HTTPS si derrière proxy
    # from django.http import HttpResponsePermanentRedirect
    # class ForceHttpsMiddleware:
    #     def __init__(self, get_response):
    #         self.get_response = get_response
    #     def __call__(self, request):
    #         if not request.is_secure() and not settings.DEBUG:
    #             url = request.build_absolute_uri()
    #             secure_url = url.replace('http://', 'https://')
    #             return HttpResponsePermanentRedirect(secure_url)
    #         return self.get_response(request)
    pass