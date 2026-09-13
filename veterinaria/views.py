from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .models import AtencionVeterinaria
from .serializers import AtencionVeterinariaSerializer


class AtencionVeterinariaViewSet(viewsets.ModelViewSet):
    queryset = AtencionVeterinaria.objects.select_related("animal").all()
    serializer_class = AtencionVeterinariaSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    search_fields = ["diagnostico", "tratamiento", "veterinario_responsable", "animal__nombre"]
    ordering_fields = ["fecha_atencion", "costo", "id"]