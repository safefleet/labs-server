from django.conf.urls import url
from vehicle import views
from django.urls import path

app_name = 'vehicles'
urlpatterns = [
    path('', views.vehicle_list),
    path('<int:vehicleId>/', views.vehicle_detail),
    path('<int:vehicleId>/positions', views.position_list),
    path('<int:vehicleId>/journeys', views.journey_list),
    path('<int:vehicleId>/journeys/<int:journeyId>/positions', views.position_list_filter),
]

