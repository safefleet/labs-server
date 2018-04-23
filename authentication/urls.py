from django.urls import path

from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token

from . import views

urlpatterns = [
    path('signup/', views.SignUp.as_view(), name='signup'),
    path('login/', obtain_jwt_token, name='login'),
    path('token/refresh/', refresh_jwt_token, name='refresh_token'),
    #path('users/me/', name='me'),
]
