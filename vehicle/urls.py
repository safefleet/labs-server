from vehicle.views import VehicleViewSet, JourneyViewSet, PositionViewSet
from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('', VehicleViewSet),
router.register(r'(?P<vehicle_id>[0-9]*)/journeys', JourneyViewSet)
router.register(r'(?P<vehicle_id>[0-9]*)/journeys/(?P<journey_id>[0-9]*)/positions', PositionViewSet)
urlpatterns = router.urls
