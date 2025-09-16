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
    # end_of_day_journal_view,
    check_journal_submission_available,
    validate_eod_prerequisites_view,
    setup_default_eod_functions,
    calculate_depreciation_api,
    calculate_depreciation_schedule,
    calculate_depreciation_api_with_journal,
    FAAssetListDepreciationInMonthViewSet,
    AssetDepreciationReportView, 
    AssetDepreciationReportView1, 
    AssetStatisticsView,

    overdue_depreciation_api,
    # trial_balance_view,
    # DairyReportViewSet,
    bulk_insert_dairy_report,
    bulk_delete,
    # bulk_insert_allcurrency,
    #Store Procedure
    trial_balance_consolidated_view,
    trial_balance_fcy_view,
    trial_balance_fcy_get_view,
    # trial_balance_fcy_currencies_view,
    TrialBalanceFCYViewSet,
    bulk_insert_dairy_reports,
    CompanyProfileViewSet,
    BalanceSheetViewSet,
    main_trial_balance_all_currency_view,
    trial_balance_by_currency_view,
    income_statement_acc_view,
    income_statement_acc_get_view,
    income_statement_mfi_get_view,
    income_statement_mfi_view,    
    IncomeStatementViewSet,
    FAAssetAuditViewSet,
    balance_sheet_acc_view,
    balance_sheet_mfi_view,
    balance_sheet_acc_get_view,
    balance_sheet_mfi_get_view,
    end_of_day_journal_view,
    retroactive_depreciation_api,
    JRNLLogViewSetAsset,
    DETB_JRNL_LOG_MASTER_ARD_ViewSet,
    JournalARDViewSet,
    bulk_insert_somtop_trial_balancesheet,
    bulk_insert_monthly_balancesheet_acc,
    bulk_insert_monthly_balancesheet_mfi,
    bulk_insert_monthly_incomestatement_acc,
    bulk_insert_monthly_incomestatement_mfi,
    trial_balance_dairy_view,
    balance_sheet_dairy_acc_view,
    balance_sheet_dairy_mfi_view,
    income_statement_dairy_mfi_view,
    income_statement_dairy_acc_view,
    journal_report_view,
    journal_report_get_view,
<<<<<<< HEAD
    bulk_insert_monthly_cashflow
=======
    get_credit_unauthorized,
