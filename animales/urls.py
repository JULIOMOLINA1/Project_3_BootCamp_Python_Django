from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AnimalViewSet, IngresoViewSet, UbicacionTemporalViewSet

router = DefaultRouter()
router.register("animales", AnimalViewSet, basename="animal")
router.register("ingresos", IngresoViewSet, basename="ingreso")
router.register("ubicaciones", UbicacionTemporalViewSet, basename="ubicacion")

urlpatterns = [
    path("", include(router.urls)),
]