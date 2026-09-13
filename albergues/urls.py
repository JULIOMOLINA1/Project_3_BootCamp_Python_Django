from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AlbergueViewSet

router = DefaultRouter()
router.register("albergues", AlbergueViewSet, basename="albergue")

urlpatterns = [
    path("", include(router.urls)),
]