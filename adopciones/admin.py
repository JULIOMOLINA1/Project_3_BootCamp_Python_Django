from django.contrib import admin

from .models import Adopcion, Adoptante, SeguimientoAdopcion, SolicitudAdopcion


@admin.register(Adoptante)
class AdoptanteAdmin(admin.ModelAdmin):
    list_display = ("nombre", "apellido", "telefono", "email")
    search_fields = ("nombre", "apellido", "email")


@admin.register(SolicitudAdopcion)
class SolicitudAdopcionAdmin(admin.ModelAdmin):
    list_display = ("animal", "adoptante", "fecha_solicitud", "estado")
    list_filter = ("estado",)
    search_fields = ("animal__nombre", "adoptante__nombre", "adoptante__apellido")


class SeguimientoInline(admin.TabularInline):
    model = SeguimientoAdopcion
    extra = 0


@admin.register(Adopcion)
class AdopcionAdmin(admin.ModelAdmin):
    list_display = ("solicitud", "fecha_adopcion")
    search_fields = ("solicitud__animal__nombre",)
    inlines = [SeguimientoInline]


@admin.register(SeguimientoAdopcion)
class SeguimientoAdopcionAdmin(admin.ModelAdmin):
    list_display = ("adopcion", "fecha", "nota")
    search_fields = ("adopcion__solicitud__animal__nombre", "nota")