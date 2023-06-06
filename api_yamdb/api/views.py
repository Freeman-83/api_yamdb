import string
import random

from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import filters, pagination, status, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView

from reviews.models import (Category,
                            Genre,
                            Title,
                            Review,
                            ConfirmationCode,
                            CustomUser)
from .serializers import (CategorySerializer,
                          GenreSerializer,
                          TitleSerializer,
                          TitleCreateSerializer,
                          CommentSerializer,
                          ReviewSerializer,
                          EmailSerializer,
                          TokenSerializer,
                          UserDetail,
                          AdminUserDetailSerializer)
from .permissions import (IsAdminOnly,
                          IsAdminOrReadOnly,
                          IsAdminModeratorOwnerOrReadOnly)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = pagination.PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = pagination.PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.select_related('category').all()
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = pagination.PageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('name', 'year', 'category__slug', 'genre__slug')

    def get_serializer_class(self):
        if self.action in ['create', 'partial_update']:
            return TitleCreateSerializer
        return TitleSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (IsAdminModeratorOwnerOrReadOnly,)

    def get_queryset(self):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAdminModeratorOwnerOrReadOnly,)

    def get_queryset(self):
        review = get_object_or_404(Review, pk=self.kwargs.get('review_id'))
        return review.comments.select_related('author').all()

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review, id=self.kwargs.get('review_id'),
            title=self.kwargs.get('title_id')
        )
        serializer.save(author=self.request.user, review=review)


class MessegeSend(APIView):
    """Вью-класс для отправки письма с кодом подтверждения."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = EmailSerializer(data=request.data)
        if serializer.is_valid():
            letters = string.ascii_lowercase
            CustomUser.objects.create(
                username=serializer.validated_data.get("username"),
                email=serializer.validated_data.get("email")
            )
            message = ConfirmationCode.objects.create(
                confirmation_code=''.join(
                    random.choice(letters) for _ in range(5)
                ),
            )
            send_mail(
                'Код регистрации',
                f'Ваш код для регистрации: {message.confirmation_code}',
                'xxx@yandex.ru',
                [f'{serializer.validated_data.get("email")}'],
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


class AdminUserDetailViewSet(viewsets.ModelViewSet):
    """Вьюсет для отображения админом всех пользователей и создания нового."""
    queryset = CustomUser.objects.all()
    serializer_class = AdminUserDetailSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    permission_classes = (IsAdminOnly,)
    pagination_class = pagination.PageNumberPagination
    search_fields = ('$username',)
    lookup_field = 'username'
    http_method_names = ('get', 'post', 'delete', 'patch')

    @action(methods=['GET', 'PATCH'], detail=False, url_path='me',
            permission_classes=(IsAuthenticated,))
    def profile(self, request):
        serializer = UserDetail(request.user)
        if request.method == 'PATCH':
            serializer = UserDetail(
                request.user,
                data=request.data,
                partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_200_OK)
