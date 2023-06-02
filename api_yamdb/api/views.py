import string
import random

from rest_framework import viewsets, mixins
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail

from reviews.models import CustomUser, ConfirmationCode
from .serializers import UserRegistrationSerializer, UserConfirmationSerializer


class EmailViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = (AllowAny,)

    @action(detail=False, methods=['post'])
    def send_mail(serializer):
        letters = string.ascii_lowercase
        message = ConfirmationCode.objects.create(
            confirmation_code=''.join(
                random.choice(letters) for i in range(10)
            ),
        )
        send_mail(
            'Код для подтверждения регистрации',
            f'{message}',
            'xxx@yandex.ru',
            [f'{serializer.initial_data.get("email")}'],
        )
