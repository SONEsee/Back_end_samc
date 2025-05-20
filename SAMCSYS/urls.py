from django.urls import path, include
from rest_framework import routers
from .views import MTTBUserViewSet, login_view,MTTBDivisionViewSet,MTTBRoleViewSet,MTTBRoleDetailViewSet,sidebar_for_user,role_sidebar,ModulesInfoViewSet,MainMenuViewSet,SubMenuViewSet,FunctionDescViewSet,CcyDefnViewSet,ExcRateViewSet, ExcRateHistoryViewSet,exchange_rate_history_for_ccy,GLMasterViewSet
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = routers.DefaultRouter()
router.register(r"users", MTTBUserViewSet, basename="user"),
router.register(r'divisions', MTTBDivisionViewSet, basename='division'),
router.register(r'roles', MTTBRoleViewSet, basename='role'),
router.register(r'role-details', MTTBRoleDetailViewSet, basename='role-detail')
router.register(r'modules', ModulesInfoViewSet, basename='modules')
router.register(r'main-menus', MainMenuViewSet, basename='main-menu')
router.register(r'sub-menus', SubMenuViewSet, basename='sub-menu')
router.register(r'functions', FunctionDescViewSet, basename='function-desc')
router.register(r'currencies', CcyDefnViewSet, basename='currency')
router.register(r'exchange-rates', ExcRateViewSet, basename='exchange-rate')
router.register(r'exchange-rate-history', ExcRateHistoryViewSet, basename='exchange-rate-history')
router.register(r'gl-master', GLMasterViewSet, basename='glmaster')

urlpatterns = [
    #TOKEN
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("api/", include(router.urls)),
    path('api/login/', login_view, name="login"),
    path('api/users/<str:user_id>/sidebar/', sidebar_for_user, name='user-sidebar'),
    path('api/role/<str:role_id>/sidebar/', role_sidebar, name='role-sidebar'),
    path('api/exchange-rate-history-for-ccy /<str:ccy_code>/',
      exchange_rate_history_for_ccy,
      name='exchange-rate-history-for-ccy'),
    
]