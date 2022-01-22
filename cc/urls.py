from django.contrib import admin
from django.urls import path

from . import views
# from .views import MyTokenObtainPairView ,TokenRefreshView
from . import views


urlpatterns = [
    # path('api/token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    # path('api/token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/uploadImage', views.PCa.uploadImage, name='uploadImage')
]
