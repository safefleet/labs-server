from django.urls import path

from liveServer import views



urlpatterns = [
    path('test/', views.room, name='room'),
]


