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
    list_provinces,
    list_districts,
    GLTreeAPIView,
    GLTreeAll,
    JRNLLogViewSet,
    DETB_JRNL_LOG_MASTER_ViewSet,
    submit_eod_journal,
    FAAssetTypeViewSet,
    verify_token,
    force_logout_user,
    get_active_sessions,
    force_logout_all_users,
    get_revoked_sessions,
    EOCMaintainViewSet,
    FAChartOfAssetViewSet,
    FASuppliersViewSet,
    FALocationViewSet,
    FAExpenseCategoryViewSet,
    FAAssetListViewSet,
    # FADepreciationMainViewSet,
    # FADepreciationSubViewSet,
    FAAssetListDepreciationMainViewSet,
    FAAssetListDepreciationViewSet,
    FAAssetListDisposalViewSet,
    FAAssetExpenseViewSet,
    FATransferLogsViewSet,
    FAAssetPhotosViewSet,
    FAMaintenanceLogsViewSet,
    FAMaintenanceLogsViewSet,
    FAAccountingMethodViewSet,
    MasterTypeViewSet,
    MasterCodeViewSet,
    YourProcessViewSet,
    force_logout_user_test,
    session_check,
    JournalProcessV2ViewSet,
    end_of_day_journal_view,
    check_journal_submission_available,
    validate_eod_prerequisites_view,
    setup_default_eod_functions,
    calculate_depreciation_api,
    calculate_depreciation_schedule,
    calculate_depreciation_api_with_journal,
    FAAssetListDepreciationInMonthViewSet,
    overdue_depreciation_api,
    trial_balance_view,
    # DairyReportViewSet,
    bulk_insert_dairy_report,
    trial_balance_view_allccy,
    bulk_delete,
    bulk_insert_allcurrency,
    check_journal_submission_available_test,
    balance_sheet_view,

    

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
router.register(r'function-desc', FunctionDescViewSet, basename='function-desc')
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
router.register(r'asset_types', FAAssetTypeViewSet , basename='asset_type')
# router.register(r'access-logs', UserAccessLogViewSet, basename='user-access-log')
router.register(r'chart_of_asset', FAChartOfAssetViewSet , basename='chart_of_asset')
router.register(r'asset_suppliers', FASuppliersViewSet , basename='asset_suppliers')
router.register(r'asset_location', FALocationViewSet , basename='asset_location')
router.register(r'asset_category', FAExpenseCategoryViewSet , basename='asset_category')
router.register(r'asset_list', FAAssetListViewSet , basename='asset_list')
# router.register(r'asset_dpca_main', FADepreciationMainViewSet , basename='asset_dpca_main')
# router.register(r'asset_dpca_sub', FADepreciationSubViewSet , basename='asset_dpca_sub')
router.register(r'asset_list_dpca_main', FAAssetListDepreciationMainViewSet , basename='asset_list_dpca_main')
router.register(r'asset_list_dpca', FAAssetListDepreciationViewSet , basename='asset_list_dpca')
router.register(r'asset_list_diposal', FAAssetListDisposalViewSet , basename='asset_list_diposal')
router.register(r'asset_expense', FAAssetExpenseViewSet , basename='asset_expense')
router.register(r'asset_transfer', FATransferLogsViewSet , basename='asset_transfer')
router.register(r'asset_photo', FAAssetPhotosViewSet , basename='asset_photo')
router.register(r'asset_mainten_log', FAMaintenanceLogsViewSet , basename='asset_mainten_log')
router.register(r'asset_account', FAAccountingMethodViewSet , basename='asset_account')
router.register(r'asset_list_dpca_inmain', FAAssetListDepreciationInMonthViewSet, basename='asset_list_dpca_inmain')
router.register(r'eoc-maintain', EOCMaintainViewSet, basename='eoc-maintain')
router.register(r'master-types', MasterTypeViewSet)
router.register(r'master-codes', MasterCodeViewSet)
app_name = 'depreciation'

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
    # Pherm Sum lup Village Tree:
    path('api/provinces/', list_provinces, name='list_provinces'),
    path('api/districts/', list_districts, name='list_districts'),
    path('api/villages_list/', list_villages, name='list_villages'),
    path('api/glsub-tree/<int:gl_code_id>', GLTreeAPIView, name='glsub-tree'),   
    path('api/glsub-tree-all/', GLTreeAll, name='glsub-tree-all'),   
    path('api/eod-journal/', submit_eod_journal, name='eod-journal'),
    path('api/end-of-day-journal/', end_of_day_journal_view, name='end-of-day-journal'), # <----- TIK Function Pid Bunsy nai mue
    path('api/end-of-day-journal/check/', check_journal_submission_available), # <----- TIK Function Kuad karn pid bunsy
    path('api/end-of-day-journal/check-test/', check_journal_submission_available_test),
    path('api/eod/setup-default-functions/', setup_default_eod_functions, name='eod-setup'),
    path('api/eod/validate-prerequisites/', validate_eod_prerequisites_view, name='eod-validate'),
    path('api/depreciation-with-journal/', calculate_depreciation_api_with_journal, name='depreciation_with_journal'),
    path('api/trial-balance/', trial_balance_view, name='trial_balance_view'),
    path('api/trial-balance-allccy/', trial_balance_view_allccy, name='trial_balance_view_allccy'),
    path('api/dairy-report/bulk-insert/', bulk_insert_dairy_report, name='bulk-insert-dairy-report'),
    path('api/dairy-report/bulk-delete/', bulk_delete, name='bulk-delete-dairy-report'),
    path('api/dairy-report/bulk-insert-allcurrency/', bulk_insert_allcurrency, name='bulk_insert_allcurrency'),
    path('api/balance-sheet/', balance_sheet_view, name='balance-sheet-view'),
    

    
    
    # Force logout endpoints (standalone)
    path('api/verify-token/',verify_token, name='verify-token'),
    path('api/force-logout/<str:user_id>/',force_logout_user, name='force-logout'),
    path('api/force-logout/',force_logout_user, name='force-logout'),
    path('api/force-logout-test/<str:user_id>/',force_logout_user_test, name='force-logout-test'),
    path('api/active-sessions/',get_active_sessions, name='active-sessions'),
    path('api/force-logout-all/',force_logout_all_users, name='force-logout-all'),
    path('api/revoked-sessions/',get_revoked_sessions, name='revoked-sessions'),
    path('api/session-check/', session_check, name='session-check'),
    path('api/process-journal/', YourProcessViewSet.as_view({'post': 'process_journal_data'})),
    path('journal/process-v2/', 
         JournalProcessV2ViewSet.as_view({'post': 'process_journal_data'}), 
         name='journal-process-v2'),
    path('api/overdue/', overdue_depreciation_api, name='overdue_api'),
    path('api/calculate/', calculate_depreciation_api, name='calculate_api'),
    
    
    
    path('api/depreciation/', calculate_depreciation_api),
    



]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)