from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CategoryViewSet,
                    GenreViewSet,
                    TitleViewSet,
                    CommentViewSet,
                    ReviewViewSet)

app_name = 'api'

router_api_v1 = DefaultRouter()

router_api_v1.register(r'categories', CategoryViewSet)
router_api_v1.register(r'genres', GenreViewSet)
router_api_v1.register(r'titles', TitleViewSet)
router_api_v1.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews'
)
router_api_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments'
)

urlpatterns = [
    path('v1/', include(router_api_v1.urls)),
]
