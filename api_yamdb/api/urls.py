from django.urls import path
from . import views
from .views import MessegeSend

app_name = 'api'

urlpatterns = [
    path('v1/auth/signup/', MessegeSend.as_view()),
    path('v1/auth/token/', views.get_token),
]
