# Create your views here.
from decimal import Decimal
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
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.utils import timezone
from .models import MTTB_Users
from .serializers import MTTBUserSerializer
class MTTBUserViewSet(viewsets.ModelViewSet):
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
    @action(detail=True, methods=['post'])
    def authorize(self, request, pk=None):
        """Authorize a journal entry"""
        users = self.get_object()

        if users.Auth_Status == 'A':
            return Response({'error': 'Entry is already authorized'}, 
                          status=status.HTTP_400_BAD_REQUEST)

        # Set Auth_Status = 'A', Once_Status = 'Y', Record_Status = 'O'
        users.Auth_Status = 'A'
        users.Once_Status = 'Y'
        users.Record_Status = 'O'
        users.Checker_Id = request.user
        users.Checker_DT_Stamp = timezone.now()
        users.save()

        serializer = self.get_serializer(users)
        return Response({
            'message': 'Entry authorized successfully',
            'entry': serializer.data
        })

    @action(detail=True, methods=['post'])
    def unauthorize(self, request, pk=None):
        """Unauthorize a journal entry (set Auth_Status = 'U', Record_Status = 'C')"""
        users = self.get_object()

        if users.Auth_Status == 'U':
            return Response({'error': 'Entry is already unauthorized'}, 
                          status=status.HTTP_400_BAD_REQUEST)

        # Set Auth_Status = 'U', Record_Status = 'C'
        users.Auth_Status = 'U'
        users.Record_Status = 'C'
        users.Checker_Id = request.user
        users.Checker_DT_Stamp = timezone.now()
        users.save()

        serializer = self.get_serializer(users)
        return Response({
            'message': 'Entry unauthorized successfully',
            'entry': serializer.data
        })

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
    CRUD for Role_Detail records, with optional filtering by role_id and/or sub_menu_id via query params.
    """
    serializer_class = RoleDetailSerializer

    def create(self, request, *args, **kwargs):
        role_id = request.data.get('role_id')
        sub_menu_id = request.data.get('sub_menu_id')

        if MTTB_Role_Detail.objects.filter(role_id=role_id, sub_menu_id=sub_menu_id).exists():
            return Response(
                {"detail": "This role_id and sub_menu_id combination already exists."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().create(request, *args, **kwargs)

    @action(detail=False, methods=['get'], url_path='single')
    def get_single(self, request):
        role_id = request.query_params.get('role_id')
        sub_menu_id = request.query_params.get('sub_menu_id')

        if not role_id or not sub_menu_id:
            return Response(
                {'detail': 'Both role_id and sub_menu_id are required.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            obj = MTTB_Role_Detail.objects.select_related('sub_menu_id', 'sub_menu_id__menu_id').get(
                role_id=role_id, sub_menu_id=sub_menu_id
            )
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
        if self.request.method == 'POST':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        qs = MTTB_Role_Detail.objects.select_related('sub_menu_id', 'sub_menu_id__menu_id').all().order_by('role_id', 'sub_menu_id')
        params = self.request.query_params
        
        # Filter parameters
        role_id = params.get('role_id')
        sub_menu_id = params.get('sub_menu_id')
        menu_id = params.get('menu_id')  # Filter by main menu
        module_id = params.get('module_Id')  # Filter by module
        
        # Apply filters
        if role_id and sub_menu_id:
            qs = qs.filter(role_id=role_id, sub_menu_id=sub_menu_id)
        elif role_id:
            qs = qs.filter(role_id=role_id)
        elif sub_menu_id:
            qs = qs.filter(sub_menu_id=sub_menu_id)
        
        if menu_id:
            qs = qs.filter(sub_menu_id__menu_id_id=menu_id)
        if module_id:
            qs = qs.filter(sub_menu_id__menu_id__module_Id_id=module_id)

        return qs

    @action(detail=False, methods=['put'], url_path='update')
    def update_role_detail(self, request):
        role_id = request.query_params.get('role_id')
        sub_menu_id = request.query_params.get('sub_menu_id')

        if not role_id or not sub_menu_id:
            return Response(
                {'detail': 'Both role_id and sub_menu_id are required.'}, 
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
def roledetail_delete(request):
    role_id = request.GET.get('role_id')
    sub_menu_id = request.GET.get('sub_menu_id')
    try:
        obj = MTTB_Role_Detail.objects.get(role_id=role_id, sub_menu_id=sub_menu_id)
        obj.delete()
        return Response({"detail": "Role detail deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    except MTTB_Role_Detail.DoesNotExist:
        return Response({"detail": "Role detail not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"detail": f"Error deleting role detail: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
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
                'Record_Status': mod.Record_Status,
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
                'Record_Status': main.Record_Status,
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
                'Record_Status':        sub.Record_Status,
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
                'Record_Status':      mod.Record_Status,
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
                'Record_Status':    main.Record_Status,
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
                'Record_Status':        sub.Record_Status,
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
        .filter(Record_Status='O')
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
            'Record_Status': mod.Record_Status,
            'main_menus': []
        }

        # 4) Fetch active main menus for this module
        main_menus = (
            MTTB_MAIN_MENU.objects
            .filter(module_Id=mod, Record_Status='O')
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
                'Record_Status': main.Record_Status,
                'sub_menus': []
            }

            # 6) Fetch active sub-menus for this main menu
            sub_menus = (
                MTTB_SUB_MENU.objects
                .filter(menu_id=main, Record_Status='O')
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
                    'Record_Status': sub.Record_Status,
                    'functions': []
                }

                # 8) Fetch active functions for this sub-menu
                functions = (
                    MTTB_Function_Desc.objects
                    .filter(sub_menu_id=sub, is_active='O')
                    .order_by('function_order')
                )

                # 9) Loop through functions
                for func in functions:
                    function_data = {
                        'function_id': func.function_id,
                        'description_la': func.description_la,
                        'description_en': func.description_en,
                        'function_order': func.function_order,
                        'Record_Status': func.is_active
                    }
                    sub_menu_data['functions'].append(function_data)

                main_menu_data['sub_menus'].append(sub_menu_data)

            module_data['main_menus'].append(main_menu_data)

        result.append(module_data)

    return Response(result, status=status.HTTP_200_OK)

from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import viewsets, status
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
            Maker_Id=user_id,
            Maker_DT_Stamp=timezone.now()
        )

    def perform_update(self, serializer):
        user = self.request.user
        user_id = getattr(user, 'user_id', None)
        serializer.save(
            modified_by=user_id,
            modified_date=timezone.now()
        )
    @action(detail=True, methods=['post'])
    def authorize(self, request, pk=None):
        """Authorize a journal entry"""
        journal_entry = self.get_object()

        if journal_entry.Auth_Status == 'A':
            return Response({'error': 'Entry is already authorized'}, 
                          status=status.HTTP_400_BAD_REQUEST)

        # Set Auth_Status = 'A', Once_Status = 'Y', Record_Status = 'O'
        journal_entry.Auth_Status = 'A'
        journal_entry.Once_Status = 'Y'
        journal_entry.Record_Status = 'O'
        journal_entry.Checker_Id = request.user
        journal_entry.Checker_DT_Stamp = timezone.now()
        journal_entry.save()

        serializer = self.get_serializer(journal_entry)
        return Response({
            'message': 'Entry authorized successfully',
            'entry': serializer.data
        })

    @action(detail=True, methods=['post'])
    def unauthorize(self, request, pk=None):
        """Unauthorize a journal entry (set Auth_Status = 'U', Record_Status = 'C')"""
        journal_entry = self.get_object()

        if journal_entry.Auth_Status == 'U':
            return Response({'error': 'Entry is already unauthorized'}, 
                          status=status.HTTP_400_BAD_REQUEST)

        # Set Auth_Status = 'U', Record_Status = 'C'
        journal_entry.Auth_Status = 'U'
        journal_entry.Record_Status = 'C'
        journal_entry.Checker_Id = request.user
        journal_entry.Checker_DT_Stamp = timezone.now()
        journal_entry.save()

        serializer = self.get_serializer(journal_entry)
        return Response({
            'message': 'Entry unauthorized successfully',
            'entry': serializer.data
        })

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
            Maker_Id=user_id,
            Maker_DT_Stamp=timezone.now()
        )

    def perform_update(self, serializer):
        user = self.request.user
        user_id = getattr(user, 'user_id', None)
        serializer.save(
            Checker_Id=user_id,
            Checker_DT_Stamp=timezone.now()
        )
#set  stt of Record_Status to 'O' for mainmenu
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def set_stt_mainmenu(self, request, pk=None):
        mainmenu = self.get_object()

        if mainmenu.Record_Status == 'O':
            return Response({'detail': 'Already unauthorized'}, status=status.HTTP_400_BAD_REQUEST)

        current_user = request.user
        user_id = getattr(current_user, 'user_id', None) or current_user.id

        serializer = self.get_serializer(mainmenu, data={
            'Record_Status': 'O',
            'Checker_Id': user_id,
            'Checker_DT_Stamp': timezone.now()
        }, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    @action(detail=True, methods=['post'])
    def authorize(self, request, pk=None):
        """Authorize a journal entry"""
        journal_entry = self.get_object()

        if journal_entry.Auth_Status == 'A':
            return Response({'error': 'Entry is already authorized'}, 
                          status=status.HTTP_400_BAD_REQUEST)

        # Set Auth_Status = 'A', Once_Status = 'Y', Record_Status = 'O'
        journal_entry.Auth_Status = 'A'
        journal_entry.Once_Status = 'Y'
        journal_entry.Record_Status = 'O'
        journal_entry.Checker_Id = request.user
        journal_entry.Checker_DT_Stamp = timezone.now()
        journal_entry.save()

        serializer = self.get_serializer(journal_entry)
        return Response({
            'message': 'Entry authorized successfully',
            'entry': serializer.data
        })

    @action(detail=True, methods=['post'])
    def unauthorize(self, request, pk=None):
        """Unauthorize a journal entry (set Auth_Status = 'U', Record_Status = 'C')"""
        journal_entry = self.get_object()

        if journal_entry.Auth_Status == 'U':
            return Response({'error': 'Entry is already unauthorized'}, 
                          status=status.HTTP_400_BAD_REQUEST)

        # Set Auth_Status = 'U', Record_Status = 'C'
        journal_entry.Auth_Status = 'U'
        journal_entry.Record_Status = 'C'
        journal_entry.Checker_Id = request.user
        journal_entry.Checker_DT_Stamp = timezone.now()
        journal_entry.save()

        serializer = self.get_serializer(journal_entry)
        return Response({
            'message': 'Entry unauthorized successfully',
            'entry': serializer.data
        })

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
            Maker_Id=user_id,
            Maker_DT_Stamp=timezone.now()
        )

    def perform_update(self, serializer):
        user = self.request.user
        user_id = getattr(user, 'user_id', None)
        serializer.save(
            Checker_Id=user_id,
            Checker_DT_Stamp=timezone.now()
        )

#set  stt of Record_Status to 'O' for submenu
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def set_stt_submenu(self, request, pk=None):
        submenu = self.get_object()

        if submenu.Record_Status == 'N':
            return Response({'detail': 'Already unauthorized'}, status=status.HTTP_400_BAD_REQUEST)

        current_user = request.user
        user_id = getattr(current_user, 'user_id', None) or current_user.id

        serializer = self.get_serializer(submenu, data={
            'Record_Status': 'N',
            'modified_by': user_id,
            'modified_date': timezone.now()
        }, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    @action(detail=True, methods=['post'])
    def authorize(self, request, pk=None):
        """Authorize a journal entry"""
        journal_entry = self.get_object()

        if journal_entry.Auth_Status == 'A':
            return Response({'error': 'Entry is already authorized'}, 
                          status=status.HTTP_400_BAD_REQUEST)

        # Set Auth_Status = 'A', Once_Status = 'Y', Record_Status = 'O'
        journal_entry.Auth_Status = 'A'
        journal_entry.Once_Status = 'Y'
        journal_entry.Record_Status = 'O'
        journal_entry.Checker_Id = request.user
        journal_entry.Checker_DT_Stamp = timezone.now()
        journal_entry.save()

        serializer = self.get_serializer(journal_entry)
        return Response({
            'message': 'Entry authorized successfully',
            'entry': serializer.data
        })

    @action(detail=True, methods=['post'])
    def unauthorize(self, request, pk=None):
        """Unauthorize a journal entry (set Auth_Status = 'U', Record_Status = 'C')"""
        journal_entry = self.get_object()

        if journal_entry.Auth_Status == 'U':
            return Response({'error': 'Entry is already unauthorized'}, 
                          status=status.HTTP_400_BAD_REQUEST)

        # Set Auth_Status = 'U', Record_Status = 'C'
        journal_entry.Auth_Status = 'U'
        journal_entry.Record_Status = 'C'
        journal_entry.Checker_Id = request.user
        journal_entry.Checker_DT_Stamp = timezone.now()
        journal_entry.save()

        serializer = self.get_serializer(journal_entry)
        return Response({
            'message': 'Entry unauthorized successfully',
            'entry': serializer.data
        })


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
            Maker_Id=user_id,
            Maker_DT_Stamp=timezone.now()
        )

    def perform_update(self, serializer):
        user = self.request.user
        user_id = getattr(user, 'user_id', None)
        serializer.save(
            Checker_Id=user_id,
            Checker_DT_Stamp=timezone.now()
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

    def get_queryset(self):
        queryset = MTTB_EXC_Rate.objects.select_related('ccy_code').all().order_by('ccy_code__ccy_code')
        ccy_code_param = self.request.query_params.get('ccy_code')
        if ccy_code_param:
            queryset = queryset.filter(ccy_code__ccy_code=ccy_code_param)
        return queryset

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
    serializer_class = GLSubSerializer

    def get_queryset(self):
        queryset = MTTB_GLSub.objects.select_related('gl_code', 'Maker_Id', 'Checker_Id').all().order_by('glsub_code')

        gl_code = self.request.query_params.get('gl_code')
        glcode_sub = self.request.query_params.get('glcode_sub')  # New search param

        if gl_code:
            queryset = queryset.filter(gl_code=gl_code)

        if glcode_sub:
            queryset = queryset.filter(glsub_code__icontains=glcode_sub)

        return queryset

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
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def authorize(self, request, pk=None):
        """
        Set Auth_Status = 'A' for a GLSub record
        """
        glsub = self.get_object()
        if glsub.Auth_Status == 'A':
            return Response({'detail': 'Already authorized'}, status=status.HTTP_400_BAD_REQUEST)
        glsub.Auth_Status = 'A'
        glsub.Checker_Id = request.user
        glsub.Checker_DT_Stamp = timezone.now()
        glsub.save()
        serializer = self.get_serializer(glsub)
        return Response(serializer.data)
    



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

# from rest_framework import viewsets
# from .models import MTTB_Per_Code
# from .serializers import PerCodeSerializer

# class PerCodeViewSet(viewsets.ModelViewSet):
#     queryset = MTTB_Per_Code.objects.all()
#     serializer_class = PerCodeSerializer
#     lookup_field = 'period_code'  # use primary key (string)


from rest_framework import viewsets
from .models import MTTB_Per_Code
from .serializers import PerCodeSerializer

class PerCodeViewSet(viewsets.ModelViewSet):
    serializer_class = PerCodeSerializer
    lookup_field = 'period_code'

    def get_queryset(self):
        queryset = MTTB_Per_Code.objects.all()
        fincycle_param = self.request.query_params.get('fincycle')

        if fincycle_param:
            queryset = queryset.filter(Fin_cycle__fin_cycle=fincycle_param)

        return queryset


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



# from rest_framework.decorators import api_view, permission_classes
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.response import Response
# from .models import MTTB_GLMaster

# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def gl_tree(request):
#     """
#     Returns GL codes nested by prefix.
#     """
#     q = MTTB_GLMaster.objects.filter(gl_code__isnull=False).order_by('gl_code')

