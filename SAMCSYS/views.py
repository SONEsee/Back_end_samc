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
                          status=status.HTTP_406_NOT_ACCEPTABLE)

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
                          status=status.HTTP_406_NOT_ACCEPTABLE)

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

# from rest_framework_simplejwt.tokens import RefreshToken
# from .models import MTTB_USER_ACCESS_LOG
# from rest_framework_simplejwt.settings import api_settings
# from django.utils import timezone

# def get_client_ip(request):
#     xff = request.META.get('HTTP_X_FORWARDED_FOR')
#     if xff:
#         return xff.split(',')[0].strip()
#     return request.META.get('REMOTE_ADDR')

# @api_view(["POST"])
# @permission_classes([AllowAny])
# def login_view(request):
#     uid = request.data.get("user_name")
#     pwd = request.data.get("user_password")
#     if not uid or not pwd:
#         # log failure
#         MTTB_USER_ACCESS_LOG.objects.create(
#             user_id=None,
#             session_id=None,
#             ip_address=get_client_ip(request),
#             user_agent=request.META.get('HTTP_USER_AGENT'),
#             login_status='F',        # F = failed
#             remarks='Missing credentials'
#         )
#         return Response(
#             {"error": "User_Name and User_Password required"},
#             status=status.HTTP_400_BAD_REQUEST,
#         )

#     hashed = _hash(pwd)
#     try:
#         user = MTTB_Users.objects.get(
#             user_name=uid, user_password=hashed
#         )
#     except MTTB_Users.DoesNotExist:
#         # log failure
#         MTTB_USER_ACCESS_LOG.objects.create(
#             user_id=None,
#             session_id=None,
#             ip_address=get_client_ip(request),
#             user_agent=request.META.get('HTTP_USER_AGENT'),
#             login_status='F',
#             remarks='Invalid credentials'
#         )
#         return Response(
#             {"error": "Invalid credentials"},
#             status=status.HTTP_401_UNAUTHORIZED,
#         )

#     # 1) Create tokens
#     refresh = RefreshToken.for_user(user)
#     access  = refresh.access_token

#     # 2) Log the successful login
#     # Grab the JTI (unique token ID) for session tracking
#     jti = refresh.get(api_settings.JTI_CLAIM)
#     MTTB_USER_ACCESS_LOG.objects.create(
#         user_id=user,
#         session_id=jti,
#         ip_address=get_client_ip(request),
#         user_agent=request.META.get('HTTP_USER_AGENT'),
#         login_status='S'   # S = success
#     )

#     # 3) Serialize your user data
#     data = MTTBUserSerializer(user).data

#     # 4) Return tokens + user info
#     return Response({
#         "message": "Login successful",
#         "refresh": str(refresh),
#         "access": str(access),
#         "user": data
#     })



