from django.contrib import admin

from .models import AtencionVeterinaria


@admin.register(AtencionVeterinaria)
class AtencionVeterinariaAdmin(admin.ModelAdmin):
    list_display = ("animal", "fecha_atencion", "diagnostico", "veterinario_responsable", "costo")
    list_filter = ("fecha_atencion",)
    search_fields = ("animal__nombre", "diagnostico", "veterinario_responsable")