#     # Build code-to-node map
#     nodes = {}
#     for gl in q:
#         if gl.gl_code:
#             nodes[gl.gl_code] = {
#                 'gl_code': gl.gl_code,
#                 'gl_Desc_la': gl.gl_Desc_la,
#                 'gl_Desc_en': gl.gl_Desc_en,
#                 'children': []
#             }

#     roots = []
#     for code, node in nodes.items():
#         parent_code = None
#         for candidate in nodes:
#             if candidate != code and code.startswith(candidate):
#                 if parent_code is None or len(candidate) > len(parent_code):
#                     parent_code = candidate
#         if parent_code:
#             nodes[parent_code]['children'].append(node)
#         else:
#             roots.append(node)

#     return Response(roots)

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import MTTB_GLMaster

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def gl_tree(request):
    """
    Returns GL codes nested by prefix.
    
    Query Parameters:
    - gl_code: Filter GL codes that start with this value (optional)
    - glType: Filter by GL type (optional)
    """
    # Get query parameters
    gl_code_filter = request.query_params.get('gl_code', None)
    gl_type_filter = request.query_params.get('glType', None)
    
    # Build base query
    q = MTTB_GLMaster.objects.filter(gl_code__isnull=False)
    
    # Apply filters if provided
    if gl_code_filter:
        q = q.filter(gl_code__startswith=gl_code_filter)
    
    if gl_type_filter:
        q = q.filter(glType=gl_type_filter)
    
    # Order by gl_code
    q = q.order_by('gl_code')

    # Build code-to-node map
    nodes = {}
    for gl in q:
        if gl.gl_code:
            nodes[gl.gl_code] = {
                'gl_code': gl.gl_code,
                'gl_Desc_la': gl.gl_Desc_la,
                'gl_Desc_en': gl.gl_Desc_en,
                'glType': gl.glType,
                'glCategory': gl.category,
                'gl_Retal': gl.retal,
                'ccy_Res': gl.ccy_Res,
                # 'Res_ccy': gl.Res_ccy,
                'Record_Status': gl.Record_Status,
                'Auth_Status': gl.Auth_Status,
                'children': []
            }

    roots = []
    for code, node in nodes.items():
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