from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .models import MTTB_USER_ACCESS_LOG, MTTB_Users
from .serializers import MTTBUserSerializer
from .tokens import CustomRefreshToken
from rest_framework_simplejwt.settings import api_settings

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

    # 1) Create tokens using CustomRefreshToken
    # refresh = RefreshToken.for_user(user)
    # access  = refresh.access_token
    refresh = CustomRefreshToken.for_user(user)
    access = refresh.access_token

    # 2) Log the successful login
    # Grab the JTI (unique token ID) for session tracking
    jti = refresh[api_settings.JTI_CLAIM]
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

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def set_open(self, request, pk=None):
        """Set Record_Status = 'O' (Open) only if Auth_Status = 'A'"""
        obj = self.get_object()
        
        if obj.record_Status == 'O':
            return Response({'detail': 'Already open.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        if getattr(obj, 'Auth_Status', None) != 'A':
            return Response({'detail': 'Cannot set to Open. Only authorized (Auth_Status = "A") records can be opened.'}, status=status.HTTP_400_BAD_REQUEST)
        obj.record_Status = 'O'
        obj.Checker_Id = MTTB_Users.objects.get(user_id=request.user.user_id)
        obj.Checker_DT_Stamp = timezone.now()
        obj.save()
        serializer = self.get_serializer(obj)
        return Response({'message': 'Set to Open.', 'entry': serializer.data})

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def set_close(self, request, pk=None):
        """Set Record_Status = 'C' (Close)"""
        obj = self.get_object()
        if obj.record_Status == 'C':
            return Response({'detail': 'Already closed.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        obj.record_Status = 'C'
        obj.Checker_Id = MTTB_Users.objects.get(user_id=request.user.user_id)
        obj.Checker_DT_Stamp = timezone.now()
        obj.save()
        serializer = self.get_serializer(obj)
        return Response({'message': 'Set to Close.', 'entry': serializer.data})

    @action(detail=True, methods=['post'])
    def authorize(self, request, pk=None):
        """Authorize a journal entry"""
        journal_entry = self.get_object()

        if journal_entry.Auth_Status == 'A':
            return Response({'error': 'Entry is already authorized'}, 
                          status=status.HTTP_406_NOT_ACCEPTABLE)

        # Set Auth_Status = 'A', Once_Status = 'Y', Record_Status = 'O'
        journal_entry.Auth_Status = 'A'
        journal_entry.Once_Status = 'Y'
        journal_entry.record_Status = 'C'
        journal_entry.Checker_Id = MTTB_Users.objects.get(user_id=request.user.user_id)
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
                          status=status.HTTP_406_NOT_ACCEPTABLE)

        # Set Auth_Status = 'U', Record_Status = 'C'
        journal_entry.Auth_Status = 'U'
        journal_entry.record_Status = 'C'
        journal_entry.Checker_Id = MTTB_Users.objects.get(user_id=request.user.user_id)
        journal_entry.Checker_DT_Stamp = timezone.now()
        journal_entry.save()

        serializer = self.get_serializer(journal_entry)
        return Response({
            'message': 'Entry unauthorized successfully',
            'entry': serializer.data
        })

    
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

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def set_open(self, request, pk=None):
        """Set Record_Status = 'O' (Open) only if Auth_Status = 'A'"""
        obj = self.get_object()
        if obj.record_Status == 'O':
            return Response({'detail': 'Already open.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        if getattr(obj, 'Auth_Status', None) != 'A':
            return Response({'detail': 'Cannot set to Open. Only authorized (Auth_Status = "A") records can be opened.'}, status=status.HTTP_400_BAD_REQUEST)
        obj.record_Status = 'O'
        obj.Checker_Id = MTTB_Users.objects.get(user_id=request.user.user_id)
        obj.Checker_DT_Stamp = timezone.now()
        obj.save()
        serializer = self.get_serializer(obj)
        return Response({'message': 'Set to Open.', 'entry': serializer.data})

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def set_close(self, request, pk=None):
        """Set Record_Status = 'C' (Close)"""
        obj = self.get_object()
        if obj.record_Status == 'C':
            return Response({'detail': 'Already closed.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        obj.record_Status = 'C'
        obj.Checker_Id = MTTB_Users.objects.get(user_id=request.user.user_id)
        obj.Checker_DT_Stamp = timezone.now()
        obj.save()
        serializer = self.get_serializer(obj)
        return Response({'message': 'Set to Close.', 'entry': serializer.data})

    @action(detail=True, methods=['post'])
    def authorize(self, request, pk=None):
        """Authorize a journal entry"""
        journal_entry = self.get_object()

        if journal_entry.Auth_Status == 'A':
            return Response({'error': 'Entry is already authorized'}, 
                          status=status.HTTP_406_NOT_ACCEPTABLE)

        # Set Auth_Status = 'A', Once_Status = 'Y', Record_Status = 'O'
        journal_entry.Auth_Status = 'A'
        journal_entry.Once_Status = 'Y'
        journal_entry.record_Status = 'C'
        journal_entry.Checker_Id = MTTB_Users.objects.get(user_id=request.user.user_id)
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
                          status=status.HTTP_406_NOT_ACCEPTABLE)

        # Set Auth_Status = 'U', Record_Status = 'C'
        journal_entry.Auth_Status = 'U'
        journal_entry.record_Status = 'C'
        journal_entry.Checker_Id = MTTB_Users.objects.get(user_id=request.user.user_id)
        journal_entry.Checker_DT_Stamp = timezone.now()
        journal_entry.save()

        serializer = self.get_serializer(journal_entry)
        return Response({
            'message': 'Entry unauthorized successfully',
            'entry': serializer.data
        })



from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import MTTB_Role_Detail
from .serializers import RoleDetailSerializer

# class MTTBRoleDetailViewSet(viewsets.ModelViewSet):
#     """
#     CRUD for Role_Detail records, with optional filtering by role_id and/or sub_menu_id via query params.
#     """
#     serializer_class = RoleDetailSerializer

#     def create(self, request, *args, **kwargs):
#         role_id = request.data.get('role_id')
#         sub_menu_id = request.data.get('sub_menu_id')

#         if MTTB_Role_Detail.objects.filter(role_id=role_id, sub_menu_id=sub_menu_id).exists():
#             return Response(
#                 {"detail": "This role_id and sub_menu_id combination already exists."},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#         return super().create(request, *args, **kwargs)

#     @action(detail=False, methods=['get'], url_path='single')
#     def get_single(self, request):
#         role_id = request.query_params.get('role_id')
#         sub_menu_id = request.query_params.get('sub_menu_id')

#         if not role_id or not sub_menu_id:
#             return Response(
#                 {'detail': 'Both role_id and sub_menu_id are required.'}, 
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         try:
#             obj = MTTB_Role_Detail.objects.select_related('sub_menu_id', 'sub_menu_id__menu_id').get(
#                 role_id=role_id, sub_menu_id=sub_menu_id
#             )
#             serializer = self.get_serializer(obj)
#             return Response(serializer.data)
#         except MTTB_Role_Detail.DoesNotExist:
#             return Response(
#                 {'detail': 'Role detail not found.'}, 
#                 status=status.HTTP_404_NOT_FOUND
#             )
#         except Exception as e:
#             return Response(
#                 {'detail': f'Error retrieving role detail: {str(e)}'}, 
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )

#     def get_permissions(self):
#         if self.request.method == 'POST':
#             return [AllowAny()]
#         return [IsAuthenticated()]

#     def get_queryset(self):
#         qs = MTTB_Role_Detail.objects.select_related('sub_menu_id', 'sub_menu_id__menu_id').all().order_by('role_id', 'sub_menu_id')
#         params = self.request.query_params
        
#         # Filter parameters
#         role_id = params.get('role_id')
#         sub_menu_id = params.get('sub_menu_id')
#         menu_id = params.get('menu_id')  # Filter by main menu
#         module_id = params.get('module_id') or params.get('module_Id')  # Accept both 'module_id' and 'module_Id'
#         auth_status = params.get('Auth_Status')
#         record_status = params.get('Record_Status')

#         # Apply filters
#         if role_id and sub_menu_id:
#             qs = qs.filter(role_id=role_id, sub_menu_id=sub_menu_id)
#         elif role_id:
#             qs = qs.filter(role_id=role_id)
#         elif sub_menu_id:
#             qs = qs.filter(sub_menu_id=sub_menu_id)
        
#         if menu_id:
#             qs = qs.filter(sub_menu_id__menu_id_id=menu_id)
#         if module_id:
#             qs = qs.filter(sub_menu_id__menu_id__module_Id_id=module_id)
#         if auth_status:
#             qs = qs.filter(Auth_Status=auth_status)
#         if record_status:
#             qs = qs.filter(Record_Status=record_status)

#         return qs
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Q, F
from .models import MTTB_Role_Detail, MTTB_Role_Master, STTB_ModulesInfo, MTTB_MAIN_MENU, MTTB_SUB_MENU
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
        
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def set_open(self, request, pk=None):
        """Set Record_Status = 'O' (Open) only if Auth_Status = 'A'"""
        obj = self.get_object()
        if obj.Record_Status == 'O':
            return Response({'detail': 'Already open.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        
        obj.Record_Status = 'O'
        obj.Checker_Id = MTTB_Users.objects.get(user_id=request.user.user_id)
        obj.Checker_DT_Stamp = timezone.now()
        obj.save()
        serializer = self.get_serializer(obj)
        return Response({'message': 'Set to Open.', 'entry': serializer.data})

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def set_close(self, request, pk=None):
        """Set Record_Status = 'C' (Close)"""
        obj = self.get_object()
        if obj.Record_Status == 'C':
            return Response({'detail': 'Already closed.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        obj.Record_Status = 'C'
        obj.Checker_Id = MTTB_Users.objects.get(user_id=request.user.user_id)
        obj.Checker_DT_Stamp = timezone.now()
        obj.save()
        serializer = self.get_serializer(obj)
        return Response({'message': 'Set to Close.', 'entry': serializer.data})


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
                    .filter(Record_Status='O')
                    .order_by('function_order')
                )

                # 9) Loop through functions
                for func in functions:
                    function_data = {
                        'function_id': func.function_id,
                        'description_la': func.description_la,
                        'description_en': func.description_en,
                        'function_order': func.function_order,
                        'Record_Status': func.Record_Status
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
            Checker_Id=user_id,
            Checker_DT_Stamp=timezone.now()
    )

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def set_open(self, request, pk=None):
        obj = self.get_object()
        if obj.Record_Status == 'O':
            return Response({'detail': 'Already open.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        if getattr(obj, 'Auth_Status', None) != 'A':
            return Response({'detail': 'Cannot set to Open. Only authorized (Auth_Status = "A") records can be opened.'}, status=status.HTTP_400_BAD_REQUEST)
        obj.Record_Status = 'O'
        obj.Checker_Id = getattr(request.user, 'user_id', None) or getattr(request.user, 'id', None) or str(request.user)
        obj.Checker_DT_Stamp = timezone.now()
        obj.save()
        serializer = self.get_serializer(obj)
        return Response({'message': 'Set to Open.', 'entry': serializer.data})

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def set_close(self, request, pk=None):
        """Set Record_Status = 'C' (Close)"""
        obj = self.get_object()
        if obj.Record_Status == 'C':
            return Response({'detail': 'Already closed.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        obj.Record_Status = 'C'
        obj.Checker_Id = getattr(request.user, 'user_id', None) or getattr(request.user, 'id', None) or str(request.user)
        obj.Checker_DT_Stamp = timezone.now()
        obj.save()
        serializer = self.get_serializer(obj)
        return Response({'message': 'Set to Close.', 'entry': serializer.data})

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
        journal_entry.Record_Status = 'C'
        journal_entry.Checker_Id = getattr(request.user, 'user_id', None) or getattr(request.user, 'id', None) or str(request.user)
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
        journal_entry.Checker_Id = getattr(request.user, 'user_id', None) or getattr(request.user, 'id', None) or str(request.user)
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
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def set_open(self, request, pk=None):
        """Set Record_Status = 'O' (Open) only if Auth_Status = 'A'"""
        obj = self.get_object()
        if obj.Record_Status == 'O':
            return Response({'detail': 'Already open.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        if getattr(obj, 'Auth_Status', None) != 'A':
            return Response({'detail': 'Cannot set to Open. Only authorized (Auth_Status = "A") records can be opened.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        obj.Record_Status = 'O'
        obj.Checker_Id = getattr(request.user, 'user_id', None) or getattr(request.user, 'id', None) or str(request.user)
        obj.Checker_DT_Stamp = timezone.now()
        obj.save()
        serializer = self.get_serializer(obj)
        return Response({'message': 'Set to Open.', 'entry': serializer.data})

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def set_close(self, request, pk=None):
        """Set Record_Status = 'C' (Close)"""
        obj = self.get_object()
        if obj.Record_Status == 'C':
            return Response({'detail': 'Already closed.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        obj.Record_Status = 'C'
        obj.Checker_Id = getattr(request.user, 'user_id', None) or getattr(request.user, 'id', None) or str(request.user)
        obj.Checker_DT_Stamp = timezone.now()
        obj.save()
        serializer = self.get_serializer(obj)
        return Response({'message': 'Set to Close.', 'entry': serializer.data})

    @action(detail=True, methods=['post'])
    def authorize(self, request, pk=None):
        """Authorize a journal entry"""
        journal_entry = self.get_object()

        if journal_entry.Auth_Status == 'A':
            return Response({'error': 'Entry is already authorized'}, 
                          status=status.HTTP_406_NOT_ACCEPTABLE)

        # Set Auth_Status = 'A', Once_Status = 'Y', Record_Status = 'O'
        journal_entry.Auth_Status = 'A'
        journal_entry.Once_Status = 'Y'
        journal_entry.Record_Status = 'C'
        journal_entry.Checker_Id = getattr(request.user, 'user_id', None) or getattr(request.user, 'id', None) or str(request.user)
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
                          status=status.HTTP_406_NOT_ACCEPTABLE)

        # Set Auth_Status = 'U', Record_Status = 'C'
        journal_entry.Auth_Status = 'U'
        journal_entry.Record_Status = 'C'
        journal_entry.Checker_Id = getattr(request.user, 'user_id', None) or getattr(request.user, 'id', None) or str(request.user)
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

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def set_open(self, request, pk=None):
        """Set Record_Status = 'O' (Open) only if Auth_Status = 'A'"""
        obj = self.get_object()
        if obj.Record_Status == 'O':
            return Response({'detail': 'Already open.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        if getattr(obj, 'Auth_Status', None) != 'A':
            return Response({'detail': 'Cannot set to Open. Only authorized (Auth_Status = "A") records can be opened.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        obj.Record_Status = 'O'
        obj.Checker_Id = getattr(request.user, 'user_id', None) or getattr(request.user, 'id', None) or str(request.user)
        obj.Checker_DT_Stamp = timezone.now()
        obj.save()
        serializer = self.get_serializer(obj)
        return Response({'message': 'Set to Open.', 'entry': serializer.data})

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def set_close(self, request, pk=None):
        """Set Record_Status = 'C' (Close)"""
        obj = self.get_object()
        if obj.Record_Status == 'C':
            return Response({'detail': 'Already closed.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        obj.Record_Status = 'C'
        obj.Checker_Id = getattr(request.user, 'user_id', None) or getattr(request.user, 'id', None) or str(request.user)
        obj.Checker_DT_Stamp = timezone.now()
        obj.save()
        serializer = self.get_serializer(obj)
        return Response({'message': 'Set to Close.', 'entry': serializer.data})

    @action(detail=True, methods=['post'])
    def authorize(self, request, pk=None):
        """Authorize a journal entry"""
        journal_entry = self.get_object()

        if journal_entry.Auth_Status == 'A':
            return Response({'error': 'Entry is already authorized'}, 
                          status=status.HTTP_406_NOT_ACCEPTABLE)

        # Set Auth_Status = 'A', Once_Status = 'Y', Record_Status = 'O'
        journal_entry.Auth_Status = 'A'
        journal_entry.Once_Status = 'Y'
        journal_entry.Record_Status = 'C'
        journal_entry.Checker_Id = getattr(request.user, 'user_id', None) or getattr(request.user, 'id', None) or str(request.user)
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
                          status=status.HTTP_406_NOT_ACCEPTABLE)

        # Set Auth_Status = 'U', Record_Status = 'C'
        journal_entry.Auth_Status = 'U'
        journal_entry.Record_Status = 'C'
        journal_entry.Checker_Id = getattr(request.user, 'user_id', None) or getattr(request.user, 'id', None) or str(request.user)
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
        queryset = MTTB_Function_Desc.objects.all().order_by('function_order')
        Record_Status = self.request.query_params.get('Record_Status')
        eod_function = self.request.query_params.get('eod_function')
        if eod_function:
            queryset = queryset.filter(eod_function=eod_function)
        if Record_Status:
            queryset = queryset.filter(Record_Status=Record_Status) 
        return queryset
    
    def perform_create(self, serializer):
        maker = None
        if self.request.user and self.request.user.is_authenticated:
            maker = self.request.user  # Always assign the user instance
        serializer.save(
            Maker_Id=maker,
            Maker_DT_Stamp=timezone.now()
        )

    def perform_update(self, serializer):
        user = self.request.user if self.request.user and self.request.user.is_authenticated else None
        serializer.save(
            Checker_Id=user,
            Checker_DT_Stamp=timezone.now()
        )
    def perform_destroy(self, instance):
        return super().perform_destroy(instance)

    def get_permissions(self):
        # Allow unauthenticated creation
        if self.request.method == 'POST':
            return [AllowAny()]
        return [IsAuthenticated()]

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def set_open(self, request, pk=None):
        """Set Record_Status = 'O' (Open) only if Auth_Status = 'A'"""
        obj = self.get_object()
        if obj.Record_Status == 'O':
            return Response({'detail': 'Already open.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        obj.Record_Status = 'O'
        obj.Checker_Id = request.user  # Assign the user instance directly
        obj.Checker_DT_Stamp = timezone.now()
        obj.save()
        serializer = self.get_serializer(obj)
        return Response({'message': 'Set to Open.', 'entry': serializer.data})

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def set_close(self, request, pk=None):
        """Set Record_Status = 'C' (Close)"""
        obj = self.get_object()
        if obj.Record_Status == 'C':
            return Response({'detail': 'Already closed.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        obj.eod_function = 'N'  # Ensure eod_function is set to 'N' when closing
        obj.Record_Status = 'C'
        obj.Checker_Id = request.user
        obj.Checker_DT_Stamp = timezone.now()
        obj.save()
        serializer = self.get_serializer(obj)
        return Response({'message': 'Set to Close.', 'entry': serializer.data})

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def set_enable_eoc(self, request, pk=None):
        """Set Record_Status = 'O' (Open) only if Auth_Status = 'A'"""
        obj = self.get_object()
        if obj.eod_function == 'Y':
            return Response({'detail': 'Already open.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        if getattr(obj, 'Record_Status', None) != 'O':
            return Response({'detail': 'Cannot set to Open. Only Record_Status = "O" records can be opened.'}, status=status.HTTP_400_BAD_REQUEST)
        obj.eod_function = 'Y'
        obj.Checker_Id = request.user
        obj.Checker_DT_Stamp = timezone.now()
        obj.save()
        serializer = self.get_serializer(obj)
        return Response({'message': 'Set to Enable.', 'entry': serializer.data})

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def set_disable_eoc(self, request, pk=None): #set_enable_eoc(self, request, pk=None):
        """Set Record_Status = 'O' (Open) only if Auth_Status = 'A'"""
        obj = self.get_object()
        if obj.eod_function == 'N':
            return Response({'detail': 'Already Disable.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        if getattr(obj, 'Record_Status', None) != 'C':
            return Response({'detail': 'Cannot set to Open. Only Record_Status = "C" records can be opened.'}, status=status.HTTP_400_BAD_REQUEST)
        obj.eod_function = 'N'
        obj.Checker_Id = request.user
        obj.Checker_DT_Stamp = timezone.now()
        obj.save()
        serializer = self.get_serializer(obj)
        return Response({'message': 'Set to Disable.', 'entry': serializer.data})

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
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def set_open(self, request, pk=None):
        """Set Record_Status = 'O' (Open) only if Auth_Status = 'A'"""
        obj = self.get_object()
        if obj.Record_Status == 'O':
            return Response({'detail': 'Already open.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        if getattr(obj, 'Auth_Status', None) != 'A':
            return Response({'detail': 'Cannot set to Open. Only authorized (Auth_Status = "A") records can be opened.'}, status=status.HTTP_400_BAD_REQUEST)
        obj.Record_Status = 'O'
        obj.Checker_Id = MTTB_Users.objects.get(user_id=request.user.user_id)
        obj.Checker_DT_Stamp = timezone.now()
        obj.save()
        serializer = self.get_serializer(obj)
        return Response({'message': 'Set to Open.', 'entry': serializer.data})

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def set_close(self, request, pk=None):
        """Set Record_Status = 'C' (Close)"""
        obj = self.get_object()
        if obj.Record_Status == 'C':
            return Response({'detail': 'Already closed.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        obj.Record_Status = 'C'
        obj.Checker_Id = MTTB_Users.objects.get(user_id=request.user.user_id)
        obj.Checker_DT_Stamp = timezone.now()
        obj.save()
        serializer = self.get_serializer(obj)
        return Response({'message': 'Set to Close.', 'entry': serializer.data})

    @action(detail=True, methods=['post'])
    def authorize(self, request, pk=None):
        """Authorize a journal entry"""
        journal_entry = self.get_object()

        if journal_entry.Auth_Status == 'A':
            return Response({'error': 'Entry is already authorized'}, 
                          status=status.HTTP_406_NOT_ACCEPTABLE)

        # Set Auth_Status = 'A', Once_Status = 'Y', Record_Status = 'O'
        journal_entry.Auth_Status = 'A'
        journal_entry.Once_Status = 'Y'
        journal_entry.Record_Status = 'C'
        journal_entry.Checker_Id = MTTB_Users.objects.get(user_id=request.user.user_id)
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
        journal_entry.Checker_Id = MTTB_Users.objects.get(user_id=request.user.user_id)
        journal_entry.Checker_DT_Stamp = timezone.now()
        journal_entry.save()

        serializer = self.get_serializer(journal_entry)
        return Response({
            'message': 'Entry unauthorized successfully',
            'entry': serializer.data
        })


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

    @action(detail=True, methods=['post'])
    def authorize(self, request, pk=None):
        """Authorize a journal entry"""
        journal_entry = self.get_object()

        if journal_entry.Auth_Status == 'A':
            return Response({'error': 'Entry is already authorized'}, 
                          status=status.HTTP_406_NOT_ACCEPTABLE)

        # Set Auth_Status = 'A', Once_Status = 'Y', Record_Status = 'O'
        journal_entry.Auth_Status = 'A'
        journal_entry.Checker_Id = MTTB_Users.objects.get(user_id=request.user.user_id)
        journal_entry.Checker_DT_Stamp = timezone.now()
        journal_entry.save()

        serializer = self.get_serializer(journal_entry)
        return Response({
            'message': 'Entry authorized successfully',
            'entry': serializer.data
        })

    @action(detail=True, methods=['post'])
    def unauthorize(self, request, pk=None):
        """Unauthorize a journal entry (set Auth_Status = 'U')"""
        journal_entry = self.get_object()

        if journal_entry.Auth_Status == 'U':
            return Response({'error': 'Entry is already unauthorized'}, 
                          status=status.HTTP_406_NOT_ACCEPTABLE)

        # Set Auth_Status = 'U'
        journal_entry.Auth_Status = 'U'
        journal_entry.Checker_Id = MTTB_Users.objects.get(user_id=request.user.user_id)
        journal_entry.Checker_DT_Stamp = timezone.now()
        journal_entry.save()

        serializer = self.get_serializer(journal_entry)
        return Response({
            'message': 'Entry unauthorized successfully',
            'entry': serializer.data
        })


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
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def set_open(self, request, pk=None):
        """Set Record_Status = 'O' (Open) only if Auth_Status = 'A'"""
        obj = self.get_object()
        if obj.Record_Status == 'O':
            return Response({'detail': 'Already open.'}, status=status.HTTP_400_BAD_REQUEST)
        if getattr(obj, 'Auth_Status', None) != 'A':
            return Response({'detail': 'Cannot set to Open. Only authorized (Auth_Status = "A") records can be opened.'}, status=status.HTTP_400_BAD_REQUEST)
        obj.Record_Status = 'O'
        obj.Checker_Id = MTTB_Users.objects.get(user_id=request.user.user_id)
        obj.Checker_DT_Stamp = timezone.now()
        obj.save()
        serializer = self.get_serializer(obj)
        return Response({'message': 'Set to Open.', 'entry': serializer.data})

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def set_close(self, request, pk=None):
        """Set Record_Status = 'C' (Close)"""
        obj = self.get_object()
        if obj.Record_Status == 'C':
            return Response({'detail': 'Already closed.'}, status=status.HTTP_400_BAD_REQUEST)
        obj.Record_Status = 'C'
        obj.Checker_Id = MTTB_Users.objects.get(user_id=request.user.user_id)
        obj.Checker_DT_Stamp = timezone.now()
        obj.save()
        serializer = self.get_serializer(obj)
        return Response({'message': 'Set to Close.', 'entry': serializer.data})

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
        journal_entry.Record_Status = 'C'
        journal_entry.Checker_Id = MTTB_Users.objects.get(user_id=request.user.user_id)
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
        journal_entry.Checker_Id = MTTB_Users.objects.get(user_id=request.user.user_id)
        journal_entry.Checker_DT_Stamp = timezone.now()
        journal_entry.save()

        serializer = self.get_serializer(journal_entry)
        return Response({
            'message': 'Entry unauthorized successfully',
            'entry': serializer.data
        })
    
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from .models import MTTB_GLSub
from .serializers import GLSubSerializer, GLSubDisplaySerializer

class GLSubViewSet(viewsets.ModelViewSet):
    """
    CRUD for General Ledger Sub-account (GLSub) records.
    """
    serializer_class = GLSubSerializer

    def get_queryset(self):
        queryset = MTTB_GLSub.objects.select_related('gl_code', 'Maker_Id', 'Checker_Id').all().order_by('glsub_code')

        gl_code = self.request.query_params.get('gl_code')
        glcode_sub = self.request.query_params.get('glcode_sub')  

        if gl_code:
            queryset = queryset.filter(gl_code=gl_code)

        if glcode_sub:
            queryset = queryset.filter(glsub_code__icontains=glcode_sub)

        return queryset

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

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def set_open(self, request, pk=None):
        """Set Record_Status = 'O' (Open) only if Auth_Status = 'A'"""
        obj = self.get_object()
        if obj.Record_Status == 'O':
            return Response({'detail': 'Already open.'}, status=status.HTTP_400_BAD_REQUEST)
        if getattr(obj, 'Auth_Status', None) != 'A':
            return Response({'detail': 'Cannot set to Open. Only authorized (Auth_Status = "A") records can be opened.'}, status=status.HTTP_400_BAD_REQUEST)
        obj.Record_Status = 'O'
        obj.Checker_Id = MTTB_Users.objects.get(user_id=request.user.user_id)
        obj.Checker_DT_Stamp = timezone.now()
        obj.save()
        serializer = self.get_serializer(obj)
        return Response({'message': 'Set to Open.', 'entry': serializer.data})

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def set_close(self, request, pk=None):
        """Set Record_Status = 'C' (Close)"""
        obj = self.get_object()
        if obj.Record_Status == 'C':
            return Response({'detail': 'Already closed.'}, status=status.HTTP_400_BAD_REQUEST)
        obj.Record_Status = 'C'
        obj.Checker_Id = MTTB_Users.objects.get(user_id=request.user.user_id)
        obj.Checker_DT_Stamp = timezone.now()
        obj.save()
        serializer = self.get_serializer(obj)
        return Response({'message': 'Set to Close.', 'entry': serializer.data})

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
        journal_entry.Record_Status = 'C'
        journal_entry.Checker_Id = MTTB_Users.objects.get(user_id=request.user.user_id)
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
        journal_entry.Checker_Id = MTTB_Users.objects.get(user_id=request.user.user_id)
        journal_entry.Checker_DT_Stamp = timezone.now()
        journal_entry.save()

        serializer = self.get_serializer(journal_entry)
        return Response({
            'message': 'Entry unauthorized successfully',
            'entry': serializer.data
        })
    
    @action(detail=False, methods=['post'])
    def display_item_by_postside(self, request):
        """Retrieve GLSub items filtered by post_side (dr or cr) from GLMaster"""
        post_side = request.data.get('post_side')

        # Validate post_side
        if post_side not in ['dr', 'cr']:
            return Response({
                'error': 'Invalid post_side',
                'detail': 'post_side must be either "dr" or "cr"'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Map post_side to filter values
            post_side_filter = ['dr', 'drcr'] if post_side == 'dr' else ['cr', 'drcr']

            # Query GLSub joined with GLMaster
            items = MTTB_GLSub.objects.select_related('gl_code').filter(
                gl_code__post_side__in=post_side_filter
            ).order_by('glsub_code')

            if not items.exists():
                return Response({
                    'message': f'No GLSub items found for post_side: {post_side}',
                    'items': []
                }, status=status.HTTP_200_OK)

            # Serialize the results
            serializer = GLSubDisplaySerializer(items, many=True)
            logger.info(f"Retrieved {len(items)} GLSub items for post_side: {post_side}")

            return Response({
                'message': f'Successfully retrieved {len(items)} GLSub items for post_side: {post_side}',
                'items': serializer.data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error retrieving GLSub items for post_side {post_side}: {str(e)}")
            return Response({
                'error': 'Failed to retrieve GLSub items',
                'detail': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


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

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def set_open(self, request, pk=None):
        """Set Record_Status = 'O' (Open) only if Auth_Status = 'A'"""
        obj = self.get_object()
        if obj.record_stat == 'O':
            return Response({'detail': 'Already open.'}, status=status.HTTP_400_BAD_REQUEST)
        if getattr(obj, 'Auth_Status', None) != 'A':
            return Response({'detail': 'Cannot set to Open. Only authorized (Auth_Status = "A") records can be opened.'}, status=status.HTTP_400_BAD_REQUEST)
        obj.record_stat = 'O'
        obj.Checker_Id = MTTB_Users.objects.get(user_id=request.user.user_id)
        obj.Checker_DT_Stamp = timezone.now()
        obj.save()
        serializer = self.get_serializer(obj)
        return Response({'message': 'Set to Open.', 'entry': serializer.data})

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def set_close(self, request, pk=None):
        """Set Record_Status = 'C' (Close)"""
        obj = self.get_object()
        if obj.record_stat == 'C':
            return Response({'detail': 'Already closed.'}, status=status.HTTP_400_BAD_REQUEST)
        obj.record_stat = 'C'
        obj.Checker_Id = MTTB_Users.objects.get(user_id=request.user.user_id)
        obj.Checker_DT_Stamp = timezone.now()
        obj.save()
        serializer = self.get_serializer(obj)
        return Response({'message': 'Set to Close.', 'entry': serializer.data})

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
        journal_entry.record_stat = 'C'
        journal_entry.Checker_Id = MTTB_Users.objects.get(user_id=request.user.user_id)
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
        journal_entry.record_stat = 'C'
        journal_entry.Checker_Id = MTTB_Users.objects.get(user_id=request.user.user_id)
        journal_entry.Checker_DT_Stamp = timezone.now()
        journal_entry.save()

        serializer = self.get_serializer(journal_entry)
        return Response({
            'message': 'Entry unauthorized successfully',
            'entry': serializer.data
        })
        

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

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def set_open(self, request, pk=None):
        """Set Record_Status = 'O' (Open) only if Auth_Status = 'A'"""
        obj = self.get_object()
        if obj.Record_Status == 'O':
            return Response({'detail': 'Already open.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        if getattr(obj, 'Auth_Status', None) != 'A':
            return Response({'detail': 'Cannot set to Open. Only authorized (Auth_Status = "A") records can be opened.'}, status=status.HTTP_400_BAD_REQUEST)
        obj.Record_Status = 'O'
        obj.Checker_Id = MTTB_Users.objects.get(user_id=request.user.user_id)
        obj.Checker_DT_Stamp = timezone.now()
        obj.save()
        serializer = self.get_serializer(obj)
        return Response({'message': 'Set to Open.', 'entry': serializer.data})

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def set_close(self, request, pk=None):
        """Set Record_Status = 'C' (Close)"""
        obj = self.get_object()
        if obj.Record_Status == 'C':
            return Response({'detail': 'Already closed.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        obj.Record_Status = 'C'
        obj.Checker_Id = MTTB_Users.objects.get(user_id=request.user.user_id)
        obj.Checker_DT_Stamp = timezone.now()
        obj.save()
        serializer = self.get_serializer(obj)
        return Response({'message': 'Set to Close.', 'entry': serializer.data})

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
        journal_entry.Record_Status = 'C'
        journal_entry.Checker_Id = MTTB_Users.objects.get(user_id=request.user.user_id)
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
                          status=status.HTTP_406_NOT_ACCEPTABLE)

        # Set Auth_Status = 'U', Record_Status = 'C'
        journal_entry.Auth_Status = 'U'
        journal_entry.Record_Status = 'C'
        journal_entry.Checker_Id = MTTB_Users.objects.get(user_id=request.user.user_id)
        journal_entry.Checker_DT_Stamp = timezone.now()
        journal_entry.save()

        serializer = self.get_serializer(journal_entry)
        return Response({
            'message': 'Entry unauthorized successfully',
            'entry': serializer.data
        })



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
    def set_open(self, request, pk=None):
        """Set Record_Status = 'O' (Open) only if Auth_Status = 'A'"""
        obj = self.get_object()
        if obj.Record_Status == 'O':
            return Response({'detail': 'Already open.'}, status=status.HTTP_400_BAD_REQUEST)
        if getattr(obj, 'Auth_Status', None) != 'A':
            return Response({'detail': 'Cannot set to Open. Only authorized (Auth_Status = "A") records can be opened.'}, status=status.HTTP_400_BAD_REQUEST)
        obj.Record_Status = 'O'
        obj.Checker_Id = MTTB_Users.objects.get(user_id=request.user.user_id)
        obj.Checker_DT_Stamp = timezone.now()
        obj.save()
        serializer = self.get_serializer(obj)
        return Response({'message': 'Set to Open.', 'entry': serializer.data})

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def set_close(self, request, pk=None):
        """Set Record_Status = 'C' (Close)"""
        obj = self.get_object()
        if obj.Record_Status == 'C':
            return Response({'detail': 'Already closed.'}, status=status.HTTP_400_BAD_REQUEST)
        obj.Record_Status = 'C'
        obj.Checker_Id = MTTB_Users.objects.get(user_id=request.user.user_id)
        obj.Checker_DT_Stamp = timezone.now()
        obj.save()
        serializer = self.get_serializer(obj)
        return Response({'message': 'Set to Close.', 'entry': serializer.data})

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
        journal_entry.Record_Status = 'C'
        journal_entry.Checker_Id = MTTB_Users.objects.get(user_id=request.user.user_id)
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
        journal_entry.Checker_Id = MTTB_Users.objects.get(user_id=request.user.user_id)
        journal_entry.Checker_DT_Stamp = timezone.now()
        journal_entry.save()

        serializer = self.get_serializer(journal_entry)
        return Response({
            'message': 'Entry unauthorized successfully',
            'entry': serializer.data
        })

    
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
    

# from rest_framework import status
# from rest_framework.decorators import api_view
# from rest_framework.response import Response
# from django.shortcuts import get_object_or_404
# from .models import MTTB_GLMaster, MTTB_GLSub
# from .serializers import GLSubSerializer
# from collections import defaultdict

# @api_view(['GET'])
# def GLTreeAll(request, gl_code_id=None):
#     """
#     Get GLSub details by GL code ID, or get all GLSub records grouped by GL Master
    
#     Args:
#         gl_code_id: Optional - The primary key (glid) of MTTB_GLMaster
#                    If provided, returns GLSub records for that specific GL Master
#                    If None, returns all GLSub records grouped by their GL Master
    
#     Returns:
#         JSON response with GLSub details grouped by GLMaster info
#     """
#     try:
#         if gl_code_id is not None:
#             # Get GLSub records for specific GL Master (existing functionality)
#             gl_master = get_object_or_404(MTTB_GLMaster, glid=gl_code_id)
            
#             glsub_records = MTTB_GLSub.objects.filter(
#                 gl_code=gl_master,
#             ).select_related('gl_code')
            
#             if not glsub_records.exists():
#                 return Response({
#                     'success': False,
#                     'message': f'No GLSub records found for GL code ID: {gl_code_id}',
#                     'data': []
#                 }, status=status.HTTP_404_NOT_FOUND)
            
#             # Serialize the data
#             serializer = GLSubSerializer(glsub_records, many=True)
            
#             return Response({
#                 'success': True,
#                 'message': f'Found {glsub_records.count()} GLSub record(s)',
#                 'gl_master_info': {
#                     'glid': gl_master.glid,
#                     'gl_code': gl_master.gl_code,
#                     'gl_Desc_en': gl_master.gl_Desc_en,
#                     'gl_Desc_la': gl_master.gl_Desc_la,
#                     'glType': gl_master.glType,
#                     'category': gl_master.category,
#                     'retal': gl_master.retal,
#                     'ccy_Res': gl_master.ccy_Res,
#                     'Res_ccy': gl_master.Res_ccy,
#                     'Record_Status': gl_master.Record_Status,
#                     'Auth_Status': gl_master.Auth_Status
#                 },
#                 'data': serializer.data
#             }, status=status.HTTP_200_OK)
            
#         else:
#             # CORRECTED LOGIC: Find all GLSub records and group by GL Master
            
#             # Step 1: Get all GLSub records with their GL Master info
#             glsub_records = MTTB_GLSub.objects.all().select_related('gl_code')
            
#             if not glsub_records.exists():
#                 return Response({
#                     'success': False,
#                     'message': 'No GLSub records found in the system',
#                     'data': []
#                 }, status=status.HTTP_404_NOT_FOUND)
            
#             # Step 2: Group GLSub records by GL Master
#             gl_master_groups = defaultdict(list)
            
#             for glsub in glsub_records:
#                 if glsub.gl_code:  # Make sure gl_code exists
#                     gl_master_groups[glsub.gl_code].append(glsub)
            
#             # Step 3: Build the tree structure
#             tree_data = []
#             total_glsub_count = 0
            
#             for gl_master, glsub_list in gl_master_groups.items():
#                 # Serialize GLSub records for this GL Master
#                 glsub_serializer = GLSubSerializer(glsub_list, many=True)
                
#                 # Build GL Master node with children
#                 gl_master_node = {
#                     'gl_master_info': {
#                         'glid': gl_master.glid,
#                         'gl_code': gl_master.gl_code,
#                         'gl_Desc_en': gl_master.gl_Desc_en,
#                         'gl_Desc_la': gl_master.gl_Desc_la,
#                         'glType': gl_master.glType,
#                         'category': gl_master.category,
#                         'Record_Status': gl_master.Record_Status,
#                         'Auth_Status': gl_master.Auth_Status
#                     },
#                     'children_count': len(glsub_list),
#                     'children': glsub_serializer.data
#                 }
                
#                 tree_data.append(gl_master_node)
#                 total_glsub_count += len(glsub_list)
            
#             # Sort by GL Master glid for consistent ordering
#             tree_data.sort(key=lambda x: x['gl_master_info']['glid'])
            
#             return Response({
#                 'success': True,
#                 'message': f'Found {len(tree_data)} GL Master(s) with {total_glsub_count} total GLSub record(s)',
#                 'total_gl_masters': len(tree_data),
#                 'total_glsub_records': total_glsub_count,
#                 'data': tree_data
#             }, status=status.HTTP_200_OK)
        
#     except MTTB_GLMaster.DoesNotExist:
#         return Response({
#             'success': False,
#             'message': f'GL Master with ID {gl_code_id} not found',
#             'data': []
#         }, status=status.HTTP_404_NOT_FOUND)
    
#     except Exception as e:
#         return Response({
#             'success': False,
#             'message': f'An error occurred: {str(e)}',
#             'data': []
#         }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
    Get GLSub details by GL code ID (glid) or gl_code string, or return all GLSub grouped by GLMaster.
    
    Query Parameters:
    - gl_code_id (int): Primary key of MTTB_GLMaster
    - gl_code (str or int): gl_code field of MTTB_GLMaster
    """
    try:
        gl_code_param = request.GET.get('gl_code', None)

        # If both gl_code_id and gl_code are provided, return an error
        if gl_code_id and gl_code_param:
            return Response({
                'success': False,
                'message': 'Please provide only one of gl_code_id or gl_code',
                'data': []
            }, status=status.HTTP_400_BAD_REQUEST)

        gl_master = None

        if gl_code_id:
            gl_master = get_object_or_404(MTTB_GLMaster, glid=gl_code_id)
        elif gl_code_param:
            gl_master = get_object_or_404(MTTB_GLMaster, gl_code=str(gl_code_param))

        # If either gl_code_id or gl_code was used, return filtered GLSub
        if gl_master:
            glsub_records = MTTB_GLSub.objects.filter(
                gl_code=gl_master
            ).select_related('gl_code')

            if not glsub_records.exists():
                return Response({
                    'success': False,
                    'message': 'No GLSub records found for the provided GL code.',
                    'data': []
                }, status=status.HTTP_404_NOT_FOUND)

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
                    'ccy_Res': getattr(gl_master.ccy_Res, 'ccy_code', gl_master.ccy_Res),
                    'Res_ccy': getattr(gl_master.Res_ccy, 'ccy_code', gl_master.Res_ccy),
                    'Record_Status': gl_master.Record_Status,
                    'Auth_Status': gl_master.Auth_Status
                },
                'data': serializer.data
            }, status=status.HTTP_200_OK)

        # If no filtering, return full GL tree
        glsub_records = MTTB_GLSub.objects.all().select_related('gl_code')

        if not glsub_records.exists():
            return Response({
                'success': False,
                'message': 'No GLSub records found in the system',
                'data': []
            }, status=status.HTTP_404_NOT_FOUND)

        gl_master_groups = defaultdict(list)
        for glsub in glsub_records:
            if glsub.gl_code:
                gl_master_groups[glsub.gl_code].append(glsub)

        tree_data = []
        total_glsub_count = 0

        for gl_master, glsub_list in gl_master_groups.items():
            glsub_serializer = GLSubSerializer(glsub_list, many=True)
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
            'message': 'GL Master not found',
            'data': []
        }, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({
            'success': False,
            'message': f'An error occurred: {str(e)}',
            'data': []
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.utils import timezone
from django.db.models import Q, Sum
from datetime import datetime, timedelta
import logging
from .models import (DETB_JRNL_LOG, 
                     MTTB_GLSub, MTTB_GLMaster,
                     MTTB_TRN_Code, 
                     DETB_JRNL_LOG_MASTER, 
                     DETB_JRNL_LOG_HIST, 
                     ACTB_DAIRY_LOG,
                     ACTB_DAIRY_LOG_HISTORY)
from .serializers import JRNLLogSerializer, JournalEntryBatchSerializer
from .utils import JournalEntryHelper

logger = logging.getLogger(__name__)

class JRNLLogViewSet(viewsets.ModelViewSet):
    parser_classes = [JSONParser]
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
            queryset = queryset.filter(Reference_No=Reference_No).order_by('JRNLLog_id')
            

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
                daily_log_entries = []
                
                # Generate base timestamp for unique history references
                base_timestamp = timezone.now().strftime("%H%M%S")  # HHMMSS format (6 chars)
                
                # Counter for Reference_sub_No, incrementing for each pair
                pair_counter = 1
                
                # Process entries in pairs (assuming entries are ordered as D, C pairs)
                for idx in range(0, len(data['entries']), 2):  # Step by 2 for pairs
                    ref_sub_no = f"{data['Reference_No']}-{pair_counter:03d}"
                    
                    # Process each entry in the pair (usually D and C)
                    for pair_idx in range(2):
                        if idx + pair_idx >= len(data['entries']):
                            break  # Avoid index out of range if odd number of entries
                        entry_data = data['entries'][idx + pair_idx]
                        
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
                            Reference_sub_No=ref_sub_no,
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

                        # Create history entry
                        history_entry = DETB_JRNL_LOG_HIST.objects.create(
                            Reference_No=data['Reference_No'],
                            Reference_sub_No=ref_sub_no,
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

                        try:
                            glsub_account = MTTB_GLSub.objects.select_related('gl_code').get(
                                glsub_id=entry_data['Account']
                            )
                            gl_master = glsub_account.gl_code
                        except MTTB_GLSub.DoesNotExist:
                            logger.warning(f"GLSub account {entry_data['Account']} not found")
                            gl_master = None
                    
                    # Increment pair counter after processing each pair
                    pair_counter += 1

                if created_entries:
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

                    total_fcy = sum(e.fcy_dr for e in created_entries)
                    total_lcy = sum(e.lcy_dr for e in created_entries)
                
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

                    logger.info(f"Journal batch created - Reference: {reference_no}, Entries: {len(created_entries)}, History: {len(history_entries)}")
                
                response_serializer = JRNLLogSerializer(created_entries, many=True)
                response_data = response_serializer.data

                for idx, entry in enumerate(created_entries):
                    response_data[idx]['Account_id'] = entry.Account.glsub_code
                
                return Response({
                    'message': f'Successfully created {len(created_entries)} journal entries with history',
                    'reference_no': data['Reference_No'],
                    'entries_created': len(created_entries),
                    'history_entries_created': len(history_entries),
                    'daily_log_entries_created': len(daily_log_entries),
                    'entries': response_data
                }, status=status.HTTP_201_CREATED)
                
        except Exception as e:
            logger.error(f"Error creating batch journal entries with history: {str(e)}")
            return Response({
                'error': 'Failed to create journal entries',
                'detail': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    # Pherm  Fucttion Delete by Pair 
    # --------------------------------------
    @action(detail=False, methods=['delete'], url_path='delete-by-pair-account')
    def delete_by_pair_account(self, request):
        """Delete journal entries by Reference_sub_No with related records"""
        reference_sub_no = request.data.get('Reference_sub_No')

        if not reference_sub_no:
            return Response({
                'error': 'Missing required field',
                'detail': 'Reference_sub_No is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                # Find journal entries matching the Reference_sub_No
                journal_entries = DETB_JRNL_LOG.objects.filter(
                    Reference_sub_No=reference_sub_no
                )

                if not journal_entries.exists():
                    return Response({
                        'error': 'No matching journal entries found',
                        'detail': f'No entries found for Reference_sub_No: {reference_sub_no}'
                    }, status=status.HTTP_404_NOT_FOUND)

                # Verify exactly two entries (debit and credit pair)
                if len(journal_entries) != 2:
                    return Response({
                        'error': 'Incomplete pair found',
                        'detail': 'Expected exactly two paired entries (debit and credit)'
                    }, status=status.HTTP_400_BAD_REQUEST)

                # Verify debit/credit pairing
                dr_cr_values = {entry.Dr_cr for entry in journal_entries}
                if dr_cr_values != {'D', 'C'}:
                    return Response({
                        'error': 'Invalid debit/credit pair',
                        'detail': 'Paired entries must include one debit (D) and one credit (C)'
                    }, status=status.HTTP_400_BAD_REQUEST)

                # Get Reference_No for master entry deletion and logging
                reference_no = journal_entries.first().Reference_No

                # Delete related records
                deleted_counts = {
                    'journal_entries': 0,
                    'history_entries': 0,
                    'daily_log_entries': 0,
                    'daily_log_history_entries': 0,
                    'master_entry': 0
                }

                # Delete journal entries
                deleted_counts['journal_entries'] = journal_entries.delete()[0]

                # Delete corresponding history entries
                history_entries = DETB_JRNL_LOG_HIST.objects.filter(
                    Reference_sub_No=reference_sub_no
                )
                deleted_counts['history_entries'] = history_entries.delete()[0]

                # Delete master entry if it exists and no other journal entries remain for the Reference_No
                if not DETB_JRNL_LOG.objects.filter(Reference_No=reference_no).exists():
                    master_entry = DETB_JRNL_LOG_MASTER.objects.filter(
                        Reference_No=reference_no
                    )
                    deleted_counts['master_entry'] = master_entry.delete()[0]

                # Log deletion
                logger.info(f"Deleted journal batch - Reference_sub_No: {reference_sub_no}, "
                            f"Reference_No: {reference_no}, "
                            f"Counts: {deleted_counts}")

                return Response({
                    'message': 'Successfully deleted journal entries and related records',
                    'reference_sub_no': reference_sub_no,
                    'reference_no': reference_no,
                    'deleted_counts': deleted_counts
                }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error deleting journal entries for Reference_sub_No: {reference_sub_no}: {str(e)}")
            return Response({
                'error': 'Failed to delete journal entries',
                'detail': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    @action(detail=False, methods=['post'], url_path='reject-by-pair-account')
    def reject_by_pair_account(self, request):
        """Reject journal entries by Reference_sub_No and set Auth_Status to 'P' (pending fix) with comments"""
        reference_sub_no = request.data.get('Reference_sub_No')
        comments = request.data.get('comments')

        # Validate required fields
        if not reference_sub_no:
            return Response({
                'error': 'Missing required field',
                'detail': 'Reference_sub_No is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        if not comments:
            return Response({
                'error': 'Missing required field',
                'detail': 'Comments are required for rejection'
            }, status=status.HTTP_400_BAD_REQUEST)

        if len(comments) > 1000:
            return Response({
                'error': 'Invalid comments',
                'detail': 'Comments must not exceed 1000 characters'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                # Find journal entries matching the Reference_sub_No
                journal_entries = DETB_JRNL_LOG.objects.filter(
                    Reference_sub_No=reference_sub_no
                )

                if not journal_entries.exists():
                    return Response({
                        'error': 'No matching journal entries found',
                        'detail': f'No entries found for Reference_sub_No: {reference_sub_no}'
                    }, status=status.HTTP_404_NOT_FOUND)

                # Verify exactly two entries (debit and credit pair)
                if len(journal_entries) != 2:
                    return Response({
                        'error': 'Incomplete pair found',
                        'detail': 'Expected exactly two paired entries (debit and credit)'
                    }, status=status.HTTP_400_BAD_REQUEST)

                # Verify debit/credit pairing
                dr_cr_values = {entry.Dr_cr for entry in journal_entries}
                if dr_cr_values != {'D', 'C'}:
                    return Response({
                        'error': 'Invalid debit/credit pair',
                        'detail': 'Paired entries must include one debit (D) and one credit (C)'
                    }, status=status.HTTP_400_BAD_REQUEST)

                # Get Reference_No for master entry update
                reference_no = journal_entries.first().Reference_No

                # Update Auth_Status and comments for journal entries
                updated_counts = {
                    'journal_entries': 0,
                    'history_entries': 0,
                    'master_entry': 0
                }
                updated_counts['journal_entries'] = journal_entries.update(
                    Auth_Status='P',
                    Checker_DT_Stamp=timezone.now(),
                    Checker_Id=request.user,
                    comments=comments
                )

                # Update corresponding history entries
                history_entries = DETB_JRNL_LOG_HIST.objects.filter(
                    Reference_sub_No=reference_sub_no
                )
                updated_counts['history_entries'] = history_entries.update(
                    Auth_Status='P',
                    Checker_DT_Stamp=timezone.now(),
                    Checker_Id=request.user,
                    comments=comments
                )

                # Update master entry if it exists
                master_entry = DETB_JRNL_LOG_MASTER.objects.filter(
                    Reference_No=reference_no
                )
                if master_entry.exists():
                    updated_counts['master_entry'] = master_entry.update(
                        Auth_Status='P',
                        Checker_DT_Stamp=timezone.now(),
                        Checker_Id=request.user
                    )

                # Log rejection
                logger.info(f"Rejected journal batch - Reference_sub_No: {reference_sub_no}, "
                           f"Reference_No: {reference_no}, "
                           f"Comments: {comments}, "
                           f"Counts: {updated_counts}")

                return Response({
                    'message': 'Successfully rejected journal entries and set Auth_Status to P',
                    'reference_sub_no': reference_sub_no,
                    'reference_no': reference_no,
                    'comments': comments,
                    'updated_counts': updated_counts
                }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error rejecting journal entries for Reference_sub_No: {reference_sub_no}: {str(e)}")
            return Response({
                'error': 'Failed to reject journal entries',
                'detail': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        
    @action(detail=False, methods=['post'], url_path='fix-rejected')
    def fix_rejected(self, request):
        """Fix rejected journal entries for a Reference_sub_No by updating DETB_JRNL_LOG and inserting new DETB_JRNL_LOG_HIST entries"""
        reference_sub_no = request.data.get('Reference_sub_No')
        comments = request.data.get('comments')
        fcy_amount = request.data.get('Fcy_Amount')
        addl_text = request.data.get('Addl_text')
        addl_sub_text = request.data.get('Addl_sub_text')
        glsub_id = request.data.get('glsub_id')  # For debit entry
        relative_glsub_id = request.data.get('relative_glsub_id')  # For credit entry

        # Validate required fields
        if not reference_sub_no:
            return Response({
                'error': 'Missing required field',
                'detail': 'Reference_sub_No is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        if not comments:
            return Response({
                'error': 'Missing required field',
                'detail': 'Comments are required for fixing rejected entries'
            }, status=status.HTTP_400_BAD_REQUEST)

        if len(comments) > 1000:
            return Response({
                'error': 'Invalid comments',
                'detail': 'Comments must not exceed 1000 characters'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate Fcy_Amount if provided
        if fcy_amount is not None:
            try:
                fcy_amount = Decimal(str(fcy_amount))
                if fcy_amount < 0:
                    raise ValueError
            except (ValueError, TypeError):
                return Response({
                    'error': 'Invalid Fcy_Amount',
                    'detail': 'Fcy_Amount must be a valid non-negative decimal'
                }, status=status.HTTP_400_BAD_REQUEST)

        # Validate glsub_id and relative_glsub_id if provided
        glsub = None
        relative_glsub = None
        if glsub_id is not None or relative_glsub_id is not None:
            if not (glsub_id and relative_glsub_id):
                return Response({
                    'error': 'Missing account fields',
                    'detail': 'Both glsub_id and relative_glsub_id must be provided together'
                }, status=status.HTTP_400_BAD_REQUEST)
            try:
                glsub = MTTB_GLSub.objects.get(glsub_id=glsub_id)
                relative_glsub = MTTB_GLSub.objects.get(glsub_id=relative_glsub_id)
            except MTTB_GLSub.DoesNotExist:
                return Response({
                    'error': 'Invalid account IDs',
                    'detail': f'glsub_id {glsub_id} or relative_glsub_id {relative_glsub_id} not found'
                }, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                # Find journal entries matching the Reference_sub_No
                journal_entries = DETB_JRNL_LOG.objects.filter(
                    Reference_sub_No=reference_sub_no,
                    Auth_Status='P'
                )

                if not journal_entries.exists():
                    return Response({
                        'error': 'No matching rejected journal entries found',
                        'detail': f'No entries found for Reference_sub_No: {reference_sub_no} with Auth_Status P'
                    }, status=status.HTTP_404_NOT_FOUND)

                # Verify exactly two entries (debit and credit pair)
                if len(journal_entries) != 2:
                    return Response({
                        'error': 'Incomplete pair found',
                        'detail': 'Expected exactly two paired entries (debit and credit)'
                    }, status=status.HTTP_400_BAD_REQUEST)

                # Verify debit/credit pairing
                dr_cr_values = {entry.Dr_cr for entry in journal_entries}
                if dr_cr_values != {'D', 'C'}:
                    return Response({
                        'error': 'Invalid debit/credit pair',
                        'detail': 'Paired entries must include one debit (D) and one credit (C)'
                    }, status=status.HTTP_400_BAD_REQUEST)

                # Get Reference_No for master entry update
                reference_no = journal_entries.first().Reference_No

                # Prepare update fields for journal entries
                update_fields = {
                    'Auth_Status': 'U',
                    'Checker_DT_Stamp': timezone.now(),
                    'Checker_Id': request.user,
                    'comments': comments
                }
                if fcy_amount is not None:
                    update_fields['Fcy_Amount'] = fcy_amount
                    update_fields['Lcy_Amount'] = None  # Will be calculated per entry
                    update_fields['fcy_dr'] = None
                    update_fields['fcy_cr'] = None
                    update_fields['lcy_dr'] = None
                    update_fields['lcy_cr'] = None
                if addl_text is not None:
                    update_fields['Addl_text'] = addl_text[:255]
                if addl_sub_text is not None:
                    update_fields['Addl_sub_text'] = addl_sub_text[:255]
                if glsub_id is not None:
                    update_fields['Account'] = None  # ✅ FIXED: Use 'Account' not 'Account_id'
                    update_fields['Account_no'] = None
                    update_fields['Ac_relatives'] = None

                # Update journal entries and create history entries
                updated_counts = {
                    'journal_entries': 0,
                    'history_entries': 0,
                    'master_entry': 0
                }
                history_entries_created = []

                # Process debit and credit entries
                debit_entry = next(e for e in journal_entries if e.Dr_cr == 'D')
                credit_entry = next(e for e in journal_entries if e.Dr_cr == 'C')

                for entry, new_account, paired_account in [
                    (debit_entry, glsub, relative_glsub),
                    (credit_entry, relative_glsub, glsub)
                ]:
                    # Calculate amounts if Fcy_Amount is provided
                    if fcy_amount is not None:
                        exchange_rate = entry.Exch_rate
                        lcy_amount = fcy_amount * exchange_rate
                        update_fields.update({
                            'Lcy_Amount': lcy_amount,
                            'fcy_dr': fcy_amount if entry.Dr_cr == 'D' else Decimal('0.00'),
                            'fcy_cr': fcy_amount if entry.Dr_cr == 'C' else Decimal('0.00'),
                            'lcy_dr': lcy_amount if entry.Dr_cr == 'D' else Decimal('0.00'),
                            'lcy_cr': lcy_amount if entry.Dr_cr == 'C' else Decimal('0.00')
                        })

                    # Update account fields if provided
                    if new_account is not None:
                        update_fields.update({
                            'Account': new_account,  # ✅ FIXED: Use 'Account' not 'Account_id'
                            'Account_no': new_account.glsub_code,
                            'Ac_relatives': paired_account.glsub_id if paired_account else entry.Ac_relatives
                        })

                    # Update journal entry
                    for field, value in update_fields.items():
                        if value is not None:
                            setattr(entry, field, value)
                    entry.save()
                    updated_counts['journal_entries'] += 1

                    # Create new history entry
                    history_entry = DETB_JRNL_LOG_HIST.objects.create(
                        module_id_id=entry.module_id_id,
                        Reference_No=entry.Reference_No,
                        Reference_sub_No=entry.Reference_sub_No,
                        comments=comments,
                        Ccy_cd_id=entry.Ccy_cd_id,
                        Fcy_Amount=fcy_amount if fcy_amount is not None else entry.Fcy_Amount,
                        Lcy_Amount=update_fields.get('Lcy_Amount', entry.Lcy_Amount),
                        fcy_dr=update_fields.get('fcy_dr', entry.fcy_dr),
                        fcy_cr=update_fields.get('fcy_cr', entry.fcy_cr),
                        lcy_dr=update_fields.get('lcy_dr', entry.lcy_dr),
                        lcy_cr=update_fields.get('lcy_cr', entry.lcy_cr),
                        Dr_cr=entry.Dr_cr,
                        Ac_relatives=update_fields.get('Ac_relatives', entry.Ac_relatives),
                        Account=update_fields.get('Account', entry.Account),  # ✅ FIXED: Use 'Account' not 'Account_id'
                        Account_no=update_fields.get('Account_no', entry.Account_no),
                        Txn_code_id=entry.Txn_code_id,
                        Value_date=entry.Value_date,
                        Exch_rate=entry.Exch_rate,
                        fin_cycle_id=entry.fin_cycle_id,
                        Period_code_id=entry.Period_code_id,
                        Addl_text=addl_text[:255] if addl_text is not None else entry.Addl_text,
                        Addl_sub_text=addl_sub_text[:255] if addl_sub_text is not None else entry.Addl_sub_text,
                        Maker_Id=entry.Maker_Id,
                        Maker_DT_Stamp=entry.Maker_DT_Stamp,
                        Checker_Id=request.user,
                        Checker_DT_Stamp=timezone.now(),
                        Auth_Status='U'
                    )
                    history_entries_created.append(history_entry)
                    updated_counts['history_entries'] += 1

                # Update master entry
                master_entry = DETB_JRNL_LOG_MASTER.objects.filter(Reference_No=reference_no)
                if master_entry.exists():
                    # Recalculate total Fcy_Amount and Lcy_Amount for the Reference_No
                    all_entries = DETB_JRNL_LOG.objects.filter(Reference_No=reference_no)
                    total_fcy = sum(e.fcy_dr for e in all_entries)
                    total_lcy = sum(e.lcy_dr for e in all_entries)
                    updated_counts['master_entry'] = master_entry.update(
                        Auth_Status='U',
                        Checker_DT_Stamp=timezone.now(),
                        Checker_Id=request.user,
                        Fcy_Amount=total_fcy,
                        Lcy_Amount=total_lcy
                    )

                # Log the fix
                logger.info(f"Fixed rejected journal batch - Reference_sub_No: {reference_sub_no}, "
                        f"Reference_No: {reference_no}, "
                        f"Comments: {comments}, "
                        f"glsub_id: {glsub_id}, "
                        f"relative_glsub_id: {relative_glsub_id}, "
                        f"Counts: {updated_counts}")

                return Response({
                    'message': 'Successfully fixed rejected journal entries and set Auth_Status to U',
                    'reference_sub_no': reference_sub_no,
                    'reference_no': reference_no,
                    'comments': comments,
                    'glsub_id': glsub_id,
                    'relative_glsub_id': relative_glsub_id,
                    'updated_counts': updated_counts
                }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error fixing rejected journal entries for Reference_sub_No: {reference_sub_no}: {str(e)}")
            return Response({
                'error': 'Failed to fix rejected journal entries',
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

    @action(detail=False, methods=["post"], url_path="approve-asset")
    def approve_asset(self, request):
        reference_no = request.data.get("Ac_relatives")
        module_id = request.data.get("module_id", "AS")

        if not reference_no:
            return Response({"error": "Ac_relatives is required."}, status=status.HTTP_400_BAD_REQUEST)

        if module_id != "AS":
            return Response({"error": "Invalid module_id. This endpoint only supports module_id = 'AS'."},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            asset = FA_Asset_Lists.objects.get(
                asset_list_id=reference_no,
                asset_status__in=["UC", "AC"]  # Look for both UC and AC status
            )
        except FA_Asset_Lists.DoesNotExist:
            return Response(
                {"error": f"No asset found with Ac_relatives={reference_no} in status UC or AC"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Determine which field to update based on asset_status
        if asset.asset_status == "UC":
            # Check if already approved
            if asset.Auth_Status == "A" and asset.Auth_Status_ARC == "A":
                return Response(
                    {"error": f"Asset {reference_no} (UC) has already been approved."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Update Auth_Status for UC assets
            asset.Auth_Status = "A"
            message = f"Asset {reference_no} (UC) has been approved successfully."
            
        elif asset.asset_status == "AC":
            # Check if already approved
            if hasattr(asset, 'Auth_Status_ARC') and asset.Auth_Status_ARC == "A":
                return Response(
                    {"error": f"Asset {reference_no} (AC) has already been approved."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Update Auth_Status_ARC for AC assets
            asset.Auth_Status_ARC = "A"
            message = f"Asset {reference_no} (AC) has been approved successfully."

        # Set common fields
        asset.Checker_Id = request.user
        asset.Checker_DT_Stamp = timezone.now()
        asset.save()

        return Response({
            "success": True,
            "message": message,
            "asset_status": asset.asset_status,
            "updated_field": "Auth_Status" if asset.asset_status == "UC" else "Auth_Status_ARC"
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='approve-all')
    def approve_all(self, request):
        """Approve all records (MASTER, LOG, HIST) for a Reference_No and insert into daily log tables"""
        reference_no = request.data.get('Reference_No')
        
        if not reference_no:
            return Response({'error': 'Reference_No is required'}, 
                        status=status.HTTP_400_BAD_REQUEST)
        
        # Check if any LOG entries have status 'P' or 'R'
        log_entries = DETB_JRNL_LOG.objects.filter(Reference_No=reference_no)
        if not log_entries.exists():
            return Response({'error': 'No entries found for this reference number'}, 
                        status=status.HTTP_404_NOT_FOUND)
        
        # Check for problematic entries
        problematic_entries = log_entries.filter(Auth_Status__in=['P', 'R'])
        if problematic_entries.exists():
            return Response({'error': 'Cannot approve: entries with status P or R found'}, 
                        status=status.HTTP_400_BAD_REQUEST)
        
        # Check if already approved
        if log_entries.filter(Auth_Status='A').exists():
            return Response({'error': 'Entries are already approved'}, 
                        status=status.HTTP_400_BAD_REQUEST)
        
        try:
            from django.db import transaction
            from django.utils import timezone
            
            with transaction.atomic():
                # Update DETB_JRNL_LOG
                log_updated = log_entries.update(
                    Auth_Status='A',
                    Checker_Id=request.user,
                    Checker_DT_Stamp=timezone.now()
                )
                
                # Update DETB_JRNL_LOG_MASTER
                try:
                    from .models import DETB_JRNL_LOG_MASTER
                    master_record = DETB_JRNL_LOG_MASTER.objects.get(Reference_No=reference_no)
                    master_record.Auth_Status = 'A'
                    master_record.Checker_Id = request.user
                    master_record.Checker_DT_Stamp = timezone.now()
                    master_record.save()
                    master_updated = 1
                except DETB_JRNL_LOG_MASTER.DoesNotExist:
                    master_updated = 0
                
                # Update DETB_JRNL_LOG_HIST (if exists)
                hist_updated = 0
                try:
                    from .models import DETB_JRNL_LOG_HIST
                    hist_updated = DETB_JRNL_LOG_HIST.objects.filter(
                        Reference_No=reference_no
                    ).update(
                        Auth_Status='A',
                        Checker_Id=request.user,
                        Checker_DT_Stamp=timezone.now()
                    )
                except:
                    pass  # HIST table might not exist
                
                # After successful approval, insert into daily log tables
                daily_log_entries_created = 0
                daily_log_hist_entries_created = 0
                
                try:
                    from .models import ACTB_DAIRY_LOG, ACTB_DAIRY_LOG_HISTORY
                    current_time = timezone.now()
                    
                    # Get the updated approved entries from DETB_JRNL_LOG
                    approved_entries = DETB_JRNL_LOG.objects.filter(
                        Reference_No=reference_no,
                        Auth_Status='A'
                    ).order_by('JRNLLog_id')
                    
                    for idx, entry in enumerate(approved_entries):
                        # Get GL Master info through the relationship chain:
                        # entry.Account (MTTB_GLSub) -> entry.Account.gl_code (MTTB_GLMaster)
                        gl_master = None
                        gl_type = None
                        category = None
                        
                        try:
                            if entry.Account and entry.Account.gl_code:
                                gl_master = entry.Account.gl_code  # This is the MTTB_GLMaster instance
                                gl_type = gl_master.glType
                                category = gl_master.category
                                print(f"Found GLMaster: {gl_master.glid}, Type: {gl_type}, Category: {category}")
                        except Exception as gl_error:
                            print(f"GLMaster lookup error: {gl_error}")
                        
                        # Calculate amounts based on Dr_cr indicator
                        fcy_amount = entry.Fcy_Amount or 0
                        lcy_amount = entry.Lcy_Amount or 0
                        exchange_rate = entry.Exch_rate or 1
                        
                        fcy_dr = fcy_amount if entry.Dr_cr == 'D' else 0
                        fcy_cr = fcy_amount if entry.Dr_cr == 'C' else 0
                        lcy_dr = lcy_amount if entry.Dr_cr == 'D' else 0
                        lcy_cr = lcy_amount if entry.Dr_cr == 'C' else 0
                        
                        # Prepare additional sub text
                        addl_sub_text = f"Approved Entry - {entry.Dr_cr} - {entry.Account_no}"
                        
                        # Common data for both ACTB_DAIRY_LOG and ACTB_DAIRY_LOG_HISTORY tables
                        daily_log_data = {
                            'module': entry.module_id,  # ForeignKey to STTB_ModulesInfo
                            'trn_ref_no': entry,  # ForeignKey to DETB_JRNL_LOG entry
                            'trn_ref_sub_no': entry.Reference_sub_No,
                            'event_sr_no': idx + 1,
                            'event': 'JRNL',
                            'ac_no': entry.Account,  # ForeignKey to MTTB_GLSub
                            'ac_no_full': entry.Account_no,
                            'ac_relative': entry.Ac_relatives,
                            'ac_ccy': entry.Ccy_cd,  # ForeignKey to MTTB_Ccy_DEFN
                            'drcr_ind': entry.Dr_cr,
                            'trn_code': entry.Txn_code,  # ForeignKey to MTTB_TRN_Code
                            'fcy_amount': fcy_amount,
                            'exch_rate': exchange_rate,
                            'lcy_amount': lcy_amount,
                            'fcy_dr': fcy_dr,
                            'fcy_cr': fcy_cr,
                            'lcy_dr': lcy_dr,
                            'lcy_cr': lcy_cr,
                            'external_ref_no': entry.Reference_No[:30],
                            'addl_text': entry.Addl_text or '',
                            'addl_sub_text': addl_sub_text,
                            'trn_dt': entry.Value_date.date() if entry.Value_date else None,
                            'glid': gl_master,  # ForeignKey to MTTB_GLMaster
                            'glType': gl_type,  # CharField from GLMaster
                            'category': category,  # CharField from GLMaster
                            'value_dt': entry.Value_date.date() if entry.Value_date else None,
                            'financial_cycle': entry.fin_cycle,  # ForeignKey to MTTB_Fin_Cycle
                            'period_code': entry.Period_code,  # ForeignKey to MTTB_Per_Code
                            'user_id': request.user,  # ForeignKey to MTTB_Users
                            'Maker_DT_Stamp': current_time,
                            'auth_id': request.user,  # ForeignKey to MTTB_Users (approver)
                            'Checker_DT_Stamp': current_time,
                            'Auth_Status': 'A',  # Authorized
                            'product': 'GL',
                            'entry_seq_no': idx + 1,
                            'delete_stat': None
                        }
                        
                        # Create ACTB_DAIRY_LOG entry
                        daily_log_entry = ACTB_DAIRY_LOG.objects.create(**daily_log_data)
                        daily_log_entries_created += 1
                        
                        # Create ACTB_DAIRY_LOG_HISTORY entry  
                        daily_log_hist_entry = ACTB_DAIRY_LOG_HISTORY.objects.create(**daily_log_data)
                        daily_log_hist_entries_created += 1
                        
                except Exception as daily_log_error:
                    # Log the error but don't fail the entire approval process
                    print(f"Error creating daily log entries: {str(daily_log_error)}")
                    import traceback
                    traceback.print_exc()
            
            return Response({
                'message': f'Successfully approved {log_updated} LOG entries, {master_updated} MASTER record, {hist_updated} HIST records',
                'daily_log_created': daily_log_entries_created,
                'daily_log_hist_created': daily_log_hist_entries_created,
                'reference_no': reference_no
            })
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({'error': f'Error during approval: {str(e)}'}, 
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    @action(detail=False, methods=['post'], url_path='reject-all')  
    def reject_all(self, request):
        """Reject all records (MASTER, LOG, HIST) for a Reference_No"""
        reference_no = request.data.get('Reference_No')
        rejection_reason = request.data.get('rejection_reason')
        
        if not reference_no:
            return Response({'error': 'Reference_No is required'}, 
                        status=status.HTTP_400_BAD_REQUEST)
        
        if not rejection_reason:
            return Response({'error': 'rejection_reason is required'}, 
                        status=status.HTTP_400_BAD_REQUEST)
        
        # Check if entries exist
        log_entries = DETB_JRNL_LOG.objects.filter(Reference_No=reference_no)
        if not log_entries.exists():
            return Response({'error': 'No entries found for this reference number'}, 
                        status=status.HTTP_404_NOT_FOUND)
        
        try:
            from django.db import transaction
            
            with transaction.atomic():
                # Update DETB_JRNL_LOG
                log_updated = log_entries.update(
                    Auth_Status='R',
                    Checker_Id=request.user,
                    Checker_DT_Stamp=timezone.now(),
                    # comments=request.data.get('comments') + f'\nRejection: {rejection_reason}'
                )
                
                # Update DETB_JRNL_LOG_MASTER
                try:
                    from .models import DETB_JRNL_LOG_MASTER
                    master_record = DETB_JRNL_LOG_MASTER.objects.get(Reference_No=reference_no)
                    master_record.Auth_Status = 'R'
                    master_record.Checker_Id = request.user
                    master_record.Checker_DT_Stamp = timezone.now()
                    master_record.Addl_text = (master_record.Addl_text or '') + f'\nRejection: {rejection_reason}'
                    master_record.save()
                    master_updated = 1
                except DETB_JRNL_LOG_MASTER.DoesNotExist:
                    master_updated = 0
                
                # Update DETB_JRNL_LOG_HIST (if exists)
                hist_updated = 0
                try:
                    from .models import DETB_JRNL_LOG_HIST
                    hist_updated = DETB_JRNL_LOG_HIST.objects.filter(
                        Reference_No=reference_no
                    ).update(
                        Auth_Status='R',
                        Checker_Id=request.user,
                        Checker_DT_Stamp=timezone.now()
                    )
                except:
                    pass  # HIST table might not exist
            
            return Response({
                'message': f'Successfully rejected {log_updated} LOG entries, {master_updated} MASTER record, {hist_updated} HIST records',
                'reference_no': reference_no,
                'rejection_reason': rejection_reason
            })
            
        except Exception as e:
            return Response({'error': f'Error during rejection: {str(e)}'}, 
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # @action(detail=True, methods=['post'])
    # def authorize(self, request, pk=None):
    #     """Authorize a journal entry"""
    #     journal_entry = self.get_object()
        
    #     if journal_entry.Auth_Status == 'A':
    #         return Response({'error': 'Entry is already authorized'}, 
    #                       status=status.HTTP_400_BAD_REQUEST)
        
    #     journal_entry.Auth_Status = 'A'
    #     journal_entry.Checker_Id = request.user
    #     journal_entry.Checker_DT_Stamp = timezone.now()
    #     journal_entry.save()
        
    #     serializer = self.get_serializer(journal_entry)
    #     return Response({
    #         'message': 'Entry authorized successfully',
    #         'entry': serializer.data
    #     })

    # @action(detail=False, methods=['post'])
    # def authorize_batch(self, request):
    #     """Authorize multiple journal entries by reference number"""
    #     reference_no = request.data.get('reference_no')
        
    #     if not reference_no:
    #         return Response({'error': 'reference_no is required'}, 
    #                       status=status.HTTP_400_BAD_REQUEST)
        
    #     entries = DETB_JRNL_LOG.objects.filter(
    #         Reference_No=reference_no,
    #     )
        
    #     if not entries.exists():
    #         return Response({'error': 'No unauthorized entries found for this reference number'}, 
    #                       status=status.HTTP_404_NOT_FOUND)
        
    #     # Check if balanced before authorization
    #     balance_info = self.balance_check(request)
    #     if not balance_info.data.get('overall_balanced'):
    #         return Response({'error': 'Cannot authorize unbalanced entries'}, 
    #                       status=status.HTTP_400_BAD_REQUEST)
        
    #     updated_count = entries.update(
    #         Auth_Status='A',
    #         Checker_Id=request.user,
    #         Checker_DT_Stamp=timezone.now()
    #     )
        
    #     return Response({
    #         'message': f'Successfully authorized {updated_count} entries',
    #         'reference_no': reference_no
    #     })
    @action(detail=False, methods=['post'])
    def reject_batch(self, request):
        """Reject multiple journal entries by reference number"""
        reference_no = request.data.get('reference_no')
        rejection_reason = request.data.get('rejection_reason')
        
        if not reference_no:
            return Response({'error': 'reference_no is required'}, 
                        status=status.HTTP_400_BAD_REQUEST)
        
        if not rejection_reason:
            return Response({'error': 'rejection_reason is required'}, 
                        status=status.HTTP_400_BAD_REQUEST)
        
        entries = DETB_JRNL_LOG.objects.filter(
            Reference_No=reference_no,
            Auth_Status='U'  # Only reject unauthorized entries
        )
        
        if not entries.exists():
            return Response({'error': 'No unauthorized entries found for this reference number'}, 
                        status=status.HTTP_404_NOT_FOUND)
        
        # Update entries with rejection status and reason
        updated_count = entries.update(
            Auth_Status='R',
            Checker_Id=request.user,
            Checker_DT_Stamp=timezone.now(),
            # You might want to add rejection reason to a specific field
            # or append it to existing additional text
            comments=('Addl_text') + '\nRejection Reason: ' + rejection_reason
        )
        
        # Also update the master record if it exists
        try:
            master_record = DETB_JRNL_LOG_MASTER.objects.get(Reference_No=reference_no)
            master_record.Auth_Status = 'R'
            master_record.Checker_Id = request.user
            master_record.Checker_DT_Stamp = timezone.now()
            master_record.Addl_text = (master_record.Addl_text or '') + f'\nRejection Reason: {rejection_reason}'
            master_record.save()
        except DETB_JRNL_LOG_MASTER.DoesNotExist:
            pass  # Master record doesn't exist, which is okay
        
        return Response({
            'message': f'Successfully rejected {updated_count} entries',
            'reference_no': reference_no,
            'rejection_reason': rejection_reason
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
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q
from .models import DETB_JRNL_LOG_MASTER
from .serializers import DETB_JRNL_LOG_MASTER_Serializer


class DETB_JRNL_LOG_MASTER_ViewSet(viewsets.ModelViewSet):
    queryset = DETB_JRNL_LOG_MASTER.objects.all()
    serializer_class = DETB_JRNL_LOG_MASTER_Serializer
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['Ccy_cd', 'Txn_code', 'fin_cycle', 'Auth_Status','Reference_No']  # Removed 'delete_stat' from filter
    search_fields = ['Reference_No', 'Addl_text']
    ordering_fields = ['Maker_DT_Stamp', 'Value_date']
    

    # def get_queryset(self):
    #     return DETB_JRNL_LOG_MASTER.objects.filter(delete_stat__isnull=True).exclude(delete_stat='D')
    def get_queryset(self):
        """
        Filter queryset based on show_all parameter (from frontend canAuthorize permission)
        - If show_all='true' (canAuthorize=1): Show all records (except deleted)
        - If show_all='false' (canAuthorize=0): Show only records created by current user
        """
        user = self.request.user
        
        # Base queryset - exclude deleted records
        base_queryset = DETB_JRNL_LOG_MASTER.objects.filter(
            Q(delete_stat__isnull=True) | ~Q(delete_stat='D')
        )
        
        # Get show_all parameter from request
        show_all = self.request.query_params.get('show_all', 'false').lower()
        
        # Apply permission-based filtering
        if show_all == 'true':
            # User has canAuthorize permission - show all records
            return base_queryset
        else:
            # User doesn't have canAuthorize permission - show only their own records
            return base_queryset.filter(Maker_Id=user)

    def list(self, request, *args, **kwargs):
        """
        Override list to add debugging information (optional)
        """
        queryset = self.filter_queryset(self.get_queryset())
        
        # Apply date range filters if provided
        date_from = request.query_params.get('Value_date__gte')
        date_to = request.query_params.get('Value_date__lte')
        
        if date_from:
            queryset = queryset.filter(Value_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(Value_date__lte=date_to)
        
        # Get page from pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    

    def retrieve(self, request, *args, **kwargs):
        """
        Override retrieve method to check if user can view specific record
        """
        instance = self.get_object()
        user = request.user
        
        try:
            user_auth_detail = self.get_user_auth_detail(user, request)
            
            print(f"DEBUG RETRIEVE: User {getattr(user, 'user_name', 'unknown')} requesting record {instance.pk}")
            print(f"DEBUG RETRIEVE: Record Maker_Id: {instance.Maker_Id}")
            print(f"DEBUG RETRIEVE: User Auth_Detail: {user_auth_detail}")
            
            # If user doesn't have Auth_Detail permission, check if they own the record
            if user_auth_detail != 1 and instance.Maker_Id != user:
                print(f"DEBUG RETRIEVE: Access denied - user doesn't own record and no auth permission")
                return Response(
                    {"detail": "You don't have permission to view this record."},
                    status=status.HTTP_403_FORBIDDEN
                )
                
        except Exception as e:
            print(f"ERROR in retrieve permission check: {e}")
            # If error checking permissions, check ownership
            if instance.Maker_Id != user:
                return Response(
                    {"detail": "You don't have permission to view this record."},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        return super().retrieve(request, *args, **kwargs)



    def perform_update(self, serializer):
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
    

    @action(detail=False, methods=['get'], url_path='journal-log-active')
    def journal_log_active(self, request):
        """
        Get all active (not deleted) journal log master records, optionally filtered by Reference_No.
        """
        reference_no = request.query_params.get('Reference_No')
        auth_status = request.query_params.get('Auth_Status')
        
        queryset = DETB_JRNL_LOG_MASTER.objects.filter(
            delete_stat__isnull=True
        ).exclude(delete_stat='D')

        if reference_no:
            queryset = queryset.filter(Reference_No=reference_no)
        if auth_status:
            queryset = queryset.filter(Auth_Status=auth_status)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    

    @action(detail=False, methods=['patch'], url_path='approve-by-reference')
    def approve_by_reference(self, request):
        reference_no = request.data.get('Reference_No')
        if not reference_no:
            return Response({'detail': 'Reference_No is required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        try:
            master_record = self.queryset.get(Reference_No=reference_no)
            
            # Update master record
            master_record.Auth_Status = 'A'
            master_record.Checker_Id = request.data.get('Checker_Id')
            master_record.Checker_DT_Stamp = request.data.get('Checker_DT_Stamp')
            master_record.save()
            
            # Update all related detail records (this will be handled by perform_update)
            serializer = self.get_serializer(master_record)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except DETB_JRNL_LOG_MASTER.DoesNotExist:
            return Response({'detail': 'Master record not found'}, 
                          status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['patch'], url_path='reject-by-reference')
    def reject_by_reference(self, request):
        reference_no = request.data.get('Reference_No')
        if not reference_no:
            return Response({'detail': 'Reference_No is required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        try:
            master_record = self.queryset.get(Reference_No=reference_no)
            
            # Update master record
            master_record.Auth_Status = 'R'
            master_record.Checker_Id = request.data.get('Checker_Id')
            master_record.Checker_DT_Stamp = request.data.get('Checker_DT_Stamp')
            if request.data.get('Addl_text'):
                master_record.Addl_text = request.data.get('Addl_text')
            master_record.save()
            
            serializer = self.get_serializer(master_record)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except DETB_JRNL_LOG_MASTER.DoesNotExist:
            return Response({'detail': 'Master record not found'}, 
                          status=status.HTTP_404_NOT_FOUND)
    
    
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from datetime import datetime
from django.utils.timezone import make_aware
from .models import STTB_Dates, MTTB_LCL_Holiday


@api_view(['GET'])  # or ['GET'] if you want it triggered without payload
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

#---------Asset-------------
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from .models import (FA_Asset_Type,FA_Chart_Of_Asset,FA_Suppliers,FA_Location,FA_Expense_Category,FA_Asset_Lists,FA_Depreciation_Main,FA_Depreciation_Sub,
                     FA_Asset_List_Depreciation,FA_Asset_List_Disposal,FA_Asset_Expense,FA_Transfer_Logs,FA_Asset_Photos,FA_Maintenance_Logs,
                     FA_Accounting_Method)
from .serializers import (FAAssetTypeSerializer,FAChartOfAssetSerializer,FASuppliersSerializer,FALocationSerializer,FAExpenseCategorySerializer,
    FAAssetListSerializer,FADepreciationMainSerializer,FADepreciationSubSerializer,FAAssetListDepreciationSerializer,FAAssetListDisposalSerializer,
    FAAssetExpenseSerializer,FATransferLogsSerializer,FAAssetPhotosSerializer,FAMaintenanceLogsSerializer,FAAccountingMethodSerializer)
from django.utils import timezone

class FAAssetTypeViewSet(viewsets.ModelViewSet):
    serializer_class = FAAssetTypeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = FA_Asset_Type.objects.all().order_by('type_id')
        type_code = self.request.query_params.get('type_code')
        if type_code:
            queryset = queryset.filter(type_code=type_code)
        return queryset
    
    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(
            Maker_Id=user,
            Maker_DT_Stamp=timezone.now()
        )

    def perform_update(self, serializer):
        user = self.request.user
        serializer.save(
            Checker_Id=user,
            Checker_DT_Stamp=timezone.now()
        )
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def set_open(self, request, pk=None):
        """Set Record_Status = 'O' """
        obj = self.get_object()
        user_obj = MTTB_Users.objects.get(user_id=request.user.user_id)  
        if obj.Record_Status == 'O':
            return Response({'detail': 'Already open.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        
        obj.Record_Status = 'O'
        obj.Checker_Id = user_obj
        obj.Checker_DT_Stamp = timezone.now()
        obj.save()
        serializer = self.get_serializer(obj)
        return Response({'message': 'Set to Open.', 'entry': serializer.data})

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def set_close(self, request, pk=None):
        """Set Record_Status = 'C' (Close)"""
        obj = self.get_object()
        user_obj = MTTB_Users.objects.get(user_id=request.user.user_id)
        if obj.Record_Status == 'C':
            return Response({'detail': 'Already closed.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        obj.Record_Status = 'C'
        obj.Checker_Id = user_obj
        obj.Checker_DT_Stamp = timezone.now()
        obj.save()
        serializer = self.get_serializer(obj)
        return Response({'message': 'Set to Close.', 'entry': serializer.data})

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def set_tangible(self, request, pk=None):
        """Allow updating only the is_tangible field"""
        obj = self.get_object()
        new_status = request.data.get('is_tangible')

        if not new_status:
            return Response({'detail': 'is_tangible is required.'}, status=status.HTTP_400_BAD_REQUEST)

        obj.is_tangible = new_status
        obj.Checker_Id = request.user
        obj.Checker_DT_Stamp = timezone.now()
        obj.save()

        serializer = self.get_serializer(obj)
        return Response({
            'message': f'Status updated to "{new_status}".',
            'entry': serializer.data
        })

class FAChartOfAssetViewSet(viewsets.ModelViewSet):
    serializer_class = FAChartOfAssetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        
        queryset = FA_Chart_Of_Asset.objects.all().order_by('coa_id')
        asset_code = self.request.query_params.get('asset_code')
        asset_type_id = self.request.query_params.get('asset_type_id')
        is_tangible = self.request.query_params.get('is_tangible')
        if asset_type_id:
            queryset = queryset.filter(asset_type_id=asset_type_id)
        if asset_code:
            queryset = queryset.filter(asset_code=asset_code)
        if is_tangible:
            queryset = queryset.filter(is_tangible=is_tangible)
        return queryset
    
    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(
            Maker_Id=user,
            Maker_DT_Stamp=timezone.now()
        )

    def perform_update(self, serializer):
        user = self.request.user
        serializer.save(
            Checker_Id=user,
            Checker_DT_Stamp=timezone.now()
        )
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def set_open(self, request, pk=None):
        """Set Record_Status = 'O'"""
        obj = self.get_object()
        user_obj = MTTB_Users.objects.get(user_id=request.user.user_id)  
        if obj.Record_Status == 'O':
            return Response({'detail': 'Already open.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        
        obj.Record_Status = 'O'
        obj.Checker_Id = user_obj
        obj.Checker_DT_Stamp = timezone.now()
        obj.save()
        serializer = self.get_serializer(obj)
        return Response({'message': 'Set to Open.', 'entry': serializer.data})

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def set_close(self, request, pk=None):
        """Set Record_Status = 'C' (Close)"""
        obj = self.get_object()
        user_obj = MTTB_Users.objects.get(user_id=request.user.user_id)
        if obj.Record_Status == 'C':
            return Response({'detail': 'Already closed.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        obj.Record_Status = 'C'
        obj.Checker_Id = user_obj
        obj.Checker_DT_Stamp = timezone.now()
        obj.save()
        serializer = self.get_serializer(obj)
        return Response({'message': 'Set to Close.', 'entry': serializer.data})

class FASuppliersViewSet(viewsets.ModelViewSet):
    serializer_class = FASuppliersSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = FA_Suppliers.objects.all().order_by('supplier_id')
        supplier_code = self.request.query_params.get('supplier_code')
        if supplier_code:
            queryset = queryset.filter(supplier_code=supplier_code)
        return queryset
    
    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(
            Maker_Id=user,
            Maker_DT_Stamp=timezone.now()
        )

    def perform_update(self, serializer):
        user = self.request.user
        serializer.save(
            Checker_Id=user,
            Checker_DT_Stamp=timezone.now()
        )
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def set_open(self, request, pk=None):
        """Set Record_Status = 'O'"""
        obj = self.get_object()
        user_obj = MTTB_Users.objects.get(user_id=request.user.user_id)  
        if obj.Record_Status == 'O':
            return Response({'detail': 'Already open.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        
        obj.Record_Status = 'O'
        obj.Checker_Id = user_obj
        obj.Checker_DT_Stamp = timezone.now()
        obj.save()
        serializer = self.get_serializer(obj)
        return Response({'message': 'Set to Open.', 'entry': serializer.data})

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def set_close(self, request, pk=None):
        """Set Record_Status = 'C' (Close)"""
        obj = self.get_object()
        user_obj = MTTB_Users.objects.get(user_id=request.user.user_id)
        if obj.Record_Status == 'C':
            return Response({'detail': 'Already closed.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        obj.Record_Status = 'C'
        obj.Checker_Id = user_obj
        obj.Checker_DT_Stamp = timezone.now()
        obj.save()
        serializer = self.get_serializer(obj)
        return Response({'message': 'Set to Close.', 'entry': serializer.data})

class FALocationViewSet(viewsets.ModelViewSet):
    serializer_class = FALocationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = FA_Location.objects.all().order_by('location_id')
        location_code = self.request.query_params.get('location_code')
        if location_code:
            queryset = queryset.filter(location_code=location_code)
        return queryset
    
    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(
            Maker_Id=user,
            Maker_DT_Stamp=timezone.now()
        )

    def perform_update(self, serializer):
        user = self.request.user
        serializer.save(
            Checker_Id=user,
            Checker_DT_Stamp=timezone.now()
        )
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def set_open(self, request, pk=None):
        """Set Record_Status = 'O'"""
        obj = self.get_object()
        user_obj = MTTB_Users.objects.get(user_id=request.user.user_id)  
        if obj.Record_Status == 'O':
            return Response({'detail': 'Already open.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        
        obj.Record_Status = 'O'
        obj.Checker_Id = user_obj
        obj.Checker_DT_Stamp = timezone.now()
        obj.save()
        serializer = self.get_serializer(obj)
        return Response({'message': 'Set to Open.', 'entry': serializer.data})

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def set_close(self, request, pk=None):
        """Set Record_Status = 'C' (Close)"""
        obj = self.get_object()
        user_obj = MTTB_Users.objects.get(user_id=request.user.user_id)
        if obj.Record_Status == 'C':
            return Response({'detail': 'Already closed.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        obj.Record_Status = 'C'
        obj.Checker_Id = user_obj
        obj.Checker_DT_Stamp = timezone.now()
        obj.save()
        serializer = self.get_serializer(obj)
        return Response({'message': 'Set to Close.', 'entry': serializer.data})

class FAExpenseCategoryViewSet(viewsets.ModelViewSet):
    serializer_class = FAExpenseCategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = FA_Expense_Category.objects.all().order_by('ec_id')
        category_code = self.request.query_params.get('category_code')
        if category_code:
            queryset = queryset.filter(category_code=category_code)
        return queryset
    
    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(
            Maker_Id=user,
            Maker_DT_Stamp=timezone.now()
        )

    def perform_update(self, serializer):
        user = self.request.user
        serializer.save(
            Checker_Id=user,
            Checker_DT_Stamp=timezone.now()
        )
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def set_open(self, request, pk=None):
        """Set Record_Status = 'O'"""
        obj = self.get_object()
        user_obj = MTTB_Users.objects.get(user_id=request.user.user_id)  
        if obj.Record_Status == 'O':
            return Response({'detail': 'Already open.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        
        obj.Record_Status = 'O'
        obj.Checker_Id = user_obj
        obj.Checker_DT_Stamp = timezone.now()
        obj.save()
        serializer = self.get_serializer(obj)
        return Response({'message': 'Set to Open.', 'entry': serializer.data})

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def set_close(self, request, pk=None):
        """Set Record_Status = 'C' (Close)"""
        obj = self.get_object()
        user_obj = MTTB_Users.objects.get(user_id=request.user.user_id)
        if obj.Record_Status == 'C':
            return Response({'detail': 'Already closed.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        obj.Record_Status = 'C'
        obj.Checker_Id = user_obj
        obj.Checker_DT_Stamp = timezone.now()
        obj.save()
        serializer = self.get_serializer(obj)
        return Response({'message': 'Set to Close.', 'entry': serializer.data})

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def set_y_approve(self, request, pk=None):
        """Set required_approval = 'Y' (Close)"""
        obj = self.get_object()
        user_obj = MTTB_Users.objects.get(user_id=request.user.user_id)
        if obj.required_approval == 'Y':
            return Response({'detail': 'Already closed.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        obj.required_approval = 'Y'
        obj.Checker_Id = user_obj
        obj.Checker_DT_Stamp = timezone.now()
        obj.save()
        serializer = self.get_serializer(obj)
        return Response({'message': 'Set to Close.', 'entry': serializer.data})
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def set_n_approve(self, request, pk=None):
        """Set required_approval = 'N' (Close)"""
        obj = self.get_object()
        user_obj = MTTB_Users.objects.get(user_id=request.user.user_id)
        if obj.required_approval == 'N':
            return Response({'detail': 'Already closed.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        obj.required_approval = 'N'
        obj.Checker_Id = user_obj
        obj.Checker_DT_Stamp = timezone.now()
        obj.save()
        serializer = self.get_serializer(obj)
        return Response({'message': 'Set to Close.', 'entry': serializer.data})

class FAAssetListViewSet(viewsets.ModelViewSet):
    serializer_class = FAAssetListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = FA_Asset_Lists.objects.all().order_by('asset_list_id')
        asset_type_id = self.request.query_params.get('asset_type_id')
        if asset_type_id:
            queryset = queryset.filter(asset_type_id=asset_type_id)
        return queryset
    
    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(
            Maker_Id=user,
            Maker_DT_Stamp=timezone.now(),
            asset_ac_by=user,
            asset_ac_datetime=timezone.now()
        )

    def perform_update(self, serializer):
        user = self.request.user
        serializer.save(
            Checker_Id=user,
            Checker_DT_Stamp=timezone.now()
        )

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def set_open(self, request, pk=None):
        """Set Record_Status = 'O'"""
        obj = self.get_object()
        user_obj = MTTB_Users.objects.get(user_id=request.user.user_id)  
        if obj.Record_Status == 'O':
            return Response({'detail': 'Already open.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        
        obj.Record_Status = 'O'
        obj.Checker_Id = user_obj
        obj.Checker_DT_Stamp = timezone.now()
        obj.save()
        serializer = self.get_serializer(obj)
        return Response({'message': 'Set to Open.', 'entry': serializer.data})

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def set_close(self, request, pk=None):
        """Set Record_Status = 'C' (Close)"""
        obj = self.get_object()
        user_obj = MTTB_Users.objects.get(user_id=request.user.user_id)
        if obj.Record_Status == 'C':
            return Response({'detail': 'Already closed.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        obj.Record_Status = 'C'
        obj.Checker_Id = user_obj
        obj.Checker_DT_Stamp = timezone.now()
        obj.save()
        serializer = self.get_serializer(obj)
        return Response({'message': 'Set to Close.', 'entry': serializer.data})
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def authorize(self, request, pk=None):
        """ອະນຸມັດ"""
        obj = self.get_object()
        user_obj = MTTB_Users.objects.get(user_id=request.user.user_id)

        if obj.Auth_Status == 'A':
            return Response({
                'error': 'Record ຖືກອະນຸມັດແລ້ວ'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Set Auth_Status = 'A', Once_Auth = 'Y', record_stat = 'C'
        obj.Auth_Status = 'A'
        obj.record_stat = 'C'
        obj.Checker_Id_id = user_obj
        obj.Checker_DT_Stamp = timezone.now()
        obj.save()

        serializer = self.get_serializer(obj)
        return Response({
            'message': 'ອະນຸມັດ ສໍາເລັດແລ້ວ',
            'data': serializer.data
        })

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def unauthorize(self, request, pk=None):
        """ຍົກເລີກການອະນຸມັດ """
        obj = self.get_object()
        user_obj = MTTB_Users.objects.get(user_id=request.user.user_id)

        if obj.Auth_Status == 'U':
            return Response({
                'error': 'Record ຍັງບໍ່ໄດ້ຮັບການອະນຸມັດ'
            }, status=status.HTTP_400_BAD_REQUEST)

        obj.Auth_Status = 'U'
        obj.Record_Status = 'C'
        obj.Checker_Id_id = user_obj
        obj.Checker_DT_Stamp = timezone.now()
        obj.save()

        serializer = self.get_serializer(obj)
        return Response({
            'message': 'ຍົກເລີກການອະນຸມັດສໍາເລັດແລ້ວ',
            'data': serializer.data
        })
    
class FADepreciationMainViewSet(viewsets.ModelViewSet):
    serializer_class = FADepreciationMainSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = FA_Depreciation_Main.objects.all().order_by('dm_id')
        dpca_type = self.request.query_params.get('dpca_type')
        if dpca_type:
            queryset = queryset.filter(dpca_type=dpca_type)
        return queryset
    
    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(
            Maker_Id=user,
            Maker_DT_Stamp=timezone.now()
        )

    def perform_update(self, serializer):
        user = self.request.user
        serializer.save(
            Checker_Id=user,
            Checker_DT_Stamp=timezone.now()
        )
    

class FADepreciationSubViewSet(viewsets.ModelViewSet):
    serializer_class = FADepreciationSubSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = FA_Depreciation_Sub.objects.all().order_by('ds_id')
        m_id = self.request.query_params.get('m_id')
        if m_id:
            queryset = queryset.filter(m_id=m_id)
        return queryset
    
    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(
            Maker_Id=user,
            Maker_DT_Stamp=timezone.now()
        )

    def perform_update(self, serializer):
        user = self.request.user
        serializer.save(
            Checker_Id=user,
            Checker_DT_Stamp=timezone.now()
        )
    

class FAAssetListDepreciationViewSet(viewsets.ModelViewSet):
    serializer_class = FAAssetListDepreciationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = FA_Asset_List_Depreciation.objects.all().order_by('ald_id')
        asset_list_id = self.request.query_params.get('asset_list_id')
        if asset_list_id:
            queryset = queryset.filter(asset_list_id=asset_list_id)
        return queryset
    
    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(
            Maker_Id=user,
            Maker_DT_Stamp=timezone.now()
        )

    def perform_update(self, serializer):
        user = self.request.user
        serializer.save(
            Checker_Id=user,
            Checker_DT_Stamp=timezone.now()
        )
    
class FAAssetListDisposalViewSet(viewsets.ModelViewSet):
    serializer_class = FAAssetListDisposalSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = FA_Asset_List_Disposal.objects.all().order_by('alds_id')
        asset_list_id = self.request.query_params.get('asset_list_id')
        if asset_list_id:
            queryset = queryset.filter(asset_list_id=asset_list_id)
        return queryset
    
    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(
            Maker_Id=user,
            Maker_DT_Stamp=timezone.now()
        )

    def perform_update(self, serializer):
        user = self.request.user
        serializer.save(
            Checker_Id=user,
            Checker_DT_Stamp=timezone.now()
        )

class FAAssetExpenseViewSet(viewsets.ModelViewSet):
    serializer_class = FAAssetExpenseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = FA_Asset_Expense.objects.all().order_by('ae_id')
        asset_list_id = self.request.query_params.get('asset_list_id')
        if asset_list_id:
            queryset = queryset.filter(asset_list_id=asset_list_id)
        return queryset
    
    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(
            Maker_Id=user,
            Maker_DT_Stamp=timezone.now()
        )

    def perform_update(self, serializer):
        user = self.request.user
        serializer.save(
            Checker_Id=user,
            Checker_DT_Stamp=timezone.now()
        )

class FATransferLogsViewSet(viewsets.ModelViewSet):
    serializer_class = FATransferLogsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = FA_Transfer_Logs.objects.all().order_by('transfer_id')
        asset_list_id = self.request.query_params.get('asset_list_id')
        if asset_list_id:
            queryset = queryset.filter(asset_list_id=asset_list_id)
        return queryset
    
    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(
            Maker_Id=user,
            Maker_DT_Stamp=timezone.now()
        )

    def perform_update(self, serializer):
        user = self.request.user
        serializer.save(
            Checker_Id=user,
            Checker_DT_Stamp=timezone.now()
        )

class FAAssetPhotosViewSet(viewsets.ModelViewSet):
    serializer_class = FAAssetPhotosSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = FA_Asset_Photos.objects.all().order_by('ap_id')
        asset_list_id = self.request.query_params.get('asset_list_id')
        if asset_list_id:
            queryset = queryset.filter(asset_list_id=asset_list_id)
        return queryset
    
    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(
            Maker_Id=user,
            Maker_DT_Stamp=timezone.now()
        )

    def perform_update(self, serializer):
        user = self.request.user
        serializer.save(
            Checker_Id=user,
            Checker_DT_Stamp=timezone.now()
        )

class FAMaintenanceLogsViewSet(viewsets.ModelViewSet):
    serializer_class = FAMaintenanceLogsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = FA_Maintenance_Logs.objects.all().order_by('maintenance_id')
        asset_list_id = self.request.query_params.get('asset_list_id')
        if asset_list_id:
            queryset = queryset.filter(asset_list_id=asset_list_id)
        return queryset
    
    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(
            Maker_Id=user,
            Maker_DT_Stamp=timezone.now()
        )

    def perform_update(self, serializer):
        user = self.request.user
        serializer.save(
            Checker_Id=user,
            Checker_DT_Stamp=timezone.now()
        )

class FAAccountingMethodViewSet(viewsets.ModelViewSet):
    serializer_class = FAAccountingMethodSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = FA_Accounting_Method.objects.all().order_by('mapping_id')
        acc_type = self.request.query_params.get('acc_type')
        if acc_type:
            queryset = queryset.filter(acc_type=acc_type)
        return queryset
    
    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(
            Maker_Id=user,
            Maker_DT_Stamp=timezone.now()
        )

    def perform_update(self, serializer):
        user = self.request.user
        serializer.save(
            Checker_Id=user,
            Checker_DT_Stamp=timezone.now()
        )
    
#----------------end of Asset-----------------

# Function Get User Login Session

# ---------------------------------------------------------------------------------------------------


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from django.utils import timezone
from django.db import transaction
from .models import MTTB_USER_ACCESS_LOG, MTTB_Users
from datetime import datetime

# @api_view(["POST"])
# @permission_classes([IsAuthenticated])
# def force_logout_user(request):
#     """
#     Force logout a user by their user_id.
#     Only admins should be able to use this endpoint.
    
#     POST /api/force-logout/
#     Body: { "user_id": "<user_id_to_logout>" }
#     """
#     # Optional: Check if the requesting user has admin privileges
#     # if not request.user.Role_ID or request.user.Role_ID.role_name != 'Admin':
#     #     return Response(
#     #         {"error": "Permission denied. Admin access required."},
#     #         status=status.HTTP_403_FORBIDDEN
#     #     )
    
#     target_user_id = request.data.get("user_id")
#     if not target_user_id:
#         return Response(
#             {"error": "user_id is required"},
#             status=status.HTTP_400_BAD_REQUEST
#         )
    
#     # Check if the target user exists
#     try:
#         target_user = MTTB_Users.objects.get(user_id=target_user_id)
#     except MTTB_Users.DoesNotExist:
#         return Response(
#             {"error": f"User with id {target_user_id} not found"},
#             status=status.HTTP_404_NOT_FOUND
#         )
    
#     # Prevent users from force logging out themselves
#     if request.user.user_id == target_user_id:
#         return Response(
#             {"error": "Cannot force logout yourself. Use normal logout instead."},
#             status=status.HTTP_400_BAD_REQUEST
#         )
    
#     with transaction.atomic():
#         # 1. Find all active sessions for this user
#         active_sessions = MTTB_USER_ACCESS_LOG.objects.filter(
#             user_id=target_user,
#             logout_datetime__isnull=True,
#             login_status='S'  # Only successful logins
#         )
        
#         session_count = active_sessions.count()
        
#         # 2. Blacklist all outstanding tokens for this user
#         blacklisted_count = 0
#         try:
#             # Get all outstanding tokens for this user
#             outstanding_tokens = OutstandingToken.objects.filter(
#                 user__user_id=target_user_id
#             )
            
#             for token in outstanding_tokens:
#                 # Check if already blacklisted
#                 if not BlacklistedToken.objects.filter(token=token).exists():
#                     BlacklistedToken.objects.create(token=token)
#                     blacklisted_count += 1
                    
#         except Exception as e:
#             # If blacklisting fails, still continue with logging out sessions
#             print(f"Error blacklisting tokens: {str(e)}")
        
#         # 3. Update all active sessions to mark them as force logged out
#         current_time = timezone.now()
#         active_sessions.update(
#             logout_datetime=current_time,
#             logout_type='F',  # F = Force logout
#             remarks=f'Force logged out by {request.user.user_id}'
#         )
        
#         # 4. Optional: Create a new log entry for the force logout action
#         MTTB_USER_ACCESS_LOG.objects.create(
#             user_id=request.user,
#             session_id=None,
#             ip_address=get_client_ip(request),
#             user_agent=request.META.get('HTTP_USER_AGENT'),
#             login_status='A',  # A = Admin action
#             remarks=f'Force logged out user {target_user_id}'
#         )
    
#     return Response({
#         "message": f"Successfully force logged out user {target_user_id}",
#         "sessions_terminated": session_count,
#         "tokens_blacklisted": blacklisted_count
#     }, status=status.HTTP_200_OK)

# views.py - Add these views to your existing views

from rest_framework.decorators import api_view, permission_classes
from django.db.models import OuterRef, Subquery, Max
from datetime import timedelta
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.decorators import action
from django.utils import timezone
from django.db import transaction
from django.db.models import Q
from .models import MTTB_USER_ACCESS_LOG, MTTB_Users, MTTB_REVOKED_SESSIONS
from .serializers import UserAccessLogSerializer
from SAMCSYS.authentication import get_jti_from_request
import logging

logger = logging.getLogger(__name__)


# Helper function
def get_client_ip(request):
    """Extract client IP from request"""
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    if xff:
        return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '')


# Custom permission class for admin-only endpoints
class IsAdminUser(BasePermission):
    """
    Custom permission to only allow admin users.
    """
    message = "Only administrators can perform this action."
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        print(f"User: {request.user}")
        print(f"Has role attr: {hasattr(request.user, 'role')}")
        if hasattr(request.user, 'role'):
            print(f"Role: {request.user.role}")
            print(f"Role ID: {getattr(request.user.role, 'role_id', 'NOT_FOUND')}")
        
        # Your permission logic here...
        
        return False
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def session_check(request):
    # Optional: verify against revoked session table
    jti = get_jti_from_request(request)
    if MTTB_REVOKED_SESSIONS.objects.filter(jti=jti).exists():
        return Response({"error": "Session revoked"}, status=status.HTTP_401_UNAUTHORIZED)

    return Response({"success": True}, status=status.HTTP_200_OK)


# @api_view(["POST"])
# @permission_classes([IsAuthenticated])
# def force_logout_user(request):
#     """
#     Force logout a user by their user_id.
#     Revokes all their active sessions and tokens.
    
#     POST /api/force-logout/
#     Body: { "user_id": "<user_id_to_logout>" }
#     """
#     target_user_id = request.data.get("user_id")
    
#     # Validation
#     if not target_user_id:
#         return Response(
#             {"error": "user_id is required"},
#             status=status.HTTP_400_BAD_REQUEST
#         )
    
#     # Check if the target user exists
#     try:
#         target_user = MTTB_Users.objects.get(user_id=target_user_id)
#     except MTTB_Users.DoesNotExist:
#         return Response(
#             {"error": f"User with id {target_user_id} not found"},
#             status=status.HTTP_404_NOT_FOUND
#         )
    
#     # Prevent users from force logging out themselves
#     if request.user.user_id == target_user_id:
#         return Response(
#             {"error": "Cannot force logout yourself. Use normal logout instead."},
#             status=status.HTTP_400_BAD_REQUEST
#         )
    
#     with transaction.atomic():
#         # Find all active sessions for this user
#         active_sessions = MTTB_USER_ACCESS_LOG.objects.filter(
#             user_id=target_user,
#             logout_datetime__isnull=True,
#             login_status='S'  # Only successful logins
#         )
        
#         session_count = active_sessions.count()
#         revoked_count = 0
        
#         # Revoke all active sessions
#         for session in active_sessions:
#             if session.session_id:  # session_id contains the JTI
#                 try:
#                     # Create revoked session entry
#                     MTTB_REVOKED_SESSIONS.objects.get_or_create(
#                         jti=session.session_id,
#                         defaults={
#                             'user_id': target_user,
#                             'revoked_by': request.user,
#                             'reason': f'Force logged out by {request.user.user_name}',
#                             'ip_address': get_client_ip(request)
#                         }
#                     )
#                     revoked_count += 1
#                 except Exception as e:
#                     logger.error(f"Error revoking session {session.session_id}: {str(e)}")
        
#         # Update all active sessions to mark them as force logged out
#         current_time = timezone.now()
#         active_sessions.update(
#             logout_datetime=current_time,
#             logout_type='F',  # F = Force logout
#             remarks=f'Force logged out by {request.user.user_name} ({request.user.user_id})'
#         )
        
#         # Log the admin action
#         MTTB_USER_ACCESS_LOG.objects.create(
#             user_id=request.user,
#             session_id=get_jti_from_request(request),
#             ip_address=get_client_ip(request),
#             user_agent=request.META.get('HTTP_USER_AGENT', '')[:255],
#             login_status='A',  # A = Admin action
#             remarks=f'Force logged out user {target_user.user_name} ({target_user_id})'
#         )
    
#     logger.info(f"Admin {request.user.user_id} force logged out user {target_user_id}")
    
#     return Response({
#         "success": True,
#         "message": f"Successfully force logged out user {target_user_id}",
#         "details": {
#             "user_id": target_user_id,
#             "user_name": target_user.user_name,
#             "sessions_terminated": session_count,
#             "tokens_revoked": revoked_count
#         }
#     }, status=status.HTTP_200_OK)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def force_logout_user(request, user_id=None):
    allowed_roles = ['SYS', 'SYA']
    user_role_id = getattr(getattr(request.user, 'Role_ID', None), 'role_id', None)

    if user_role_id not in allowed_roles:
        return Response({
            "success": False,
            "message": "You do not have permission to perform this action."
        }, status=status.HTTP_403_FORBIDDEN)

    target_user_id = user_id or request.data.get("user_id")
    if not target_user_id:
        return Response({"error": "user_id is required"}, status=status.HTTP_400_BAD_REQUEST)

    if request.user.user_id == target_user_id:
        return Response({"error": "Cannot force logout yourself. Please use normal logout."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        target_user = MTTB_Users.objects.get(user_id=target_user_id)
    except MTTB_Users.DoesNotExist:
        return Response({"error": f"User with id {target_user_id} not found"}, status=status.HTTP_404_NOT_FOUND)

    with transaction.atomic():
        latest_session = MTTB_USER_ACCESS_LOG.objects.filter(
            user_id=target_user,
            logout_datetime__isnull=True,
            login_status='S'
        ).order_by('-login_datetime').first()

        if not latest_session:
            return Response({
                "success": False,
                "message": "No active session found for this user."
            }, status=status.HTTP_404_NOT_FOUND)

        same_session_logs = MTTB_USER_ACCESS_LOG.objects.filter(
            session_id=latest_session.session_id,
            logout_datetime__isnull=True,
            login_status='S'
        )

        forced_users = []
        revoked_count = 0
        current_time = timezone.now()

        for log in same_session_logs:
            uid = log.user_id.user_id if log.user_id else "??"
            forced_users.append(f"({uid})")

            if log.session_id:
                try:
                    MTTB_REVOKED_SESSIONS.objects.get_or_create(
                        jti=log.session_id,
                        defaults={
                            'user_id': log.user_id,
                            'revoked_by': request.user,
                            'reason': f'Force logged out by {request.user.user_name}',
                            'ip_address': get_client_ip(request)
                        }
                    )
                    revoked_count += 1
                except Exception as e:
                    logger.error(f"Error revoking session {log.session_id}: {str(e)}")

            # update remark of user who  force logout
            log.logout_datetime = current_time
            log.logout_type = 'F'
            log.remarks = f"Force logged out by {request.user.user_name} ({request.user.user_id})"
            log.save()

        # update remark in log latest admin (who force logout)
        admin_log = MTTB_USER_ACCESS_LOG.objects.filter(
            user_id=request.user,
            logout_datetime__isnull=True,
            login_status='S'
        ).order_by('-login_datetime').first()

        if admin_log:
            existing_remark = admin_log.remarks or ''

            prefix_all = "Force logout all user"
            prefix_forced = "Force logged out user "

            part_all = ""
            part_forced = ""

            # แยกข้อความ existing_remark
            if existing_remark.startswith(prefix_all):
                if ',' in existing_remark:
                    parts = existing_remark.split(',', 1)
                    part_all = parts[0].strip()
                    part_forced = parts[1].strip()
                else:
                    part_all = existing_remark.strip()
                    part_forced = ""
            else:
                part_forced = existing_remark.strip()

            # แยก user เก่าใน part_forced
            old_users = []
            if part_forced.startswith(prefix_forced):
                old_users_str = part_forced[len(prefix_forced):].strip()
                old_users = [u.strip() for u in old_users_str.split(',') if u.strip()]
            elif part_forced:
                # in case hvae old message is keep it
                pass

            # list user old + new
            combined_users_set = set(old_users)
            combined_users_set.update(forced_users)
            combined_users = sorted(combined_users_set)

            combined_forced_part = prefix_forced + ", ".join(combined_users)

            if part_all:
                combined_remark = f"{part_all}, {combined_forced_part}"
            else:
                combined_remark = combined_forced_part

            # update when have change
            if combined_remark != existing_remark:
                admin_log.remarks = combined_remark
                admin_log.save()
        else:
            logger.warning("No active admin log found to update remarks for force logout action.")

    logger.info(f"Admin {request.user.user_id} force logged out users: {', '.join(forced_users)}")

    return Response({
        "success": True,
        "message": f"Successfully force logged out session {latest_session.log_id}",
        "log_ids": [log.log_id for log in same_session_logs],
        "forced_users": forced_users,
        "admin_remark": admin_log.remarks if admin_log else None,
        "tokens_revoked": revoked_count
    }, status=status.HTTP_200_OK)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def force_logout_user_test(request, user_id):
    """
    Force logout a user by their user_id from the URL.
    Revokes all their active sessions and tokens.

    POST /api/force-logout/<user_id>/
    """
    # Check if the target user exists
    try:
        target_user = MTTB_Users.objects.get(user_id=user_id)
    except MTTB_Users.DoesNotExist:
        return Response(
            {"error": f"User with id {user_id} not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    # Prevent users from force logging out themselves
    if request.user.user_id == user_id:
        return Response(
            {"error": "Cannot force logout yourself. Use normal logout instead."},
            status=status.HTTP_400_BAD_REQUEST
        )

    with transaction.atomic():
        # Find all active sessions for this user
        active_sessions = MTTB_USER_ACCESS_LOG.objects.filter(
            user_id=target_user,
            logout_datetime__isnull=True,
            login_status='S'  # Only successful logins
        )

        session_count = active_sessions.count()
        revoked_count = 0

        # Revoke all active sessions
        for session in active_sessions:
            if session.session_id:  # session_id contains the JTI
                try:
                    MTTB_REVOKED_SESSIONS.objects.get_or_create(
                        jti=session.session_id,
                        defaults={
                            'user_id': target_user,
                            'revoked_by': request.user,
                            'reason': f'Force logged out by {request.user.user_name}',
                            'ip_address': get_client_ip(request)
                        }
                    )
                    revoked_count += 1
                except Exception as e:
                    logger.error(f"Error revoking session {session.session_id}: {str(e)}")

        # Update all active sessions to mark them as force logged out
        current_time = timezone.now()
        active_sessions.update(
            logout_datetime=current_time,
            logout_type='F',
            remarks=f'Force logged out by {request.user.user_name} ({request.user.user_id})'
        )

        # Log the admin action
        MTTB_USER_ACCESS_LOG.objects.create(
            user_id=request.user,
            session_id=get_jti_from_request(request),
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:255],
            login_status='A',
            remarks=f'Force logged out user {target_user.user_name} ({user_id})'
        )

    logger.info(f"Admin {request.user.user_id} force logged out user {user_id}")

    return Response({
        "success": True,
        "message": f"Successfully force logged out user {user_id}",
        "details": {
            "user_id": user_id,
            "user_name": target_user.user_name,
            "sessions_terminated": session_count,
            "tokens_revoked": revoked_count
        }
    }, status=status.HTTP_200_OK)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_active_sessions(request):
    user = request.user

    allowed_roles = ['SYS', 'SYA']
    user_role_id = None
    if hasattr(user, 'Role_ID') and user.Role_ID:
        user_role_id = getattr(user.Role_ID, 'role_id', None)

    if user_role_id not in allowed_roles:
        return Response({
            "success": False,
            "message": "You do not have permission to access this API."
        }, status=status.HTTP_403_FORBIDDEN)

    # user info add on response
    own_user_info = {
        "own_user_id": getattr(user, 'user_id', None),
        "own_user_name": getattr(user, 'user_name', None),
        "own_role_id": user_role_id,
    }

    SESSION_TIMEOUT_MINUTES = 30
    time_limit = timezone.now() - timedelta(minutes=SESSION_TIMEOUT_MINUTES)

    latest_log_id_subquery = MTTB_USER_ACCESS_LOG.objects.filter(
        user_id=OuterRef('user_id')
    ).order_by('-login_datetime').values('log_id')[:1]

    latest_logs = MTTB_USER_ACCESS_LOG.objects.filter(
        log_id__in=Subquery(latest_log_id_subquery),
        login_status='S',
        logout_datetime__isnull=True,
        login_datetime__gte=time_limit
    ).select_related('user_id').order_by('-login_datetime')

    active_user_ids = list(
        latest_logs.values_list('user_id__user_id', flat=True).distinct()
    )

    sessions_data = []
    for session in latest_logs:
        session_info = {
            'log_id': session.log_id,
            'user_id': session.user_id.user_id if session.user_id else None,
            'user_name': session.user_id.user_name if session.user_id else None,
            'login_datetime': session.login_datetime,
            'session_duration': str(timezone.now() - session.login_datetime) if session.login_datetime else None,
            'ip_address': session.ip_address,
        }
        sessions_data.append(session_info)

    return Response({
        "success": True,
        **own_user_info,  # show user_id / user_name / role_id is own
        "active_sessions": sessions_data,
        "total_count": len(sessions_data),
        "total_active_users_all": len(active_user_ids),
        "active_user_ids": active_user_ids,
        "current_time": timezone.now()
    }, status=status.HTTP_200_OK)



# @api_view(["GET"])
# @permission_classes([IsAuthenticated])
# def get_active_sessions(request):
#     """
#     Get all active sessions (users currently logged in).
#     Regular users can only see their own sessions.
#     Admins can see all sessions.
    
#     GET /api/active-sessions/
#     Optional query params:
#     - user_id: Filter by specific user (admin only)
#     - include_details: Include detailed session info
#     """
#     # Check if user is admin
#     is_admin = IsAdminUser().has_permission(request, None)
    
#     # Base query for active sessions
#     query = MTTB_USER_ACCESS_LOG.objects.filter(
#         logout_datetime__isnull=True,
#         login_status='S'
#     ).select_related('user_id')
    
#     # Non-admins can only see their own sessions
#     if not is_admin:
#         query = query.filter(user_id=request.user)
#     else:
#         # Admins can filter by user_id if provided
#         filter_user_id = request.query_params.get('user_id')
#         if filter_user_id:
#             query = query.filter(user_id__user_id=filter_user_id)
    
#     # Order by login time (most recent first)
#     query = query.order_by('-login_datetime')
    
#     # Prepare response data
#     sessions_data = []
#     for session in query:
#         session_info = {
#             'log_id': session.log_id,
#             'user_id': session.user_id.user_id if session.user_id else None,
#             'user_name': session.user_id.user_name if session.user_id else None,
#             'login_datetime': session.login_datetime,
#             'session_duration': str(timezone.now() - session.login_datetime) if session.login_datetime else None,
#             'ip_address': session.ip_address,
#         }
        
#         # Include additional details if requested
#         if request.query_params.get('include_details') == 'true':
#             session_info.update({
#                 'user_agent': session.user_agent,
#                 'session_id': session.session_id[:10] + '...' if session.session_id else None,  # Partial JTI for security
#                 'user_email': session.user_id.user_email if session.user_id else None,
#                 'user_status': session.user_id.User_Status if session.user_id else None,
#             })
        
#         sessions_data.append(session_info)
    
#     return Response({
#         "success": True,
#         "active_sessions": sessions_data,
#         "total_count": len(sessions_data),
#         "is_admin_view": is_admin,
#         "current_time": timezone.now()
#     }, status=status.HTTP_200_OK)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def force_logout_all_users(request):
    allowed_roles = ['SYS', 'SYA']
    user = request.user
    user_role_id = getattr(getattr(user, 'Role_ID', None), 'role_id', None)

    if user_role_id not in allowed_roles:
        return Response({
            "success": False,
            "message": "You do not have permission to perform this action."
        }, status=status.HTTP_403_FORBIDDEN)

    with transaction.atomic():
        now = timezone.now()

        # log latest of admin
        admin_log = MTTB_USER_ACCESS_LOG.objects.filter(
            user_id=user,
            logout_datetime__isnull=True,
            login_status='S'
        ).order_by('-login_datetime').first()

        # log lest of other user (ยกเว้น admin)
        latest_logs = {}
        sessions = MTTB_USER_ACCESS_LOG.objects.filter(
            logout_datetime__isnull=True,
            login_status='S'
        ).exclude(user_id=user).order_by('user_id', '-login_datetime')

        for log in sessions:
            if log.user_id_id not in latest_logs:
                latest_logs[log.user_id_id] = log

        forced_users = []

        for log in latest_logs.values():
            # Revoke token
            if log.session_id:
                MTTB_REVOKED_SESSIONS.objects.get_or_create(
                    jti=log.session_id,
                    defaults={
                        'user_id': log.user_id,
                        'revoked_by': user,
                        'reason': f'Force logged out by {user.user_name}',
                        'ip_address': get_client_ip(request)
                    }
                )

            # update logout
            log.logout_datetime = now
            log.logout_type = 'F'
            log.remarks = (log.remarks or '') + f' Force logged out by {user.user_name} ({user.user_id})'
            log.save()

            forced_users.append(f"{log.user_id.user_name} ({log.user_id.user_id})")

        # update remark of admin session
        if admin_log:
            old_remark = admin_log.remarks or ''
            if 'Force logout all user' not in old_remark:
                if old_remark.strip():
                    admin_log.remarks = f'Force logout all user, {old_remark}'
                else:
                    admin_log.remarks = 'Force logout all user'
                admin_log.save()

    return Response({
        "success": True,
        "message": "All users have been forcefully logged out.",
        "forced_user_count": len(forced_users),
        "forced_users": forced_users
    }, status=status.HTTP_200_OK)


# @api_view(["POST"])
# @permission_classes([IsAuthenticated])
# def force_logout_all_users(request):
#     """
#     Force logout all users except the requesting admin.
#     Requires explicit confirmation.
    
#     POST /api/force-logout-all/
#     Body: { "confirm": true, "reason": "optional reason" }
#     """
#     # Require explicit confirmation
#     if not request.data.get("confirm"):
#         return Response(
#             {"error": "Confirmation required. Set 'confirm': true in request body."},
#             status=status.HTTP_400_BAD_REQUEST
#         )
    
#     reason = request.data.get("reason", "Mass force logout by administrator")
    
#     # Get current user's JTI to exclude it
#     current_jti = get_jti_from_request(request)
    
#     with transaction.atomic():
#         # Get all active sessions except current user's
#         active_sessions = MTTB_USER_ACCESS_LOG.objects.filter(
#             logout_datetime__isnull=True,
#             login_status='S'
#         ).exclude(
#             Q(user_id=request.user) | Q(session_id=current_jti)
#         ).select_related('user_id')
        
#         session_count = active_sessions.count()
#         revoked_count = 0
#         affected_users = set()
        
#         # Revoke all sessions
#         for session in active_sessions:
#             if session.session_id:
#                 try:
#                     MTTB_REVOKED_SESSIONS.objects.get_or_create(
#                         jti=session.session_id,
#                         defaults={
#                             'user_id': session.user_id,
#                             'revoked_by': request.user,
#                             'reason': reason,
#                             'ip_address': get_client_ip(request)
#                         }
#                     )
#                     revoked_count += 1
#                     if session.user_id:
#                         affected_users.add(session.user_id.user_name)
#                 except Exception as e:
#                     logger.error(f"Error revoking session in mass logout: {str(e)}")
        
#         # Mark all sessions as logged out
#         current_time = timezone.now()
#         active_sessions.update(
#             logout_datetime=current_time,
#             logout_type='F',
#             remarks=f'{reason} by {request.user.user_name}'
#         )
        
#         # Log the mass logout action
#         MTTB_USER_ACCESS_LOG.objects.create(
#             user_id=request.user,
#             session_id=current_jti,
#             ip_address=get_client_ip(request),
#             user_agent=request.META.get('HTTP_USER_AGENT', '')[:255],
#             login_status='A',
#             remarks=f'Performed mass force logout: {reason}'
#         )
    
#     logger.warning(f"Admin {request.user.user_id} performed mass force logout. Affected {len(affected_users)} users.")
    
#     return Response({
#         "success": True,
#         "message": "Successfully force logged out all users",
#         "details": {
#             "sessions_terminated": session_count,
#             "tokens_revoked": revoked_count,
#             "users_affected": len(affected_users),
#             "reason": reason
#         }
#     }, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def verify_token(request):
    """
    Simple endpoint to verify if a token is still valid.
    Used by frontend to check authentication status.
    
    GET /api/verify-token/
    """
    return Response({
        "valid": True,
        "user_id": request.user.user_id,
        "user_name": request.user.user_name,
        "jti": get_jti_from_request(request),
        "timestamp": timezone.now()
    }, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsAdminUser])
def get_revoked_sessions(request):
    """
    Get list of revoked sessions (admin only).
    Useful for audit purposes.
    
    GET /api/revoked-sessions/
    Query params:
    - user_id: Filter by specific user
    - days: Number of days to look back (default: 7)
    """
    days = int(request.query_params.get('days', 7))
    cutoff_date = timezone.now() - timezone.timedelta(days=days)
    
    query = MTTB_REVOKED_SESSIONS.objects.filter(
        revoked_at__gte=cutoff_date
    ).select_related('user_id', 'revoked_by')
    
    # Filter by user if specified
    user_id_filter = request.query_params.get('user_id')
    if user_id_filter:
        query = query.filter(user_id__user_id=user_id_filter)
    
    revoked_sessions = []
    for session in query.order_by('-revoked_at')[:100]:  # Limit to 100 most recent
        revoked_sessions.append({
            'id': session.id,
            'user_id': session.user_id.user_id if session.user_id else None,
            'user_name': session.user_id.user_name if session.user_id else None,
            'revoked_at': session.revoked_at,
            'revoked_by': session.revoked_by.user_name if session.revoked_by else 'System',
            'reason': session.reason,
            'ip_address': session.ip_address
        })
    
    return Response({
        "success": True,
        "revoked_sessions": revoked_sessions,
        "total_count": len(revoked_sessions),
        "date_range": {
            "from": cutoff_date,
            "to": timezone.now()
        }
    }, status=status.HTTP_200_OK)


from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import MTTB_EOC_MAINTAIN
from .serializers import EOCMaintainSerializer

class EOCMaintainViewSet(viewsets.ModelViewSet):
    """
    ViewSet ສໍາລັບການຈັດການ EOC Maintain
    ປະກອບດ້ວຍ CRUD operations ແລະ custom actions
    """
    queryset = MTTB_EOC_MAINTAIN.objects.all()
    serializer_class = EOCMaintainSerializer
    permission_classes = [IsAuthenticated]
    
    # Filtering and searching
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['eoc_type', 'Record_Status', 'Auth_Status', 'Once_Auth', 'module_id', 'function_id']
    search_fields = ['eoc_type', 'module_id__module_name', 'function_id__function_name']
    ordering_fields = ['eoc_id', 'eoc_seq_no', 'Maker_DT_Stamp', 'Checker_DT_Stamp']
    ordering = ['-eoc_id']

    def get_queryset(self):
        """Custom queryset with optimized joins"""
        return MTTB_EOC_MAINTAIN.objects.select_related(
            'module_id', 'function_id', 'Maker_Id', 'Checker_Id'
        ).all()

    def perform_create(self, serializer):
        """ກໍານົດຄ່າເມື່ອສ້າງ record ໃໝ່"""
        user = self.request.user
        user_id = getattr(user, 'user_id', None)
        
        serializer.save(
            Maker_Id_id=user_id,  # Use _id for foreign key
            Maker_DT_Stamp=timezone.now(),
            Record_Status='C',  # Default to closed
            Auth_Status='U',  # Default to unauthorized
            Once_Auth='N'     # Default to not authorized once
        )

    def perform_update(self, serializer):
        """ກໍານົດຄ່າເມື່ອອັບເດດ record"""
        user = self.request.user
        user_id = getattr(user, 'user_id', None)
        
        serializer.save(
            Checker_Id_id=user_id,
            Checker_DT_Stamp=timezone.now()
        )

    def create(self, request, *args, **kwargs):
        """Override create to add custom response"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        headers = self.get_success_headers(serializer.data)
        return Response({
            'message': 'ສ້າງ EOC Maintain ສໍາເລັດແລ້ວ',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        """Override update to add custom response"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        # Check if record can be updated
        if instance.Auth_Status == 'A' and instance.Record_Status == 'C':
            return Response({
                'error': 'ບໍ່ສາມາດແກ້ໄຂ record ທີ່ຖືກອະນຸມັດແລ້ວ'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response({
            'message': 'ອັບເດດ EOC Maintain ສໍາເລັດແລ້ວ',
            'data': serializer.data
        })

    def destroy(self, request, *args, **kwargs):
        """Override destroy to add validation"""
        instance = self.get_object()
        
        # Check if record can be deleted
        if instance.Auth_Status == 'A':
            return Response({
                'error': 'ບໍ່ສາມາດລຶບ record ທີ່ຖືກອະນຸມັດແລ້ວ'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        self.perform_destroy(instance)
        return Response({
            'message': 'ລຶບ EOC Maintain ສໍາເລັດແລ້ວ'
        }, status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def set_open(self, request, pk=None):
        """ເປີດ record (record_stat = 'O')"""
        obj = self.get_object()
        
        if obj.Record_Status == 'O':
            return Response({
                'detail': 'Record ເປີດຢູ່ແລ້ວ'
            }, status=status.HTTP_406_NOT_ACCEPTABLE)
        
        if obj.Auth_Status != 'A':
            return Response({
                'detail': 'ບໍ່ສາມາດເປີດໄດ້. ສາມາດເປີດໄດ້ເລີມີ record ທີ່ຖືກອະນຸມັດແລ້ວເທົ່ານັ້ນ (Auth_Status = "A")'
            }, status=status.HTTP_400_BAD_REQUEST)

        obj.Record_Status = 'O'
        obj.Checker_Id_id = getattr(request.user, 'user_id', None)
        obj.Checker_DT_Stamp = timezone.now()
        obj.save()
        
        serializer = self.get_serializer(obj)
        return Response({
            'message': 'ເປີດ record ສໍາເລັດແລ້ວ',
            'data': serializer.data
        })

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def set_close(self, request, pk=None):
        """ປິດ record (record_stat = 'C')"""
        obj = self.get_object()

        if obj.Record_Status == 'C':
            return Response({
                'detail': 'Record ປິດຢູ່ແລ້ວ'
            }, status=status.HTTP_406_NOT_ACCEPTABLE)

        obj.Record_Status = 'C'
        obj.Checker_Id_id = getattr(request.user, 'user_id', None)
        obj.Checker_DT_Stamp = timezone.now()
        obj.save()
        
        serializer = self.get_serializer(obj)
        return Response({
            'message': 'ປິດ record ສໍາເລັດແລ້ວ',
            'data': serializer.data
        })

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def authorize(self, request, pk=None):
        """ອະນຸມັດ EOC Maintain"""
        eoc_entry = self.get_object()

        if eoc_entry.Auth_Status == 'A':
            return Response({
                'error': 'Record ຖືກອະນຸມັດແລ້ວ'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Set Auth_Status = 'A', Once_Auth = 'Y', record_stat = 'C'
        eoc_entry.Auth_Status = 'A'
        eoc_entry.Once_Auth = 'Y'
        eoc_entry.record_stat = 'C'
        eoc_entry.Checker_Id_id = getattr(request.user, 'user_id', None)
        eoc_entry.Checker_DT_Stamp = timezone.now()
        eoc_entry.save()

        serializer = self.get_serializer(eoc_entry)
        return Response({
            'message': 'ອະນຸມັດ EOC Maintain ສໍາເລັດແລ້ວ',
            'data': serializer.data
        })

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def unauthorize(self, request, pk=None):
        """ຍົກເລີກການອະນຸມັດ EOC Maintain"""
        eoc_entry = self.get_object()

        if eoc_entry.Auth_Status == 'U':
            return Response({
                'error': 'Record ຍັງບໍ່ໄດ້ຮັບການອະນຸມັດ'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Set Auth_Status = 'U', record_stat = 'C'
        eoc_entry.Auth_Status = 'U'
        eoc_entry.Record_Status = 'C'
        eoc_entry.Checker_Id_id = getattr(request.user, 'user_id', None)
        eoc_entry.Checker_DT_Stamp = timezone.now()
        eoc_entry.save()

        serializer = self.get_serializer(eoc_entry)
        return Response({
            'message': 'ຍົກເລີກການອະນຸມັດ EOC Maintain ສໍາເລັດແລ້ວ',
            'data': serializer.data
        })
    
# from rest_framework import viewsets, permissions
# from rest_framework.permissions import AllowAny, IsAuthenticated
# from django_filters.rest_framework import DjangoFilterBackend
# from .models import MasterType, MasterCode
# from .serializers import MasterTypeSerializer, MasterCodeSerializer

# class MasterTypeViewSet(viewsets.ModelViewSet):
#     queryset = MasterType.objects.all()
#     serializer_class = MasterTypeSerializer
#     filter_backends = [DjangoFilterBackend]
#     filterset_fields = ['M_code', 'M_name_la', 'M_name_en', 'Status']

#     def get_permissions(self):
#         # Allow unauthenticated POST, require auth otherwise
#         if self.request.method == 'POST':
#             return [AllowAny()]
#         return [IsAuthenticated()]

# class MasterCodeViewSet(viewsets.ModelViewSet):
#     queryset = MasterCode.objects.all()
#     serializer_class = MasterCodeSerializer
#     filter_backends = [DjangoFilterBackend]
#     filterset_fields = ['MC_code', 'MC_name_la', 'MC_name_en', 'Status', 'BOL_code', 'BOL_name', 'M_id']

#     def get_permissions(self):
#         # Allow unauthenticated POST, require auth otherwise
#         if self.request.method == 'POST':
#             return [AllowAny()]
#         return [IsAuthenticated()]
    
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import MasterType, MasterCode
from .serializers import MasterTypeSerializer, MasterCodeSerializer

class MasterTypeViewSet(viewsets.ModelViewSet):
    queryset = MasterType.objects.all()
    serializer_class = MasterTypeSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['M_code', 'M_name_la', 'M_name_en', 'Status']
    lookup_field = 'M_id'  # Use M_id for standard CRUD operations

    def get_permissions(self):
        if self.request.method == 'POST':
            return [AllowAny()]
        return [IsAuthenticated()]

    @action(detail=False, methods=['get'], url_path='tree/(?P<m_code>[^/.]+)')
    def get_tree(self, request, m_code=None):
        """
        Retrieve MasterType with related MasterCode entries in a tree structure.
        :param m_code: M_code of the MasterType
        """
        try:
            master_type = MasterType.objects.get(M_code=m_code)  # Fetch by M_code
            master_codes = MasterCode.objects.filter(M_id=master_type)

            # Serialize MasterType
            type_serializer = MasterTypeSerializer(master_type)
            
            # Serialize related MasterCodes
            code_serializer = MasterCodeSerializer(master_codes, many=True)

            # Construct tree response
            tree_data = {
                'MasterType': type_serializer.data,
                'MasterCodes': code_serializer.data
            }

            return Response(tree_data)
        except MasterType.DoesNotExist:
            return Response({'error': 'MasterType not found'}, status=404)

class MasterCodeViewSet(viewsets.ModelViewSet):
    queryset = MasterCode.objects.all()
    serializer_class = MasterCodeSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['MC_code', 'MC_name_la', 'MC_name_en', 'Status', 'BOL_code', 'BOL_name', 'M_id']
    lookup_field = 'MC_code' 

    def get_permissions(self):
        if self.request.method == 'POST':
            return [AllowAny()]
        return [IsAuthenticated()]
    
# sone perm code.............................................................................



# from rest_framework import viewsets, status
# from rest_framework.decorators import action
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.request import Request
# from django.db import transaction
# from django.utils import timezone
# from django.test import RequestFactory
# import json

# class YourProcessViewSet(viewsets.ModelViewSet):

#     @action(detail=False, methods=['post'])
#     def process_journal_data(self, request):
#         try:
#             data = request.data
#             glsub_ids = []
#             glsub_map = {}  

            
#             ccy_cd = data.get('Ccy_cd')
#             try:
#                 ccy_record = MTTB_Ccy_DEFN.objects.get(ccy_code=ccy_cd)
#                 alt_ccy_code = ccy_record.ALT_Ccy_Code
#             except MTTB_Ccy_DEFN.DoesNotExist:
#                 return Response({
#                     'success': False,
#                     'message': f'ບໍ່ພົບ currency code: {ccy_cd} ໃນ MTTB_Ccy_DEFN'
#                 }, status=status.HTTP_400_BAD_REQUEST)

#             with transaction.atomic():
#                 for entry in data.get('entries', []):
#                     account_no = entry.get('Account_no')
#                     addl_sub_text = entry.get('Addl_sub_text')

#                     gl_code_part = account_no.split('.')[0] if '.' in account_no else account_no

#                     try:
#                         gl_master = MTTB_GLMaster.objects.get(gl_code=gl_code_part)
#                         gl_code_obj = gl_master  
#                     except MTTB_GLMaster.DoesNotExist:
#                         return Response({
#                             'success': False,
#                             'message': f'ບໍ່ພົບ gl_code: {gl_code_part} ໃນ MTTB_GLMaster'
#                         }, status=status.HTTP_400_BAD_REQUEST)

                    
#                     if entry.get("Dr_cr") == "D":
#                         current_time = timezone.now()
                        
                        
#                         try:
#                             maker_user = MTTB_Users.objects.get(user_id=request.user.user_id)
#                         except MTTB_Users.DoesNotExist:
#                             return Response({
#                                 'success': False,
#                                 'message': f'ບໍ່ພົບຜູ້ໃຊ້: {request.user.user_id}'
#                             }, status=status.HTTP_400_BAD_REQUEST)
                        
#                         glsub_record = MTTB_GLSub.objects.create(
#                             glsub_code=account_no,
#                             glsub_Desc_la=addl_sub_text,
#                             gl_code=gl_code_obj, 
#                             Maker_DT_Stamp=current_time,
#                             Checker_DT_Stamp=current_time,
#                             Maker_Id=maker_user,  
#                             Checker_Id=maker_user, 
#                             Record_Status="O",
#                             Auth_Status="A"
#                         )
#                         glsub_id = glsub_record.glsub_id
#                     else:
                       
#                         try:
#                             glsub = MTTB_GLSub.objects.get(glsub_code=account_no)
#                             glsub_id = glsub.glsub_id
#                         except MTTB_GLSub.DoesNotExist:
#                             return Response({
#                                 'success': False,
#                                 'message': f'ບໍ່ພົບ GLSub ສໍາລັບ Account_no: {account_no}'
#                             }, status=status.HTTP_400_BAD_REQUEST)

#                     glsub_ids.append(glsub_id)
#                     glsub_map[account_no] = glsub_id

#                 processed_data = {
#                     "Reference_No": data.get('Reference_No'),
#                     "Ccy_cd": data.get('Ccy_cd'),
#                     "Txn_code": data.get('Txn_code'),
#                     "Value_date": data.get('Value_date'),
#                     "Addl_text": data.get('Addl_text'),
#                     "fin_cycle": data.get('fin_cycle'),
#                     "Period_code": data.get('Period_code'),
#                     "module_id": data.get('module_id'),
#                     "Maker_Id": request.user.user_id, 
#                     "Record_Status": "O",  
#                     "Auth_Status": "A",   
#                     "entries": []
#                 }

              
#                 for i, entry in enumerate(data.get('entries', [])):
#                     original_acc_no = entry.get("Account_no")
#                     acc_id = glsub_map.get(original_acc_no)
#                     # ac_rel = list(glsub_map.values())[1] if i == 0 else list(glsub_map.values())[0]
#                     # ac_rel = list(glsub_map.keys())[1] if i == 0 else list(glsub_map.keys())[0]
#                     ac_rel = list(glsub_map.keys())[1] if i == 0 else list(glsub_map.keys())[0]

                    
#                     # modified_acc_no = f"{alt_ccy_code}.{original_acc_no}"
#                     # modified_acc_no = f"{alt_ccy_code}.{original_acc_no}"
#                     modified_acc_no = f"{alt_ccy_code}.{original_acc_no}"
#                     all_modified_accounts = [f"{alt_ccy_code}.{acc}" for acc in glsub_map.keys()]
#                     ac_rel = all_modified_accounts[1] if i == 0 else all_modified_accounts[0]

#                     processed_entry = {
#                         "Account": acc_id,
#                         "Account_no": modified_acc_no, 
#                         "Amount": entry.get('Amount'),
#                         "Dr_cr": entry.get('Dr_cr'),
#                         "Addl_sub_text": entry.get('Addl_sub_text'),
#                         # "Ac_relatives": str(ac_rel),
#                         "Ac_relatives": ac_rel,
#                         "Maker_Id": request.user.user_id,  
#                         "Record_Status": "O", 
#                         "Auth_Status": "A"    
#                     }
#                     processed_data["entries"].append(processed_entry)

                
#                 try:
#                     from SAMCSYS.views import JRNLLogViewSet

#                     factory = RequestFactory()
                    
                   
#                     raw_request = factory.post(
#                         '/api/journal-entries/batch_create/',
#                         data=json.dumps(processed_data),
#                         content_type='application/json'
#                     )
#                     raw_request.user = request.user
#                     drf_request = Request(raw_request)

#                     viewset = JRNLLogViewSet()
#                     viewset.request = drf_request
#                     viewset.format_kwarg = None

#                     batch_response = viewset.batch_create(drf_request)

#                     if batch_response.status_code in [200, 201]:
#                         journal_response = {
#                             'success': True,
#                             'status_code': batch_response.status_code,
#                             'data': batch_response.data,
#                             'method': 'internal_batch_create'
#                         }
#                     else:
#                         journal_response = {
#                             'success': False,
#                             'status_code': batch_response.status_code,
#                             'error': batch_response.data,
#                             'method': 'internal_batch_create_failed'
#                         }

#                 except Exception as e:
                    
#                     try:
#                         viewset = JRNLLogViewSet()
                        
#                         viewset.request = request
#                         viewset.format_kwarg = None
                        
                        
#                         from unittest.mock import Mock
#                         mock_request = Mock()
#                         mock_request.data = processed_data
#                         mock_request.user = request.user
                        
#                         batch_response = viewset.batch_create(mock_request)
                        
#                         if batch_response.status_code in [200, 201]:
#                             journal_response = {
#                                 'success': True,
#                                 'status_code': batch_response.status_code,
#                                 'data': batch_response.data,
#                                 'method': 'direct_call'
#                             }
#                         else:
#                             journal_response = {
#                                 'success': False,
#                                 'status_code': batch_response.status_code,
#                                 'error': batch_response.data,
#                                 'method': 'direct_call_failed'
#                             }
#                     except Exception as e2:
#                         journal_response = {
#                             'success': False,
#                             'error': f'ViewSet Error: {str(e)} | Direct call error: {str(e2)}',
#                             'note': 'GLSub records created. Please create journal entry manually.'
#                         }

#                 return Response({
#                     'success': True,
#                     'message': 'ປະມວນຜົນແລະບັນທຶກຂໍ້ມູນສຳເລັດແລ້ວ',
#                     'processed_data': processed_data,
#                     'glsub_ids': glsub_ids,
#                     'alt_ccy_code': alt_ccy_code,  
#                     'journal_response': journal_response
#                 }, status=status.HTTP_201_CREATED)

#         except Exception as e:
#             return Response({
#                 'success': False,
#                 'message': f'ເກີດຂໍ້ຜິດພາດ: {str(e)}'
#             }, status=status.HTTP_400_BAD_REQUEST)
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from django.db import transaction
from django.utils import timezone
from django.test import RequestFactory
import json

class YourProcessViewSet(viewsets.ModelViewSet):

    @action(detail=False, methods=['post'])
    def process_journal_data(self, request):
        try:
            data = request.data
            glsub_ids = []
            glsub_map = {}  

            
            ccy_cd = data.get('Ccy_cd')
            try:
                ccy_record = MTTB_Ccy_DEFN.objects.get(ccy_code=ccy_cd)
                alt_ccy_code = ccy_record.ALT_Ccy_Code
            except MTTB_Ccy_DEFN.DoesNotExist:
                return Response({
                    'success': False,
                    'message': f'ບໍ່ພົບ currency code: {ccy_cd} ໃນ MTTB_Ccy_DEFN'
                }, status=status.HTTP_400_BAD_REQUEST)

            with transaction.atomic():
                for entry in data.get('entries', []):
                    account_no = entry.get('Account_no')
                    addl_sub_text = entry.get('Addl_sub_text')

                    gl_code_part = account_no.split('.')[0] if '.' in account_no else account_no

                    try:
                        gl_master = MTTB_GLMaster.objects.get(gl_code=gl_code_part)
                        gl_code_obj = gl_master  
                    except MTTB_GLMaster.DoesNotExist:
                        return Response({
                            'success': False,
                            'message': f'ບໍ່ພົບ gl_code: {gl_code_part} ໃນ MTTB_GLMaster'
                        }, status=status.HTTP_400_BAD_REQUEST)

                    
                    if entry.get("Dr_cr") == "D":
                        current_time = timezone.now()
                        
                        
                        try:
                            maker_user = MTTB_Users.objects.get(user_id=request.user.user_id)
                        except MTTB_Users.DoesNotExist:
                            return Response({
                                'success': False,
                                'message': f'ບໍ່ພົບຜູ້ໃຊ້: {request.user.user_id}'
                            }, status=status.HTTP_400_BAD_REQUEST)
                        
                        glsub_record = MTTB_GLSub.objects.create(
                            glsub_code=account_no,
                            glsub_Desc_la=addl_sub_text,
                            gl_code=gl_code_obj, 
                            Maker_DT_Stamp=current_time,
                            Checker_DT_Stamp=current_time,
                            Maker_Id=maker_user,  
                            Checker_Id=maker_user, 
                            Record_Status="O",
                            Auth_Status="A"
                        )
                        glsub_id = glsub_record.glsub_id
                    else:
                       
                        try:
                            glsub = MTTB_GLSub.objects.get(glsub_code=account_no)
                            glsub_id = glsub.glsub_id
                        except MTTB_GLSub.DoesNotExist:
                            return Response({
                                'success': False,
                                'message': f'ບໍ່ພົບ GLSub ສໍາລັບ Account_no: {account_no}'
                            }, status=status.HTTP_400_BAD_REQUEST)

                    glsub_ids.append(glsub_id)
                    glsub_map[account_no] = glsub_id

                processed_data = {
                    "Reference_No": data.get('Reference_No'),
                    "Ccy_cd": data.get('Ccy_cd'),
                    "Txn_code": data.get('Txn_code'),
                    "Value_date": data.get('Value_date'),
                    "Addl_text": data.get('Addl_text'),
                    "fin_cycle": data.get('fin_cycle'),
                    "Period_code": data.get('Period_code'),
                    "module_id": data.get('module_id'),
                    "Maker_Id": request.user.user_id, 
                    "Record_Status": "O",  
                    "Auth_Status": "A",   
                    "entries": []
                }

              
                for i, entry in enumerate(data.get('entries', [])):
                    original_acc_no = entry.get("Account_no")
                    acc_id = glsub_map.get(original_acc_no)
                    
                    # ໃຊ້ Ac_relatives ທີ່ສົ່ງມາຈາກ frontend
                    ac_relatives = entry.get('Ac_relatives', '')
                    
                    modified_acc_no = f"{alt_ccy_code}.{original_acc_no}"

                    processed_entry = {
                        "Account": acc_id,
                        "Account_no": modified_acc_no, 
                        "Amount": entry.get('Amount'),
                        "Dr_cr": entry.get('Dr_cr'),
                        "Addl_sub_text": entry.get('Addl_sub_text'),
                        "Ac_relatives": ac_relatives,  # ໃຊ້ຄ່າຈາກ frontend
                        "Maker_Id": request.user.user_id,  
                        "Record_Status": "O", 
                        "Auth_Status": "A"    
                    }
                    processed_data["entries"].append(processed_entry)

                
                try:
                    from SAMCSYS.views import JRNLLogViewSet

                    factory = RequestFactory()
                    
                   
                    raw_request = factory.post(
                        '/api/journal-entries/batch_create/',
                        data=json.dumps(processed_data),
                        content_type='application/json'
                    )
                    raw_request.user = request.user
                    drf_request = Request(raw_request)

                    viewset = JRNLLogViewSet()
                    viewset.request = drf_request
                    viewset.format_kwarg = None

                    batch_response = viewset.batch_create(drf_request)

                    if batch_response.status_code in [200, 201]:
                        journal_response = {
                            'success': True,
                            'status_code': batch_response.status_code,
                            'data': batch_response.data,
                            'method': 'internal_batch_create'
                        }
                    else:
                        journal_response = {
                            'success': False,
                            'status_code': batch_response.status_code,
                            'error': batch_response.data,
                            'method': 'internal_batch_create_failed'
                        }

                except Exception as e:
                    
                    try:
                        viewset = JRNLLogViewSet()
                        
                        viewset.request = request
                        viewset.format_kwarg = None
                        
                        
                        from unittest.mock import Mock
                        mock_request = Mock()
                        mock_request.data = processed_data
                        mock_request.user = request.user
                        
                        batch_response = viewset.batch_create(mock_request)
                        
                        if batch_response.status_code in [200, 201]:
                            journal_response = {
                                'success': True,
                                'status_code': batch_response.status_code,
                                'data': batch_response.data,
                                'method': 'direct_call'
                            }
                        else:
                            journal_response = {
                                'success': False,
                                'status_code': batch_response.status_code,
                                'error': batch_response.data,
                                'method': 'direct_call_failed'
                            }
                    except Exception as e2:
                        journal_response = {
                            'success': False,
                            'error': f'ViewSet Error: {str(e)} | Direct call error: {str(e2)}',
                            'note': 'GLSub records created. Please create journal entry manually.'
                        }

                return Response({
                    'success': True,
                    'message': 'ປະມວນຜົນແລະບັນທຶກຂໍ້ມູນສຳເລັດແລ້ວ',
                    'processed_data': processed_data,
                    'glsub_ids': glsub_ids,
                    'alt_ccy_code': alt_ccy_code,  
                    'journal_response': journal_response
                }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({
                'success': False,
                'message': f'ເກີດຂໍ້ຜິດພາດ: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
# from rest_framework import viewsets, status
# from rest_framework.decorators import action
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.request import Request
# from django.db import transaction
# from django.utils import timezone
# from django.test import RequestFactory
# import json

# class YourProcessViewSet(viewsets.ModelViewSet):

#     @action(detail=False, methods=['post'])
#     def process_journal_data(self, request):
#         try:
#             data = request.data
#             glsub_ids = []
#             glsub_map = {}  

            
#             ccy_cd = data.get('Ccy_cd')
#             try:
#                 ccy_record = MTTB_Ccy_DEFN.objects.get(ccy_code=ccy_cd)
#                 alt_ccy_code = ccy_record.ALT_Ccy_Code
#             except MTTB_Ccy_DEFN.DoesNotExist:
#                 return Response({
#                     'success': False,
#                     'message': f'ບໍ່ພົບ currency code: {ccy_cd} ໃນ MTTB_Ccy_DEFN'
#                 }, status=status.HTTP_400_BAD_REQUEST)

#             with transaction.atomic():
#                 for entry in data.get('entries', []):
#                     account_no = entry.get('Account_no')
#                     addl_sub_text = entry.get('Addl_sub_text')

#                     gl_code_part = account_no.split('.')[0] if '.' in account_no else account_no

#                     try:
#                         gl_master = MTTB_GLMaster.objects.get(gl_code=gl_code_part)
#                         gl_code_id = gl_master.glid
#                     except MTTB_GLMaster.DoesNotExist:
#                         return Response({
#                             'success': False,
#                             'message': f'ບໍ່ພົບ gl_code: {gl_code_part} ໃນ MTTB_GLMaster'
#                         }, status=status.HTTP_400_BAD_REQUEST)

                    
#                     if entry.get("Dr_cr") == "D":
#                         current_time = timezone.now()
#                         glsub_record = MTTB_GLSub.objects.create(
#                             glsub_code=account_no,
#                             glsub_Desc_la=addl_sub_text,
#                             gl_code_id=gl_code_id,
#                             Maker_DT_Stamp=current_time,
#                             Checker_DT_Stamp=current_time,
#                             Record_Status="O",
#                             Auth_Status="A" 
#                         )
#                         glsub_id = glsub_record.glsub_id
#                     else:
                       
#                         try:
#                             glsub = MTTB_GLSub.objects.get(glsub_code=account_no)
#                             glsub_id = glsub.glsub_id
#                         except MTTB_GLSub.DoesNotExist:
#                             return Response({
#                                 'success': False,
#                                 'message': f'ບໍ່ພົບ GLSub ສໍາລັບ Account_no: {account_no}'
#                             }, status=status.HTTP_400_BAD_REQUEST)

#                     glsub_ids.append(glsub_id)
#                     glsub_map[account_no] = glsub_id

#                 processed_data = {
#                     "Reference_No": data.get('Reference_No'),
#                     "Ccy_cd": data.get('Ccy_cd'),
#                     "Txn_code": data.get('Txn_code'),
#                     "Value_date": data.get('Value_date'),
#                     "Addl_text": data.get('Addl_text'),
#                     "fin_cycle": data.get('fin_cycle'),
#                     "Period_code": data.get('Period_code'),
#                     "module_id": data.get('module_id'),
#                     "entries": []
#                 }

              
#                 for i, entry in enumerate(data.get('entries', [])):
#                     original_acc_no = entry.get("Account_no")
#                     acc_id = glsub_map.get(original_acc_no)
#                     ac_rel = list(glsub_map.values())[1] if i == 0 else list(glsub_map.values())[0]

                    
#                     modified_acc_no = f"{alt_ccy_code}.{original_acc_no}"

#                     processed_entry = {
#                         "Account": acc_id,
#                         "Account_no": modified_acc_no, 
#                         "Amount": entry.get('Amount'),
#                         "Dr_cr": entry.get('Dr_cr'),
#                         "Addl_sub_text": entry.get('Addl_sub_text'),
#                         "Ac_relatives": str(ac_rel)
#                     }
#                     processed_data["entries"].append(processed_entry)

                
#                 try:
#                     from SAMCSYS.views import JRNLLogViewSet

#                     factory = RequestFactory()
                    
                   
#                     raw_request = factory.post(
#                         '/api/journal-entries/batch_create/',
#                         data=json.dumps(processed_data),
#                         content_type='application/json'
#                     )
#                     raw_request.user = request.user
#                     drf_request = Request(raw_request)

#                     viewset = JRNLLogViewSet()
#                     viewset.request = drf_request
#                     viewset.format_kwarg = None

#                     batch_response = viewset.batch_create(drf_request)

#                     if batch_response.status_code in [200, 201]:
#                         journal_response = {
#                             'success': True,
#                             'status_code': batch_response.status_code,
#                             'data': batch_response.data,
#                             'method': 'internal_batch_create'
#                         }
#                     else:
#                         journal_response = {
#                             'success': False,
#                             'status_code': batch_response.status_code,
#                             'error': batch_response.data,
#                             'method': 'internal_batch_create_failed'
#                         }

#                 except Exception as e:
                    
#                     try:
#                         viewset = JRNLLogViewSet()
                        
#                         viewset.request = request
#                         viewset.format_kwarg = None
                        
                        
#                         from unittest.mock import Mock
#                         mock_request = Mock()
#                         mock_request.data = processed_data
#                         mock_request.user = request.user
                        
#                         batch_response = viewset.batch_create(mock_request)
                        
#                         if batch_response.status_code in [200, 201]:
#                             journal_response = {
#                                 'success': True,
#                                 'status_code': batch_response.status_code,
#                                 'data': batch_response.data,
#                                 'method': 'direct_call'
#                             }
#                         else:
#                             journal_response = {
#                                 'success': False,
#                                 'status_code': batch_response.status_code,
#                                 'error': batch_response.data,
#                                 'method': 'direct_call_failed'
#                             }
#                     except Exception as e2:
#                         journal_response = {
#                             'success': False,
#                             'error': f'ViewSet Error: {str(e)} | Direct call error: {str(e2)}',
#                             'note': 'GLSub records created. Please create journal entry manually.'
#                         }

#                 return Response({
#                     'success': True,
#                     'message': 'ປະມວນຜົນແລະບັນທຶກຂໍ້ມູນສຳເລັດແລ້ວ',
#                     'processed_data': processed_data,
#                     'glsub_ids': glsub_ids,
#                     'alt_ccy_code': alt_ccy_code,  
#                     'journal_response': journal_response
#                 }, status=status.HTTP_201_CREATED)

#         except Exception as e:
#             return Response({
#                 'success': False,
#                 'message': f'ເກີດຂໍ້ຜິດພາດ: {str(e)}'
#             }, status=status.HTTP_400_BAD_REQUEST)
class JournalProcessV2ViewSet(viewsets.ModelViewSet):

    @action(detail=False, methods=['post'])
    def process_journal_data(self, request):
        try:
            data = request.data
            glsub_ids = []
            glsub_map = {}  

            ccy_cd = data.get('Ccy_cd')
            try:
                ccy_record = MTTB_Ccy_DEFN.objects.get(ccy_code=ccy_cd)
                alt_ccy_code = ccy_record.ALT_Ccy_Code
            except MTTB_Ccy_DEFN.DoesNotExist:
                return Response({
                    'success': False,
                    'message': f'ບໍ່ພົບ currency code: {ccy_cd} ໃນ MTTB_Ccy_DEFN'
                }, status=status.HTTP_400_BAD_REQUEST)

            with transaction.atomic():
                for entry in data.get('entries', []):
                    account_no = entry.get('Account_no')
                    addl_sub_text = entry.get('Addl_sub_text')

                    gl_code_part = account_no.split('.')[0] if '.' in account_no else account_no

                    try:
                        gl_master = MTTB_GLMaster.objects.get(gl_code=gl_code_part)
                        gl_code_obj = gl_master  
                    except MTTB_GLMaster.DoesNotExist:
                        return Response({
                            'success': False,
                            'message': f'ບໍ່ພົບ gl_code: {gl_code_part} ໃນ MTTB_GLMaster'
                        }, status=status.HTTP_400_BAD_REQUEST)

                    
                    current_time = timezone.now()
                    
                    try:
                        maker_user = MTTB_Users.objects.get(user_id=request.user.user_id)
                    except MTTB_Users.DoesNotExist:
                        return Response({
                            'success': False,
                            'message': f'ບໍ່ພົບຜູ້ໃຊ້: {request.user.user_id}'
                        }, status=status.HTTP_400_BAD_REQUEST)
                    
                    
                    glsub_record = MTTB_GLSub.objects.create(
                        glsub_code=account_no,
                        glsub_Desc_la=addl_sub_text,
                        gl_code=gl_code_obj, 
                        Maker_DT_Stamp=current_time,
                        Checker_DT_Stamp=current_time,
                        Maker_Id=maker_user,  
                        Checker_Id=maker_user, 
                        Record_Status="O",
                        Auth_Status="A"
                    )
                    glsub_id = glsub_record.glsub_id

                    glsub_ids.append(glsub_id)
                    glsub_map[account_no] = glsub_id

                processed_data = {
                    "Reference_No": data.get('Reference_No'),
                    "Ccy_cd": data.get('Ccy_cd'),
                    "Txn_code": data.get('Txn_code'),
                    "Value_date": data.get('Value_date'),
                    "Addl_text": data.get('Addl_text'),
                    "fin_cycle": data.get('fin_cycle'),
                    "Period_code": data.get('Period_code'),
                    "module_id": data.get('module_id'),
                    "Maker_Id": request.user.user_id, 
                    "Record_Status": "O",  
                    "Auth_Status": "A",   
                    "entries": []
                }

                for i, entry in enumerate(data.get('entries', [])):
                    original_acc_no = entry.get("Account_no")
                    acc_id = glsub_map.get(original_acc_no)
                    
                    modified_acc_no = f"{alt_ccy_code}.{original_acc_no}"
                    
                    # ໃຊ້ Ac_relatives ທີ່ສົ່ງມາຈາກ frontend
                    ac_relatives = entry.get('Ac_relatives', '')

                    processed_entry = {
                        "Account": acc_id,
                        "Account_no": modified_acc_no, 
                        "Amount": entry.get('Amount'),
                        "Dr_cr": entry.get('Dr_cr'),
                        "Addl_sub_text": entry.get('Addl_sub_text'),
                        "Ac_relatives": ac_relatives,  # ໃຊ້ຄ່າຈາກ frontend
                        "Maker_Id": request.user.user_id,  
                        "Record_Status": "O", 
                        "Auth_Status": "A"    
                    }
                    processed_data["entries"].append(processed_entry)

                try:
                    from SAMCSYS.views import JRNLLogViewSet

                    factory = RequestFactory()
                    raw_request = factory.post(
                        '/api/journal-entries/batch_create/',
                        data=json.dumps(processed_data),
                        content_type='application/json'
                    )
                    raw_request.user = request.user
                    drf_request = Request(raw_request)

                    viewset = JRNLLogViewSet()
                    viewset.request = drf_request
                    viewset.format_kwarg = None

                    batch_response = viewset.batch_create(drf_request)

                    if batch_response.status_code in [200, 201]:
                        journal_response = {
                            'success': True,
                            'status_code': batch_response.status_code,
                            'data': batch_response.data,
                            'method': 'internal_batch_create'
                        }
                    else:
                        journal_response = {
                            'success': False,
                            'status_code': batch_response.status_code,
                            'error': batch_response.data,
                            'method': 'internal_batch_create_failed'
                        }

                except Exception as e:
                    try:
                        viewset = JRNLLogViewSet()
                        viewset.request = request
                        viewset.format_kwarg = None
                        
                        from unittest.mock import Mock
                        mock_request = Mock()
                        mock_request.data = processed_data
                        mock_request.user = request.user
                        
                        batch_response = viewset.batch_create(mock_request)
                        
                        if batch_response.status_code in [200, 201]:
                            journal_response = {
                                'success': True,
                                'status_code': batch_response.status_code,
                                'data': batch_response.data,
                                'method': 'direct_call'
                            }
                        else:
                            journal_response = {
                                'success': False,
                                'status_code': batch_response.status_code,
                                'error': batch_response.data,
                                'method': 'direct_call_failed'
                            }
                    except Exception as e2:
                        journal_response = {
                            'success': False,
                            'error': f'ViewSet Error: {str(e)} | Direct call error: {str(e2)}',
                            'note': 'GLSub records created. Please create journal entry manually.'
                        }

                return Response({
                    'success': True,
                    'message': 'ປະມວນຜົນແລະບັນທຶກຂໍ້ມູນສຳເລັດແລ້ວ (ສ້າງ GLSub ໃໝ່ທັງໝົດ)',
                    'processed_data': processed_data,
                    'glsub_ids': glsub_ids,
                    'alt_ccy_code': alt_ccy_code,  
                    'journal_response': journal_response
                }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({
                'success': False,
                'message': f'ເກີດຂໍ້ຜິດພາດ: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
# class JournalProcessV2ViewSet(viewsets.ModelViewSet):

#     @action(detail=False, methods=['post'])
#     def process_journal_data(self, request):
#         try:
#             data = request.data
#             glsub_ids = []
#             glsub_map = {}  

#             ccy_cd = data.get('Ccy_cd')
#             try:
#                 ccy_record = MTTB_Ccy_DEFN.objects.get(ccy_code=ccy_cd)
#                 alt_ccy_code = ccy_record.ALT_Ccy_Code
#             except MTTB_Ccy_DEFN.DoesNotExist:
#                 return Response({
#                     'success': False,
#                     'message': f'ບໍ່ພົບ currency code: {ccy_cd} ໃນ MTTB_Ccy_DEFN'
#                 }, status=status.HTTP_400_BAD_REQUEST)

#             with transaction.atomic():
#                 for entry in data.get('entries', []):
#                     account_no = entry.get('Account_no')
#                     addl_sub_text = entry.get('Addl_sub_text')

#                     gl_code_part = account_no.split('.')[0] if '.' in account_no else account_no

#                     try:
#                         gl_master = MTTB_GLMaster.objects.get(gl_code=gl_code_part)
#                         gl_code_obj = gl_master  
#                     except MTTB_GLMaster.DoesNotExist:
#                         return Response({
#                             'success': False,
#                             'message': f'ບໍ່ພົບ gl_code: {gl_code_part} ໃນ MTTB_GLMaster'
#                         }, status=status.HTTP_400_BAD_REQUEST)

                    
#                     current_time = timezone.now()
                    
#                     try:
#                         maker_user = MTTB_Users.objects.get(user_id=request.user.user_id)
#                     except MTTB_Users.DoesNotExist:
#                         return Response({
#                             'success': False,
#                             'message': f'ບໍ່ພົບຜູ້ໃຊ້: {request.user.user_id}'
#                         }, status=status.HTTP_400_BAD_REQUEST)
                    
                    
#                     glsub_record = MTTB_GLSub.objects.create(
#                         glsub_code=account_no,
#                         glsub_Desc_la=addl_sub_text,
#                         gl_code=gl_code_obj, 
#                         Maker_DT_Stamp=current_time,
#                         Checker_DT_Stamp=current_time,
#                         Maker_Id=maker_user,  
#                         Checker_Id=maker_user, 
#                         Record_Status="O",
#                         Auth_Status="A"
#                     )
#                     glsub_id = glsub_record.glsub_id

#                     glsub_ids.append(glsub_id)
#                     glsub_map[account_no] = glsub_id

#                 processed_data = {
#                     "Reference_No": data.get('Reference_No'),
#                     "Ccy_cd": data.get('Ccy_cd'),
#                     "Txn_code": data.get('Txn_code'),
#                     "Value_date": data.get('Value_date'),
#                     "Addl_text": data.get('Addl_text'),
#                     "fin_cycle": data.get('fin_cycle'),
#                     "Period_code": data.get('Period_code'),
#                     "module_id": data.get('module_id'),
#                     "Maker_Id": request.user.user_id, 
#                     "Record_Status": "O",  
#                     "Auth_Status": "A",   
#                     "entries": []
#                 }

#                 for i, entry in enumerate(data.get('entries', [])):
#                     original_acc_no = entry.get("Account_no")
#                     acc_id = glsub_map.get(original_acc_no)
                    
#                     modified_acc_no = f"{alt_ccy_code}.{original_acc_no}"
#                     all_modified_accounts = [f"{alt_ccy_code}.{acc}" for acc in glsub_map.keys()]
#                     ac_rel = all_modified_accounts[1] if i == 0 else all_modified_accounts[0]

#                     processed_entry = {
#                         "Account": acc_id,
#                         "Account_no": modified_acc_no, 
#                         "Amount": entry.get('Amount'),
#                         "Dr_cr": entry.get('Dr_cr'),
#                         "Addl_sub_text": entry.get('Addl_sub_text'),
#                         "Ac_relatives": ac_rel,
#                         "Maker_Id": request.user.user_id,  
#                         "Record_Status": "O", 
#                         "Auth_Status": "A"    
#                     }
#                     processed_data["entries"].append(processed_entry)

#                 try:
#                     from SAMCSYS.views import JRNLLogViewSet

#                     factory = RequestFactory()
#                     raw_request = factory.post(
#                         '/api/journal-entries/batch_create/',
#                         data=json.dumps(processed_data),
#                         content_type='application/json'
#                     )
#                     raw_request.user = request.user
#                     drf_request = Request(raw_request)

#                     viewset = JRNLLogViewSet()
#                     viewset.request = drf_request
#                     viewset.format_kwarg = None

#                     batch_response = viewset.batch_create(drf_request)

#                     if batch_response.status_code in [200, 201]:
#                         journal_response = {
#                             'success': True,
#                             'status_code': batch_response.status_code,
#                             'data': batch_response.data,
#                             'method': 'internal_batch_create'
#                         }
#                     else:
#                         journal_response = {
#                             'success': False,
#                             'status_code': batch_response.status_code,
#                             'error': batch_response.data,
#                             'method': 'internal_batch_create_failed'
#                         }

#                 except Exception as e:
#                     try:
#                         viewset = JRNLLogViewSet()
#                         viewset.request = request
#                         viewset.format_kwarg = None
                        
#                         from unittest.mock import Mock
#                         mock_request = Mock()
#                         mock_request.data = processed_data
#                         mock_request.user = request.user
                        
#                         batch_response = viewset.batch_create(mock_request)
                        
#                         if batch_response.status_code in [200, 201]:
#                             journal_response = {
#                                 'success': True,
#                                 'status_code': batch_response.status_code,
#                                 'data': batch_response.data,
#                                 'method': 'direct_call'
#                             }
#                         else:
#                             journal_response = {
#                                 'success': False,
#                                 'status_code': batch_response.status_code,
#                                 'error': batch_response.data,
#                                 'method': 'direct_call_failed'
#                             }
#                     except Exception as e2:
#                         journal_response = {
#                             'success': False,
#                             'error': f'ViewSet Error: {str(e)} | Direct call error: {str(e2)}',
#                             'note': 'GLSub records created. Please create journal entry manually.'
#                         }

#                 return Response({
#                     'success': True,
#                     'message': 'ປະມວນຜົນແລະບັນທຶກຂໍ້ມູນສຳເລັດແລ້ວ (ສ້າງ GLSub ໃໝ່ທັງໝົດ)',
#                     'processed_data': processed_data,
#                     'glsub_ids': glsub_ids,
#                     'alt_ccy_code': alt_ccy_code,  
#                     'journal_response': journal_response
#                 }, status=status.HTTP_201_CREATED)

#         except Exception as e:
#             return Response({
#                 'success': False,
#                 'message': f'ເກີດຂໍ້ຜິດພາດ: {str(e)}'
#             }, status=status.HTTP_400_BAD_REQUEST)