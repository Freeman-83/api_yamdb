import string
import random

from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, pagination, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView


from reviews.models import Category, Genre, Title, Review, ConfirmationCode, CustomUser
from .serializers import (CategorySerializer,
                          GenreSerializer,
                          TitleSerializer,
                          TitleCreateSerializer,
                          CommentSerializer,
                          ReviewSerializer,
                          EmailSerializer,
                          TokenSerializer,
                          UserDetail,
                          AdminUserDetailSerializer
                          )
from .permissions import AdminOrReadOnly, IsAdminModeratorOwnerOrReadOnly


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (AdminOrReadOnly,)
    pagination_class = pagination.PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (AdminOrReadOnly,)
    pagination_class = pagination.PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.select_related('category').all()
    permission_classes = (AdminOrReadOnly,)
    pagination_class = pagination.PageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('name', 'year', 'category', 'genre')


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


class AdminUserDetail(viewsets.ModelViewSet):
    """Вьюсет для отображения админом всех пользователей и создания нового."""
    queryset = CustomUser.objects.all()
    serializer_class = AdminUserDetailSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    permission_classes = (IsAdminUser,)
    pagination_class = pagination.PageNumberPagination
    search_fields = ('$username',)
    lookup_field = 'username'


class UserDetailViewSet(viewsets.ModelViewSet):
    """Вьюсет для отображения и редактирования профиля пользователя."""
    serializer_class = UserDetail
    filter_backends = (DjangoFilterBackend,)

    def get_queryset(self):
        return get_object_or_404(CustomUser, username=self.request.user)

