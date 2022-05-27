from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework import generics
from rest_framework import permissions
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer
from rest_framework.authentication import TokenAuthentication

class UserView(generics.ListAPIView):
    #only admin
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAdminUser,)

class RegisterView(APIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        print(token)
        return Response({
            "user": UserSerializer(user, context=self.serializer_class.context).data,
            "token": token.key
        }, status=status.HTTP_200_OK)


class LoginView(APIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.validated_data
            token, _ = Token.objects.get_or_create(user=user)
            return Response(
                {
                    "user": UserSerializer(user, context=self.serializer_class.context).data,
                    "token": token.key
                }, status=status.HTTP_200_OK
            )
        return Response({'Not found': 'user doesnt exists, u need to register'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST', 'DELETE'])
@authentication_classes([TokenAuthentication,])
@permission_classes((permissions.IsAuthenticated, ))
def logout_view(request):
    user = request.user
    token = Token.objects.get(user=user)
    token.delete()
    return Response('successfully deleted', status=status.HTTP_204_NO_CONTENT)