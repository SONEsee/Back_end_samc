# Create your views here.
import hashlib
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import MTTB_Users
from .serializers import MTTBUserSerializer

# class MTTBUserViewSet(viewsets.ModelViewSet):
#     """
#     GET    /api/users/         → list
#     POST   /api/users/         → create
#     GET    /api/users/{pk}/    → retrieve
#     PUT    /api/users/{pk}/    → update
#     PATCH  /api/users/{pk}/    → partial update
#     DELETE /api/users/{pk}/    → destroy
#     """
#     queryset = MTTB_Users.objects.all()
#     serializer_class = MTTBUserSerializer

#     # allow unauthenticated user to create an account
#     def get_permissions(self):
#         if self.request.method == "POST":
#             return [AllowAny()]
#         return super().get_permissions()

def _hash(raw_password):
    return hashlib.md5(raw_password.encode("utf-8")).hexdigest()
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.utils import timezone
from .models import MTTB_Users
from .serializers import MTTBUserSerializer
class MTTBUserViewSet(viewsets.ModelViewSet):
    """
    CRUD for users, supporting:
      - file uploads via multipart/form-data
      - filtering by ?div_id=... and ?Role_ID=...
    """
    serializer_class = MTTBUserSerializer
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get_permissions(self):
        # Allow open signup
        if self.request.method == 'POST':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        # start from all users
        qs = MTTB_Users.objects.select_related('div_id', 'Role_ID').all()

        params = self.request.query_params

        # filter by division if provided
        div = params.get('div_id')
        if div:
            qs = qs.filter(div_id__div_id=div)

        # filter by role if provided
        role = params.get('role_id')
        if role:
            qs = qs.filter(Role_ID__role_id=role)

        return qs.order_by('user_id')

    def perform_create(self, serializer):
        maker = self.request.user if self.request.user.is_authenticated else None
        serializer.save(
            Maker_Id=maker,
            Maker_DT_Stamp=timezone.now()
        )

    def perform_update(self, serializer):
        checker = self.request.user if self.request.user.is_authenticated else None
        serializer.save(
            Checker_Id=checker,
            Checker_DT_Stamp=timezone.now()
        )

from rest_framework_simplejwt.tokens import RefreshToken
from .models import MTTB_USER_ACCESS_LOG
from rest_framework_simplejwt.settings import api_settings
from django.utils import timezone

def get_client_ip(request):
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    if xff:
        return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')

