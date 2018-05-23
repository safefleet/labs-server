from vehicle.views import VehicleViewSet, JourneyViewSet, PositionViewSet
from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('', VehicleViewSet),
router.register(r'(?P<vehicleId>[0-9]*)/journeys', JourneyViewSet)
router.register(r'(?P<vehicleId>[0-9]*)/journeys/(?P<journeyId>[0-9]*)/positions', PositionViewSet)
urlpatterns = router.urls
