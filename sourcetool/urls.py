from django.urls import path
from . import views

urlpatterns = [
    path('', views.post_listener, name='post_listener')
]
