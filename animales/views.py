from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .models import Animal, Ingreso, UbicacionTemporal
from .serializers import AnimalSerializer, IngresoSerializer, UbicacionTemporalSerializer


class AnimalViewSet(viewsets.ModelViewSet):
    serializer_class = AnimalSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    search_fields = ["nombre", "especie", "raza"]
    ordering_fields = ["nombre", "especie", "id"]

    def get_queryset(self):
        return (
            Animal.objects.all()
            .prefetch_related(
                "ingresos__albergue_inicial",
                "ubicaciones__albergue",
                "atenciones_medicas",
                "solicitudes__adoptante",
                "solicitudes__adopcion",
            )
        )


class IngresoViewSet(viewsets.ModelViewSet):
    queryset = Ingreso.objects.select_related("animal", "albergue_inicial").all()
    serializer_class = IngresoSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    search_fields = ["motivo_ingreso", "animal__nombre"]
    ordering_fields = ["fecha_ingreso", "id"]


class UbicacionTemporalViewSet(viewsets.ModelViewSet):
    queryset = UbicacionTemporal.objects.select_related("animal", "albergue").all()
    serializer_class = UbicacionTemporalSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    search_fields = ["observaciones", "animal__nombre", "albergue__nombre"]
    ordering_fields = ["fecha_entrada", "fecha_salida", "id"]