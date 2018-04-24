from django.contrib import admin
from django.urls import path, include

from project import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.api_root),
    path('api/v1/auth/', include('authentication.urls')),
]
