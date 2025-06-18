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
    roledetail_delete,
    ProvinceViewSet, 
    DistrictViewSet, 
    VillageViewSet,
    # VillageInfoViewSet_name,
    # ProvinceViewSets,
    # DistrictViewSets,
    count_menus_by_module,
    count_submenus_per_menu,
    PerCodeViewSet,
    MTTB_LCL_HolidayViewSet,
    MTTB_TRN_CodeViewSet,
    Data_EntryViewSet,
    list_villages,
    GLTreeAPIView,
    GLTreeAll,
    JRNLLogViewSet,
    DETB_JRNL_LOG_MASTER_ViewSet
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
# router.register(r'lcl_holiday', HolidayViewSet, basename='holiday')
router.register(r'lcl_holiday', MTTB_LCL_HolidayViewSet, basename='holiday')
router.register(r'fin-cycles', FinCycleViewSet, basename='fin-cycle')
router.register(r'user-access-logs',    UserAccessLogViewSet,     basename='user-access-log')
router.register(r'user-activity-logs',  UserActivityLogViewSet,   basename='user-activity-log')
router.register(r'percodes', PerCodeViewSet, basename='percode')
router.register(r'trn-codes', MTTB_TRN_CodeViewSet, basename='trn-code')
router.register(r'provinceinfo', ProvinceViewSet, basename='provinceinfo')
router.register(r'districtinfo', DistrictViewSet, basename='districtinfo')
router.register(r'villageinfo', VillageViewSet, basename='villageinfo')
router.register(r'villageinfo_name', VillageViewSet, basename='villageinfo_name')
router.register(r'mttb-data-entry', Data_EntryViewSet, basename='data-entry')
# router.register(r'gl-capture', JRNLLogViewSet)
router.register(r'journal-entries', JRNLLogViewSet, basename='journal-entry')
router.register(r'journal-log-master', DETB_JRNL_LOG_MASTER_ViewSet, basename='jrnl_log_master')



urlpatterns = [
    #TOKEN
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("api/", include(router.urls)),
    path('api/login/', login_view, name="login"),
    path('api/logout/', logout_view, name='logout'),
    path('api/roledetail-delete/', roledetail_delete, name='roles-delete'),
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
    path('api/villages_list/', list_villages, name='list_villages'),
    path('api/glsub-tree/<int:gl_code_id>', GLTreeAPIView, name='glsub-tree'),   
    path('api/glsub-tree-all/', GLTreeAll, name='glsub-tree-all'),   
    


]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)