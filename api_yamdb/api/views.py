from rest_framework import filters, pagination, permissions, viewsets
from django_filters.rest_framework import DjangoFilterBackend
from reviews.models import Category, Genre, Title
from .serializers import (CategorySerializer,
                          GenreSerializer,
                          TitleSerializer)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = pagination.LimitOffsetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return (permissions.AllowAny(),)
        return super().get_permissions()


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    pagination_class = pagination.LimitOffsetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return (permissions.AllowAny(),)
        return super().get_permissions()


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.select_related('category').all()
    serializer_class = TitleSerializer
    pagination_class = pagination.LimitOffsetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('name', 'year', 'category', 'genre')

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return (permissions.AllowAny(),)
        return super().get_permissions()
