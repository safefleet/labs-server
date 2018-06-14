from django.contrib import admin
from django.urls import path, include
from rest_framework.documentation import include_docs_urls
from rest_framework_jwt.views import obtain_jwt_token

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/vehicles/', include('vehicle.urls')),
    path('api/auth/', include('authentication.urls')),
    path('api/docs/', include_docs_urls(title='Safefleet LABS',
                                        authentication_classes=[],
                                        permission_classes=[])),
    path('api-token-auth/', obtain_jwt_token)
]
