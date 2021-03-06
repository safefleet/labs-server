from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.conf.urls import url
from . import consumers

application = ProtocolTypeRouter({
    # (http->django views is added by default)
    'websocket': AuthMiddlewareStack(
        URLRouter(
            [
                url(r'^ws/vehicles/(?P<vehicle_id>\d+)/positions/$', consumers.VehicleConsumer),
            ]
        )
    ),
})
