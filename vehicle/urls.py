from vehicle.views import VehicleViewSet,PositionViewSet,JourneyViewSet
from django.urls import path

vehicle_list = VehicleViewSet.as_view({'get': 'list', 'post': 'create'})
vehicle_detail = VehicleViewSet.as_view({'get': 'retrieve', 'put': 'update',
                                         'patch': 'partial_update', 'delete': 'destroy'})

position_list = PositionViewSet.as_view({'get': 'list'})
position_list_filter = PositionViewSet.as_view({'get': 'retrieve','post': 'create'})

journey_list = JourneyViewSet.as_view({'get': 'list','post': 'create'})

app_name = 'vehicles'
urlpatterns = [
    path('', vehicle_list),
    path('<int:vehicleId>/', vehicle_detail),
    path('<int:vehicleId>/positions', position_list),
    path('<int:vehicleId>/journeys', journey_list),
    path('<int:vehicleId>/journeys/<int:journeyId>/positions', position_list_filter),
]