from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Count
from .models import MTTB_MAIN_MENU

@api_view(['GET'])
def count_menus_by_module(request):
    module_id = request.query_params.get('module_Id')

    queryset = MTTB_MAIN_MENU.objects.all()

    if module_id:
        queryset = queryset.filter(module_Id=module_id)

    data = (
        queryset
        .values('module_Id')
        .annotate(c_main=Count('menu_id'))
    )

    return Response(data)


from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Count
from .models import MTTB_SUB_MENU

@api_view(['GET'])
def count_submenus_per_menu(request):
    menu_id = request.query_params.get('menu_id')

    queryset = MTTB_SUB_MENU.objects.all()

    if menu_id:
        queryset = queryset.filter(menu_id=menu_id)

    data = (
        queryset
        .values(
            'menu_id',
            'menu_id__menu_name_la',
            'menu_id__menu_name_en'
        )
        .annotate(count_menu=Count('sub_menu_id'))
        .order_by('menu_id')
    )

    result = [
        {
            "menu_id": item['menu_id'],
            "menu_name_la": item['menu_id__menu_name_la'],
            "menu_name_en": item['menu_id__menu_name_en'],
            "count_menu": item['count_menu']
        }
        for item in data
    ]

    return Response(result)

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from rest_framework import filters
from rest_framework import viewsets, status
from .models import MTTB_LCL_Holiday
from .serializers import MTTB_LCL_HolidaySerializer