@api_view(["POST"])
@permission_classes([AllowAny])
def login_view(request):
    uid = request.data.get("user_name")
    pwd = request.data.get("user_password")
    if not uid or not pwd:
        # log failure
        MTTB_USER_ACCESS_LOG.objects.create(
            user_id=None,
            session_id=None,
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT'),
            login_status='F',        # F = failed
            remarks='Missing credentials'
        )
        return Response(
            {"error": "User_Name and User_Password required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    hashed = _hash(pwd)
    try:
        user = MTTB_Users.objects.get(
            user_name=uid, user_password=hashed
        )
    except MTTB_Users.DoesNotExist:
        # log failure
        MTTB_USER_ACCESS_LOG.objects.create(
            user_id=None,
            session_id=None,
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT'),
            login_status='F',
            remarks='Invalid credentials'
        )
        return Response(
            {"error": "Invalid credentials"},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    # 1) Create tokens
    refresh = RefreshToken.for_user(user)
    access  = refresh.access_token

    # 2) Log the successful login
    # Grab the JTI (unique token ID) for session tracking
    jti = refresh.get(api_settings.JTI_CLAIM)
    MTTB_USER_ACCESS_LOG.objects.create(
        user_id=user,
        session_id=jti,
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT'),
        login_status='S'   # S = success
    )

    # 3) Serialize your user data
    data = MTTBUserSerializer(user).data

    # 4) Return tokens + user info
    return Response({
        "message": "Login successful",
        "refresh": str(refresh),
        "access": str(access),
        "user": data
    })

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.utils import timezone
from .models import MTTB_USER_ACCESS_LOG
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework_simplejwt.settings import api_settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from .models import MTTB_USER_ACCESS_LOG

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    POST /api/logout/
    Body: { "refresh": "<refresh_token>" }
    """
    refresh_token = request.data.get("refresh")
    if not refresh_token:
        return Response(
            {"error": "Refresh token required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        token = RefreshToken(refresh_token)
    except TokenError:
        return Response(
            {"error": "Invalid refresh token"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Extract the JTI claim
    jti = token[api_settings.JTI_CLAIM]

    # Mark the logout in the access log
    try:
        log = MTTB_USER_ACCESS_LOG.objects.get(
            session_id=jti,
            logout_datetime__isnull=True
        )
        log.logout_datetime = timezone.now()
        log.logout_type     = 'U'  # U = user-initiated logout
        log.save()
    except MTTB_USER_ACCESS_LOG.DoesNotExist:
        # No open session found; ignore
        pass

    return Response({"message": "Logged out"}, status=status.HTTP_200_OK)
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import MTTB_USER_ACCESS_LOG, MTTB_USER_ACTIVITY_LOG
from .serializers import UserAccessLogSerializer, UserActivityLogSerializer

class UserAccessLogViewSet(viewsets.ModelViewSet):
    """
    CRUD for user access logs (login/logout events).
    """
    queryset = MTTB_USER_ACCESS_LOG.objects.select_related('user_id').all().order_by('-login_datetime')
    serializer_class = UserAccessLogSerializer
    permission_classes = [IsAuthenticated]

class UserActivityLogViewSet(viewsets.ModelViewSet):
    """
    CRUD for user activity logs (detailed actions).
    """
    queryset = MTTB_USER_ACTIVITY_LOG.objects.select_related('user_id').all().order_by('-activity_datetime')
    serializer_class = UserActivityLogSerializer
    permission_classes = [IsAuthenticated]

from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from .models import MTTB_Divisions
from .serializers import MTTBDivisionSerializer
from django.utils import timezone
from rest_framework_simplejwt.authentication import JWTAuthentication


class MTTBDivisionViewSet(viewsets.ModelViewSet):
    """
    Provides list, create, retrieve, update and destroy for Divisions.
    """
    queryset = MTTB_Divisions.objects.all().order_by('div_id')
    serializer_class = MTTBDivisionSerializer

    def get_permissions(self):
        # Allow anyone to create new divisions (POST), but require auth for others
        if self.request.method == 'POST':
            return [AllowAny()]
        return [IsAuthenticated()]
    def get_authenticators(self):
        # debug which authenticators are being used
        print("Authenticators:", self.authentication_classes)
        return super().get_authenticators()

    def perform_create(self, serializer):
        # Automatically stamp the maker and date
        maker = None
        if self.request.user.is_authenticated:
            maker = self.request.user
        serializer.save(
            Maker_Id=maker,
            Maker_DT_Stamp=timezone.now(),
        )
        

    def perform_update(self, serializer):
        checker = self.request.user if self.request.user.is_authenticated else None
        # set Checker_Id and Checker_DT_Stamp
        serializer.save(
            Checker_Id=checker,
            Checker_DT_Stamp=timezone.now()
        )

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from .models import MTTB_Role_Master
from .serializers import MTTBRoleSerializer

class MTTBRoleViewSet(viewsets.ModelViewSet):
    """
    Provides CRUD for Role_Master.
    """
    queryset = MTTB_Role_Master.objects.all().order_by('role_id')
    serializer_class = MTTBRoleSerializer

    def get_permissions(self):
        # Allow open creation, require auth for all other actions
        if self.request.method == 'POST':
            return [AllowAny()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        # Stamp maker and timestamp
        maker = self.request.user if self.request.user.is_authenticated else None
        serializer.save(
            Maker_Id=maker,
            Maker_DT_Stamp=timezone.now(),
        )

    def perform_update(self, serializer):
        checker = self.request.user if self.request.user.is_authenticated else None
        # set Checker_Id and Checker_DT_Stamp
        serializer.save(
            Checker_Id=checker,
            Checker_DT_Stamp=timezone.now()
        )


from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import MTTB_Role_Detail
from .serializers import RoleDetailSerializer

class MTTBRoleDetailViewSet(viewsets.ModelViewSet):
    """
    CRUD for Role_Detail records, with optional filtering by role_id and/or function_id via query params.
    """
    serializer_class = RoleDetailSerializer

    @action(detail=False, methods=['get'], url_path='single')
    def get_single(self, request):
        role_id = request.query_params.get('role_id')
        sub_menu_id = request.query_params.get('sub_menu_id')

        if not role_id or not sub_menu_id:
            return Response(
                {'detail': 'Both role_id and function_id are required.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            obj = MTTB_Role_Detail.objects.get(role_id=role_id, sub_menu_id=sub_menu_id)
            serializer = self.get_serializer(obj)
            return Response(serializer.data)
        except MTTB_Role_Detail.DoesNotExist:
            return Response(
                {'detail': 'Role detail not found.'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'detail': f'Error retrieving role detail: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get_permissions(self):
        # Allow open creation; require auth for read/update/delete
        if self.request.method == 'POST':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        qs = MTTB_Role_Detail.objects.all()
        params = self.request.query_params
        role = params.get('role_id')
        func = params.get('sub_menu_id')
        
        # If role_id and function_id are direct fields (not foreign keys)
        if role and func:
            qs = qs.filter(role_id=role, sub_menu_id=func)
        elif role:
            qs = qs.filter(role_id=role)
        elif func:
            qs = qs.filter(sub_menu_id=func)
            
        return qs

    # Optional: Add custom update method for your frontend URL pattern
    @action(detail=False, methods=['put'], url_path='update')
    def update_role_detail(self, request):
        role_id = request.query_params.get('role_id')
        sub_menu_id = request.query_params.get('sub_menu_id')

        if not role_id or not sub_menu_id:
            return Response(
                {'detail': 'Both role_id and function_id are required.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            obj = MTTB_Role_Detail.objects.get(role_id=role_id, sub_menu_id=sub_menu_id)
            serializer = self.get_serializer(obj, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except MTTB_Role_Detail.DoesNotExist:
            return Response(
                {'detail': 'Role detail not found.'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'detail': f'Error updating role detail: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def roledetaildelete(request):
    role_id = request.GET.get('role_id')
    sub_menu_id = request.GET.get('sub_menu_id')
    try:
        obj = MTTB_Role_Detail.objects.get(role_id=role_id, sub_menu_id=sub_menu_id)
        obj.delete()
        return Response({"detail": "Deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    except MTTB_Role_Detail.DoesNotExist:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

# Function Loop Sidebar Menu

from collections import OrderedDict
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import (
    MTTB_Users,
    MTTB_Role_Detail,
    MTTB_SUB_MENU,
    MTTB_MAIN_MENU,
    STTB_ModulesInfo,
)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def sidebar_for_user(request, user_id):
    """
    GET /api/users/{user_id}/sidebar/
    Returns modules → main menus → sub menus with permissions.
    """
    # 1) Load user & role
    user = get_object_or_404(MTTB_Users, user_id=user_id)
    role = user.Role_ID

    if not role:
        return Response([])  # no role, no sidebar

    # 2) Fetch all role_detail for this role, with joins down to module
    details = (
        MTTB_Role_Detail.objects
          .filter(role_id=role)
          .select_related(
              'sub_menu_id',
              'sub_menu_id__menu_id',
              'sub_menu_id__menu_id__module_Id'
          )
    )

    # 3) Build nested dict: module → main_menu → sub_menu
    modules = OrderedDict()
    for det in details:
        sub   = det.sub_menu_id
        main  = sub.menu_id if sub else None
        mod   = main.module_Id if main else None
        if not (sub and main and mod):
            continue

        # Module level
        mod_key = mod.module_Id
        if mod_key not in modules:
            modules[mod_key] = {
                'module_Id':      mod.module_Id,
                'module_name_la': mod.module_name_la,
                'module_name_en': mod.module_name_en,
                'module_icon':    mod.module_icon,
                'module_order':   mod.module_order,
                'is_active':      mod.is_active,
                'main_menus':     OrderedDict()
            }

        # Main menu level
        mm_key = main.menu_id
        mm_group = modules[mod_key]['main_menus']
        if mm_key not in mm_group:
            mm_group[mm_key] = {
                'menu_id':      main.menu_id,
                'menu_name_la': main.menu_name_la,
                'menu_name_en': main.menu_name_en,
                'menu_icon':    main.menu_icon,
                'menu_order':   main.menu_order,
                'is_active':    main.is_active,
                'sub_menus':    OrderedDict()
            }

        # Sub menu level
        sm_key = sub.sub_menu_id
        sm_group = mm_group[mm_key]['sub_menus']
        if sm_key not in sm_group:
            sm_group[sm_key] = {
                'sub_menu_id':      sub.sub_menu_id,
                'sub_menu_name_la': sub.sub_menu_name_la,
                'sub_menu_name_en': sub.sub_menu_name_en,
                'sub_menu_icon':    sub.sub_menu_icon,
                'sub_menu_order':   sub.sub_menu_order,
                'sub_menu_urls':    sub.sub_menu_urls,
                'is_active':        sub.is_active,
                'permissions': {
                    'new':    det.New_Detail,
                    'delete': det.Del_Detail,
                    'edit':   det.Edit_Detail,
                    'auth':   det.Auth_Detail,
                    'view':   det.View_Detail,
                }
            }

    # 4) Convert sub-dicts to lists
    result = []
    for mod in modules.values():
        mm_list = []
        for mm in mod['main_menus'].values():
            sm_list = list(mm['sub_menus'].values())
            mm['sub_menus'] = sm_list
            mm_list.append(mm)
        mod['main_menus'] = mm_list
        result.append(mod)

    return Response(result)

from collections import OrderedDict
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import (
    MTTB_Role_Master,
    MTTB_Role_Detail,
    MTTB_SUB_MENU,
    MTTB_MAIN_MENU,
    STTB_ModulesInfo,
)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def role_sidebar(request, role_id=None):
    """
    GET /api/role/<role_id>/sidebar/
    Returns modules → main menus → sub menus with permissions.
    """
    # 1) Initialize query based on role_id
    if role_id:
        role = get_object_or_404(MTTB_Role_Master, role_id=role_id)
        details = (
            MTTB_Role_Detail.objects
            .filter(role_id=role)
            .select_related(
                'sub_menu_id',
                'sub_menu_id__menu_id',
                'sub_menu_id__menu_id__module_Id'
            )
            .order_by(
                'sub_menu_id__menu_id__module_Id__module_order',
                'sub_menu_id__menu_id__menu_order',
                'sub_menu_id__sub_menu_order'
            )
        )
    else:
        details = (
            MTTB_Role_Detail.objects
            .select_related(
                'sub_menu_id',
                'sub_menu_id__menu_id',
                'sub_menu_id__menu_id__module_Id'
            )
            .order_by(
                'sub_menu_id__menu_id__module_Id__module_order',
                'sub_menu_id__menu_id__menu_order',
                'sub_menu_id__sub_menu_order'
            )
        )

    # 2) Group into nested dicts
    modules = OrderedDict()
    for det in details:
        sub = det.sub_menu_id
        main = sub.menu_id
        mod = main.module_Id

        if not (sub and main and mod):
            continue

        # Module level
        if mod.module_Id not in modules:
            modules[mod.module_Id] = {
                'module_Id':      mod.module_Id,
                'module_name_la': mod.module_name_la,
                'module_name_en': mod.module_name_en,
                'module_icon':    mod.module_icon,
                'module_order':   mod.module_order,
                'is_active':      mod.is_active,
                'main_menus':     OrderedDict()
            }
        mm_group = modules[mod.module_Id]['main_menus']

        # Main-menu level
        if main.menu_id not in mm_group:
            mm_group[main.menu_id] = {
                'menu_id':      main.menu_id,
                'menu_name_la': main.menu_name_la,
                'menu_name_en': main.menu_name_en,
                'menu_icon':    main.menu_icon,
                'menu_order':   main.menu_order,
                'is_active':    main.is_active,
                'sub_menus':    OrderedDict()
            }
        sm_group = mm_group[main.menu_id]['sub_menus']

        # Sub-menu level
        if sub.sub_menu_id not in sm_group:
            sm_group[sub.sub_menu_id] = {
                'sub_menu_id':      sub.sub_menu_id,
                'sub_menu_name_la': sub.sub_menu_name_la,
                'sub_menu_name_en': sub.sub_menu_name_en,
                'sub_menu_icon':    sub.sub_menu_icon,
                'sub_menu_order':   sub.sub_menu_order,
                'sub_menu_urls':    sub.sub_menu_urls,
                'is_active':        sub.is_active,
                'permissions': {
                    'new':    det.New_Detail,
                    'delete': det.Del_Detail,
                    'edit':   det.Edit_Detail,
                    'auth':   det.Auth_Detail,
                    'view':   det.View_Detail
                }
            }

    # 3) Convert nested OrderedDicts to lists
    sidebar = []
    for mod in modules.values():
        main_menus = []
        for mm in mod['main_menus'].values():
            mm['sub_menus'] = list(mm['sub_menus'].values())
            main_menus.append(mm)
        mod['main_menus'] = main_menus
        sidebar.append(mod)

    return Response(sidebar, status=status.HTTP_200_OK)


from collections import OrderedDict
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import (
    STTB_ModulesInfo,
    MTTB_MAIN_MENU,
    MTTB_SUB_MENU,
    MTTB_Function_Desc,
)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def AllModule(request):
    """
    GET /api/modules/all/
    Returns all modules -> main menus -> sub menus -> functions.
    Only includes active records, ordered by their respective order fields.
    """
    # 1) Fetch all active modules
    modules = (
        STTB_ModulesInfo.objects
        .filter(is_active='Y')
        .order_by('module_order')
    )

    # 2) Initialize response structure
    result = []

    # 3) Loop through modules
    for mod in modules:
        module_data = {
            'module_Id': mod.module_Id,
            'module_name_la': mod.module_name_la,
            'module_name_en': mod.module_name_en,
            'module_icon': mod.module_icon,
            'module_order': mod.module_order,
            'is_active': mod.is_active,
            'main_menus': []
        }

        # 4) Fetch active main menus for this module
        main_menus = (
            MTTB_MAIN_MENU.objects
            .filter(module_Id=mod, is_active='Y')
            .order_by('menu_order')
        )

        # 5) Loop through main menus
        for main in main_menus:
            main_menu_data = {
                'menu_id': main.menu_id,
                'menu_name_la': main.menu_name_la,
                'menu_name_en': main.menu_name_en,
                'menu_icon': main.menu_icon,
                'menu_order': main.menu_order,
                'is_active': main.is_active,
                'sub_menus': []
            }

            # 6) Fetch active sub-menus for this main menu
            sub_menus = (
                MTTB_SUB_MENU.objects
                .filter(menu_id=main, is_active='Y')
                .order_by('sub_menu_order')
            )

            # 7) Loop through sub-menus
            for sub in sub_menus:
                sub_menu_data = {
                    'sub_menu_id': sub.sub_menu_id,
                    'sub_menu_name_la': sub.sub_menu_name_la,
                    'sub_menu_name_en': sub.sub_menu_name_en,
                    'sub_menu_icon': sub.sub_menu_icon,
                    'sub_menu_order': sub.sub_menu_order,
                    'sub_menu_urls': sub.sub_menu_urls,
                    'is_active': sub.is_active,
                    'functions': []
                }

                # 8) Fetch active functions for this sub-menu
                functions = (
                    MTTB_Function_Desc.objects
                    .filter(sub_menu_id=sub, is_active='Y')
                    .order_by('function_order')
                )

                # 9) Loop through functions
                for func in functions:
                    function_data = {
                        'function_id': func.function_id,
                        'description_la': func.description_la,
                        'description_en': func.description_en,
                        'function_order': func.function_order,
                        'is_active': func.is_active
                    }
                    sub_menu_data['functions'].append(function_data)

                main_menu_data['sub_menus'].append(sub_menu_data)

            module_data['main_menus'].append(main_menu_data)

        result.append(module_data)

    return Response(result, status=status.HTTP_200_OK)


from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import (
    STTB_ModulesInfo,
    MTTB_MAIN_MENU,
    MTTB_SUB_MENU,
    MTTB_Function_Desc,
)
from .serializers import (
    ModulesInfoSerializer,
    MainMenuSerializer,
    SubMenuSerializer,
    FunctionDescSerializer,
)

class ModulesInfoViewSet(viewsets.ModelViewSet):
    queryset = STTB_ModulesInfo.objects.all().order_by('module_order')
    serializer_class = ModulesInfoSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        user_id = getattr(user, 'user_id', None)  # ปรับให้เข้ากับ user model ของคุณ
        serializer.save(
            created_by=user_id,
            created_date=timezone.now()
        )

    def perform_update(self, serializer):
        user = self.request.user
        user_id = getattr(user, 'user_id', None)
        serializer.save(
            modified_by=user_id,
            modified_date=timezone.now()
        )

class MainMenuViewSet(viewsets.ModelViewSet):
    serializer_class = MainMenuSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = MTTB_MAIN_MENU.objects.select_related('module_Id').all().order_by('menu_order')
        module_id = self.request.query_params.get('module_Id')
        if module_id:
            queryset = queryset.filter(module_Id=module_id) 
        return queryset
    
    def perform_create(self, serializer):
        user = self.request.user
        user_id = getattr(user, 'user_id', None)  # ปรับให้เข้ากับ user model ของคุณ
        serializer.save(
            created_by=user_id,
            created_date=timezone.now()
        )

    def perform_update(self, serializer):
        user = self.request.user
        user_id = getattr(user, 'user_id', None)
        serializer.save(
            modified_by=user_id,
            modified_date=timezone.now()
        )
    

class SubMenuViewSet(viewsets.ModelViewSet):
    serializer_class = SubMenuSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = MTTB_SUB_MENU.objects.select_related('menu_id').all().order_by('menu_id','sub_menu_order')
        menu_id = self.request.query_params.get('menu_id')
        if menu_id:
            queryset = queryset.filter(menu_id=menu_id) 
        return queryset
    
    def perform_create(self, serializer):
        user = self.request.user
        user_id = getattr(user, 'user_id', None)  # ปรับให้เข้ากับ user model ของคุณ
        serializer.save(
            created_by=user_id,
            created_date=timezone.now()
        )

    def perform_update(self, serializer):
        user = self.request.user
        user_id = getattr(user, 'user_id', None)
        serializer.save(
            modified_by=user_id,
            modified_date=timezone.now()
        )

class FunctionDescViewSet(viewsets.ModelViewSet):
    serializer_class = FunctionDescSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = MTTB_Function_Desc.objects.select_related('sub_menu_id').all().order_by('function_order')
        sub_menu_id = self.request.query_params.get('sub_menu_id')
        if sub_menu_id:
            queryset = queryset.filter(sub_menu_id=sub_menu_id) 
        return queryset
    
    def perform_create(self, serializer):
        user = self.request.user
        user_id = getattr(user, 'user_id', None)  # ปรับให้เข้ากับ user model ของคุณ
        serializer.save(
            created_by=user_id,
            created_date=timezone.now()
        )

    def perform_update(self, serializer):
        user = self.request.user
        user_id = getattr(user, 'user_id', None)
        serializer.save(
            modified_by=user_id,
            modified_date=timezone.now()
        )

from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.utils import timezone
from .models import MTTB_Ccy_DEFN
from .serializers import CcyDefnSerializer

class CcyDefnViewSet(viewsets.ModelViewSet):
    """
    CRUD for currency definitions.
    """
    queryset = MTTB_Ccy_DEFN.objects.all().order_by('ccy_code')
    serializer_class = CcyDefnSerializer

    def get_permissions(self):
        # Allow unauthenticated creation
        if self.request.method == 'POST':
            return [AllowAny()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        # Stamp maker and date
        maker = None
        if self.request.user and self.request.user.is_authenticated:
            maker = self.request.user
        serializer.save(
            Maker_Id=maker,
            Maker_DT_Stamp=timezone.now(),
        )

    def perform_update(self, serializer):
        checker = self.request.user if self.request.user.is_authenticated else None

        serializer.save(
            Checker_Id=checker,
            Checker_DT_Stamp=timezone.now()
        )

from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.utils import timezone
from .models import MTTB_EXC_Rate, MTTB_EXC_Rate_History
from .serializers import ExcRateSerializer, ExcRateHistorySerializer

class ExcRateViewSet(viewsets.ModelViewSet):
    """
    CRUD for Exchange Rates.
    """
    queryset = MTTB_EXC_Rate.objects.select_related('ccy_code').all().order_by('ccy_code__ccy_code')
    serializer_class = ExcRateSerializer

    def get_permissions(self):
        # Allow unauthenticated create
        if self.request.method == 'POST':
            return [AllowAny()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        maker = None
        if self.request.user and self.request.user.is_authenticated:
            maker = self.request.user
        exc_rate = serializer.save(
            Maker_Id=maker,
            Maker_DT_Stamp=timezone.now()
        )
        # Also record initial history entry
        MTTB_EXC_Rate_History.objects.create(
            ccy_code=exc_rate.ccy_code,
            Buy_Rate=exc_rate.Buy_Rate,
            Sale_Rate=exc_rate.Sale_Rate,
            INT_Auth_Status=exc_rate.INT_Auth_Status,
            Maker_Id=maker,
            Maker_DT_Stamp=timezone.now(),
            Auth_Status=exc_rate.Auth_Status
        )

    def perform_update(self, serializer):
        checker = None
        if self.request.user and self.request.user.is_authenticated:
            checker = self.request.user
        exc_rate = serializer.save(
            Checker_DT_Stamp=timezone.now()
        )
        # Record history on each update
        MTTB_EXC_Rate_History.objects.create(
            ccy_code=exc_rate.ccy_code,
            Buy_Rate=exc_rate.Buy_Rate,
            Sale_Rate=exc_rate.Sale_Rate,
            INT_Auth_Status=exc_rate.INT_Auth_Status,
            Maker_Id=checker,
            Maker_DT_Stamp=timezone.now(),
            Auth_Status=exc_rate.Auth_Status
        )

class ExcRateHistoryViewSet(viewsets.ModelViewSet):
    """
    CRUD for Exchange Rate History.
    """
    queryset = MTTB_EXC_Rate_History.objects.select_related('ccy_code').all().order_by('-Maker_DT_Stamp')
    serializer_class = ExcRateHistorySerializer

    def get_permissions(self):
        # Read operations require authentication; creation only via ExcRateViewSet
        if self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return [IsAuthenticated()]
        return [IsAuthenticated()]
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def exchange_rate_history_for_ccy(request, ccy_code):
    """
    GET /api/exchange-rate-history/<ccy_code>/
    Returns all history entries for the given currency code.
    """
    histories = MTTB_EXC_Rate_History.objects.filter(ccy_code__ccy_code=ccy_code).order_by('-Maker_DT_Stamp')
    serializer = ExcRateHistorySerializer(histories, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from .models import MTTB_GLMaster
from .serializers import GLMasterSerializer

class GLMasterViewSet(viewsets.ModelViewSet):
    """
    CRUD for General Ledger Master records,
    with optional filtering on ?glType=X&category=Y
    and search via ?gl_code=substring
    """
    serializer_class = GLMasterSerializer

    def get_permissions(self):
        # Allow unauthenticated POST, require auth otherwise
        if self.request.method == 'POST':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        # Base queryset (with your related joins/order)
        qs = (
            MTTB_GLMaster.objects
            .select_related('Maker_Id', 'Checker_Id')
            .all()
            .order_by('gl_code')
        )

        params = self.request.query_params

        # Filter by glType if provided
        gltype = params.get('glType')
        if gltype:
            qs = qs.filter(glType=gltype)

        # Filter by category if provided
        category = params.get('category')
        if category:
            qs = qs.filter(category=category)

        # Search gl_code substring if provided
        code = params.get('gl_code')
        if code:
            qs = qs.filter(gl_code=code)

        return qs

    def perform_create(self, serializer):
        maker = self.request.user if self.request.user.is_authenticated else None
        serializer.save(
            Maker_Id=maker,
            Maker_DT_Stamp=timezone.now()
        )

    def perform_update(self, serializer):
        checker = self.request.user if self.request.user.is_authenticated else None
        serializer.save(
            Checker_Id=checker,
            Checker_DT_Stamp=timezone.now()
        )
    
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from .models import MTTB_GLSub
from .serializers import GLSubSerializer

class GLSubViewSet(viewsets.ModelViewSet):
    """
    CRUD for General Ledger Sub-account (GLSub) records.
    """
    queryset = MTTB_GLSub.objects.select_related('gl_code', 'Maker_Id', 'Checker_Id').all().order_by('glsub_code')
    serializer_class = GLSubSerializer

    def get_permissions(self):
        # Allow unauthenticated create if needed
        if self.request.method == 'POST':
            return [AllowAny()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        maker = self.request.user if self.request.user and self.request.user.is_authenticated else None
        serializer.save(
            Maker_Id=maker,
            Maker_DT_Stamp=timezone.now()
        )

    def perform_update(self, serializer):
        checker = self.request.user if self.request.user and self.request.user.is_authenticated else None
        serializer.save(
            Checker_Id=checker,
            Checker_DT_Stamp=timezone.now()
        )



# class MTTB_EMPLOYEEViewSet(viewsets.ModelViewSet):
#     serializer_class = MTTB_EMPLOYEESerializer
#     permission_classes = [IsAuthenticated]
#     lookup_field = 'employee_id'

#     def get_queryset(self):
#         queryset = MTTB_EMPLOYEE.objects.all().order_by('employee_id')
#         div_id = self.request.query_params.get('div_id')
#         if div_id:
#             queryset = queryset.filter(division_id=div_id)
#         return queryset

#     def create(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         if serializer.is_valid():
#             self.perform_create(serializer)
#             return Response({
#                 "status": "success",
#                 "message": "Employee created successfully.",
#                 "data": serializer.data
#             }, status=status.HTTP_201_CREATED)
#         else:
#             return Response({
#                 "status": "error",
#                 "message": "Failed to create employee.",
#                 "errors": serializer.errors
#             }, status=status.HTTP_400_BAD_REQUEST)

#     def destroy(self, request, *args, **kwargs):
#         try:
#             instance = self.get_object()
#             self.perform_destroy(instance)
#             return Response({
#                 "status": "success",
#                 "message": "Employee deleted successfully."
#             }, status=status.HTTP_204_NO_CONTENT)
#         except Exception as e:
#             return Response({
#                 "status": "error",
#                 "message": f"Failed to delete employee: {str(e)}"
#             }, status=status.HTTP_400_BAD_REQUEST)

#     def perform_create(self, serializer):
#         maker = self.request.user if self.request.user and self.request.user.is_authenticated else None
#         serializer.save(
#             Maker_Id=maker,
#             Maker_DT_Stamp=timezone.now()
#         )

#     def perform_update(self, serializer):
#         checker = self.request.user if self.request.user and self.request.user.is_authenticated else None
#         serializer.save(
#             Checker_Id=checker,
#             Checker_DT_Stamp=timezone.now()
#         )
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from django.utils import timezone
from .models import MTTB_EMPLOYEE, MTTB_Users, MTTB_Divisions
from .serializers import EmployeeSerializer

class EmployeeViewSet(viewsets.ModelViewSet):
    """
    CRUD for employees, supporting:
      - JSON and multipart/form-data for file uploads
      - Filtering by ?div_id=...
      - Soft deletion via record_stat='D'
    """
    serializer_class = EmployeeSerializer
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Returns active employees (record_stat='A'), optionally filtered by div_id.
        """
        qs = MTTB_EMPLOYEE.objects.select_related('user_id', 'div_id', 'Maker_Id', 'Checker_Id').filter(record_stat='O')
        
        params = self.request.query_params
        div_id = params.get('div_id')
        if div_id:
            qs = qs.filter(div_id_id__div_id=div_id)
        
        return qs.order_by('employee_id')

    def perform_create(self, serializer):
        """
        Sets audit fields for creation.
        """
        serializer.save(
            Maker_Id=self.request.user if self.request.user.is_authenticated else None,
            Maker_DT_Stamp=timezone.now(),
            record_stat='A',
            Auth_Status='U',
            Once_Auth='N'
        )

    def perform_update(self, serializer):
        """
        Sets audit fields for updates.
        """
        serializer.save(
            Checker_Id=self.request.user if self.request.user.is_authenticated else None,
            Checker_DT_Stamp=timezone.now()
        )

    def perform_destroy(self, instance):
        """
        Soft deletes the employee by setting record_stat to 'D'.
        """
        instance.record_stat = 'D'
        instance.Checker_Id = self.request.user if self.request.user.is_authenticated else None
        instance.Checker_DT_Stamp = timezone.now()
        instance.save()

from .serializers import MTTB_LCL_HolidaySerializer
from .models import MTTB_LCL_Holiday
class HolidayViewSet(viewsets.ModelViewSet):
    queryset = MTTB_LCL_Holiday.objects.all().order_by('lcl_holiday_id')
    serializer_class = MTTB_LCL_HolidaySerializer
    permission_classes = [IsAuthenticated]

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import MTTB_Role_Detail
from .serializers import RoleDetailSerializer

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_role_detail(request):
    role_id = request.query_params.get('role_id')
    sub_menu_id = request.query_params.get('sub_menu_id')

    try:
        obj = MTTB_Role_Detail.objects.get(role_id=role_id, sub_menu_id=sub_menu_id)
    except MTTB_Role_Detail.DoesNotExist:
        return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

    serializer = RoleDetailSerializer(obj, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from .models import MTTB_Fin_Cycle
from .serializers import FinCycleSerializer

class FinCycleViewSet(viewsets.ModelViewSet):
    """
    CRUD for Financial Cycles.
    """
    queryset = MTTB_Fin_Cycle.objects.select_related('Maker_Id', 'Checker_Id').all().order_by('fin_cycle')
    serializer_class = FinCycleSerializer

    def get_permissions(self):
        # Allow anyone to create a new cycle, require auth elsewhere
        if self.request.method == 'POST':
            return [AllowAny()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        maker = self.request.user if self.request.user and self.request.user.is_authenticated else None
        serializer.save(
            Maker_Id=maker,
            Maker_DT_Stamp=timezone.now()
        )

    def perform_update(self, serializer):
        checker = self.request.user if self.request.user and self.request.user.is_authenticated else None
        serializer.save(
             Checker_Id=checker,
            Checker_DT_Stamp=timezone.now()
        )



from collections import OrderedDict
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import MTTB_GLMaster
from .serializers import GLMasterSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def gl_hierarchy(request):

    qs = MTTB_GLMaster.objects.all().order_by('glType', 'category', 'gl_code')

    # 2) group
    hierarchy = OrderedDict()
    for gl in qs:
        # group by type
        by_cat = hierarchy.setdefault(gl.glType or 'None', OrderedDict())
        # then by category
        lst = by_cat.setdefault(gl.category or 'None', [])
        # append serialized record
        lst.append(GLMasterSerializer(gl).data)

    # 3) build JSON‐friendly list
    result = []
    for gltype, cats in hierarchy.items():
        type_obj = {'glType': gltype, 'categories': []}
        for cat, items in cats.items():
            type_obj['categories'].append({
                'category': cat,
                'items': items
            })
        result.append(type_obj)

    return Response(result)

# views.py

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import MTTB_GLMaster

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def gl_tree(request):
    """
    GET /api/gl-tree/
    Returns all GL codes nested by prefix:
    [
      {
        "gl_code": "110",
        "gl_Desc_la": "...",
        "gl_Desc_en": "...",
        "children": [
          {
            "gl_code": "1101",
            "gl_Desc_la": "...",
            "gl_Desc_en": "...",
            "children": [
              {
                "gl_code": "11011",
                "children": [
                  { "gl_code": "110111", "children": [] },
                  { "gl_code": "110112", "children": [] }
                ]
              },
              { "gl_code": "11012", "children": [] }
            ]
          }
        ]
      }
    ]
    """
    # 1) load and order all
    q = MTTB_GLMaster.objects.all().order_by('gl_code')
    # 2) build a lookup of code -> node dict
    nodes = {}
    for gl in q:
        nodes[gl.gl_code] = {
            'gl_code': gl.gl_code,
            'gl_Desc_la': gl.gl_Desc_la,
            'gl_Desc_en': gl.gl_Desc_en,
            'children': []
        }

    roots = []
    # 3) attach each node to its parent (longest prefix)
    for code, node in nodes.items():
        # find the longest other code that's a strict prefix
        parent_code = None
        for candidate in nodes:
            if candidate != code and code.startswith(candidate):
                if parent_code is None or len(candidate) > len(parent_code):
                    parent_code = candidate
        if parent_code:
            nodes[parent_code]['children'].append(node)
        else:
            roots.append(node)

    return Response(roots)
