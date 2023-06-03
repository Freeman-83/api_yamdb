import string
import random

from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404

from reviews.models import ConfirmationCode, CustomUser
from .serializers import EmailSerializer, TokenSerializer


class MessegeSend(APIView):
    """Вью-класс для отправки письма с кодом подтверждения."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = EmailSerializer(data=request.data)
        if serializer.is_valid():
            letters = string.ascii_lowercase
            message = ConfirmationCode.objects.create(
                confirmation_code=''.join(
                    random.choice(letters) for i in range(10)
                ),
            )
            send_mail(
                'Код регистрации',
                f'Ваш код для регистрации: {message.confirmation_code}',
                'xxx@yandex.ru',
                [f'{serializer.validated_data.get("email")}'],
            )
            CustomUser.objects.create(
                username=serializer.validated_data.get("username"),
                email=serializer.validated_data.get("email")
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny, ])
def get_token(request):
    """Вью-функция для получения токена пользователем"""
    serializer = TokenSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.validated_data.get("username")
        user = get_object_or_404(CustomUser, username=username)
        refresh = RefreshToken.for_user(user)
        new_token = {'access': str(refresh.access_token)}
        return Response(new_token, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
