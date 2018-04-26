from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser

from django.contrib.auth import login, authenticate

from authentication.models import User
from .serializers import UserSerializer
from rest_framework import viewsets

class AuthRegister(APIView):

    # Register a new user.
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AuthLogin(APIView):

    # Manual implementation of login method
    @staticmethod
    def post(request, format=None):
        data = request.data
        email = data.get('email', None)
        password = data.get('password', None)

        account = authenticate(email=email, password=password)
        # Generate token and add it to the response object
        if account is not None:
            login(request, account)
            return Response({
                'status': 'Successful',
                'message': 'You have successfully been logged into your account.'
            }, status=status.HTTP_200_OK)

        return Response({
            'status': 'Unauthorized',
            'message': 'Username/password combination invalid.'
        }, status=status.HTTP_401_UNAUTHORIZED)


class UserList(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdminUser,)


class UserDetail(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)
    lookup_field = 'username'

    def get_queryset(self):
        username = self.kwargs['username']
        return User.objects.filter(username=username)