from django.conf.urls import url
from django.urls import path

from . import consumers

websocket_urlpatterns = [
    url(r'^ws/position/(?P<vehicle_id>\d+)/$', consumers.VehicleConsumer),
    #path('ws/position/<int:vehicle_id>', consumers.VehicleConsumer),
]
