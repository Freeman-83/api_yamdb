from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (AdminUserDetailViewSet,
                    CategoryViewSet,
                    CommentViewSet,
                    GenreViewSet,
                    ReviewViewSet,
                    TitleViewSet,
                    MessageSend,
                    get_token)

app_name = 'api'

router_api_v1 = DefaultRouter()

router_api_v1.register('categories', CategoryViewSet)
router_api_v1.register('genres', GenreViewSet)
router_api_v1.register('titles', TitleViewSet)
router_api_v1.register('users', AdminUserDetailViewSet, basename='users')
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
    path('v1/auth/signup/', MessageSend.as_view()),
    path('v1/auth/token/', get_token),
    path('v1/', include(router_api_v1.urls)),
]
