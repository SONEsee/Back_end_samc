from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers
from .views import (
    MTTBUserViewSet, 
    login_view,
    MTTBDivisionViewSet,
    MTTBRoleViewSet,
    MTTBRoleDetailViewSet,
    sidebar_for_user,role_sidebar,
    ModulesInfoViewSet,
    MainMenuViewSet,
    SubMenuViewSet,
    CcyDefnViewSet,
    ExcRateViewSet,
    FunctionDescViewSet,
    ExcRateHistoryViewSet,
    GLMasterViewSet,
    GLSubViewSet,
    FinCycleViewSet,
    logout_view,
    UserAccessLogViewSet,
    UserActivityLogViewSet,
    EmployeeViewSet,
    HolidayViewSet,
    update_role_detail,
    gl_hierarchy,
    gl_tree,
    exchange_rate_history_for_ccy,
    AllModule,
    roledetaildelete,
    ProvinceInfoViewSet,
    DistrictInfoViewSet,
    VillageInfoViewSet,
    VillageInfoViewSet_name,
    ProvinceViewSets,
    DistrictViewSets,
    count_menus_by_module,
    count_submenus_per_menu
)
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
router.register(r'currencies', CcyDefnViewSet, basename='currency')
router.register(r'exc-rate', ExcRateViewSet, basename='exc-rate')
router.register(r'exc-rate-history', ExcRateHistoryViewSet, basename='exc-rate-history')
router.register(r'gl-master', GLMasterViewSet, basename='gl-master')
router.register(r'gl-sub', GLSubViewSet, basename='gl-sub')
router.register(r'functions', FunctionDescViewSet, basename='function-desc')
router.register(r'employees', EmployeeViewSet, basename='employee')
router.register(r'lcl_holiday', HolidayViewSet, basename='holiday')
router.register(r'fin-cycles', FinCycleViewSet, basename='fin-cycle')
router.register(r'user-access-logs',    UserAccessLogViewSet,     basename='user-access-log')
router.register(r'user-activity-logs',  UserActivityLogViewSet,   basename='user-activity-log')
router.register(r'provinceinfo', ProvinceInfoViewSet, basename='provinceinfo')
router.register(r'districtinfo', DistrictInfoViewSet, basename='districtinfo')
router.register(r'villageinfo', VillageInfoViewSet, basename='villageinfo')
router.register(r'villageinfo_name', VillageInfoViewSet_name, basename='villageinfo_name')
router.register(r'provinces', ProvinceViewSets, basename='province')
router.register(r'districts', DistrictViewSets, basename='district')

urlpatterns = [
    #TOKEN
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("api/", include(router.urls)),
    path('api/login/', login_view, name="login"),
    path('api/logout/', logout_view, name='logout'),
    path('api/roledetail-delete/', roledetaildelete, name='roles-delete'),
    path('api/users/<str:user_id>/sidebar/', sidebar_for_user, name='user-sidebar'),
    path('api/role/<str:role_id>/sidebar/', role_sidebar, name='role-sidebar'),
    path('api/role/sidebar/', role_sidebar, name='role-sidebar-all'),
    path('api/module/all/',AllModule, name='module-all'),
    path('api/exchange-rate-history-for-ccy/<str:ccy_code>/',exchange_rate_history_for_ccy,name='exchange-rate-history-for-ccy'),
    path('api/v1/role-details/update/', update_role_detail, name='update-role-detail'),
    path('api/gl-hierarchy/', gl_hierarchy, name='gl-hierarchy'),
    path('api/gl-tree/', gl_tree, name='gl-tree'),
    path('api/count-menus/', count_menus_by_module, name='count-menus'),
    path('api/count-sub-menus/', count_submenus_per_menu, name='count-sub-menus'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)