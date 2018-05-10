from django.urls import path

from authentication import views


urlpatterns = [
    path('register/', views.AuthRegister.as_view(), name='register'),
    path('login/', views.AuthLogin.as_view(), name='login'),
    path('token-refresh/', views.AuthRefresh.as_view(), name='token-refresh'),
    path('token-verify/', views.AuthVerify.as_view(), name='token-verify'),
    path('users/', views.UserList.as_view(), name='user-list'),
    path('users/me/', views.UserDetail.as_view(), name='user-detail'),
]
