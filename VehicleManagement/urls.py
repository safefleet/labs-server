from django.conf.urls import url
from VehicleManagement import views

urlpatterns = [
    url(r'^vehicle/$', views.#vehicle ),
    url(r'^vehicle/(?P<pk>[0-9]+)/$', views.#vehicle_detail),
]