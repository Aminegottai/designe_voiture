from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from home import views as home_views  # vue home_view dans l’app home
from cars import views as cars_views

urlpatterns = [
    path("", home_views.home_view, name="home"),
    path("accounts/", include("accounts.urls")),
    path("cars/", include("cars.urls")),
    path("admin/", admin.site.urls),
    path("renders/new/", cars_views.render_new, name="render_new_root"),
]

# Optionnel : servir les fichiers médias en dev
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)