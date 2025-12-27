from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Importer les vues de tes apps
from cars import views as cars_views
from home import views as home_views  # Renommé 'core' -> 'home'

urlpatterns = [
    path('admin/', admin.site.urls),

    # Page d'accueil publique
    path('', home_views.home_view, name='home'),

    # Upload et résultats (pour utilisateurs connectés)
    path('upload/', cars_views.upload_view, name='upload'),
    path('result/<int:pk>/', cars_views.result_view, name='result'),

    # Pages comptes (login/signup)
    path('accounts/', include('accounts.urls')),
]

# Servir les fichiers media pendant le développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
