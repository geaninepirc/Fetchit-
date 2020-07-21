from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.settings import api_settings

from .serializers import UserSerializer, UserSerializerWithToken, UserSerializerForRegister
from .models import User

class handle_user(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user_info = User.objects.get(pk=int(request.user.id))
        serializer = UserSerializer(user_info)
        return Response(serializer.data, status=status.HTTP_200_OK)

class new_user(APIView):
    """
    Create a new user.
    """

    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        serializer = UserSerializerForRegister(data=request.data)
        # email send part
        if serializer.is_valid():
            serializer.save()
            send_verification_mail(
                serializer.data['email'], 
                request.build_absolute_uri('/verify/' + encrypt_string(serializer.data['email']))
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class token_auth(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        serializer = UserSerializerWithToken(request.user)

        return Response(serializer.data, status=status.HTTP_200_OK)