from django.urls import path
from . import views

app_name = "cars"

urlpatterns = [
    path("", views.home, name="home"),           # accueil
    path("upload/", views.upload_car, name="upload"),
    path("design/<int:pk>/", views.car_detail, name="car_detail"),
    path("design/<int:pk>/import/", views.import_latest_generated, name="import_generated"),
    path("base/", views.base_page, name="base"),
    path("renders/new/", views.render_new, name="render_new"),
]