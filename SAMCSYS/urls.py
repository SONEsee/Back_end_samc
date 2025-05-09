from django.urls import path, include
from rest_framework import routers
from .views import MTTBUserViewSet, login_view,MTTBDivisionViewSet
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = routers.DefaultRouter()
router.register(r"users", MTTBUserViewSet, basename="user"),
router.register(r'divisions', MTTBDivisionViewSet, basename='division')

urlpatterns = [
    #TOKEN
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path("api/", include(router.urls)),
    path("api/login/", login_view, name="login"),
]