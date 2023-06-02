from django.urls import path
from .views import EmailViewSet

app_name = 'api'

urlpatterns = [
    path('v1/auth/signup/', EmailViewSet.as_view({'post'})),
]
