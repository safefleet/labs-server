from django.conf.urls import url

from . import consumers

websocket_urlpatterns = [
    url(r'^position/(?P<vehicle_id>\d+)/$', consumers.VehicleConsumer),
]
