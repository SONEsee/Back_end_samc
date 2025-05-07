from django.urls import path
from . import views

urlpatterns = [
    path('get-csrf-token/', views.get_csrf_token_view, name='get_csrf_token'),
    path('users/', views.api_user_list, name='api_user_list'),
    path('users/<str:user_id>/', views.api_user_detail, name='api_user_detail'),
    path('users/create/', views.api_create_user, name='api_create_user'),  # ເພີ່ມ trailing slash
    path('users/<str:user_id>/update/', views.api_update_user, name='api_update_user'),
    path('users/<str:user_id>/delete/', views.api_delete_user, name='api_delete_user'),
    path('users/<str:user_id>/approve/', views.api_approve_user, name='api_approve_user'),
    path('users/<str:user_id>/reject/', views.api_reject_user, name='api_reject_user'),
    path('login/', views.api_login, name='api_login'),
]