from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework_jwt.views import ObtainJSONWebToken, RefreshJSONWebToken, VerifyJSONWebToken
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from django.contrib.auth import login, authenticate

from authentication.models import User

from .serializers import UserSerializer


class AuthRegister(APIView):
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AuthLogin(ObtainJSONWebToken):
    pass
    
class AuthVerify(VerifyJSONWebToken):
    pass

class AuthRefresh(RefreshJSONWebToken):
    pass

class UserList(generics.ListCreateAPIView):
    serializer_class = UserSerializer
    permission_classes = (IsAdminUser, )
    queryset = User.objects.all()

    

class UserDetail(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (AllowAny, )


    def get_object(self):
        user = self.request.user
        return user
