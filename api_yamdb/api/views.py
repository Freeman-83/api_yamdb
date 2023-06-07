from django.conf import settings
from django.core.mail import send_mail
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend

from random import randint
from rest_framework import filters, pagination, status, viewsets, mixins
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView

from reviews.models import (CustomUser,
                            Category,
                            Genre,
                            Review,
                            Title)

from .serializers import (AdminUserDetailSerializer,
                          CategorySerializer,
                          CommentSerializer,
                          EmailSerializer,
                          GenreSerializer,
                          ReviewSerializer,
                          TitleSerializer,
                          TitleCreateSerializer,
                          TokenSerializer,
                          UserDetailSerializer)

from .permissions import (IsAdminOnly,
                          IsAdminOrReadOnly,
                          IsAdminModeratorOwnerOrReadOnly)

from .filters import TitleFilterSet


class CreateDeleteListViewSet(mixins.CreateModelMixin,
                              mixins.DestroyModelMixin,
                              mixins.ListModelMixin,
                              viewsets.GenericViewSet):
    pass


class CategoryViewSet(CreateDeleteListViewSet):
    """Вьюсет для категорий"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = pagination.PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('=name',)

    def destroy(self, request, *args, **kwargs):
        category = get_object_or_404(Category, slug=kwargs['pk'])
        self.perform_destroy(category)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, category):
        category.delete()


class GenreViewSet(CreateDeleteListViewSet):
    """Вьюсет для жанров"""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = pagination.PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)

    def destroy(self, request, *args, **kwargs):
        genre = get_object_or_404(Genre, slug=kwargs['pk'])
        self.perform_destroy(genre)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, category):
        category.delete()


class TitleViewSet(viewsets.ModelViewSet):
    """Вьюсет для произведений"""
    queryset = Title.objects.select_related('category').all()
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = pagination.PageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilterSet

    def get_serializer_class(self):
        if self.action in ['create', 'partial_update']:
            return TitleCreateSerializer
        return TitleSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """Вьюсет для отзывов к произведениям"""
    serializer_class = ReviewSerializer
    permission_classes = (IsAdminModeratorOwnerOrReadOnly,)

    def get_queryset(self):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    """Вьюсет для комментариев к отзывам"""
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


class MessageSend(APIView):
    """Вью-класс для отправки письма с кодом подтверждения."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = EmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.data['username']
        email = serializer.data['email']
        confirmation_code = randint(10000, 99999)
        try:
            user, _ = CustomUser.objects.get_or_create(
                username=username,
                email=email
            )
        except IntegrityError:
            return Response(
                'Пользователь с указанными данными уже существует.',
                status=status.HTTP_400_BAD_REQUEST,
            )
        send_mail(
            subject='Код регистрации',
            message=f'Ваш код для регистрации: {confirmation_code}',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
        )

        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def get_token(request):
    """Вью-функция для получения токена пользователем"""
    serializer = TokenSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        user = get_object_or_404(
            CustomUser,
            username=serializer.data.get('username'))
    if serializer.data['confirmation_code'] == user.confirmation_code:
        refresh = RefreshToken.for_user(user)
        new_token = {'access': str(refresh.access_token)}
        return Response(new_token, status=status.HTTP_201_CREATED)
    return Response('Неверный код подтверждения confirmation_code.',
                    status=status.HTTP_400_BAD_REQUEST)


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
        serializer = UserDetailSerializer(request.user)
        if request.method == 'PATCH':
            serializer = UserDetailSerializer(
                request.user,
                data=request.data,
                partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_200_OK)
