from django.contrib import admin

from .models import Animal, Ingreso, UbicacionTemporal


class IngresoInline(admin.TabularInline):
    model = Ingreso
    extra = 0


class UbicacionInline(admin.TabularInline):
    model = UbicacionTemporal
    extra = 0


@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    list_display = ("nombre", "especie", "raza", "edad_aproximada", "sexo", "estado_actual")
    list_filter = ("especie", "sexo", "estado_actual")
    search_fields = ("nombre", "raza")
    inlines = [IngresoInline, UbicacionInline]


@admin.register(Ingreso)
class IngresoAdmin(admin.ModelAdmin):
    list_display = ("animal", "fecha_ingreso", "albergue_inicial", "motivo_ingreso")
    list_filter = ("albergue_inicial",)
    search_fields = ("animal__nombre", "motivo_ingreso")


@admin.register(UbicacionTemporal)
class UbicacionTemporalAdmin(admin.ModelAdmin):
    list_display = ("animal", "albergue", "fecha_entrada", "fecha_salida")
    list_filter = ("albergue",)
    search_fields = ("animal__nombre",)