>>>>>>> b72494cc4ef01df7fa1f7dbd6aa945edcbd6b0ba

    


)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    
)
from . import views
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
router.register(r'journal-ard', JournalARDViewSet)
router.register(r'journal-log-master', DETB_JRNL_LOG_MASTER_ViewSet, basename='jrnl_log_master')
router.register(r'journal-log-ard', DETB_JRNL_LOG_MASTER_ARD_ViewSet, basename='jrnl_log_ard')
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
router.register(r'trial-balance-fcy', TrialBalanceFCYViewSet, basename='trial-balance-fcy')
router.register(r'companies', CompanyProfileViewSet, basename='company-profile')
router.register(r'income-statement', IncomeStatementViewSet, basename='income-statement')
router.register(r'asset_audit', FAAssetAuditViewSet, basename='FAAssetAudit')
# router.register(r'dairy-report', DairyReportViewSet)
router.register(r'balance-sheet', BalanceSheetViewSet, basename='balance-sheet')
router.register(r'jrnl-logs-with-asset', JRNLLogViewSetAsset, basename='jrnl_logs_with_asset')
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
    # urls.py
    path('journal/credit-unauthorized/', get_credit_unauthorized, name='credit_unauthorized'),


    # Pid Bunsy nai mue 
    path('api/end-of-day-journal/', end_of_day_journal_view , name='end-of-day-journal'),
    
    
    # path('api/end-of-day-journal/', end_of_day_journal_view, name='end-of-day-journal'), # <----- TIK Function Pid Bunsy nai mue
    path('api/end-of-day-journal/check/', check_journal_submission_available), # <----- TIK Function Kuad karn pid bunsy
    path('api/eod/setup-default-functions/', setup_default_eod_functions, name='eod-setup'),
    path('api/eod/validate-prerequisites/', validate_eod_prerequisites_view, name='eod-validate'),
    path('api/depreciation-with-journal/', calculate_depreciation_api_with_journal, name='depreciation_with_journal'),
    # path('api/trial-balance/', trial_balance_view, name='trial_balance_view'),
    # path('api/trial-balance-allccy/', trial_balance_view_allccy, name='trial_balance_view_allccy'),
    # path('api/dairy-report/bulk-insert/', bulk_insert_dairy_report, name='bulk-insert-dairy-report'),
    path('api/dairy-report/bulk-delete/', bulk_delete, name='bulk-delete-dairy-report'),
    # path('api/dairy-report/bulk-insert-allcurrency/', bulk_insert_allcurrency, name='bulk_insert_allcurrency'),


    # Store Procedure <---- Bulk Insert For DairyReport------>
    path('api/dairy-reports/bulk-insert/', bulk_insert_dairy_reports, name='bulk-insert-dairy-reports'),
    # Store Procedure <---- Bulk Insert Sub Trial Balance ------>
    path('api/somtop-trial-balance/bulk-insert/', bulk_insert_somtop_trial_balancesheet, name='bulk-insert-somtop-trial-balancesheet'),
    # Store Procedure <----  Balance Sheets ------>
    path('api/balancesheet/acc/bulk-insert/', bulk_insert_monthly_balancesheet_acc, name='bulk_insert_monthly_balancesheet_acc'),
    path('api/balancesheet/mfi/bulk-insert/', bulk_insert_monthly_balancesheet_mfi, name='bulk_insert_monthly_balancesheet_mfi'),
    # Store Procedure <----  Income Statement ------>
    path('api/incomestatement/acc/bulk-insert/', bulk_insert_monthly_incomestatement_acc, name='bulk_insert_incomestatement_acc'),
    path('api/incomestatement/mfi/bulk-insert/', bulk_insert_monthly_incomestatement_mfi, name='bulk_insert_incomestatement_mfi'),
    # Store Procedure <---- Main Trial Balance ------>
    path('api/main-trial-balance/all-currencies/', main_trial_balance_all_currency_view, name='main-trial-balance-all'),
    path('api/trial-balance/by-currency/', trial_balance_by_currency_view, name='trial-balance-by-currency'),


    # Dairy Report <---- Components ------>
    path('api/main-trial-balance/all-currencies/dairy-report/', trial_balance_dairy_view, name='main-trial-balance-all-currencies-dairy-report'),


    path('api/income-statement/acc/dairy-report/', income_statement_dairy_acc_view, name='income-statement-acc-post-dairy-report'),
    path('api/income-statement/mfi/dairy-report/', income_statement_dairy_mfi_view, name='income-statement-mfi-post-dairy-report'),


    path('api/balance-sheet/acc/dairy-report/', balance_sheet_dairy_acc_view, name='balance-sheet-acc-dairy-report'),
    path('api/balance-sheet/mfi/dairy-report/', balance_sheet_dairy_mfi_view, name='balance-sheet-mfi-dairy-report'),


    # Store Procedure <----- Report End ----->
    path('api/journal-report/', journal_report_view, name='journal_report_post'),
    path('api/journal-report-get/',journal_report_get_view, name='journal_report_get'),


    # Store Procedure <---- Sub Trail Balance ------>
    path('api/trial-balance/consolidated/', 
         trial_balance_consolidated_view, 
         name='trial_balance_consolidated'),
    path('api/trial-balance/fcy/', trial_balance_fcy_view, name='trial-balance-fcy-post'),
    path('api/trial-balance/fcy/get/', trial_balance_fcy_get_view, name='trial-balance-fcy-get'),

   
    # Stroe Procedure <---- Balance Sheet ------>
    path('api/balance-sheet/acc/', balance_sheet_acc_view, name='balance-sheet-acc'),
    path('api/balance-sheet/mfi/', balance_sheet_mfi_view, name='balance-sheet-mfi'),
    path('api/balance-sheet/acc/get/', balance_sheet_acc_get_view, name='balance-sheet-acc-get'),
    path('api/balance-sheet/mfi/get/', balance_sheet_mfi_get_view, name='balance-sheet-mfi-get'),

    #Store Procedure <---- Income Statement ------>
    path('api/income-statement/acc/', income_statement_acc_view, name='income-statement-acc-post'),
    path('api/income-statement/acc/get/', income_statement_acc_get_view, name='income-statement-acc-get'),
    path('api/income-statement/mfi/', income_statement_mfi_view, name='income-statement-mfi-post'),
    path('api/income-statement/mfi/get/', income_statement_mfi_get_view, name='income-statement-mfi-get'),


    #Store Procedure <------ CashFlow ------>
    path('api/bulk-insert-monthly-cashflow/', bulk_insert_monthly_cashflow, name='cash-flow-acc'),

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
    path('api/retroactive/', retroactive_depreciation_api, name='retroactive-depreciation-api'),
    path('api/overdue/', overdue_depreciation_api, name='overdue_api'),
    path('api/calculate/', calculate_depreciation_api, name='calculate_api'),
    path('api/assets/', views.AssetListAPIView.as_view(), name='asset_list_api'),
    path('api/assets/summary/', views.AssetSummaryView.as_view(), name='asset_summary_api'),
    path('api/assets/depreciation/', AssetDepreciationReportView1.as_view()),
    path('api/assets/statistics/', AssetStatisticsView.as_view()),
    path('api/asset-depreciation-report/', 
         AssetDepreciationReportView.as_view(), 
         name='asset_depreciation_report'),
    
    path('latest-eod/', views.get_latest_eod_date, name='latest_eod_date'),
    path('api/depreciation/', calculate_depreciation_api),
    



]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)