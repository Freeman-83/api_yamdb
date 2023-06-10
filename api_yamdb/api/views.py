from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend

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
                          UserRegistrationSerializer,
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
    
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = pagination.PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class CategoryViewSet(CreateDeleteListViewSet):
    """Вьюсет для категорий."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(CreateDeleteListViewSet):
    """Вьюсет для жанров."""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    """Вьюсет для произведений."""
    queryset = Title.objects.select_related(
        'category'
    ).prefetch_related(
        'genre'
    ).annotate(
        rating=Avg('reviews__score')
    ).order_by('name')
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = pagination.PageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilterSet

    def get_serializer_class(self):
        if self.action in ['create', 'partial_update']:
            return TitleCreateSerializer
        return TitleSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """Вьюсет для отзывов к произведениям."""
    serializer_class = ReviewSerializer
    permission_classes = (IsAdminModeratorOwnerOrReadOnly,)

    def get_queryset(self):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        return title.reviews.select_related('author').all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    """Вьюсет для комментариев к отзывам."""
    serializer_class = CommentSerializer
    permission_classes = (IsAdminModeratorOwnerOrReadOnly,)

    def get_queryset(self):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        review = title.reviews.get(pk=self.kwargs.get('review_id'))
        return review.comments.select_related('author').all()

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review, id=self.kwargs.get('review_id'),
            title=self.kwargs.get('title_id')
        )
        serializer.save(author=self.request.user, review=review)


class UserRegistration(APIView):
    """Вью-класс для создания пользователя."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.data['username']
        email = serializer.data['email']
        user, _ = CustomUser.objects.get_or_create(
            username=username,
            email=email
        )
        confirmation_code = default_token_generator.make_token(user)
        user.confirmation_code = confirmation_code
        user.save()
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
    """Вью-функция для получения токена пользователем."""
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
