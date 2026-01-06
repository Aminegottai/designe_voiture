from django.contrib import admin
from . models import CarDesign

@admin.register(CarDesign)
class CarDesignAdmin(admin. ModelAdmin):
    list_display = ('id', 'user', 'created_at', 'original_image', 'generated_image')
    list_filter = ('created_at', 'user')