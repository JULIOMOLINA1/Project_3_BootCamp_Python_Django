from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .models import Adopcion, Adoptante, SeguimientoAdopcion, SolicitudAdopcion
from .serializers import (
    AdopcionSerializer,
    AdoptanteSerializer,
    SeguimientoAdopcionSerializer,
    SolicitudAdopcionSerializer,
)


class AdoptanteViewSet(viewsets.ModelViewSet):
    queryset = Adoptante.objects.all()
    serializer_class = AdoptanteSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    search_fields = ["nombre", "apellido", "email"]
    ordering_fields = ["apellido", "nombre", "id"]


class SolicitudAdopcionViewSet(viewsets.ModelViewSet):
    queryset = SolicitudAdopcion.objects.select_related("animal", "adoptante").all()
    serializer_class = SolicitudAdopcionSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    search_fields = ["animal__nombre", "adoptante__nombre", "adoptante__apellido", "estado"]
    ordering_fields = ["fecha_solicitud", "estado", "id"]


class AdopcionViewSet(viewsets.ModelViewSet):
    queryset = Adopcion.objects.select_related(
        "solicitud__animal", "solicitud__adoptante"
    ).all()
    serializer_class = AdopcionSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    search_fields = ["solicitud__animal__nombre", "solicitud__adoptante__apellido"]
    ordering_fields = ["fecha_adopcion", "id"]


class SeguimientoAdopcionViewSet(viewsets.ModelViewSet):
    queryset = SeguimientoAdopcion.objects.select_related(
        "adopcion__solicitud__animal"
    ).all()
    serializer_class = SeguimientoAdopcionSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    search_fields = ["nota", "adopcion__solicitud__animal__nombre"]
    ordering_fields = ["fecha", "id"]