from django.urls import reverse_lazy
from django.views import generic

from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from .forms import CustomUserCreationForm

class SignUp(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'

class UserGetToken(APIView):
    permission_classes = (AllowAny,)
