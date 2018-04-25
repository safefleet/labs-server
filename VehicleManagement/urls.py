from django.conf.urls import url
from VehicleManagement import views
from django.urls import path

app_name = 'vehicles'
urlpatterns = [
    path('', views.vehicle_list),
    path('<int:pk>/', views.vehicle_detail),
    path('<int:pk>/positions', views.position_list),
    path('<int:pk>/journeys', views.journey_list),
    path('<int:pk>/journeys/<int:pk1>/positions', views.position_list_filter),
]

