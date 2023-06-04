from django.urls import path, include
from . import views
from .views import (
    MessegeSend,
    AdminUserDetail
)
from rest_framework.routers import DefaultRouter

app_name = 'api'

router_api_v1 = DefaultRouter()
router_api_v1.register('users', AdminUserDetail, basename='users')

urlpatterns = [
    path('v1/auth/signup/', MessegeSend.as_view()),
    path('v1/auth/token/', views.get_token),
    path('v1/', include(router_api_v1.urls)),
]
