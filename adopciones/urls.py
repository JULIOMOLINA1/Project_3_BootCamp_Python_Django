from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AdopcionViewSet,
    AdoptanteViewSet,
    SeguimientoAdopcionViewSet,
    SolicitudAdopcionViewSet,
)

router = DefaultRouter()
router.register("adoptantes", AdoptanteViewSet, basename="adoptante")
router.register("solicitudes", SolicitudAdopcionViewSet, basename="solicitud")
router.register("adopciones", AdopcionViewSet, basename="adopcion")
router.register("seguimientos", SeguimientoAdopcionViewSet, basename="seguimiento")

urlpatterns = [
    path("", include(router.urls)),
]