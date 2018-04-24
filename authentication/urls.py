from django.urls import path

from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token, verify_jwt_token

from authentication.views import AuthRegister
from authentication import views

urlpatterns = [
    path('register/', AuthRegister.as_view(), name='register'),
    path('login/', obtain_jwt_token, name='login'),
    path('token-refresh/', refresh_jwt_token, name='token-refresh'),
    path('token-verify/', verify_jwt_token, name='token-verify'),
    path('users/', views.UserList.as_view(), name='user-list'),
    path('users/<int:pk>/', views.UserDetail.as_view(), name='user-detail'),
]