class MTTB_LCL_HolidayViewSet(viewsets.ModelViewSet):
    """
    ViewSet for MTTB_LCL_Holiday model providing CRUD operations.
    
    list: Get all holidays with optional filtering
    create: Create a new holiday (no authentication required)
    retrieve: Get a specific holiday by ID
    update: Update a holiday (full update)
    partial_update: Update a holiday (partial update)
    destroy: Delete a holiday
    """
    queryset = MTTB_LCL_Holiday.objects.all()
    serializer_class = MTTB_LCL_HolidaySerializer
    lookup_field = 'lcl_holiday_id'
    
    # Enable filtering, searching, and ordering
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    # Define filterable fields
    filterset_fields = {
        'HYear': ['exact', 'in'],
        'HMonth': ['exact', 'in'],
        'HDate': ['exact', 'gte', 'lte', 'range'],
        'Holiday_List': ['exact'],
        'Record_Status': ['exact', 'in'],
        'Auth_Status': ['exact', 'in'],
        'Once_Auth': ['exact'],
        'Maker_Id': ['exact'],
        'Checker_Id': ['exact']
    }
    
    # Define searchable fields
    search_fields = ['lcl_holiday_id', 'HYear', 'HMonth']
    
    # Define ordering fields
    ordering_fields = ['lcl_holiday_id', 'HDate', 'HYear', 'HMonth', 'Maker_DT_Stamp']
    ordering = ['-Maker_DT_Stamp']  # Default ordering
    
    def get_permissions(self):
        # Allow anyone to create a new holiday, require auth elsewhere
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
    
    def get_queryset(self):
        """
        Optionally restricts the returned holidays based on query parameters.
        """
        queryset = super().get_queryset()
        
        # Example: Filter holidays by date range
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        
        if start_date and end_date:
            queryset = queryset.filter(HDate__range=[start_date, end_date])
        
        # Example: Filter only active records
        active_only = self.request.query_params.get('active_only', None)
        if active_only and active_only.lower() == 'true':
            queryset = queryset.filter(Record_Status='C')
        
        return queryset
    

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def pending_authorization(self, request):
        """
        Get all holidays pending authorization (Auth_Status='U')
        """
        pending = self.get_queryset().filter(Auth_Status='U')
        serializer = self.get_serializer(pending, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def authorize(self, request, lcl_holiday_id=None):
        """
        Authorize a holiday record
        """
        holiday = self.get_object()
        
        if holiday.Auth_Status == 'A':
            return Response(
                {'detail': 'Holiday already authorized'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Prevent self-authorization
        if holiday.Maker_Id and holiday.Maker_Id == request.user:
            return Response(
                {'detail': 'Cannot authorize your own record'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        holiday.Auth_Status = 'A'
        holiday.Checker_Id = request.user
        holiday.Checker_DT_Stamp = timezone.now()
        holiday.save()
        
        serializer = self.get_serializer(holiday)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def reject(self, request, lcl_holiday_id=None):
        """
        Reject a holiday record
        """
        holiday = self.get_object()
        
        if holiday.Auth_Status == 'U':
            return Response(
                {'detail': 'Holiday already rejected'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        holiday.Auth_Status = 'U'
        holiday.Checker_Id = request.user
        holiday.Checker_DT_Stamp = timezone.now()
        holiday.save()
        
        serializer = self.get_serializer(holiday)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_year_month(self, request):
        """
        Get holidays for a specific year and month
        """
        year = request.query_params.get('year', None)
        month = request.query_params.get('month', None)
        
        if not year:
            return Response(
                {'detail': 'Year parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(HYear=year)
        
        if month:
            queryset = queryset.filter(HMonth=month)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """
        Get upcoming holidays (HDate >= today)
        """
        from datetime import date
        today = date.today()
        
        upcoming = self.get_queryset().filter(
            HDate__gte=today,
            Record_Status='C',
            Auth_Status='A'
        ).order_by('HDate')
        
        serializer = self.get_serializer(upcoming, many=True)
        return Response(serializer.data)
    
    def perform_destroy(self, instance):
        instance.delete()

from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import MTTB_TRN_CodeSerializer
from .models import MTTB_TRN_Code

class MTTB_TRN_CodeViewSet(viewsets.ModelViewSet):
    """
    Enhanced CRUD ViewSet with filtering and searching
    """
    queryset = MTTB_TRN_Code.objects.all()
    serializer_class = MTTB_TRN_CodeSerializer
    lookup_field = 'trn_code'
    
    # Add filtering, searching, and ordering
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['Record_Status', 'Auth_Status', 'Once_Auth']
    search_fields = ['trn_code', 'trn_Desc_la', 'trn_Desc_en']
    ordering_fields = ['trn_code', 'Maker_DT_Stamp']
    ordering = ['-Maker_DT_Stamp']
    
    def get_permissions(self):
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
    
    def perform_destroy(self, instance):
        instance.Record_Status = 'D'
        instance.save()
    
    def get_queryset(self):
        """Add custom query filters"""
        queryset = super().get_queryset()
        
        # Filter only active records by default
        if self.request.query_params.get('all') != 'true':
            queryset = queryset.exclude(Record_Status='D')
        
        # Filter by authorization status
        auth_status = self.request.query_params.get('auth_status')
        if auth_status:
            queryset = queryset.filter(Auth_Status=auth_status)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get all pending transaction codes"""
        pending = self.get_queryset().filter(Auth_Status='U')
        serializer = self.get_serializer(pending, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def authorize(self, request, trn_code=None):
        """Authorize a transaction code"""
        trn_code_obj = self.get_object()
        
        if trn_code_obj.Auth_Status == 'A':
            return Response({'detail': 'Already authorized'}, status=status.HTTP_400_BAD_REQUEST)
        
        if trn_code_obj.Maker_Id == request.user:
            return Response({'detail': 'Cannot authorize your own record'}, status=status.HTTP_403_FORBIDDEN)
        
        trn_code_obj.Auth_Status = 'A'
        trn_code_obj.Checker_Id = request.user
        trn_code_obj.Checker_DT_Stamp = timezone.now()
        trn_code_obj.save()
        
        serializer = self.get_serializer(trn_code_obj)
        return Response(serializer.data)
    
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from django.db.models import Q
from .models import MTTB_ProvinceInfo, MTTB_DistrictInfo, MTTB_VillageInfo
from .serializers import ProvinceSerializer, DistrictSerializer, VillageSerializer

class ProvinceViewSet(viewsets.ModelViewSet):

    " CRUD for provinces with custom list and create  methods"

    queryset = MTTB_ProvinceInfo.objects.all().order_by('pro_id')
    serializer_class = ProvinceSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        count = queryset.count()

        if count == 0:
            return Response({
                "status": False,
                "message": "ບໍ່ພົບຂໍ້ມູນແຂວງ",
                "count": 0,
                "data": []
            }, status=status.HTTP_200_OK)

        return Response({
            "status": True,
            "message": "ສຳເລັດການດຶງຂໍ້ມູນແຂວງທັງໝົດ",
            "count": count,
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        try:
            response = super().create(request, *args, **kwargs)
            return Response({
                "status": True,
                "message": "ສຳເລັດການເພີ່ມຂໍ້ມູນແຂວງ",
                "data": response.data
            }, status=response.status_code)
        except Exception as e:
            return Response({
                "status": False,
                "message": f"ເພີ່ມຂໍ້ມູນແຂວງບໍ່ສຳເລັດ: {str(e)}"
            }, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        try:
            response = super().update(request, *args, **kwargs)
            return Response({
                "status": True,
                "message": "ອັບເດດຂໍ້ມູນແຂວງສຳເລັດ",
                "data": response.data
            }, status=response.status_code)
        except Exception as e:
            return Response({
                "status": False,
                "message": f"ອັບເດດຂໍ້ມູນແຂວງບໍ່ສຳເລັດ: {str(e)}"
            }, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response({
                "status": True,
                "message": "ລົບຂໍ້ມູນແຂວງສຳເລັດ"
            }, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({
                "status": False,
                "message": f"ລົບຂໍ້ມູນແຂວງບໍ່ສຳເລັດ: {str(e)}"
            }, status=status.HTTP_400_BAD_REQUEST)


class DistrictViewSet(viewsets.ModelViewSet):
    "CRUD for districts with custom list and create methods"
        # queryset = DistrictInfo_new.objects.all().order_by('pro_id', 'dis_id')
    serializer_class = DistrictSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = MTTB_DistrictInfo.objects.all().order_by('pro_id', 'dis_id')
        pro_id = self.request.query_params.get('pro_id')
        if pro_id:
            queryset = queryset.filter(pro_id=pro_id) 
        return queryset
    
    def perform_create(self, serializer):
        user = self.request.user
        user_id = getattr(user, 'user_id', None)
        serializer.save(
            user_id=user_id,
            date_insert=timezone.now()
        )

    def perform_update(self, serializer):
        serializer.save(
            date_update=timezone.now()
        )
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        pro_id = self.request.query_params.get('pro_id')
        pro_name = None

        if pro_id:
            try:
                province = MTTB_ProvinceInfo.objects.get(pro_id=pro_id)
                pro_name = province.pro_name_l
            except MTTB_ProvinceInfo.DoesNotExist:
                pro_name = None

        count = queryset.count()

        if count == 0:
            message = "ບໍ່ພົບຂໍ້ມູນທີ່ຄົນຄົນຫາ."
            return Response({
                "status": False,
                "message": message,
                "count": 0,
                "data": []
            }, status=status.HTTP_200_OK)
    
        if pro_name:
            message = f"ສຳເລັດການດຶງຂໍ້ມູນເມືອງຂອງແຂວງ={pro_name}."
        else:
            message = "ສຳເລັດການດຶງຂໍ້ມູນເມືອງທັງໝົດ."

        return Response({
            "status": True,
            "message": message,
            "count": queryset.count(),
            "data": serializer.data
        }, status=status.HTTP_200_OK)


    def create(self, request, *args, **kwargs):
        try:
            response = super().create(request, *args, **kwargs)
            return Response({
                "status": True,
                "message": "ສຳເລັດການເພີ່ມຂໍ້ມູນເມືອງ",
                "data": response.data
            }, status=response.status_code)
        except Exception as e:
            return Response({
                "status": False,
                "message": f"ການເພີ່ມຂໍ້ມູນເມືອງບໍ່ສຳເລັດ: {str(e)}"
            }, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        try:
            response = super().update(request, *args, **kwargs)
            return Response({
                "status": True,
                "message": "ອັບເດດຂໍ້ມູນເມືອງສຳເລັດ.",
                "data": response.data
            }, status=response.status_code)
        except Exception as e:
            return Response({
                "status": False,
                "message": f"ອັບເດດຂໍ້ມູນເມືອງບໍ່ສຳເລັດ: {str(e)}"
            }, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response({
                "status": True,
                "message": "ລົບຂໍ້ມູນສຳເລັດ."
            }, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({
                "status": False,
                "message": f"ລົບຂໍ້ມູນບໍ່ສຳເລັດ: {str(e)}"
            }, status=status.HTTP_400_BAD_REQUEST)

class VillageViewSet(viewsets.ModelViewSet):
    "CRUD for villages with custom list and create methods"
    serializer_class = VillageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = MTTB_VillageInfo.objects.all().order_by('pro_id', 'dis_id', 'vil_id')
        pro_id = self.request.query_params.get('pro_id')
        dis_id = self.request.query_params.get('dis_id')
        search_name = self.request.query_params.get('search_name')

        if pro_id:
            queryset = queryset.filter(pro_id=pro_id)
        if dis_id:
            queryset = queryset.filter(dis_id=dis_id)
        if search_name:
            queryset = queryset.filter(
                Q(vil_name_e__icontains=search_name) | Q(vil_name_l__icontains=search_name)
            )
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        pro_id = request.query_params.get('pro_id')
        dis_id = request.query_params.get('dis_id')

        pro_name = None
        dis_name = None

        if pro_id:
            try:
                province = MTTB_ProvinceInfo.objects.get(pro_id=pro_id.strip())
                pro_name = province.pro_name_l
            except MTTB_ProvinceInfo.DoesNotExist:
                pro_name = None
        
        if dis_id:
            try:
                district = MTTB_DistrictInfo.objects.get(dis_code=dis_id.strip())
                dis_name = district.dis_name_l
            except MTTB_DistrictInfo.DoesNotExist:
                dis_name = None

        count = queryset.count()

        if count == 0:
            return Response({
                "status": False,
                "message": "ບໍ່ພົບຂໍ້ມູນບ້ານທີ່ຄົ້ນຫາ",
                "count": 0,
                "data": []
            }, status=status.HTTP_200_OK)

        if pro_name and dis_name:
            message = f"ສຳເລັດການດຶງຂໍ້ມູນບ້ານໃນແຂວງ {pro_name} ແລະ ເມືອງ {dis_name}."
        elif pro_name:
            message = f"ສຳເລັດການດຶງຂໍ້ມູນບ້ານໃນແຂວງ {pro_name}."
        elif dis_name:
            message = f"ສຳເລັດການດຶງຂໍ້ມູນບ້ານໃນເມືອງ {dis_name}."
        else:
            message = "ສຳເລັດການດຶງຂໍ້ມູນບ້ານທັງໝົດ."

        return Response({
            "status": True,
            "message": message,
            "count": count,
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        user = self.request.user
        user_id = getattr(user, 'user_id', None)
        serializer.save(
            user_id=user_id,
            date_insert=timezone.now()
        )

    def perform_update(self, serializer):
        serializer.save(
            date_update=timezone.now()
        )

    def create(self, request, *args, **kwargs):
        try:
            response = super().create(request, *args, **kwargs)
            return Response({
                "status": True,
                "message": "ສຳເລັດການເພີ່ມຂໍ້ມູນບ້ານ",
                "data": response.data
            }, status=response.status_code)
        except Exception as e:
            return Response({
                "status": False,
                "message": f"ການເພີ່ມຂໍ້ມູນບ້ານບໍ່ສຳເລັດ: {str(e)}"
            }, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        try:
            response = super().update(request, *args, **kwargs)
            return Response({
                "status": True,
                "message": "ອັບເດດຂໍ້ມູນບ້ານສຳເລັດ",
                "data": response.data
            }, status=response.status_code)
        except Exception as e:
            return Response({
                "status": False,
                "message": f"ອັບເດດຂໍ້ມູນບ້ານບໍ່ສຳເລັດ: {str(e)}"
            }, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response({
                "status": True,
                "message": "ລົບຂໍ້ມູນສຳເລັດ"
            }, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({
                "status": False,
                "message": f"ລົບຂໍ້ມູນບໍ່ສຳເລັດ: {str(e)}"
            }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET']) 
@permission_classes([IsAuthenticated])
def list_villages(request):

    "method GET to list villages with optional filters only GET list_villages/"

    queryset = MTTB_VillageInfo.objects.all().order_by('pro_id', 'dis_id', 'vil_id')
    pro_id = request.query_params.get('pro_id')
    dis_id = request.query_params.get('dis_id')
    search_name = request.query_params.get('search_name')

    if pro_id:
        queryset = queryset.filter(pro_id=pro_id)
    if dis_id:
        queryset = queryset.filter(dis_id=dis_id)
    if search_name:
        queryset = queryset.filter(
            Q(vil_name_e__icontains=search_name) | Q(vil_name_l__icontains=search_name)
        )

    if not queryset.exists():
        return Response({
            "status": False,
            "message": "ບໍ່ພົບຂໍ້ມູນບ້ານທີ່ຄົ້ນຫາ",
            "count": 0,
            "data": []
        }, status=status.HTTP_404_NOT_FOUND)

    pro_name = None
    dis_name = None

    if pro_id:
        try:
            province = MTTB_ProvinceInfo.objects.get(pro_id=pro_id.strip())
            pro_name = province.pro_name_l
        except MTTB_ProvinceInfo.DoesNotExist:
            pro_name = None

    if dis_id:
        try:
            district = MTTB_DistrictInfo.objects.get(dis_code=dis_id.strip())
            dis_name = district.dis_name_l
        except MTTB_DistrictInfo.DoesNotExist:
            dis_name = None

    if pro_name and dis_name:
        message = f"ສຳເລັດການດຶງຂໍ້ມູນບ້ານໃນແຂວງ {pro_name} ແລະ ເມືອງ {dis_name}."
    elif pro_name:
        message = f"ສຳເລັດການດຶງຂໍ້ມູນບ້ານໃນແຂວງ {pro_name}."
    elif dis_name:
        message = f"ສຳເລັດການດຶງຂໍ້ມູນບ້ານໃນເມືອງ {dis_name}."
    else:
        message = "ສຳເລັດການດຶງຂໍ້ມູນບ້ານທັງໝົດ."

    serializer = VillageSerializer(queryset, many=True)

    return Response({
        "status": True,
        "message": message,
        "count": queryset.count(),
        "data": serializer.data
    }, status=status.HTTP_200_OK)

from rest_framework import viewsets
from .models import MTTB_DATA_Entry
from .serializers import MTTB_DATA_EntrySerializer

class Data_EntryViewSet(viewsets.ModelViewSet):
    queryset = MTTB_DATA_Entry.objects.all()
    serializer_class = MTTB_DATA_EntrySerializer

    def get_permissions(self):
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

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import MTTB_GLMaster, MTTB_GLSub
from .serializers import GLSubSerializer

@api_view(['GET'])
def GLTreeAPIView(request, gl_code_id):
    """
    Get GLSub details by GL code ID
    
    Args:
        gl_code_id: The primary key (glid) of MTTB_GLMaster
    
    Returns:
        JSON response with GLSub details and related GLMaster info
    """
    try:
        # Verify GL Master exists
        gl_master = get_object_or_404(MTTB_GLMaster, glid=gl_code_id)
        
        # Get all GLSub records for this GL code
        glsub_records = MTTB_GLSub.objects.filter(
            gl_code=gl_master,
           
        ).select_related('gl_code')
        
        if not glsub_records.exists():
            return Response({
                'success': False,
                'message': f'No GLSub records found for GL code ID: {gl_code_id}',
                'data': []
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Serialize the data
        serializer = GLSubSerializer(glsub_records, many=True)
        
        return Response({
            'success': True,
            'message': f'Found {glsub_records.count()} GLSub record(s)',
            'gl_master_info': {
                'glid': gl_master.glid,
                'gl_code': gl_master.gl_code,
                'gl_Desc_en': gl_master.gl_Desc_en,
                'gl_Desc_la': gl_master.gl_Desc_la
            },
            'data': serializer.data
        }, status=status.HTTP_200_OK)
        
    except MTTB_GLMaster.DoesNotExist:
        return Response({
            'success': False,
            'message': f'GL Master with ID {gl_code_id} not found',
            'data': []
        }, status=status.HTTP_404_NOT_FOUND)
    
    except Exception as e:
        return Response({
            'success': False,
            'message': f'An error occurred: {str(e)}',
            'data': []
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import MTTB_GLMaster, MTTB_GLSub
from .serializers import GLSubSerializer
from collections import defaultdict

@api_view(['GET'])
def GLTreeAll(request, gl_code_id=None):
    """
    Get GLSub details by GL code ID, or get all GLSub records grouped by GL Master
    
    Args:
        gl_code_id: Optional - The primary key (glid) of MTTB_GLMaster
                   If provided, returns GLSub records for that specific GL Master
                   If None, returns all GLSub records grouped by their GL Master
    
    Returns:
        JSON response with GLSub details grouped by GLMaster info
    """
    try:
        if gl_code_id is not None:
            # Get GLSub records for specific GL Master (existing functionality)
            gl_master = get_object_or_404(MTTB_GLMaster, glid=gl_code_id)
            
            glsub_records = MTTB_GLSub.objects.filter(
                gl_code=gl_master,
            ).select_related('gl_code')
            
            if not glsub_records.exists():
                return Response({
                    'success': False,
                    'message': f'No GLSub records found for GL code ID: {gl_code_id}',
                    'data': []
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Serialize the data
            serializer = GLSubSerializer(glsub_records, many=True)
            
            return Response({
                'success': True,
                'message': f'Found {glsub_records.count()} GLSub record(s)',
                'gl_master_info': {
                    'glid': gl_master.glid,
                    'gl_code': gl_master.gl_code,
                    'gl_Desc_en': gl_master.gl_Desc_en,
                    'gl_Desc_la': gl_master.gl_Desc_la,
                    'glType': gl_master.glType,
                    'category': gl_master.category,
                    'retal': gl_master.retal,
                    'ccy_Res': gl_master.ccy_Res,
                    'Res_ccy': gl_master.Res_ccy,
                    'Record_Status': gl_master.Record_Status,
                    'Auth_Status': gl_master.Auth_Status
                },
                'data': serializer.data
            }, status=status.HTTP_200_OK)
            
        else:
            # CORRECTED LOGIC: Find all GLSub records and group by GL Master
            
            # Step 1: Get all GLSub records with their GL Master info
            glsub_records = MTTB_GLSub.objects.all().select_related('gl_code')
            
            if not glsub_records.exists():
                return Response({
                    'success': False,
                    'message': 'No GLSub records found in the system',
                    'data': []
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Step 2: Group GLSub records by GL Master
            gl_master_groups = defaultdict(list)
            
            for glsub in glsub_records:
                if glsub.gl_code:  # Make sure gl_code exists
                    gl_master_groups[glsub.gl_code].append(glsub)
            
            # Step 3: Build the tree structure
            tree_data = []
            total_glsub_count = 0
            
            for gl_master, glsub_list in gl_master_groups.items():
                # Serialize GLSub records for this GL Master
                glsub_serializer = GLSubSerializer(glsub_list, many=True)
                
                # Build GL Master node with children
                gl_master_node = {
                    'gl_master_info': {
                        'glid': gl_master.glid,
                        'gl_code': gl_master.gl_code,
                        'gl_Desc_en': gl_master.gl_Desc_en,
                        'gl_Desc_la': gl_master.gl_Desc_la,
                        'glType': gl_master.glType,
                        'category': gl_master.category,
                        'Record_Status': gl_master.Record_Status,
                        'Auth_Status': gl_master.Auth_Status
                    },
                    'children_count': len(glsub_list),
                    'children': glsub_serializer.data
                }
                
                tree_data.append(gl_master_node)
                total_glsub_count += len(glsub_list)
            
            # Sort by GL Master glid for consistent ordering
            tree_data.sort(key=lambda x: x['gl_master_info']['glid'])
            
            return Response({
                'success': True,
                'message': f'Found {len(tree_data)} GL Master(s) with {total_glsub_count} total GLSub record(s)',
                'total_gl_masters': len(tree_data),
                'total_glsub_records': total_glsub_count,
                'data': tree_data
            }, status=status.HTTP_200_OK)
        
    except MTTB_GLMaster.DoesNotExist:
        return Response({
            'success': False,
            'message': f'GL Master with ID {gl_code_id} not found',
            'data': []
        }, status=status.HTTP_404_NOT_FOUND)
    
    except Exception as e:
        return Response({
            'success': False,
            'message': f'An error occurred: {str(e)}',
            'data': []
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

# from rest_framework import viewsets
# from .models import DETB_JRNL_LOG
# from .serializers import JRNLLogSerializer
# from rest_framework.permissions import IsAuthenticated

# class JRNLLogViewSet(viewsets.ModelViewSet):
#     queryset = DETB_JRNL_LOG.objects.select_related(
#     'Ccy_cd', 'Account', 'Txn_code', 'fin_cycle', 'Period_code',
#     'Maker_Id', 'Checker_Id'
# ).all().order_by('-Maker_DT_Stamp')

#     serializer_class = JRNLLogSerializer
#     permission_classes = [IsAuthenticated]  # optional, add/remove based on your needs

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.utils import timezone
from django.db.models import Q, Sum
from datetime import datetime, timedelta
import logging
from .models import DETB_JRNL_LOG, MTTB_GLSub, MTTB_GLMaster,MTTB_TRN_Code, DETB_JRNL_LOG_MASTER, DETB_JRNL_LOG_HIST
from .serializers import JRNLLogSerializer, JournalEntryBatchSerializer
from .utils import JournalEntryHelper

logger = logging.getLogger(__name__)

class JRNLLogViewSet(viewsets.ModelViewSet):
    queryset = DETB_JRNL_LOG.objects.select_related(
        'Ccy_cd', 'Account', 'Account__gl_code', 'Txn_code', 
        'fin_cycle', 'Period_code', 'Maker_Id', 'Checker_Id', 'module_id'
    ).all().order_by('-Maker_DT_Stamp')
    
    serializer_class = JRNLLogSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['Reference_No', 'Ccy_cd', 'Dr_cr', 'Auth_Status', 'Txn_code']
    search_fields = ['Reference_No', 'Addl_text', 'Account__glsub_code', 'Account__glsub_Desc_la']
    ordering_fields = ['Maker_DT_Stamp', 'Value_date', 'Reference_No']

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(Value_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(Value_date__lte=end_date)
        
        # Filter by account
        account_id = self.request.query_params.get('account_id')
        if account_id:
            queryset = queryset.filter(Account_id=account_id)

        # Filter by Currency
        ccy_cd = self.request.query_params.get('Ccy_cd')
        if ccy_cd:
            queryset = queryset.filter(Ccy_cd_id=ccy_cd)

        Auth_Status = self.request.query_params.get('Auth_Status')
        if Auth_Status:
            queryset = queryset.filter(Auth_Status=Auth_Status)

        # Filter by Reference_No
        Reference_No = self.request.query_params.get('Reference_No')
        if Reference_No:
            queryset = queryset.filter(Reference_No=Reference_No)
            

        return queryset

    def perform_create(self, serializer):
        """Set audit fields on creation"""
        user = self.request.user
        serializer.save(
            Maker_Id=user,
            Maker_DT_Stamp=timezone.now(),
            Auth_Status='U'  # Unauthorized
        )

    def perform_update(self, serializer):
        """Update only if not authorized"""
        instance = serializer.instance
        if instance.Auth_Status == 'A':
            raise serializer.ValidationError("Cannot modify authorized entries.")
        
        user = self.request.user
        serializer.save(
            Maker_Id=user,
            Maker_DT_Stamp=timezone.now()
        )

    # @action(detail=False, methods=['post'])
    # def batch_create(self, request):
    #     """Create multiple journal entries in a single transaction"""
    #     serializer = JournalEntryBatchSerializer(data=request.data)
        
    #     if not serializer.is_valid():
    #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    #     data = serializer.validated_data
        
    #     try:
    #         with transaction.atomic():
    #             # Auto-generate reference number if not provided
    #             if not data.get('Reference_No'):
    #                 data['Reference_No'] = JournalEntryHelper.generate_reference_number(
    #                     module_id=data.get('module_id', 'GL'),
    #                     txn_code=data['Txn_code'],
    #                     date=data['Value_date'].date() if data.get('Value_date') else None
    #                 )
                
    #             # Get exchange rate
    #             exchange_rate = self.get_exchange_rate(data['Ccy_cd'])
                
    #             created_entries = []
    #             history_entries = []
                
    #             for entry_data in data['entries']:
    #                 # Calculate amounts based on Dr_cr
    #                 fcy_amount = Decimal(str(entry_data['Amount']))
    #                 lcy_amount = fcy_amount * exchange_rate
                    
    #                 # Set debit/credit amounts
    #                 fcy_dr = fcy_amount if entry_data['Dr_cr'] == 'D' else Decimal('0.00')
    #                 fcy_cr = fcy_amount if entry_data['Dr_cr'] == 'C' else Decimal('0.00')
    #                 lcy_dr = lcy_amount if entry_data['Dr_cr'] == 'D' else Decimal('0.00')
    #                 lcy_cr = lcy_amount if entry_data['Dr_cr'] == 'C' else Decimal('0.00')
                    
    #                 addl_sub_text = (
    #                     entry_data.get('Addl_sub_text') or 
    #                     data.get('Addl_sub_text', '') or 
    #                     f"Entry for {entry_data['Dr_cr']} {fcy_amount}"
    #                 )

    #                 account_no = entry_data.get('Account_no')

    #                 # Create journal entry
    #                 journal_entry = DETB_JRNL_LOG.objects.create(
    #                     module_id_id=data.get('module_id'),
    #                     Reference_No=data['Reference_No'],  # Now includes module_id
    #                     Ccy_cd_id=data['Ccy_cd'],
    #                     Fcy_Amount=fcy_amount,
    #                     Lcy_Amount=lcy_amount,
    #                     fcy_dr=fcy_dr,
    #                     fcy_cr=fcy_cr,
    #                     lcy_dr=lcy_dr,
    #                     lcy_cr=lcy_cr,
    #                     Dr_cr=entry_data['Dr_cr'],
    #                     Ac_relatives=entry_data.get('Ac_relatives'),
    #                     Account_id=entry_data['Account'],
    #                     Account_no=account_no,
    #                     Txn_code_id=data['Txn_code'],
    #                     Value_date=data['Value_date'],
    #                     Exch_rate=exchange_rate,
    #                     fin_cycle_id=data.get('fin_cycle'),
    #                     Period_code_id=data.get('Period_code'),
    #                     Addl_text=data.get('Addl_text', ''),
    #                     Addl_sub_text=addl_sub_text,
    #                     Maker_Id=request.user,
    #                     Maker_DT_Stamp=timezone.now(),
    #                     Auth_Status='U'
    #                 )

    #                 created_entries.append(journal_entry)

    #                 history_ref_no = f"{data['Reference_No']}-{len(history_entries) + 1:03d}"
                
    #                 history_entry = DETB_JRNL_LOG_HISTORY.objects.create(
    #                     Reference_No=history_ref_no,  # Unique reference for history
    #                     module_id_id=data.get('module_id'),
    #                     Ccy_cd_id=data['Ccy_cd'],
    #                     Fcy_Amount=fcy_amount,
    #                     Lcy_Amount=lcy_amount,
    #                     fcy_dr=fcy_dr,
    #                     fcy_cr=fcy_cr,
    #                     lcy_dr=lcy_dr,
    #                     lcy_cr=lcy_cr,
    #                     Dr_cr=entry_data['Dr_cr'],
    #                     Ac_relatives=entry_data.get('Ac_relatives'),
    #                     Account_id=entry_data['Account'],
    #                     Account_no=account_no,
    #                     Txn_code_id=data['Txn_code'],
    #                     Value_date=data['Value_date'],
    #                     Exch_rate=exchange_rate,
    #                     fin_cycle_id=data.get('fin_cycle'),
    #                     Period_code_id=data.get('Period_code'),
    #                     Addl_text=data.get('Addl_text', ''),
    #                     Addl_sub_text=addl_sub_text,
    #                     Maker_Id=request.user,
    #                     Maker_DT_Stamp=timezone.now(),
    #                     Auth_Status='U'
    #                 )
                    
    #                 history_entries.append(history_entry)

    #             if created_entries:
    #                 # Use the first entry as a reference for shared fields
    #                 entry_seq_no = len(created_entries) 
    #                 first = created_entries[0]
    #                 reference_no = first.Reference_No
    #                 module_id = first.module_id
    #                 ccy_cd = first.Ccy_cd
    #                 txn_code = first.Txn_code
    #                 value_date = first.Value_date
    #                 exch_rate = first.Exch_rate
    #                 fin_cycle = first.fin_cycle
    #                 period_code = first.Period_code
    #                 addl_text = first.Addl_text

    #                 # Sum Fcy_Amount and Lcy_Amount for this batch
    #                 total_fcy = sum(e.Fcy_Amount for e in created_entries)
    #                 total_lcy = sum(e.Lcy_Amount for e in created_entries)

    #                 DETB_JRNL_LOG_MASTER.objects.create(
    #                     module_id=module_id,
    #                     Reference_No=reference_no,
    #                     Ccy_cd=ccy_cd,
    #                     Fcy_Amount=total_fcy,
    #                     Lcy_Amount=total_lcy,
    #                     Txn_code=txn_code,
    #                     Value_date=value_date,
    #                     Exch_rate=exch_rate,
    #                     fin_cycle=fin_cycle,
    #                     Period_code=period_code,
    #                     Addl_text=addl_text,
    #                     Maker_Id=request.user,
    #                     Maker_DT_Stamp=timezone.now(),
    #                     Auth_Status='U',
    #                     entry_seq_no=entry_seq_no 
    #                 )

                    

                
    #             # Serialize response
    #             response_serializer = JRNLLogSerializer(created_entries, many=True)
    #             response_data = response_serializer.data

    #             for idx, entry in enumerate(created_entries):
    #                 response_data[idx]['Account_id'] = entry.Account.glsub_code
                
    #             return Response({
    #                 'message': f'Successfully created {len(created_entries)} journal entries',
    #                 'reference_no': data['Reference_No'],  # Return the generated reference
    #                 'entries': response_data
    #             }, status=status.HTTP_201_CREATED)
                
    #     except Exception as e:
    #         logger.error(f"Error creating batch journal entries: {str(e)}")
    #         return Response({
    #             'error': 'Failed to create journal entries',
    #             'detail': str(e)
    #         }, status=status.HTTP_400_BAD_REQUEST)
        
    @action(detail=False, methods=['post'])
    def batch_create(self, request):
        """Create multiple journal entries in a single transaction"""
        serializer = JournalEntryBatchSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        try:
            with transaction.atomic():
                # Auto-generate reference number if not provided
                if not data.get('Reference_No'):
                    data['Reference_No'] = JournalEntryHelper.generate_reference_number(
                        module_id=data.get('module_id', 'GL'),
                        txn_code=data['Txn_code'],
                        date=data['Value_date'].date() if data.get('Value_date') else None
                    )
                
                # Get exchange rate
                exchange_rate = self.get_exchange_rate(data['Ccy_cd'])
                
                created_entries = []
                history_entries = []
                
                # Generate base timestamp for unique history references
                base_timestamp = timezone.now().strftime("%H%M%S")  # HHMMSS format (6 chars)
                
                for idx, entry_data in enumerate(data['entries']):
                    # Calculate amounts based on Dr_cr
                    fcy_amount = Decimal(str(entry_data['Amount']))
                    lcy_amount = fcy_amount * exchange_rate
                    
                    # Set debit/credit amounts
                    fcy_dr = fcy_amount if entry_data['Dr_cr'] == 'D' else Decimal('0.00')
                    fcy_cr = fcy_amount if entry_data['Dr_cr'] == 'C' else Decimal('0.00')
                    lcy_dr = lcy_amount if entry_data['Dr_cr'] == 'D' else Decimal('0.00')
                    lcy_cr = lcy_amount if entry_data['Dr_cr'] == 'C' else Decimal('0.00')
                    
                    addl_sub_text = (
                        entry_data.get('Addl_sub_text') or 
                        data.get('Addl_sub_text', '') or 
                        f"Entry for {entry_data['Dr_cr']} {fcy_amount}"
                    )

                    account_no = entry_data.get('Account_no')
                    current_time = timezone.now()

                    # Create journal entry
                    journal_entry = DETB_JRNL_LOG.objects.create(
                        module_id_id=data.get('module_id'),
                        Reference_No=data['Reference_No'],
                        Ccy_cd_id=data['Ccy_cd'],
                        Fcy_Amount=fcy_amount,
                        Lcy_Amount=lcy_amount,
                        fcy_dr=fcy_dr,
                        fcy_cr=fcy_cr,
                        lcy_dr=lcy_dr,
                        lcy_cr=lcy_cr,
                        Dr_cr=entry_data['Dr_cr'],
                        Ac_relatives=entry_data.get('Ac_relatives'),
                        Account_id=entry_data['Account'],
                        Account_no=account_no,
                        Txn_code_id=data['Txn_code'],
                        Value_date=data['Value_date'],
                        Exch_rate=exchange_rate,
                        fin_cycle_id=data.get('fin_cycle'),
                        Period_code_id=data.get('Period_code'),
                        Addl_text=data.get('Addl_text', ''),
                        Addl_sub_text=addl_sub_text,
                        Maker_Id=request.user,
                        Maker_DT_Stamp=current_time,
                        Auth_Status='U'
                    )

                    created_entries.append(journal_entry)

                    # Generate shorter history reference number (max 20 chars)
                    # Strategy: Use first part of original ref + timestamp + sequence
                    original_ref = data['Reference_No']
                    
                    # Method 1: Truncate original and add timestamp + sequence
                    
                    history_entry = DETB_JRNL_LOG_HIST.objects.create(
                        Reference_No=original_ref,
                        module_id_id=data.get('module_id'),
                        Ccy_cd_id=data['Ccy_cd'],
                        Fcy_Amount=fcy_amount,
                        Lcy_Amount=lcy_amount,
                        fcy_dr=fcy_dr,
                        fcy_cr=fcy_cr,
                        lcy_dr=lcy_dr,
                        lcy_cr=lcy_cr,
                        Dr_cr=entry_data['Dr_cr'],
                        Ac_relatives=entry_data.get('Ac_relatives'),
                        Account_id=entry_data['Account'],
                        Account_no=account_no,
                        Txn_code_id=data['Txn_code'],
                        Value_date=data['Value_date'],
                        Exch_rate=exchange_rate,
                        fin_cycle_id=data.get('fin_cycle'),
                        Period_code_id=data.get('Period_code'),
                        Addl_text=data.get('Addl_text', ''),
                        Addl_sub_text=addl_sub_text,
                        Maker_Id=request.user,
                        Maker_DT_Stamp=current_time,
                        Auth_Status='U'
                    )
                    
                    history_entries.append(history_entry)
                
                

                if created_entries:
                    # Use the first entry as a reference for shared fields
                    entry_seq_no = len(created_entries) 
                    first = created_entries[0]
                    reference_no = first.Reference_No
                    module_id = first.module_id
                    ccy_cd = first.Ccy_cd
                    txn_code = first.Txn_code
                    value_date = first.Value_date
                    exch_rate = first.Exch_rate
                    fin_cycle = first.fin_cycle
                    period_code = first.Period_code
                    addl_text = first.Addl_text

                    # Sum Fcy_Amount and Lcy_Amount for this batch
                    total_fcy = sum(e.Fcy_Amount for e in created_entries)
                    total_lcy = sum(e.Lcy_Amount for e in created_entries)

                    master_entry = DETB_JRNL_LOG_MASTER.objects.create(
                        module_id=module_id,
                        Reference_No=reference_no,
                        Ccy_cd=ccy_cd,
                        Fcy_Amount=total_fcy,
                        Lcy_Amount=total_lcy,
                        Txn_code=txn_code,
                        Value_date=value_date,
                        Exch_rate=exch_rate,
                        fin_cycle=fin_cycle,
                        Period_code=period_code,
                        Addl_text=addl_text,
                        Maker_Id=request.user,
                        Maker_DT_Stamp=timezone.now(),
                        Auth_Status='U',
                        entry_seq_no=entry_seq_no 
                    )

                    # Log successful creation
                    logger.info(f"Journal batch created - Reference: {reference_no}, Entries: {len(created_entries)}, History: {len(history_entries)}")
                
                # Serialize response
                response_serializer = JRNLLogSerializer(created_entries, many=True)
                response_data = response_serializer.data

                for idx, entry in enumerate(created_entries):
                    response_data[idx]['Account_id'] = entry.Account.glsub_code
                
                return Response({
                    'message': f'Successfully created {len(created_entries)} journal entries with history',
                    'reference_no': data['Reference_No'],
                    'entries_created': len(created_entries),
                    'history_entries_created': len(history_entries),
                    'entries': response_data
                }, status=status.HTTP_201_CREATED)
                
        except Exception as e:
            logger.error(f"Error creating batch journal entries with history: {str(e)}")
            return Response({
                'error': 'Failed to create journal entries',
                'detail': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def balance_check(self, request):
        """Check if journal entries are balanced by reference number"""
        reference_no = request.query_params.get('reference_no')
        
        if not reference_no:
            return Response({'error': 'reference_no parameter is required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        entries = DETB_JRNL_LOG.objects.filter(Reference_No=reference_no)
        
        if not entries.exists():
            return Response({'error': 'No entries found for this reference number'}, 
                          status=status.HTTP_404_NOT_FOUND)
        
        # Calculate totals
        totals = entries.aggregate(
            total_lcy_dr=Sum('lcy_dr'),
            total_lcy_cr=Sum('lcy_cr'),
            total_fcy_dr=Sum('fcy_dr'),
            total_fcy_cr=Sum('fcy_cr')
        )
        
        lcy_balanced = abs((totals['total_lcy_dr'] or 0) - (totals['total_lcy_cr'] or 0)) < 0.01
        fcy_balanced = abs((totals['total_fcy_dr'] or 0) - (totals['total_fcy_cr'] or 0)) < 0.01
        
        return Response({
            'reference_no': reference_no,
            'entry_count': entries.count(),
            'lcy_totals': {
                'debit': totals['total_lcy_dr'] or 0,
                'credit': totals['total_lcy_cr'] or 0,
                'balanced': lcy_balanced
            },
            'fcy_totals': {
                'debit': totals['total_fcy_dr'] or 0,
                'credit': totals['total_fcy_cr'] or 0,
                'balanced': fcy_balanced
            },
            'overall_balanced': lcy_balanced and fcy_balanced
        })

    @action(detail=True, methods=['post'])
    def authorize(self, request, pk=None):
        """Authorize a journal entry"""
        journal_entry = self.get_object()
        
        if journal_entry.Auth_Status == 'A':
            return Response({'error': 'Entry is already authorized'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        journal_entry.Auth_Status = 'A'
        journal_entry.Checker_Id = request.user
        journal_entry.Checker_DT_Stamp = timezone.now()
        journal_entry.save()
        
        serializer = self.get_serializer(journal_entry)
        return Response({
            'message': 'Entry authorized successfully',
            'entry': serializer.data
        })

    @action(detail=False, methods=['post'])
    def authorize_batch(self, request):
        """Authorize multiple journal entries by reference number"""
        reference_no = request.data.get('reference_no')
        
        if not reference_no:
            return Response({'error': 'reference_no is required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        entries = DETB_JRNL_LOG.objects.filter(
            Reference_No=reference_no,
            Auth_Status='U'
        )
        
        if not entries.exists():
            return Response({'error': 'No unauthorized entries found for this reference number'}, 
                          status=status.HTTP_404_NOT_FOUND)
        
        # Check if balanced before authorization
        balance_info = self.balance_check(request)
        if not balance_info.data.get('overall_balanced'):
            return Response({'error': 'Cannot authorize unbalanced entries'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        updated_count = entries.update(
            Auth_Status='A',
            Checker_Id=request.user,
            Checker_DT_Stamp=timezone.now()
        )
        
        return Response({
            'message': f'Successfully authorized {updated_count} entries',
            'reference_no': reference_no
        })

    @action(detail=False, methods=['get'])
    def summary_report(self, request):
        """Generate summary report for journal entries"""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        queryset = self.get_queryset()
        
        if start_date:
            queryset = queryset.filter(Value_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(Value_date__lte=end_date)
        
        # Summary statistics
        summary = queryset.aggregate(
            total_entries=models.Count('JRNLLog_id'),
            total_lcy_amount=Sum('Lcy_Amount'),
            total_fcy_amount=Sum('Fcy_Amount'),
            authorized_count=models.Count('JRNLLog_id', filter=Q(Auth_Status='A')),
            unauthorized_count=models.Count('JRNLLog_id', filter=Q(Auth_Status='U'))
        )
        
        # By currency breakdown
        by_currency = queryset.values('Ccy_cd__ccy_code', 'Ccy_cd__Ccy_Name_la').annotate(
            entry_count=models.Count('JRNLLog_id'),
            total_amount=Sum('Fcy_Amount')
        ).order_by('-total_amount')
        
        # By transaction code breakdown
        by_txn_code = queryset.values('Txn_code__trn_code', 'Txn_code__trn_Desc_la').annotate(
            entry_count=models.Count('JRNLLog_id'),
            total_amount=Sum('Lcy_Amount')
        ).order_by('-total_amount')
        
        return Response({
            'period': {
                'start_date': start_date,
                'end_date': end_date
            },
            'summary': summary,
            'by_currency': list(by_currency),
            'by_transaction_code': list(by_txn_code)
        })

    def get_exchange_rate(self, currency_code):
        """Get current exchange rate for currency"""
        try:
            if currency_code == 'LAK':
                return Decimal('1.00')
            
            exc_rate = MTTB_EXC_Rate.objects.filter(
                ccy_code__ccy_code=currency_code,
                Auth_Status='A'
            ).first()
            
            if exc_rate:
                return exc_rate.Sale_Rate
            else:
                # Fallback to currency definition or default
                currency = MTTB_Ccy_DEFN.objects.get(ccy_code=currency_code)
                return getattr(currency, 'default_rate', Decimal('1.00'))
                
        except Exception:
            return Decimal('1.00')
    @action(detail=False, methods=['post'])
    def generate_reference(self, request):
        """Generate a reference number without creating entries"""
        module_id = request.data.get('module_id', 'GL')
        txn_code = request.data.get('txn_code')
        value_date = request.data.get('value_date')
        
        if not txn_code:
            return Response({'error': 'txn_code is required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Parse date if provided
        date = None
        if value_date:
            try:
                from datetime import datetime
                date = datetime.fromisoformat(value_date.replace('Z', '+00:00')).date()
            except:
                pass
        
        reference_no = JournalEntryHelper.generate_reference_number(
            module_id=module_id,
            txn_code=txn_code,
            date=date
        )
        
        return Response({
            'reference_no': reference_no,
            'module_id': module_id,
            'txn_code': txn_code,
            'date': date or timezone.now().date()
        })

from rest_framework import viewsets, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import DETB_JRNL_LOG_MASTER
from .serializers import DETB_JRNL_LOG_MASTER_Serializer

class DETB_JRNL_LOG_MASTER_ViewSet(viewsets.ModelViewSet):
    queryset = DETB_JRNL_LOG_MASTER.objects.all()
    serializer_class = DETB_JRNL_LOG_MASTER_Serializer

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['Ccy_cd', 'Txn_code', 'fin_cycle', 'Auth_Status', 'delete_stat']  # Add more as needed
    search_fields = ['Reference_No', 'Addl_text']  # Optional
    ordering_fields = ['Maker_DT_Stamp', 'Value_date']  # Optional

    def perform_update(self, serializer):
        """
        If Auth_Status is set to 'A', set all DETB_JRNL_LOG rows with the same Reference_No to 'A'.
        """
        instance = serializer.save()
        if instance.Auth_Status == 'A':
            from .models import DETB_JRNL_LOG
            DETB_JRNL_LOG.objects.filter(
                Reference_No=instance.Reference_No
            ).update(Auth_Status='A')

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # Soft delete logic
        instance.delete_stat = 'D'
        instance.save()
        return Response({'detail': 'Marked as deleted.'}, status=status.HTTP_204_NO_CONTENT)
    
    
    

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from datetime import datetime
from django.utils.timezone import make_aware
from .models import STTB_Dates, MTTB_LCL_Holiday


@api_view(['POST'])  # or ['GET'] if you want it triggered without payload
@permission_classes([IsAuthenticated])
def submit_eod_journal(request):
    today = datetime.today().date()
    current_year = today.year
    current_month = today.month
    current_day = today.day

    try:
        # Get Holiday Entry for Current Month and Year
        holiday = MTTB_LCL_Holiday.objects.get(HYear=str(current_year), HMonth=str(current_month))

        # Check Working Day from Holiday_List
        day_index = current_day - 1  # 0-based index
        if day_index >= len(holiday.Holiday_List):
            return Response({"status": "error", "message": "Holiday list does not include today."}, status=400)

        day_type = holiday.Holiday_List[day_index]
        if day_type != 'W':
            return Response({"status": "error", "message": f"Today is not a working day: {day_type}"}, status=400)

        # Check if EOD Already Submitted
        last_eod = STTB_Dates.objects.filter(eod_time='Y').order_by('-Start_Date').first()

        if last_eod and last_eod.Start_Date.date() >= today:
            return Response({"status": "error", "message": "EOD already submitted for today or later."}, status=400)

        # Save New EOD Entry
        new_eod = STTB_Dates.objects.create(
            Start_Date=make_aware(datetime.combine(today, datetime.min.time())),
            prev_Wroking_Day=last_eod.Start_Date if last_eod else None,
            next_working_Day=None,  # To be calculated if needed
            eod_time='Y'
        )

        return Response({
            "status": "success",
            "message": f"EOD submitted for {today}",
            "eod_id": new_eod.date_id
        }, status=201)

    except MTTB_LCL_Holiday.DoesNotExist:
        return Response({"status": "error", "message": "Holiday data not found for this month."}, status=404)

    except Exception as e:
        return Response({"status": "error", "message": str(e)}, status=500)