from django.contrib import admin
from django.urls import path, include

from project import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('authentication.urls')),
]

