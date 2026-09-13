from django.contrib import admin

from .models import Albergue


@admin.register(Albergue)
class AlbergueAdmin(admin.ModelAdmin):
    list_display = ("nombre", "direccion", "telefono")
    search_fields = ("nombre", "direccion")