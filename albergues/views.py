from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .models import Albergue
from .serializers import AlbergueSerializer


class AlbergueViewSet(viewsets.ModelViewSet):
    queryset = Albergue.objects.all()
    serializer_class = AlbergueSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    search_fields = ["nombre", "direccion", "telefono"]
    ordering_fields = ["nombre", "id"]