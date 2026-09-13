from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AtencionVeterinariaViewSet

router = DefaultRouter()
router.register("atenciones", AtencionVeterinariaViewSet, basename="atencion")

urlpatterns = [
    path("", include(router.urls)),
]