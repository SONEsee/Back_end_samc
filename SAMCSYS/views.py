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
          .filter(role_id=role, Record_Status='O')
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

        # Ensure all related records have Record_Status = 'O'
        if not (sub and main and mod):
            continue
        if sub.Record_Status != 'O' or main.Record_Status != 'O' or mod.Record_Status != 'O':
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

    # check Record_Status = 'O' 
        if not (sub and main and mod):
            continue
        if mod.Record_Status != 'O':
            continue
        if main.Record_Status != 'O':
            continue
        if sub.Record_Status != 'O':
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

# class EmployeeViewSet(viewsets.ModelViewSet):
#     """
#     CRUD for employees, supporting:
#       - JSON and multipart/form-data for file uploads
#       - Filtering by ?div_id=...
#       - Soft deletion via record_stat='D'
#     """
#     serializer_class = EmployeeSerializer
#     parser_classes = [JSONParser, MultiPartParser, FormParser]
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         """
#         Returns active employees (record_stat='A'), optionally filtered by div_id.
#         """
#         qs = MTTB_EMPLOYEE.objects.select_related('user_id', 'div_id', 'Maker_Id', 'Checker_Id').filter(record_stat='O')
        
#         params = self.request.query_params
#         div_id = params.get('div_id')
#         if div_id:
#             qs = qs.filter(div_id_id__div_id=div_id)
        
#         return qs.order_by('employee_id')

#     def perform_create(self, serializer):
#         """
#         Sets audit fields for creation.
#         """
#         serializer.save(
#             Maker_Id=self.request.user if self.request.user.is_authenticated else None,
#             Maker_DT_Stamp=timezone.now(),
#             record_stat='A',
#             Auth_Status='U',
#             Once_Auth='N'
#         )

#     def perform_update(self, serializer):
#         """
#         Sets audit fields for updates.
#         """
#         serializer.save(
#             Checker_Id=self.request.user if self.request.user.is_authenticated else None,
#             Checker_DT_Stamp=timezone.now()
#         )

#     def perform_destroy(self, instance):
#         """
#         Soft deletes the employee by setting record_stat to 'D'.
#         """
#         instance.record_stat = 'D'
#         instance.Checker_Id = self.request.user if self.request.user.is_authenticated else None
#         instance.Checker_DT_Stamp = timezone.now()
#         instance.save()

#     @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
#     def set_open(self, request, pk=None):
#         """Set Record_Status = 'O' (Open) only if Auth_Status = 'A'"""
#         obj = self.get_object()
#         if obj.record_stat == 'O':
#             return Response({'detail': 'Already open.'}, status=status.HTTP_400_BAD_REQUEST)
#         if getattr(obj, 'Auth_Status', None) != 'A':
#             return Response({'detail': 'Cannot set to Open. Only authorized (Auth_Status = "A") records can be opened.'}, status=status.HTTP_400_BAD_REQUEST)
#         obj.record_stat = 'O'
#         obj.Checker_Id = MTTB_Users.objects.get(user_id=request.user.user_id)
#         obj.Checker_DT_Stamp = timezone.now()
#         obj.save()
#         serializer = self.get_serializer(obj)
#         return Response({'message': 'Set to Open.', 'entry': serializer.data})

#     @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
#     def set_close(self, request, pk=None):
#         """Set Record_Status = 'C' (Close)"""
#         obj = self.get_object()
#         if obj.record_stat == 'C':
#             return Response({'detail': 'Already closed.'}, status=status.HTTP_400_BAD_REQUEST)
#         obj.record_stat = 'C'
#         obj.Checker_Id = MTTB_Users.objects.get(user_id=request.user.user_id)
#         obj.Checker_DT_Stamp = timezone.now()
#         obj.save()
#         serializer = self.get_serializer(obj)
#         return Response({'message': 'Set to Close.', 'entry': serializer.data})

#     @action(detail=True, methods=['post'])
#     def authorize(self, request, pk=None):
#         """Authorize a journal entry"""
#         journal_entry = self.get_object()

#         if journal_entry.Auth_Status == 'A':
#             return Response({'error': 'Entry is already authorized'}, 
#                           status=status.HTTP_400_BAD_REQUEST)

#         # Set Auth_Status = 'A', Once_Status = 'Y', Record_Status = 'O'
#         journal_entry.Auth_Status = 'A'
#         journal_entry.Once_Status = 'Y'
#         journal_entry.record_stat = 'C'
#         journal_entry.Checker_Id = MTTB_Users.objects.get(user_id=request.user.user_id)
#         journal_entry.Checker_DT_Stamp = timezone.now()
#         journal_entry.save()

#         serializer = self.get_serializer(journal_entry)
#         return Response({
#             'message': 'Entry authorized successfully',
#             'entry': serializer.data
#         })

#     @action(detail=True, methods=['post'])
#     def unauthorize(self, request, pk=None):
#         """Unauthorize a journal entry (set Auth_Status = 'U', Record_Status = 'C')"""
#         journal_entry = self.get_object()

#         if journal_entry.Auth_Status == 'U':
#             return Response({'error': 'Entry is already unauthorized'}, 
#                           status=status.HTTP_400_BAD_REQUEST)

#         # Set Auth_Status = 'U', Record_Status = 'C'
#         journal_entry.Auth_Status = 'U'
#         journal_entry.record_stat = 'C'
#         journal_entry.Checker_Id = MTTB_Users.objects.get(user_id=request.user.user_id)
#         journal_entry.Checker_DT_Stamp = timezone.now()
#         journal_entry.save()

#         serializer = self.get_serializer(journal_entry)
#         return Response({
#             'message': 'Entry unauthorized successfully',
#             'entry': serializer.data
#         })

class EmployeeViewSet(viewsets.ModelViewSet):
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'employee_id'

    def get_queryset(self):
        """
        Returns active employees (Record_Status='O'), optionally filtered by div_id.
        """
        qs = MTTB_EMPLOYEE.objects.select_related('user_id', 'div_id', 'Maker_Id', 'Checker_Id')
        params = self.request.query_params
        div_id = params.get('div_id')
        if div_id:
            qs = qs.filter(div_id_id__div_id=div_id)

        return qs.order_by('employee_id')

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(
            Maker_Id=user,
            Maker_DT_Stamp=timezone.now()
        )

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response({
            'message': 'Employee created successfully.',
            'entry': response.data
        }, status=response.status_code)

    def perform_update(self, serializer):
        user = self.request.user
        serializer.save(
            Checker_Id=user,
            Checker_DT_Stamp=timezone.now()
        )

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return Response({
            'message': 'Employee updated successfully.',
            'entry': response.data
        }, status=response.status_code)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            'message': 'Employee deleted successfully.'
        }, status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def set_open(self, request, employee_id=None):
        """Set Record_Status = 'O' (Open) only if Auth_Status = 'A'"""
        obj = self.get_object()
        if obj.Record_Status == 'O':
            return Response({'detail': 'Already open.'}, status=status.HTTP_400_BAD_REQUEST)
        if getattr(obj, 'Auth_Status', None) != 'A':
            return Response({'detail': 'Cannot set to Open. Only authorized records can be opened.'}, status=status.HTTP_400_BAD_REQUEST)
        obj.Record_Status = 'O'
        obj.Checker_Id = request.user
        obj.Checker_DT_Stamp = timezone.now()
        obj.save()
        serializer = self.get_serializer(obj)
        return Response({'message': 'Set to Open.', 'entry': serializer.data})

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def set_close(self, request, employee_id=None):
        """Set Record_Status = 'C' (Close)"""
        obj = self.get_object()
        if obj.Record_Status == 'C':
            return Response({'detail': 'Already closed.'}, status=status.HTTP_400_BAD_REQUEST)
        obj.Record_Status = 'C'
        obj.Checker_Id = request.user
        obj.Checker_DT_Stamp = timezone.now()
        obj.save()
        serializer = self.get_serializer(obj)
        return Response({'message': 'Set to Close.', 'entry': serializer.data})

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def authorize(self, request, employee_id=None):
        """Authorize an employee record"""
        obj = self.get_object()
        if obj.Auth_Status == 'A':
            return Response({'error': 'Entry is already authorized'}, status=status.HTTP_400_BAD_REQUEST)

        obj.Auth_Status = 'A'
        obj.Once_Auth = 'Y'
        obj.Record_Status = 'C'
        obj.Checker_Id = request.user
        obj.Checker_DT_Stamp = timezone.now()
        obj.save()

        serializer = self.get_serializer(obj)
        return Response({'message': 'Entry authorized successfully.', 'entry': serializer.data})

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def unauthorize(self, request, employee_id=None):
        """Unauthorize an employee record"""
        obj = self.get_object()
        if obj.Auth_Status == 'U':
            return Response({'error': 'Entry is already unauthorized'}, status=status.HTTP_400_BAD_REQUEST)

        obj.Auth_Status = 'U'
        obj.Record_Status = 'C'
        obj.Checker_Id = request.user
        obj.Checker_DT_Stamp = timezone.now()
        obj.save()

        serializer = self.get_serializer(obj)
        return Response({'message': 'Entry unauthorized successfully.', 'entry': serializer.data})

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
    
    Holiday_List now always contains exactly 31 characters:
    - H: Holiday
    - W: Working day
    - N: Weekend day
    - O: Non-existent day in month (e.g., Feb 29-31)
    
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
            queryset = queryset.filter(Record_Status='O')
        
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

# from rest_framework.decorators import action
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated, AllowAny
# from django_filters.rest_framework import DjangoFilterBackend
# from django.utils import timezone
# from rest_framework import filters
# from rest_framework import viewsets, status
# from .models import MTTB_LCL_Holiday
# from .serializers import MTTB_LCL_HolidaySerializer

# class MTTB_LCL_HolidayViewSet(viewsets.ModelViewSet):
#     """
#     ViewSet for MTTB_LCL_Holiday model providing CRUD operations.
    
#     list: Get all holidays with optional filtering
#     create: Create a new holiday (no authentication required)
#     retrieve: Get a specific holiday by ID
#     update: Update a holiday (full update)
#     partial_update: Update a holiday (partial update)
#     destroy: Delete a holiday
#     """
#     queryset = MTTB_LCL_Holiday.objects.all()
#     serializer_class = MTTB_LCL_HolidaySerializer
#     lookup_field = 'lcl_holiday_id'
    
#     # Enable filtering, searching, and ordering
#     filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
#     # Define filterable fields
#     filterset_fields = {
#         'HYear': ['exact', 'in'],
#         'HMonth': ['exact', 'in'],
#         'HDate': ['exact', 'gte', 'lte', 'range'],
#         'Holiday_List': ['exact'],
#         'Record_Status': ['exact', 'in'],
#         'Auth_Status': ['exact', 'in'],
#         'Once_Auth': ['exact'],
#         'Maker_Id': ['exact'],
#         'Checker_Id': ['exact']
#     }
    
#     # Define searchable fields
#     search_fields = ['lcl_holiday_id', 'HYear', 'HMonth']
    
#     # Define ordering fields
#     ordering_fields = ['lcl_holiday_id', 'HDate', 'HYear', 'HMonth', 'Maker_DT_Stamp']
#     ordering = ['-Maker_DT_Stamp']  # Default ordering
    
#     def get_permissions(self):
#         # Allow anyone to create a new holiday, require auth elsewhere
#         if self.request.method == 'POST':
#             return [AllowAny()]
#         return [IsAuthenticated()]
    
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
    
#     def get_queryset(self):
#         """
#         Optionally restricts the returned holidays based on query parameters.
#         """
#         queryset = super().get_queryset()
        
#         # Example: Filter holidays by date range
#         start_date = self.request.query_params.get('start_date', None)
#         end_date = self.request.query_params.get('end_date', None)
        
#         if start_date and end_date:
#             queryset = queryset.filter(HDate__range=[start_date, end_date])
        
#         # Example: Filter only active records
#         active_only = self.request.query_params.get('active_only', None)
#         if active_only and active_only.lower() == 'true':
#             queryset = queryset.filter(Record_Status='O')
        
#         return queryset
    

#     @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
#     def pending_authorization(self, request):
#         """
#         Get all holidays pending authorization (Auth_Status='U')
#         """
#         pending = self.get_queryset().filter(Auth_Status='U')
#         serializer = self.get_serializer(pending, many=True)
#         return Response(serializer.data)
    
#     @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
#     def authorize(self, request, lcl_holiday_id=None):
#         """
#         Authorize a holiday record
#         """
#         holiday = self.get_object()
        
#         if holiday.Auth_Status == 'A':
#             return Response(
#                 {'detail': 'Holiday already authorized'},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
        
#         # Prevent self-authorization
#         if holiday.Maker_Id and holiday.Maker_Id == request.user:
#             return Response(
#                 {'detail': 'Cannot authorize your own record'},
#                 status=status.HTTP_403_FORBIDDEN
#             )
        
#         holiday.Auth_Status = 'A'
#         holiday.Checker_Id = request.user
#         holiday.Checker_DT_Stamp = timezone.now()
#         holiday.save()
        
#         serializer = self.get_serializer(holiday)
#         return Response(serializer.data)
    
#     @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
#     def reject(self, request, lcl_holiday_id=None):
#         """
#         Reject a holiday record
#         """
#         holiday = self.get_object()
        
#         if holiday.Auth_Status == 'U':
#             return Response(
#                 {'detail': 'Holiday already rejected'},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
        
#         holiday.Auth_Status = 'U'
#         holiday.Checker_Id = request.user
#         holiday.Checker_DT_Stamp = timezone.now()
#         holiday.save()
        
#         serializer = self.get_serializer(holiday)
#         return Response(serializer.data)
    
#     @action(detail=False, methods=['get'])
#     def by_year_month(self, request):
#         """
#         Get holidays for a specific year and month
#         """
#         year = request.query_params.get('year', None)
#         month = request.query_params.get('month', None)
        
#         if not year:
#             return Response(
#                 {'detail': 'Year parameter is required'},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
        
#         queryset = self.get_queryset().filter(HYear=year)
        
#         if month:
#             queryset = queryset.filter(HMonth=month)
        
#         serializer = self.get_serializer(queryset, many=True)
#         return Response(serializer.data)
    
#     @action(detail=False, methods=['get'])
#     def upcoming(self, request):
#         """
#         Get upcoming holidays (HDate >= today)
#         """
#         from datetime import date
#         today = date.today()
        
#         upcoming = self.get_queryset().filter(
#             HDate__gte=today,
#             Record_Status='C',
#             Auth_Status='A'
#         ).order_by('HDate')
        
#         serializer = self.get_serializer(upcoming, many=True)
#         return Response(serializer.data)
    
#     def perform_destroy(self, instance):
#         instance.delete()

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
def list_provinces(request):
    """Get all provinces"""
    queryset = MTTB_ProvinceInfo.objects.all().order_by('pro_id')
    serializer = ProvinceSerializer(queryset, many=True)
    
    return Response({
        "status": True,
        "message": "ສຳເລັດການດຶງຂໍ້ມູນແຂວງ",
        "count": queryset.count(),
        "data": serializer.data
    }, status=status.HTTP_200_OK)

@api_view(['GET']) 
@permission_classes([IsAuthenticated])
def list_districts(request):
    """Get all districts with optional province filter"""
    queryset = MTTB_DistrictInfo.objects.all().order_by('pro_id', 'dis_code')
    pro_id = request.query_params.get('pro_id')
    
    if pro_id:
        queryset = queryset.filter(pro_id=pro_id)
    
    serializer = DistrictSerializer(queryset, many=True)
    
    return Response({
        "status": True,
        "message": "ສຳເລັດການດຶງຂໍ້ມູນເມືອງ",
        "count": queryset.count(),
        "data": serializer.data
    }, status=status.HTTP_200_OK)
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
                    Auth_Status__in=['P','U']
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
    
    @action(detail=False, methods=["post"], url_path="pending-asset")
    def pending_asset(self, request):
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
            asset.Auth_Status = "P"
            message = f"Asset {reference_no} (UC) has been Pending successfully."
            
        elif asset.asset_status == "AC":
            # Check if already approved
            if hasattr(asset, 'Auth_Status_ARC') and asset.Auth_Status_ARC == "A":
                return Response(
                    {"error": f"Asset {reference_no} (AC) has already been approved."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Update Auth_Status_ARC for AC assets
            asset.Auth_Status_ARC = "P"
            message = f"Asset {reference_no} (AC) has been Pending successfully."

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


    @action(detail=False, methods=["post"], url_path="reject-asset")
    def reject_asset(self, request):
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
            # Check if already rejected
            if asset.Auth_Status == "R" and asset.Auth_Status_ARC == "R":
                return Response(
                    {"error": f"Asset {reference_no} (UC) has already been rejected."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Update Auth_Status for UC assets
            asset.Auth_Status = "R"
            message = f"Asset {reference_no} (UC) has been rejected successfully."

        elif asset.asset_status == "AC":
            # Check if already rejected
            if hasattr(asset, 'Auth_Status_ARC') and asset.Auth_Status_ARC == "R":
                return Response(
                    {"error": f"Asset {reference_no} (AC) has already been rejected."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Update Auth_Status_ARC for AC assets
            asset.Auth_Status_ARC = "R"
            message = f"Asset {reference_no} (AC) has been rejected successfully."

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
                        # addl_sub_text = f"Approved Entry - {entry.Dr_cr} - {entry.Account_no}"
                        addl_sub_text = f"{entry.Addl_sub_text[:30] if entry.Addl_sub_text else ''}"


                        
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
                            # 'addl_sub_text':  entry.addl_sub_text or '',
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

    @action(detail=False, methods=['post'], url_path='pending-all')  
    def pending_all(self, request):
        """Reject all records (MASTER, LOG, HIST) for a Reference_No"""
        reference_no = request.data.get('Reference_No')
        pending_reason = request.data.get('pending_reason')

        if not reference_no:
            return Response({'error': 'Reference_No is required'}, 
                        status=status.HTTP_400_BAD_REQUEST)

        if not pending_reason:
            return Response({'error': 'pending_reason is required'}, 
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
                    Auth_Status='P',
                    Checker_Id=request.user,
                    Checker_DT_Stamp=timezone.now(),
                    # comments=request.data.get('comments') + f'\nRejection: {rejection_reason}'
                )
                
                # Update DETB_JRNL_LOG_MASTER
                try:
                    from .models import DETB_JRNL_LOG_MASTER
                    master_record = DETB_JRNL_LOG_MASTER.objects.get(Reference_No=reference_no)
                    master_record.Auth_Status = 'P'
                    master_record.Checker_Id = request.user
                    master_record.Checker_DT_Stamp = timezone.now()
                    master_record.Addl_text = (master_record.Addl_text or '') + f'\nPending: {pending_reason}'
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
                        Auth_Status='P',
                        Checker_Id=request.user,
                        Checker_DT_Stamp=timezone.now()
                    )
                except:
                    pass  # HIST table might not exist
            
            return Response({
                'message': f'Successfully pending {log_updated} LOG entries, {master_updated} MASTER record, {hist_updated} HIST records',
                'reference_no': reference_no,
                'rejection_reason': pending_reason
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
from django.utils.dateparse import parse_datetime, parse_date


class DETB_JRNL_LOG_MASTER_ViewSet(viewsets.ModelViewSet):
    queryset = DETB_JRNL_LOG_MASTER.objects.all()
    serializer_class = DETB_JRNL_LOG_MASTER_Serializer
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['Ccy_cd', 'Txn_code', 'fin_cycle', 'Auth_Status','Reference_No']  # Removed 'delete_stat' from filter
    search_fields = ['Reference_No', 'Addl_text']
    ordering_fields = ['-Auth_Status', 'Checker_Id','Maker_DT_Stamp', 'Value_date']

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

    # def list(self, request, *args, **kwargs):
    #     """
    #     Override list to add Value_date filtering
    #     """
    #     queryset = self.filter_queryset(self.get_queryset())
        
    #     # Apply date filtering if provided
    #     date_param = request.query_params.get('Value_date')
        
    #     if date_param:
    #         try:
    #             # Parse the date string (e.g., "2025-07-18")
    #             filter_date = parse_date(date_param)
    #             if filter_date:
    #                 # Option 1: Use __date lookup (recommended - simpler)
    #                 queryset = queryset.filter(Value_date__date=filter_date)
                    
    #                 # Option 2: Alternative using date range (if __date doesn't work)
    #                 # start_datetime = datetime.combine(filter_date, datetime.min.time())
    #                 # end_datetime = datetime.combine(filter_date, datetime.max.time())
    #                 # queryset = queryset.filter(Value_date__range=[start_datetime, end_datetime])
                    
    #             else:
    #                 # If date parsing fails, return empty queryset
    #                 queryset = queryset.none()
    #         except ValueError:
    #             # If date format is invalid, return empty queryset
    #             queryset = queryset.none()
        
    #     # Get page from pagination
    #     page = self.paginate_queryset(queryset)
    #     if page is not None:
    #         serializer = self.get_serializer(page, many=True)
    #         return self.get_paginated_response(serializer.data)

    #     serializer = self.get_serializer(queryset, many=True)
    #     return Response(serializer.data)
    def list(self, request, *args, **kwargs):
        """
        Override list to add comprehensive date filtering and permission-based access
        Supports:
        - Specific date: Value_date=2024-01-15
        - Date range: Value_date__gte=2024-01-01&Value_date__lte=2024-01-31
        - Permission-based filtering: show_all=true/false
        """
        queryset = self.filter_queryset(self.get_queryset())
        
        # Permission-based filtering
        show_all = request.query_params.get('show_all', 'false').lower() == 'true'
        
        # If user doesn't have authorization permission, filter to only their own records
        if not show_all:
            # Assuming the user ID is available in request.user
            user_id = getattr(request.user, 'user_id', None) or getattr(request.user, 'id', None)
            if user_id:
                queryset = queryset.filter(Maker_Id=user_id)
            else:
                # If no user ID found, return empty queryset for security
                queryset = queryset.none()
        
        # Date filtering logic
        try:
            # 1. Handle specific date filtering (Value_date=2024-01-15)
            specific_date = request.query_params.get('Value_date')
            if specific_date:
                filter_date = parse_date(specific_date)
                if filter_date:
                    # Filter for exact date match
                    queryset = queryset.filter(Value_date__date=filter_date)
                else:
                    # Invalid date format, return empty queryset
                    return Response({
                        'error': 'Invalid date format for Value_date. Expected YYYY-MM-DD.',
                        'results': [],
                        'count': 0
                    }, status=400)
            
            # 2. Handle date range filtering (Value_date__gte and Value_date__lte)
            else:
                date_from = request.query_params.get('Value_date__gte')
                date_to = request.query_params.get('Value_date__lte')
                
                if date_from:
                    from_date = parse_date(date_from)
                    if from_date:
                        queryset = queryset.filter(Value_date__date__gte=from_date)
                    else:
                        return Response({
                            'error': 'Invalid date format for Value_date__gte. Expected YYYY-MM-DD.',
                            'results': [],
                            'count': 0
                        }, status=400)
                
                if date_to:
                    to_date = parse_date(date_to)
                    if to_date:
                        queryset = queryset.filter(Value_date__date__lte=to_date)
                    else:
                        return Response({
                            'error': 'Invalid date format for Value_date__lte. Expected YYYY-MM-DD.',
                            'results': [],
                            'count': 0
                        }, status=400)
        
        except Exception as e:
            # Log the error for debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Date filtering error: {str(e)}")
            
            return Response({
                'error': 'Error processing date filters.',
                'results': [],
                'count': 0
            }, status=400)
        
        # Additional filtering parameters
        try:
            # Module filtering
            module_id = request.query_params.get('module_id')
            if module_id:
                queryset = queryset.filter(module_id=module_id)
            
            # Currency filtering
            ccy_cd = request.query_params.get('Ccy_cd')
            if ccy_cd:
                queryset = queryset.filter(Ccy_cd=ccy_cd)
            
            # Authorization status filtering
            auth_status = request.query_params.get('Auth_Status')
            if auth_status:
                queryset = queryset.filter(Auth_Status=auth_status)
            
            # Search filtering (search in Reference_No and Addl_text)
            search = request.query_params.get('search')
            if search:
                from django.db.models import Q
                queryset = queryset.filter(
                    Q(Reference_No__icontains=search) | 
                    Q(Addl_text__icontains=search) |
                    Q(Txn_code__icontains=search)
                )
            
            # Exclude soft deleted records
            delete_stat_ne = request.query_params.get('delete_stat__ne')
            if delete_stat_ne:
                queryset = queryset.exclude(delete_stat=delete_stat_ne)
            
            # Ordering
            ordering = request.query_params.get('ordering', '-Maker_DT_Stamp')
            if ordering:
                # Validate ordering field to prevent SQL injection
                valid_fields = [
                    'Maker_DT_Stamp', '-Maker_DT_Stamp',
                    'Value_date', '-Value_date',
                    'Reference_No', '-Reference_No',
                    'Fcy_Amount', '-Fcy_Amount',
                    'Auth_Status', '-Auth_Status'
                ]
                if ordering in valid_fields:
                    queryset = queryset.order_by(ordering)
                else:
                    queryset = queryset.order_by('-Maker_DT_Stamp')  # Default ordering
        
        except Exception as e:
            # Log the error for debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Additional filtering error: {str(e)}")
            
            return Response({
                'error': 'Error processing filters.',
                'results': [],
                'count': 0
            }, status=400)
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

        Today = timezone.now().date()
        reference_no = request.query_params.get('Reference_No')
        auth_status = request.query_params.get('Auth_Status')
        
        queryset = DETB_JRNL_LOG_MASTER.objects.filter( 
            delete_stat__isnull=True
            , Value_date=Today
        ).exclude(delete_stat='D', Auth_Status='A')

        if reference_no:
            queryset = queryset.filter(Reference_No=reference_no)
        if auth_status:
            queryset = queryset.filter(Auth_Status=auth_status)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    
    @action(detail=False, methods=['get'], url_path='journal-log-detail')
    def journal_log_detail(self, request):
        """
        Get all active (not deleted) journal log master records, optionally filtered by Reference_No.
        
        """

        # Today = timezone.now().date()
        reference_no = request.query_params.get('Reference_No')
        auth_status = request.query_params.get('Auth_Status')
        
        queryset = DETB_JRNL_LOG_MASTER.objects.filter( 
            delete_stat__isnull=True
            # , Value_date=Today
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
            prev_Working_Day=last_eod.Start_Date if last_eod else None,
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
    


# from datetime import datetime, timedelta
# from django.utils import timezone
# import pytz
# from .models import MTTB_LCL_Holiday, STTB_Dates

# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def end_of_day_journal_view(request):
#     """
#     API endpoint to validate and process end-of-day journal submission.
#     Requires authentication.
#     """
#     success, message = end_of_day_journal()
#     if success:
#         return Response({"message": message}, status=status.HTTP_201_CREATED)
#     return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)
# def end_of_day_journal():
#     """
#     Validates and processes end-of-day journal submission.
#     Checks if today is a working day and matches the next_working_date in STTB_Dates.
#     If valid, creates a new STTB_Dates entry for the next working day.
    
#     Returns:
#         tuple: (bool, str) - (Success status, Message)
#     """
#     try:
#         # Set timezone to +07:00 as per user context
#         tz = pytz.timezone('Asia/Bangkok')  # UTC+07:00
#         today = timezone.now().astimezone(tz).date()
#         year_str = str(today.year)
#         month_str = str(today.month).zfill(2)  # Ensure two-digit month
#         print(f"Processing end-of-day journal for {year_str}-{month_str} on {today} in timezone {tz}")
#         # Step 1: Check if today is a working day in MTTB_LCL_Holiday
#         try:
#             holiday_record = MTTB_LCL_Holiday.objects.get(
#                 HYear=year_str, HMonth=month_str
#             )
#             print(f"Holiday record found for {year_str}-{month_str}: {holiday_record.Holiday_List}")
#         except MTTB_LCL_Holiday.DoesNotExist:
#             return False, f"No holiday record found for {year_str}-{month_str}."

#         holiday_list = holiday_record.Holiday_List
#         if len(holiday_list) != 31:
#             return False, "Invalid Holiday_List length. Must be 31 characters."

#         # Get the day index (1-based) for today
#         day_index = today.day - 1
#         if day_index >= len(holiday_list) or holiday_list[day_index] != 'W':
#             return False, f"Today ({today}) is not a working day."

#         # Step 2: Check the latest STTB_Dates row
#         try:
#             latest_eod = STTB_Dates.objects.latest('date_id')
#         except STTB_Dates.DoesNotExist:
#             return False, "No records found in STTB_Dates."

#         # Convert next_working_day to date for comparison
#         next_working_date = latest_eod.next_working_Day.astimezone(tz).date()
#         if next_working_date != today:
#             return False, f"Today ({today}) does not match the next working day ({next_working_date})."

#         # Step 3: Find the next working day after today
#         current_date = today
#         next_working_date = None
#         while True:
#             current_date += timedelta(days=1)
#             # Check if we need to fetch a new holiday record for the next month
#             if current_date.month != today.month:
#                 try:
#                     holiday_record = MTTB_LCL_Holiday.objects.get(
#                         HYear=str(current_date.year), HMonth=str(current_date.month).zfill(2),
#                         Record_Status='C', Auth_Status='U'
#                     )
#                     holiday_list = holiday_record.Holiday_List
#                 except MTTB_LCL_Holiday.DoesNotExist:
#                     return False, f"No holiday record found for {current_date.year}-{current_date.month:02d}."
#             day_index = current_date.day - 1
#             if day_index < len(holiday_list) and holiday_list[day_index] == 'W':
#                 next_working_date = current_date
#                 break
#             if current_date > today + timedelta(days=31):  # Prevent infinite loop
#                 return False, "No working day found in the next 31 days."

#         # Step 4: Create new STTB_Dates entry
#         new_eod = STTB_Dates(
#             Start_Date=latest_eod.next_working_Day,  # Use next_working_Day from latest row
#             prev_Working_Day=latest_eod.Start_Date,  # Use Start_Date from latest row
#             next_working_Day=timezone.make_aware(
#                 datetime.combine(next_working_date, datetime.min.time()), timezone=tz
#             ),
#             eod_time='N'
#         )
#         new_eod.save()

#         return True, f"Journal submission successful for {today}. New entry created for {next_working_date}."

#     except Exception as e:
#         return False, f"Error processing journal submission: {str(e)}"


from datetime import datetime, timedelta
from django.utils import timezone
from django.db import transaction
import pytz
import logging
from .models import MTTB_LCL_Holiday, STTB_Dates, MTTB_EOC_MAINTAIN, MTTB_Function_Desc, STTB_EOC_DAILY_LOG, ACTB_DAIRY_LOG
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

# Set up logging
logger = logging.getLogger(__name__)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def end_of_day_journal_view(request):
    """
    API endpoint with transaction support - all operations succeed or fail together.
    Clear EOD journal runs at the end after all processes.
    """
    try:
        # Get the value_date from request or use current date
        value_date = request.data.get('value_date')
        if not value_date:
            value_date = timezone.now().date()
        elif isinstance(value_date, str):
            value_date = datetime.strptime(value_date, '%Y-%m-%d').date()
        
        logger.info(f"Starting transactional EOD process for date: {value_date}, User: {request.user}")
        
        with transaction.atomic():
            # Step 1: Validate EOD requirements
            validation_success, validation_message = validate_eod_requirements()
            if not validation_success:
                logger.error(f"EOD validation failed: {validation_message}")
                raise Exception(validation_message)
            
            # Step 2: Execute main EOD process
            eod_success, eod_message = execute_eod_process(request.user)
            if not eod_success:
                logger.error(f"EOD process failed: {eod_message}")
                raise Exception(eod_message)
            
            # Step 3: Clear EOD journal (guaranteed to run at the end)
            clear_success, clear_message = clear_eod_journal_with_transaction(value_date)
            if not clear_success:
                logger.error(f"EOD clear failed: {clear_message}")
                raise Exception(clear_message)
            
            # All steps successful
            final_message = f"ການປະມວນຜົນ EOD ສຳເລັດແລ້ວສົມບູນ ສຳລັບວັນທີ {value_date}"
            logger.info(f"Complete transactional EOD process successful for {value_date}")
            
            return Response({
                "message": final_message,
                "success": True,
                "details": {
                    "validation": validation_message,
                    "eod_process": eod_message,
                    "clear_journal": clear_message
                }
            }, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        logger.error(f"Transactional EOD process failed for {value_date}: {str(e)}")
        return Response({
            "error": f"ການປະມວນຜົນ EOD ລົ້ມເຫລວ: {str(e)}",
            "success": False
        }, status=status.HTTP_400_BAD_REQUEST)


def clear_eod_journal_with_transaction(value_date):
    """
    Clears EOD journal entries with transaction support.
    This version ensures all deletions succeed or fail together.
    """
    try:
        from datetime import datetime
        from django.db import transaction
        from .models import DETB_JRNL_LOG, DETB_JRNL_LOG_MASTER
        
        # Convert value_date to proper format if it's a string
        if isinstance(value_date, str):
            value_date = datetime.strptime(value_date, '%Y-%m-%d').date()
        
        with transaction.atomic():
            cleared_count = 0
            cleared_details = []
            
            # Clear STTB_EOC_DAILY_LOG for specific date
            # sttb_count = STTB_EOC_DAILY_LOG.objects.filter(value_date=value_date).count()
            # if sttb_count > 0:
            #     STTB_EOC_DAILY_LOG.objects.filter(value_date=value_date).delete()
            #     cleared_count += sttb_count
            #     cleared_details.append(f"STTB_EOC_DAILY_LOG: {sttb_count}")
            
            # Clear ACTB_DAIRY_LOG for specific date
            actb_count = ACTB_DAIRY_LOG.objects.filter(value_dt=value_date).count()
            if actb_count > 0:
                ACTB_DAIRY_LOG.objects.filter(value_dt=value_date).delete()
                cleared_count += actb_count
                cleared_details.append(f"ACTB_DAIRY_LOG: {actb_count}")
            
            # Clear DETB_JRNL_LOG for specific date
            jrnl_count = DETB_JRNL_LOG.objects.filter(Value_date=value_date).count()
            if jrnl_count > 0:
                DETB_JRNL_LOG.objects.filter(Value_date=value_date).delete()
                cleared_count += jrnl_count
                cleared_details.append(f"DETB_JRNL_LOG: {jrnl_count}")
            
            # Clear DETB_JRNL_LOG_MASTER for specific date
            master_count = DETB_JRNL_LOG_MASTER.objects.filter(Value_date=value_date).count()
            if master_count > 0:
                DETB_JRNL_LOG_MASTER.objects.filter(Value_date=value_date).delete()
                cleared_count += master_count
                cleared_details.append(f"DETB_JRNL_LOG_MASTER: {master_count}")
            
            if cleared_count > 0:
                details_str = ", ".join(cleared_details)
                message = f"ລຶບຂໍ້ມູນ EOD ສຳເລັດສຳລັບວັນທີ {value_date} (ດ້ວຍ Transaction). ລາຍການທີ່ລຶບ: {details_str}. ລວມ: {cleared_count} ລາຍການ"
                logger.info(f"EOD journal cleared with transaction for date {value_date}. Total: {cleared_count}")
                return True, message
            else:
                message = f"ບໍ່ມີຂໍ້ມູນ EOD ໃຫ້ລຶບສຳລັບວັນທີ {value_date}"
                logger.info(f"No EOD journal entries found for date {value_date}")
                return True, message
                
    except Exception as e:
        error_message = f"ເກີດຂໍ້ຜິດພາດໃນການລຶບຂໍ້ມູນ EOD ດ້ວຍ Transaction ສຳລັບວັນທີ {value_date}: {str(e)}"
        logger.error(error_message)
        return False, error_message

def validate_eod_requirements():
    """
    Validates if EOD can be performed (same as your existing end_of_day_journal validation)
    """
    try:
        # Set timezone to +07:00 as per user context
        tz = pytz.timezone('Asia/Bangkok')  # UTC+07:00
        today = timezone.now().astimezone(tz).date()
        year_str = str(today.year)
        month_str = str(today.month).zfill(2)
        
        # Step 1: Check if today is a working day
        try:
            holiday_record = MTTB_LCL_Holiday.objects.get(
                HYear=year_str, HMonth=month_str
            )
        except MTTB_LCL_Holiday.DoesNotExist:
            return False, f"No holiday record found for {year_str}-{month_str}."

        holiday_list = holiday_record.Holiday_List
        if len(holiday_list) != 31:
            return False, "Invalid Holiday_List length. Must be 31 characters."

        day_index = today.day - 1
        if day_index >= len(holiday_list) or holiday_list[day_index] != 'W':
            return False, f"Today ({today}) is not a working day."

        # Step 2: Check the latest STTB_Dates row
        try:
            latest_eod = STTB_Dates.objects.latest('date_id')
        except STTB_Dates.DoesNotExist:
            return False, "No records found in STTB_Dates."

        next_working_date = latest_eod.next_working_Day.astimezone(tz).date()
        if next_working_date != today:
            return False, f"Today ({today}) does not match the next working day ({next_working_date})."

        return True, f"EOD validation passed for {today}"

    except Exception as e:
        return False, f"Error in EOD validation: {str(e)}"

def execute_eod_process(user):
    """
    Main EOD execution process that runs all sub-functions in sequence
    """
    try:
        with transaction.atomic():
            # Get all EOD functions ordered by sequence
            eod_functions = get_eod_functions()
            
            if not eod_functions:
                return False, "ບໍ່ພົບຟັງຊັນ EOD ທີ່ຕ້ອງປະມວນຜົນ"
            
            # Execute functions in sequence
            execution_results = []
            total_executed = 0
            total_skipped = 0
            
            for eod_function in eod_functions:
                try:
                    if should_execute_function(eod_function):
                        # Execute the function
                        func_success, func_message = execute_eod_function(eod_function, user)
                        
                        if func_success:
                            total_executed += 1
                            execution_results.append({
                                'function': eod_function.function_id.description_la,
                                'status': 'success',
                                'message': func_message
                            })
                            logger.info(f"EOD Function {eod_function.function_id.function_id} executed successfully")
                        else:
                            # If any critical function fails, stop the process
                            logger.error(f"EOD Function {eod_function.function_id.function_id} failed: {func_message}")
                            return False, f"ຟັງຊັນ {eod_function.function_id.description_la} ລົ້ມເຫລວ: {func_message}"
                    else:
                        total_skipped += 1
                        execution_results.append({
                            'function': eod_function.function_id.description_la,
                            'status': 'skipped',
                            'message': 'ຟັງຊັນຖືກປິດ (Record_Status = C)'
                        })
                        logger.info(f"EOD Function {eod_function.function_id.function_id} skipped (closed)")
                        
                except Exception as e:
                    logger.error(f"Error executing EOD function {eod_function.function_id.function_id}: {str(e)}")
                    return False, f"ຂໍ້ຜິດພາດໃນຟັງຊັນ {eod_function.function_id.description_la}: {str(e)}"
            
            # After all functions are executed, create new STTB_Dates entry
            success, message = create_next_working_day_entry(user)
            if not success:
                return False, f"ບໍ່ສາມາດສ້າງ entry ວັນເຮັດການໃໝ່ໄດ້: {message}"
            
            # Prepare summary message
            summary_message = f"ປິດບັນຊີປະຈຳວັນສຳເລັດແລ້ວ - ປະມວນຜົນ: {total_executed} ຟັງຊັນ, ຂ້າມ: {total_skipped} ຟັງຊັນ"
            
            return True, summary_message

    except Exception as e:
        logger.error(f"Error in EOD process execution: {str(e)}")
        return False, f"ເກີດຂໍ້ຜິດພາດໃນການປະມວນຜົນ EOD: {str(e)}"

def get_eod_functions():
    """
    Get all EOD functions that should be considered for execution
    """
    return MTTB_EOC_MAINTAIN.objects.filter(
        eoc_type='EOD',
        Auth_Status='A'  # Only authorized functions
    ).select_related('function_id', 'module_id').order_by('eoc_seq_no')

def should_execute_function(eod_function):
    """
    Determine if a function should be executed based on its status
    """
    # Execute only if Record_Status is 'O' (Open)
    return eod_function.Record_Status == 'O'

def execute_eod_function(eod_function, user):
    """
    Execute a specific EOD function based on its function_id
    """
    function_id = eod_function.function_id.function_id
    
    try:
        # Map function IDs to their corresponding execution methods
        function_mapping = {
            'FN006': execute_bulk_journal,
            'EOD_BALANCE': execute_balance_calculation,
            'EOD_INTEREST': execute_interest_calculation,
            'EOD_REPORT': execute_report_generation,
            'EOD_BACKUP': execute_backup_process,
            # Add more function mappings as needed
        }
        
        if function_id in function_mapping:
            # Execute the mapped function
            return function_mapping[function_id](eod_function, user)
        else:
            # Generic execution for unmapped functions
            return execute_generic_function(eod_function, user)
            
    except Exception as e:
        logger.error(f"Error executing function {function_id}: {str(e)}")
        return False, f"ຂໍ້ຜິດພາດໃນການປະມວນຜົນ: {str(e)}"


# from django.db import transaction
# from django.core.exceptions import ValidationError
# import logging

# logger = logging.getLogger(__name__)

# def execute_bulk_journal(eod_function, user):
#     """
#     Execute the bulk journal function (move data from ACTB_DAIRY_LOG to STTB_EOC_DAILY_LOG)
#     """
#     try:
#         with transaction.atomic():
#             # Fetch authorized records from ACTB_DAIRY_LOG
#             authorized_logs = ACTB_DAIRY_LOG.objects.filter(Auth_Status='A')
            
#             if not authorized_logs.exists():
#                 return True, "ບໍ່ມີ journal ທີ່ຕ້ອງປະມວນຜົນ"
            
#             logger.info(f"Processing {authorized_logs.count()} authorized journal entries")
            
#             # Prepare bulk create objects
#             eoc_logs = []
#             processed_ids = []
            
#             # Iterate through authorized logs and prepare STTB_EOC_DAILY_LOG objects
#             for log in authorized_logs:
#                 try:
#                     # Safely extract ForeignKey values with proper null checking
#                     eoc_log = STTB_EOC_DAILY_LOG(
#                         module=getattr(log.module, 'module_code', '') if log.module else '',
#                         trn_ref_no=getattr(log.trn_ref_no, 'trn_ref_no', '') if log.trn_ref_no else '',
#                         trn_ref_sub_no=log.trn_ref_sub_no or '',
#                         # Handle potential BigInt to Int conversion
#                         event_sr_no=min(log.event_sr_no or 0, 2147483647),  # Max int value
#                         event=log.event or '',
#                         ac_no=getattr(log.ac_no, 'gl_sub_code', '') if log.ac_no else '',
#                         ac_ccy=getattr(log.ac_ccy, 'ccy_code', '') if log.ac_ccy else '',
#                         drcr_ind=log.drcr_ind or '',
#                         trn_code=getattr(log.trn_code, 'trn_code', '') if log.trn_code else '',
#                         fcy_amount=log.fcy_amount,
#                         exch_rate=log.exch_rate,
#                         lcy_amount=log.lcy_amount,
#                         external_ref_no=log.external_ref_no or '',
#                         addl_text=log.addl_text or '',
#                         addl_sub_text=log.addl_sub_text or '',
#                         trn_dt=log.trn_dt,
#                         type=log.glType or '',
#                         category=log.category or '',
#                         value_dt=log.value_dt,
#                         financial_cycle=getattr(log.financial_cycle, 'fin_cycle', '') if log.financial_cycle else '',
#                         period_code=getattr(log.period_code, 'per_code', '') if log.period_code else '',
#                         user_id=getattr(log.user_id, 'user_id', '') if log.user_id else '',
#                         Maker_DT_Stamp=log.Maker_DT_Stamp,
#                         auth_id=getattr(log.auth_id, 'user_id', '') if log.auth_id else '',
#                         Checker_DT_Stamp=log.Checker_DT_Stamp,
#                         Auth_Status=log.Auth_Status or 'U',
#                         product=log.product or '',
#                         entry_seq_no=log.entry_seq_no
#                     )
                    
#                     # Validate the object before adding to bulk list
#                     eoc_log.full_clean()
#                     eoc_logs.append(eoc_log)
#                     processed_ids.append(log.ac_entry_sr_no)
                    
#                 except ValidationError as ve:
#                     logger.error(f"Validation error for log ID {log.ac_entry_sr_no}: {ve}")
#                     continue
#                 except Exception as e:
#                     logger.error(f"Error processing log ID {log.ac_entry_sr_no}: {str(e)}")
#                     continue
            
#             if not eoc_logs:
#                 return False, "ບໍ່ສາມາດປະມວນຜົນ journal ໃດໆໄດ້"
            
#             # Bulk create records in STTB_EOC_DAILY_LOG
#             created_records = STTB_EOC_DAILY_LOG.objects.bulk_create(eoc_logs)
            
#             # Update source records to prevent reprocessing
#             # Option 1: Mark as processed
#             ACTB_DAIRY_LOG.objects.filter(
#                 ac_entry_sr_no__in=processed_ids
#             ).update(Auth_Status='P')  # P for Processed
            
#             # Option 2: Delete processed records (uncomment if needed)
#             # ACTB_DAIRY_LOG.objects.filter(
#             #     ac_entry_sr_no__in=processed_ids
#             # ).delete()
            
#             logger.info(f"Successfully processed {len(created_records)} journal entries")
#             return True, f"ບັນທຶກ journal ສຳເລັດ: {len(created_records)} ລາຍການ"
        
#     except Exception as e:
#         logger.error(f"Error in execute_bulk_journal: {str(e)}")
#         return False, f"ຂໍ້ຜິດພາດໃນການບັນທຶກ journal: {str(e)}"


from django.db import transaction
from django.core.exceptions import ValidationError
import logging
def execute_bulk_journal(eod_function, user):
    """
    Execute the bulk journal function (move data from ACTB_DAIRY_LOG to STTB_EOC_DAILY_LOG)
    """
    try:
        with transaction.atomic():
            # Fetch authorized records from ACTB_DAIRY_LOG
            authorized_logs = ACTB_DAIRY_LOG.objects.filter(Auth_Status='A')
            
            if not authorized_logs.exists():
                return True, "ບໍ່ມີ journal ທີ່ຕ້ອງປະມວນຜົນ"
            
            logger.info(f"Processing {authorized_logs.count()} authorized journal entries")
            
            # Prepare bulk create objects
            eoc_logs = []
            processed_ids = []
            
            # Iterate through authorized logs and prepare STTB_EOC_DAILY_LOG objects
            for log in authorized_logs:
                try:
                    # Debug: Print log data to understand the structure
                    logger.debug(f"Processing log ID {log.ac_entry_sr_no}")
                    logger.debug(f"Module: {log.module}, TRN_REF_NO: {log.trn_ref_no}, AC_NO: {log.ac_no}")
                    
                    # Extract values with proper handling for ForeignKeys and field length limits
                    module_value = ''
                    if log.module:
                        # Try different possible field names for module
                        module_value = str(getattr(log.module, 'module_code', None) or 
                                         getattr(log.module, 'code', None) or 
                                         getattr(log.module, 'id', ''))[:2]  # Max 2 chars
                    
                    trn_ref_no_value = ''
                    if log.trn_ref_no:
                        # Try different possible field names for trn_ref_no
                        trn_ref_no_value = str(getattr(log.trn_ref_no, 'trn_ref_no', None) or
                                             getattr(log.trn_ref_no, 'reference_no', None) or
                                             getattr(log.trn_ref_no, 'id', ''))[:15]  # Max 15 chars
                    
                    ac_no_value = ''
                    if log.ac_no:
                        # Try different possible field names for ac_no
                        ac_no_value = str(getattr(log.ac_no, 'gl_sub_code', None) or
                                        getattr(log.ac_no, 'account_code', None) or
                                        getattr(log.ac_no, 'code', None) or
                                        getattr(log.ac_no, 'id', ''))[:20]  # Max 20 chars
                    
                    ac_ccy_value = ''
                    if log.ac_ccy:
                        ac_ccy_value = str(getattr(log.ac_ccy, 'ccy_code', None) or
                                         getattr(log.ac_ccy, 'code', None) or
                                         getattr(log.ac_ccy, 'id', ''))[:3]  # Max 3 chars
                    
                    trn_code_value = ''
                    if log.trn_code:
                        trn_code_value = str(getattr(log.trn_code, 'trn_code', None) or
                                           getattr(log.trn_code, 'code', None) or
                                           getattr(log.trn_code, 'id', ''))[:3]  # Max 3 chars
                    
                    financial_cycle_value = ''
                    if log.financial_cycle:
                        financial_cycle_value = str(getattr(log.financial_cycle, 'fin_cycle', None) or
                                                  getattr(log.financial_cycle, 'cycle', None) or
                                                  getattr(log.financial_cycle, 'id', ''))[:9]  # Max 9 chars
                    
                    period_code_value = ''
                    if log.period_code:
                        period_code_value = str(getattr(log.period_code, 'per_code', None) or
                                              getattr(log.period_code, 'code', None) or
                                              getattr(log.period_code, 'id', ''))[:3]  # Max 3 chars
                    
                    user_id_value = ''
                    if log.user_id:
                        user_id_value = str(getattr(log.user_id, 'user_id', None) or
                                          getattr(log.user_id, 'username', None) or
                                          getattr(log.user_id, 'id', ''))[:12]  # Max 12 chars
                    
                    auth_id_value = ''
                    if log.auth_id:
                        auth_id_value = str(getattr(log.auth_id, 'user_id', None) or
                                          getattr(log.auth_id, 'username', None) or
                                          getattr(log.auth_id, 'id', ''))[:12]  # Max 12 chars
                    
                    # Handle external_ref_no length limit (16 chars max)
                    external_ref_no_value = (log.external_ref_no or '')[:16]
                    
                    # Ensure required fields have values
                    if not module_value:
                        module_value = 'GL'  # Default module
                    if not trn_ref_no_value:
                        trn_ref_no_value = f'TRN{log.ac_entry_sr_no}'[:15]  # Generate from ID
                    if not ac_no_value:
                        ac_no_value = f'AC{log.ac_entry_sr_no}'[:20]  # Generate from ID
                    if not ac_ccy_value:
                        ac_ccy_value = 'LAK'  # Default currency
                    if not trn_code_value:
                        trn_code_value = 'GL'  # Default transaction code
                    if not financial_cycle_value:
                        financial_cycle_value = '2025'  # Default financial cycle
                    if not period_code_value:
                        period_code_value = f'{log.trn_dt.year}{log.trn_dt.month:02d}' if log.trn_dt else '202507'
                    
                    eoc_log = STTB_EOC_DAILY_LOG(
                        module=module_value,
                        trn_ref_no=trn_ref_no_value,
                        trn_ref_sub_no=log.trn_ref_sub_no or '',
                        # Handle potential BigInt to Int conversion
                        event_sr_no=min(log.event_sr_no or 0, 2147483647),  # Max int value
                        event=log.event or '',
                        ac_no=ac_no_value,
                        ac_ccy=ac_ccy_value,
                        drcr_ind=log.drcr_ind or 'D',
                        trn_code=trn_code_value,
                        fcy_amount=log.fcy_amount,
                        exch_rate=log.exch_rate,
                        lcy_amount=log.lcy_amount,
                        external_ref_no=external_ref_no_value,
                        addl_text=log.addl_text or '',
                        addl_sub_text=log.addl_sub_text or '',
                        trn_dt=log.trn_dt,
                        type=log.glType or '',
                        category=log.category or '',
                        value_dt=log.value_dt,
                        financial_cycle=financial_cycle_value,
                        period_code=period_code_value,
                        user_id=user_id_value,
                        Maker_DT_Stamp=log.Maker_DT_Stamp,
                        auth_id=auth_id_value,
                        Checker_DT_Stamp=log.Checker_DT_Stamp,
                        Auth_Status=log.Auth_Status or 'U',
                        product=log.product or '',
                        entry_seq_no=log.entry_seq_no
                    )
                    
                    # Validate the object before adding to bulk list
                    eoc_log.full_clean()
                    eoc_logs.append(eoc_log)
                    processed_ids.append(log.ac_entry_sr_no)
                    
                except ValidationError as ve:
                    logger.error(f"Validation error for log ID {log.ac_entry_sr_no}: {ve}")
                    continue
                except Exception as e:
                    logger.error(f"Error processing log ID {log.ac_entry_sr_no}: {str(e)}")
                    continue
            
            if not eoc_logs:
                return False, "ບໍ່ສາມາດປະມວນຜົນ journal ໃດໆໄດ້"
            
            # Bulk create records in STTB_EOC_DAILY_LOG
            created_records = STTB_EOC_DAILY_LOG.objects.bulk_create(eoc_logs)
            
            # Update source records to prevent reprocessing
            # Option 1: Mark as processed
            ACTB_DAIRY_LOG.objects.filter(
                ac_entry_sr_no__in=processed_ids
            ).update(Auth_Status='P')  # P for Processed
            
            # Option 2: Delete processed records (uncomment if needed)
            # ACTB_DAIRY_LOG.objects.filter(
            #     ac_entry_sr_no__in=processed_ids
            # ).delete()
            
            logger.info(f"Successfully processed {len(created_records)} journal entries")
            return True, f"ບັນທຶກ journal ສຳເລັດ: {len(created_records)} ລາຍການ"
        
    except Exception as e:
        logger.error(f"Error in execute_bulk_journal: {str(e)}")
        return False, f"ຂໍ້ຜິດພາດໃນການບັນທຶກ journal: {str(e)}"

def execute_balance_calculation(eod_function, user):
    """
    Execute balance calculation function
    """
    try:
        # Add your balance calculation logic here
        # This is a placeholder implementation
        
        return True, "ຄິດໄລ່ຍອດເງິນສຳເລັດ"
        
    except Exception as e:
        return False, f"ຂໍ້ຜິດພາດໃນການຄິດໄລ່ຍອດເງິນ: {str(e)}"

def execute_interest_calculation(eod_function, user):
    """
    Execute interest calculation function
    """
    try:
        # Add your interest calculation logic here
        # This is a placeholder implementation
        
        return True, "ຄິດໄລ່ດອກເບ້ຍສຳເລັດ"
        
    except Exception as e:
        return False, f"ຂໍ້ຜິດພາດໃນການຄິດໄລ່ດອກເບ້ຍ: {str(e)}"

def execute_report_generation(eod_function, user):
    """
    Execute report generation function
    """
    try:
        # Add your report generation logic here
        # This is a placeholder implementation
        
        return True, "ສ້າງລາຍງານສຳເລັດ"
        
    except Exception as e:
        return False, f"ຂໍ້ຜິດພາດໃນການສ້າງລາຍງານ: {str(e)}"

def execute_backup_process(eod_function, user):
    """
    Execute backup process function
    """
    try:
        # Add your backup logic here
        # This is a placeholder implementation
        
        return True, "ສຳຮອງຂໍ້ມູນສຳເລັດ"
        
    except Exception as e:
        return False, f"ຂໍ້ຜິດພາດໃນການສຳຮອງຂໍ້ມູນ: {str(e)}"

def execute_generic_function(eod_function, user):
    """
    Generic function execution for unmapped functions
    """
    try:
        # Generic implementation - can be customized based on your needs
        # This could call external scripts, APIs, or other processes
        
        function_name = eod_function.function_id.description_la
        return True, f"ປະມວນຜົນຟັງຊັນ {function_name} ສຳເລັດ"
        
    except Exception as e:
        return False, f"ຂໍ້ຜິດພາດໃນການປະມວນຜົນຟັງຊັນ: {str(e)}"

def create_next_working_day_entry(user):
    """
    Create the next working day entry in STTB_Dates (from your original end_of_day_journal function)
    """
    try:
        tz = pytz.timezone('Asia/Bangkok')
        today = timezone.now().astimezone(tz).date()
        
        # Get the latest STTB_Dates row
        latest_eod = STTB_Dates.objects.latest('date_id')
        
        # Find the next working day after today
        current_date = today
        next_working_date = None
        
        while True:
            current_date += timedelta(days=1)
            
            # Check if we need to fetch a new holiday record for the next month
            if current_date.month != today.month:
                try:
                    holiday_record = MTTB_LCL_Holiday.objects.get(
                        HYear=str(current_date.year), 
                        HMonth=str(current_date.month).zfill(2),
                        Record_Status='C', 
                        Auth_Status='U'
                    )
                    holiday_list = holiday_record.Holiday_List
                except MTTB_LCL_Holiday.DoesNotExist:
                    return False, f"No holiday record found for {current_date.year}-{current_date.month:02d}."
            else:
                holiday_record = MTTB_LCL_Holiday.objects.get(
                    HYear=str(today.year), HMonth=str(today.month).zfill(2)
                )
                holiday_list = holiday_record.Holiday_List
                
            day_index = current_date.day - 1
            if day_index < len(holiday_list) and holiday_list[day_index] == 'W':
                next_working_date = current_date
                break
                
            if current_date > today + timedelta(days=31):  # Prevent infinite loop
                return False, "No working day found in the next 31 days."

        # Create new STTB_Dates entry
        new_eod = STTB_Dates(
            Start_Date=latest_eod.next_working_Day,
            prev_Working_Day=latest_eod.Start_Date,
            next_working_Day=timezone.make_aware(
                datetime.combine(next_working_date, datetime.min.time()), timezone=tz
            ),
            eod_time='N'
        )
        new_eod.save()

        return True, f"ສ້າງ entry ວັນເຮັດການໃໝ່ສຳເລັດ: {next_working_date}"

    except Exception as e:
        return False, f"ຂໍ້ຜິດພາດໃນການສ້າງ entry ວັນເຮັດການໃໝ່: {str(e)}"


# from rest_framework.decorators import api_view, permission_classes
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.response import Response
# from rest_framework import status

# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def check_journal_submission_available(request):
#     """
#     GET: Check if today is available for journal submission.
#     Returns True if:
#     - Today is a working day (W)
#     - Today matches the latest next_working_Day
#     - eod_time is 'N' (not yet submitted)
#     """
#     try:
#         tz = pytz.timezone('Asia/Bangkok')
#         today = timezone.now().astimezone(tz).date()
#         year_str = str(today.year)
#         month_str = str(today.month).zfill(2)

#         # Step 1: Check holiday list
#         try:
#             holiday_record = MTTB_LCL_Holiday.objects.get(HYear=year_str, HMonth=month_str)
#             holiday_list = holiday_record.Holiday_List
#         except MTTB_LCL_Holiday.DoesNotExist:
#             return Response({
#                 "available": False,
#                 "reason": f"No holiday record for {year_str}-{month_str}."
#             }, status=status.HTTP_200_OK)

#         if len(holiday_list) != 31:
#             return Response({
#                 "available": False,
#                 "reason": "Holiday_List is invalid length."
#             }, status=status.HTTP_200_OK)

#         day_index = today.day - 1
#         if holiday_list[day_index] != 'W':
#             return Response({
#                 "available": False,
#                 "reason": f"Today ({today}) is not a working day."
#             }, status=status.HTTP_200_OK)

#         # Step 2: Check latest STTB_Dates
#         try:
#             latest_eod = STTB_Dates.objects.latest('date_id')
#         except STTB_Dates.DoesNotExist:
#             return Response({
#                 "available": False,
#                 "reason": "No EOD records found."
#             }, status=status.HTTP_200_OK)

#         latest_next_working = latest_eod.next_working_Day.astimezone(tz).date()
#         if latest_next_working != today:
#             return Response({
#                 "available": False,
#                 "reason": f"Today ({today}) does not match next working day ({latest_next_working})."
#             }, status=status.HTTP_200_OK)

#         if latest_eod.eod_time != 'N':
#             return Response({
#                 "available": False,
#                 "reason": "Journal already submitted for today."
#             }, status=status.HTTP_200_OK)

#         # All checks passed
#         return Response({
#             "available": True,
#             "reason": f"Today ({today}) is valid for journal submission."
#         }, status=status.HTTP_200_OK)

#     except Exception as e:
#         return Response({
#             "available": False,
#             "reason": f"Error checking availability: {str(e)}"
#         }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import pytz
from django.utils import timezone
from .models import MTTB_LCL_Holiday, STTB_Dates, MTTB_DATA_Entry

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_journal_submission_available(request):
    """
    GET: Check if today is available for journal submission.
    Returns True if:
    - Today is a working day (W) OR MOD_NO = 'Y' (bypass condition)
    - Today matches the latest next_working_Day OR BACK_VALUE = 'Y' (bypass condition)
    - eod_time is 'N' (not yet submitted) OR BACK_VALUE = 'Y' (bypass condition)
    """
    # <-------------- Make Change here -------------->

    # test update chanegs Journal Submisison Validated
    try:
        tz = pytz.timezone('Asia/Bangkok')
        today = timezone.now().astimezone(tz).date()
        year_str = str(today.year)
        month_str = str(today.month).zfill(2)

        # Get MTTB_DATA_Entry configuration
        try:
            # Assuming you want the latest record or a specific one
            # You might need to adjust this query based on your business logic
            data_entry = MTTB_DATA_Entry.objects.filter(
                # Record_Status='A',  # Assuming 'A' means active, adjust as needed
                Auth_Status='A'     # Assuming 'A' means authorized, adjust as needed
            ).first()
            
            # If no data entry found, use default behavior (no bypass)
            if not data_entry:
                bypass_working_day = False
                bypass_eod_check = False
            else:
                bypass_working_day = data_entry.MOD_NO == 'Y'
                bypass_eod_check = data_entry.BACK_VALUE == 'Y'
                
        except Exception as e:
            # If error getting data entry, proceed with normal checks
            bypass_working_day = False
            bypass_eod_check = False

        # Step 1: Check working day (bypass if MOD_NO = 'Y')
        if not bypass_working_day:
            try:
                holiday_record = MTTB_LCL_Holiday.objects.get(HYear=year_str, HMonth=month_str)
                holiday_list = holiday_record.Holiday_List
            except MTTB_LCL_Holiday.DoesNotExist:
                return Response({
                    "available": False,
                    "reason": f"ບໍ່ສາມາດດລົງບັນຊີໃນວັນພັກໄດ້{year_str}-{month_str}."
                }, status=status.HTTP_200_OK)

            if len(holiday_list) != 31:
                return Response({
                    "available": False,
                    "reason": "Holiday_List is invalid length."
                }, status=status.HTTP_200_OK)

            day_index = today.day - 1
            if holiday_list[day_index] != 'W':
                return Response({
                    "available": False,
                    "reason": f"ມື້ນີ້ບໍ່ສາມາດບັນທຶກບັນຊີໄດ້ ວັນທີ ({today}) ບໍ່ເເມ່ນວັນເຮັດການ."
                }, status=status.HTTP_200_OK)
        else:
            # Log that working day check was bypassed
            bypass_reason = "ອະນຸຍາດໃຫ້ບັນທຶກບັນຊີມື້ພັກໄດ້ (MOD_NO = 'Y')"

        # Step 2: Check EOD conditions (bypass if BACK_VALUE = 'Y')
        if not bypass_eod_check:
            try:
                latest_eod = STTB_Dates.objects.latest('date_id')
            except STTB_Dates.DoesNotExist:
                return Response({
                    "available": False,
                    "reason": "No EOD records found."
                }, status=status.HTTP_200_OK)

            latest_next_working = latest_eod.next_working_Day.astimezone(tz).date()
            if latest_next_working != today:
                return Response({
                    "available": False,
                    "reason": f"ມື້ນີ້ວັນທີ ({today}) ກະລຸນາປິດບັນຊີຂອງວັນທີ່ ({latest_next_working}) ກ່ອນດໍາເນີນການ."
                }, status=status.HTTP_200_OK)

            if latest_eod.eod_time != 'N':
                return Response({
                    "available": False,
                    "reason": "Journal already submitted for today."
                }, status=status.HTTP_200_OK)
        else:
            # Log that EOD check was bypassed
            bypass_reason = "EOD check bypassed (BACK_VALUE = 'Y')"

        # Prepare response reason
        if bypass_working_day and bypass_eod_check:
            reason = f"ມື້ນີ້ວັນທີ ({today}) ສາມາດບັນທຶກບັນຊີໄດ້. ອະນຸຍາດໃຫ້ບັນທຶກບັນຊີມື້ພັກ ເເລະ ລົງຍ້ອນຫຼັງໄດ້ (MOD_NO = 'Y', BACK_VALUE = 'Y')."
        elif bypass_working_day:
            reason = f"ມື້ນີ້ວັນທີ ({today}) ສາມາດບັນທຶກບັນຊີໄດ້. ອະນຸຍາດໃຫ້ບັນທຶກບັນຊີມື້ພັກໄດ້ (MOD_NO = 'Y')."
        elif bypass_eod_check:
            reason = f"ມື້ນີ້ວັນທີ ({today}) ສາມາດບັນທຶກບັນຊີໄດ້. ອະນຸຍາດໃຫ້ບັນທຶກບັນຊີຍ້ອນຫຼັງໄດ້ (BACK_VALUE = 'Y')."
        else:
            reason = f"ມື້ນີ້ວັນທີ ({today}) ສາມາດບັນທຶກບັນຊີໄດ້."

        # All checks passed or bypassed
        return Response({
            "available": True,
            "reason": reason,
            "bypass_info": {
                "working_day_bypassed": bypass_working_day,
                "eod_check_bypassed": bypass_eod_check
            }
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            "available": False,
            "reason": f"Error checking availability: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#---------Asset-------------
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from .models import (FA_Asset_Type,FA_Chart_Of_Asset,FA_Suppliers,FA_Location,FA_Expense_Category,FA_Asset_Lists,FA_Asset_List_Disposal,FA_Asset_Expense,FA_Transfer_Logs,FA_Asset_Photos,FA_Maintenance_Logs,
                     FA_Accounting_Method,FA_Asset_List_Depreciation_Main,FA_Asset_List_Depreciation,FA_Asset_List_Depreciation_InMonth)
from .serializers import (FAAssetTypeSerializer,FAChartOfAssetSerializer,FASuppliersSerializer,FALocationSerializer,FAExpenseCategorySerializer,
    FAAssetListSerializer,FAAssetListDisposalSerializer,FAAssetListDepreciationMainSerializer,FAAssetListDepreciationSerializer,
    FAAssetExpenseSerializer,FATransferLogsSerializer,FAAssetPhotosSerializer,FAMaintenanceLogsSerializer,FAAccountingMethodSerializer,FAAssetListDepreciationInMonthSerializer)
from django.utils import timezone
from django.db.models.functions import Substr

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
    
# class FADepreciationMainViewSet(viewsets.ModelViewSet):
#     serializer_class = FADepreciationMainSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         queryset = FA_Depreciation_Main.objects.all().order_by('dm_id')
#         dpca_type = self.request.query_params.get('dpca_type')
#         if dpca_type:
#             queryset = queryset.filter(dpca_type=dpca_type)
#         return queryset
    
#     def perform_create(self, serializer):
#         user = self.request.user
#         serializer.save(
#             Maker_Id=user,
#             Maker_DT_Stamp=timezone.now()
#         )

#     def perform_update(self, serializer):
#         user = self.request.user
#         serializer.save(
#             Checker_Id=user,
#             Checker_DT_Stamp=timezone.now()
#         )
    

# class FADepreciationSubViewSet(viewsets.ModelViewSet):
#     serializer_class = FADepreciationSubSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         queryset = FA_Depreciation_Sub.objects.all().order_by('ds_id')
#         m_id = self.request.query_params.get('m_id')
#         if m_id:
#             queryset = queryset.filter(m_id=m_id)
#         return queryset
    
#     def perform_create(self, serializer):
#         user = self.request.user
#         serializer.save(
#             Maker_Id=user,
#             Maker_DT_Stamp=timezone.now()
#         )

#     def perform_update(self, serializer):
#         user = self.request.user
#         serializer.save(
#             Checker_Id=user,
#             Checker_DT_Stamp=timezone.now()
#         )
    

class FAAssetListDepreciationMainViewSet(viewsets.ModelViewSet):
    serializer_class = FAAssetListDepreciationMainSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = FA_Asset_List_Depreciation_Main.objects.all().order_by('aldm_id')
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

# class FATransferLogsViewSet(viewsets.ModelViewSet):
#     serializer_class = FATransferLogsSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         queryset = FA_Transfer_Logs.objects.all().order_by('transfer_id')
#         asset_list_id = self.request.query_params.get('asset_list_id')
#         if asset_list_id:
#             queryset = queryset.filter(asset_list_id=asset_list_id)
#         return queryset
    
#     def perform_create(self, serializer):
#         user = self.request.user
#         serializer.save(
#             Maker_Id=user,
#             Maker_DT_Stamp=timezone.now()
#         )

#     def perform_update(self, serializer):
#         user = self.request.user
#         serializer.save(
#             Checker_Id=user,
#             Checker_DT_Stamp=timezone.now()
#         )
# ເພີ່ມ imports ໃນດ້ານເທິງຂອງ file
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import FA_Transfer_Logs, FA_Asset_Lists  # ເພີ່ມ imports ເຫຼົ່ານີ້
from .serializers import FATransferLogsSerializer

class FATransferLogsViewSet(viewsets.ModelViewSet):
    queryset = FA_Transfer_Logs.objects.all()
    serializer_class = FATransferLogsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = FA_Transfer_Logs.objects.all().order_by('transfer_id')
        asset_list_id = self.request.query_params.get('asset_list_id')
        if asset_list_id:
            queryset = queryset.filter(asset_list_id=asset_list_id)
        return queryset

    def perform_create(self, serializer):
        from django.db import transaction
        import logging
        
        logger = logging.getLogger(__name__)
        user = self.request.user
        
        with transaction.atomic():
            # ບັນທຶກ transfer log
            transfer_log = serializer.save(
                Maker_Id=user,
                Maker_DT_Stamp=timezone.now()
            )
            
            logger.info(f"Transfer log created: {transfer_log.transfer_id}")
            
            try:
                # Debug: ກວດສອບ transfer_log ກ່ອນ
                print(f"🔍 Transfer log asset_list_id: {transfer_log.asset_list_id}")
                print(f"🔍 Transfer log asset_list_id type: {type(transfer_log.asset_list_id)}")
                print(f"🔍 Transfer log asset_list_id pk: {transfer_log.asset_list_id.pk if transfer_log.asset_list_id else 'None'}")
                
                # ກວດສອບວ່າ asset_list_id ບໍ່ເປັນ None
                if not transfer_log.asset_list_id:
                    raise ValueError("Asset list ID is None")
                
                # ໃຊ້ asset object ທີ່ມີຢູ່ແລ້ວ
                asset_obj = transfer_log.asset_list_id
                
                # ຫຼື ລອງ get ແບບລະມັດລະວັງ
                try:
                    asset_obj_fresh = FA_Asset_Lists.objects.get(asset_list_id=asset_obj.asset_list_id)
                    print(f"✅ Successfully got fresh asset object: {asset_obj_fresh.asset_list_id}")
                    asset_obj = asset_obj_fresh
                except FA_Asset_Lists.DoesNotExist:
                    print(f"⚠️ Could not get fresh asset, using existing: {asset_obj.asset_list_id}")
                    # ໃຊ້ asset object ທີ່ມີຢູ່ແລ້ວ
                
                old_location = asset_obj.asset_location_id
                new_location = transfer_log.to_location_id
                
                print(f"🔥 Asset ID: {asset_obj.asset_list_id}")
                print(f"🔥 Old location: {old_location}")
                print(f"🔥 New location: {new_location}")
                print(f"🔥 New location type: {type(new_location)}")
                
                # ອັບເດດສະຖານທີ່
                asset_obj.asset_location_id = new_location
                
                # ບັງຄັບບັນທຶກດ້ວຍ update_fields
                asset_obj.save(update_fields=['asset_location_id'])
                
                # ກວດສອບວ່າອັບເດດແລ້ວຈິງບໍ
                asset_obj.refresh_from_db()
                
                print(f"✅ Asset location updated from {old_location} to {asset_obj.asset_location_id}")
                logger.info(f"Asset {asset_obj.asset_list_id} moved from {old_location} to {asset_obj.asset_location_id}")
                
            except FA_Asset_Lists.DoesNotExist:
                error_msg = f"Asset not found: {transfer_log.asset_list_id}"
                logger.error(error_msg)
                raise ValueError(error_msg)
                
            except Exception as e:
                error_msg = f"Failed to update asset location: {e}"
                logger.error(error_msg)
                print(f"❌ ERROR: {error_msg}")
                import traceback
                print(traceback.format_exc())
                raise

    # ເພີ່ມ method ນີ້ເພື່ອກວດສອບຫຼັງການອັບເດດ
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        
        # ກວດສອບວ່າການອັບເດດສຳເລັດແລ້ວ
        if response.status_code == 201:
            transfer_log_id = response.data.get('transfer_id')
            if transfer_log_id:
                try:
                    
                    from .models import FA_Transfer_Logs  
                    transfer_log = FA_Transfer_Logs.objects.get(pk=transfer_log_id)
                    asset = transfer_log.asset_list_id
                    
                    print(f"🔍 Final verification - Asset {asset.asset_list_id} location: {asset.asset_location_id}")
                    
                except Exception as e:
                    print(f"⚠️ Verification failed: {e}")
        
        return response
    
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

# class FAAccountingMethodViewSet(viewsets.ModelViewSet):
#     serializer_class = FAAccountingMethodSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         queryset = FA_Accounting_Method.objects.all().order_by('mapping_id')
#         acc_type = self.request.query_params.get('acc_type')
#         if acc_type:
#             queryset = queryset.filter(acc_type=acc_type)
#         return queryset
    
#     def perform_create(self, serializer):
#         user = self.request.user
#         serializer.save(
#             Maker_Id=user,
#             Maker_DT_Stamp=timezone.now()
#         )

#     def perform_update(self, serializer):
#         user = self.request.user
#         serializer.save(
#             Checker_Id=user,
#             Checker_DT_Stamp=timezone.now()
#         )
from django.http import Http404
from rest_framework import status
from rest_framework.response import Response
from django.db import IntegrityError, transaction
from django.utils import timezone
from SAMCSYS.models import MTTB_GLSub, MTTB_GLMaster  # ເພີ່ມ MTTB_GLMaster

class FAAccountingMethodViewSet(viewsets.ModelViewSet):
    serializer_class = FAAccountingMethodSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = FA_Accounting_Method.objects.all().order_by('mapping_id')
        acc_type = self.request.query_params.get('acc_type')
        if acc_type:
            queryset = queryset.filter(acc_type=acc_type)
        return queryset
    
    def create_glsub_record(self, account_code, description):
        """ສ້າງ record ໃໝ່ໃນ MTTB_GLSub"""
        try:
           
            if '.' in account_code:
                gl_code = account_code.split('.')[0]
            else:
                gl_code = account_code
            
           
            try:
                gl_master = MTTB_GLMaster.objects.get(gl_code=gl_code)
                gl_code_id = gl_master.glid  
            except MTTB_GLMaster.DoesNotExist:
                raise ValueError(f"ບໍ່ພົບ gl_code '{gl_code}' ໃນ MTTB_GLMaster")
            
            
            glsub_record = MTTB_GLSub.objects.create(
                glsub_code=account_code,
                glsub_Desc_la=description,
                gl_code_id=gl_code_id,
                Maker_Id=self.request.user,
                Maker_DT_Stamp=timezone.now(),
                Record_Status='O',
                Auth_Status='A'   
               
            )
            
            return glsub_record
            
        except Exception as e:
            raise Exception(f"ຜິດພາດໃນການສ້າງ GLSub: {str(e)}")
    
    def create(self, request, *args, **kwargs):
        """Override create method ເພື່ອກວດສອບແລະສ້າງ GLSub records"""
        
        
        debit_account_id = request.data.get('debit_account_id')
        credit_account_id = request.data.get('credit_account_id')
        description = request.data.get('description', '')  # ສຳລັບ glsub_Desc_la
        
        
        if not debit_account_id or not credit_account_id:
            return Response(
                {'error': 'debit_account_id ແລະ credit_account_id ຈຳເປັນຕ້ອງມີ'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
           
            with transaction.atomic():
                
                
                debit_exists = MTTB_GLSub.objects.filter(glsub_code=debit_account_id).exists()
                credit_exists = MTTB_GLSub.objects.filter(glsub_code=credit_account_id).exists()
                
                if debit_exists:
                    return Response(
                        {
                            'error': f'debit_account_id "{debit_account_id}" ມີຢູ່ໃນລະບົບແລ້ວ',
                            'code': 'DUPLICATE_DEBIT_ACCOUNT'
                        }, 
                        status=status.HTTP_501_NOT_IMPLEMENTED
                    )
                
                if credit_exists:
                    return Response(
                        {
                            'error': f'credit_account_id "{credit_account_id}" ມີຢູ່ໃນລະບົບແລ້ວ',
                            'code': 'DUPLICATE_CREDIT_ACCOUNT'
                        }, 
                        status=status.HTTP_501_NOT_IMPLEMENTED
                    )
                
                
                try:
                    
                    debit_glsub = self.create_glsub_record(
                        debit_account_id, 
                        f" {description}"
                    )
                    
                    
                    credit_glsub = self.create_glsub_record(
                        credit_account_id, 
                        f" {description}"
                    )
                    
                    print(f"✅ ສ້າງ GLSub records ສຳເລັດ: {debit_glsub.glsub_code}, {credit_glsub.glsub_code}")
                    
                except Exception as e:
                    return Response(
                        {'error': f'ຜິດພາດໃນການສ້າງ GLSub records: {str(e)}'}, 
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
                
                
                response = super().create(request, *args, **kwargs)
                
                
                if response.status_code == 201:
                    response.data['glsub_created'] = {
                        'debit_account': debit_account_id,
                        'credit_account': credit_account_id,
                        'message': 'GLSub records ຖືກສ້າງສຳເລັດ'
                    }
                
                return response
                
        except Exception as e:
            return Response(
                {'error': f'ຜິດພາດໃນການດຳເນີນການ: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def perform_create(self, serializer):
        """ບັນທຶກຂໍ້ມູນພ້ອມ Maker info"""
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
    
class FAAssetListDepreciationInMonthViewSet(viewsets.ModelViewSet):
    serializer_class = FAAssetListDepreciationInMonthSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = FA_Asset_List_Depreciation_InMonth.objects.all()

        # แยกปีและเดือนจาก string "MM-YYYY"
        queryset = queryset.annotate(
            dpca_year=Substr('dpca_month', 4, 4),     # 'YYYY'
            dpca_month_num=Substr('dpca_month', 1, 2) # 'MM'
        ).order_by('-dpca_year', '-dpca_month_num')   # เรียงจากล่าสุดไปเก่าสุด

        dpca_status = self.request.query_params.get('dpca_status')
        if dpca_status:
            queryset = queryset.filter(dpca_status=dpca_status)

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
from django.db import transaction
import logging
from .models import MTTB_EOC_MAINTAIN, STTB_EOC_DAILY_LOG, MTTB_Function_Desc
from .serializers import EOCMaintainSerializer

logger = logging.getLogger(__name__)

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
    search_fields = ['eoc_type', 'module_id__module_name', 'function_id__description_la']
    ordering_fields = ['eoc_id', 'eoc_seq_no', 'Maker_DT_Stamp', 'Checker_DT_Stamp']
    ordering = ['eoc_seq_no', 'eoc_id']  # Changed to order by sequence first

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
            Maker_Id_id=user_id,
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
        """ເປີດ record (Record_Status = 'O') - ເປີດໃຫ້ປະມວນຜົນໃນ EOD"""
        obj = self.get_object()
        
        if obj.Record_Status == 'O':
            return Response({
                'message': 'Record ເປີດຢູ່ແລ້ວ'
            }, status=status.HTTP_200_OK)
        
        if obj.Auth_Status != 'A':
            return Response({
                'error': 'ບໍ່ສາມາດເປີດໄດ້. ສາມາດເປີດໄດ້ເມື່ອ record ຖືກອະນຸມັດແລ້ວເທົ່ານັ້ນ (Auth_Status = "A")'
            }, status=status.HTTP_400_BAD_REQUEST)

        obj.Record_Status = 'O'
        obj.Checker_Id_id = getattr(request.user, 'user_id', None)
        obj.Checker_DT_Stamp = timezone.now()
        obj.save()
        
        serializer = self.get_serializer(obj)
        return Response({
            'message': f'ເປີດຟັງຊັນ {obj.function_id.description_la} ສໍາເລັດແລ້ວ - ຈະຖືກປະມວນຜົນໃນ EOD',
            'data': serializer.data
        })

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def set_close(self, request, pk=None):
        """ປິດ record (Record_Status = 'C') - ປິດບໍ່ໃຫ້ປະມວນຜົນໃນ EOD"""
        obj = self.get_object()

        if obj.Record_Status == 'C':
            return Response({
                'message': 'Record ປິດຢູ່ແລ້ວ'
            }, status=status.HTTP_200_OK)

        obj.Record_Status = 'C'
        obj.Checker_Id_id = getattr(request.user, 'user_id', None)
        obj.Checker_DT_Stamp = timezone.now()
        obj.save()
        
        serializer = self.get_serializer(obj)
        return Response({
            'message': f'ປິດຟັງຊັນ {obj.function_id.description_la} ສໍາເລັດແລ້ວ - ຈະບໍ່ຖືກປະມວນຜົນໃນ EOD',
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

        # Set Auth_Status = 'A', Once_Auth = 'Y', keep current Record_Status
        eoc_entry.Auth_Status = 'A'
        eoc_entry.Once_Auth = 'Y'
        eoc_entry.Checker_Id_id = getattr(request.user, 'user_id', None)
        eoc_entry.Checker_DT_Stamp = timezone.now()
        eoc_entry.save()

        serializer = self.get_serializer(eoc_entry)
        return Response({
            'message': f'ອະນຸມັດຟັງຊັນ {eoc_entry.function_id.description_la} ສໍາເລັດແລ້ວ',
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

        # Set Auth_Status = 'U', Record_Status = 'C' (closed for safety)
        eoc_entry.Auth_Status = 'U'
        eoc_entry.Record_Status = 'C'
        eoc_entry.Checker_Id_id = getattr(request.user, 'user_id', None)
        eoc_entry.Checker_DT_Stamp = timezone.now()
        eoc_entry.save()

        serializer = self.get_serializer(eoc_entry)
        return Response({
            'message': f'ຍົກເລີກການອະນຸມັດຟັງຊັນ {eoc_entry.function_id.description_la} ສໍາເລັດແລ້ວ',
            'data': serializer.data
        })

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def eod_status(self, request):
        """ກວດສອບສະຖານະຟັງຊັນ EOD ທັງໝົດ"""
        eod_functions = MTTB_EOC_MAINTAIN.objects.filter(
            eoc_type='EOD'
        ).select_related('function_id', 'module_id').order_by('eoc_seq_no')

        if not eod_functions.exists():
            return Response({
                'message': 'ບໍ່ພົບຟັງຊັນ EOD',
                'functions': []
            })

        functions_data = []
        total_functions = eod_functions.count()
        authorized_functions = 0
        open_functions = 0
        ready_for_execution = 0

        for func in eod_functions:
            is_authorized = func.Auth_Status == 'A'
            is_open = func.Record_Status == 'O'
            is_ready = is_authorized and is_open

            if is_authorized:
                authorized_functions += 1
            if is_open:
                open_functions += 1
            if is_ready:
                ready_for_execution += 1

            functions_data.append({
                'eoc_id': func.eoc_id,
                'sequence': func.eoc_seq_no,
                'function_name': func.function_id.description_la,
                'function_id': func.function_id.function_id,
                'module_name': func.module_id.module_name if func.module_id else None,
                'record_status': func.Record_Status,
                'auth_status': func.Auth_Status,
                'is_authorized': is_authorized,
                'is_open': is_open,
                'will_execute': is_ready,
                'status_text': self._get_status_text(func.Record_Status, func.Auth_Status)
            })

        return Response({
            'summary': {
                'total_functions': total_functions,
                'authorized_functions': authorized_functions,
                'open_functions': open_functions,
                'ready_for_execution': ready_for_execution,
                'can_start_eod': ready_for_execution > 0 or total_functions == 0
            },
            'functions': functions_data
        })

    def _get_status_text(self, record_status, auth_status):
        """ສ້າງຂໍ້ຄວາມສະຖານະເປັນພາສາລາວ"""
        if auth_status != 'A':
            return 'ຍັງບໍ່ໄດ້ອະນຸມັດ'
        elif record_status == 'O':
            return 'ພ້ອມປະມວນຜົນ'
        elif record_status == 'C':
            return 'ປິດ - ຈະບໍ່ປະມວນຜົນ'
        else:
            return 'ສະຖານະບໍ່ຮູ້ຈັກ'

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def bulk_open(self, request):
        """ເປີດຟັງຊັນ EOD ທັງໝົດທີ່ຖືກອະນຸມັດແລ້ວ"""
        try:
            with transaction.atomic():
                eod_functions = MTTB_EOC_MAINTAIN.objects.filter(
                    eoc_type='EOD',
                    Auth_Status='A',
                    Record_Status='C'
                )

                if not eod_functions.exists():
                    return Response({
                        'message': 'ບໍ່ມີຟັງຊັນທີ່ສາມາດເປີດໄດ້'
                    })

                user_id = getattr(request.user, 'user_id', None)
                update_time = timezone.now()

                updated_count = eod_functions.update(
                    Record_Status='O',
                    Checker_Id_id=user_id,
                    Checker_DT_Stamp=update_time
                )

                return Response({
                    'message': f'ເປີດຟັງຊັນ EOD ສໍາເລັດ: {updated_count} ຟັງຊັນ',
                    'updated_count': updated_count
                })

        except Exception as e:
            logger.error(f"Error in bulk_open: {str(e)}")
            return Response({
                'error': f'ເກີດຂໍ້ຜິດພາດ: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def bulk_close(self, request):
        """ປິດຟັງຊັນ EOD ທັງໝົດ"""
        try:
            with transaction.atomic():
                eod_functions = MTTB_EOC_MAINTAIN.objects.filter(
                    eoc_type='EOD',
                    Record_Status='O'
                )

                if not eod_functions.exists():
                    return Response({
                        'message': 'ບໍ່ມີຟັງຊັນທີ່ສາມາດປິດໄດ້'
                    })

                user_id = getattr(request.user, 'user_id', None)
                update_time = timezone.now()

                updated_count = eod_functions.update(
                    Record_Status='C',
                    Checker_Id_id=user_id,
                    Checker_DT_Stamp=update_time
                )

                return Response({
                    'message': f'ປິດຟັງຊັນ EOD ສໍາເລັດ: {updated_count} ຟັງຊັນ',
                    'updated_count': updated_count
                })

        except Exception as e:
            logger.error(f"Error in bulk_close: {str(e)}")
            return Response({
                'error': f'ເກີດຂໍ້ຜິດພາດ: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Keep your existing bulk_journal method but it's now called by the main EOD process
    @action(detail=False, methods=['post'], url_path='bulk-journal', permission_classes=[IsAuthenticated])
    def bulk_journal(self, request, pk=None):
        """
        Legacy method - now this is called automatically by the main EOD process
        But kept for backward compatibility or manual execution
        """
        try:
            from views import execute_bulk_journal
            
            # Create a mock eod_function object for the call
            class MockEODFunction:
                function_id = type('obj', (object,), {'function_id': 'EOD_JOURNAL'})
            
            success, message = execute_bulk_journal(MockEODFunction(), request.user)
            
            if success:
                return Response({
                    'status': 'success',
                    'message': message
                })
            else:
                return Response({
                    'status': 'error',
                    'message': message
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Error in bulk_journal: {str(e)}")
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
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
    
from rest_framework import viewsets
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
# =====================================
# ຟັງຊັ້ນຄິດຄ່າເສື່ອມລາຄາ Backend ເທົ່ານັ້ນ
# ເພີ່ມໃນ views.py ຂອງທ່ານ
# =====================================

import json
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from decimal import Decimal, ROUND_HALF_UP
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db import transaction

# Import models ຂອງທ່ານ - ເພີ່ມຕາຕະລາງປະຫວັດ
from .models import (
    FA_Accounting_Method, 
    FA_Asset_Lists,
    FA_Asset_List_Depreciation_Main,
    FA_Asset_List_Depreciation,
    MTTB_Users
)

# =====================================
# Utility Functions
# =====================================

def get_last_day_of_month(year, month):
    """ຫາວັນສຸດທ້າຍຂອງເດືອນ"""
    if month == 12:
        return (datetime(year + 1, 1, 1) - timedelta(days=1)).day
    else:
        return (datetime(year, month + 1, 1) - timedelta(days=1)).day

def get_month_name_la(month_num):
    """ຊື່ເດືອນເປັນພາສາລາວ"""
    months = {
        1: 'ມັງກອນ', 2: 'ກຸມພາ', 3: 'ມີນາ', 4: 'ເມສາ',
        5: 'ພຶດສະພາ', 6: 'ມິຖຸນາ', 7: 'ກໍລະກົດ', 8: 'ສິງຫາ',
        9: 'ກັນຍາ', 10: 'ຕຸລາ', 11: 'ພະຈິກ', 12: 'ທັນວາ'
    }
    return months.get(month_num, f'ເດືອນ {month_num}')


def get_current_user_id():
    """ຫາ user_id ປັດຈຸບັນ - ແກ້ໄຂແລ້ວ"""
    try:
        first_user = MTTB_Users.objects.first()
        if first_user:
            return first_user.user_id
        else:
            return None
    except Exception as e:
        print(f"Get user error: {str(e)}")
        return None

def validate_user_id(user_id):
    """ກວດສອບວ່າ user_id ມີຢູ່ບໍ"""
    if not user_id:
        return None
    try:
        user = MTTB_Users.objects.get(user_id=user_id)
        return user.user_id
    except MTTB_Users.DoesNotExist:
        print(f"User ID {user_id} ບໍ່ມີຢູ່")
        return None
    except Exception as e:
        print(f"Validate user error: {str(e)}")
        return None
# =====================================
# History Recording Functions
# =====================================

def create_depreciation_history(asset, depreciation_data, user_id=None):
    """
    ສ້າງປະຫວັດການຫັກຄ່າເສື່ອມລາຄາໃນທັງ 2 ຕາຕະລາງ - ມີການ UPDATE/INSERT
    """
    try:
        if user_id:
            validated_user_id = validate_user_id(user_id)
        else:
            validated_user_id = get_current_user_id()
        
        if not validated_user_id:
            print("Warning: ບໍ່ມີ user_id ທີ່ຖືກຕ້ອງ - ຈະບັນທຶກໂດຍບໍ່ມີ user")
        
        current_time = datetime.now()
        depreciation_date = depreciation_data['period_start']
        
        description = f"ຫັກຄ່າເສື່ອມລາຄາເດືອນທີ່ {depreciation_data['month_number']} ({depreciation_data['month_year']})"
        
        main_record_data = {
            'asset_list_id': asset,
            'dpca_year': str(depreciation_date.year),
            'dpca_month': f"{depreciation_date.year}-{depreciation_date.month:02d}",
            'dpca_date': depreciation_date,
            'dpca_value': Decimal(str(depreciation_data['monthly_depreciation'])),
            'dpca_no_of_days': depreciation_data['days_count'],
            'remaining_value': Decimal(str(depreciation_data['remaining_value'])),
            'accumulated_dpca': Decimal(str(depreciation_data['new_accumulated'])),
            'dpca_desc': description,
            'dpca_ac_yesno': 'N',
            'dpca_datetime': current_time,
            'Record_Status': 'C',
        }
        
        if validated_user_id:
            main_record_data['Maker_Id_id'] = validated_user_id
            main_record_data['Maker_DT_Stamp'] = current_time
        
        main_record = FA_Asset_List_Depreciation_Main.objects.create(**main_record_data)
        
        existing_record = FA_Asset_List_Depreciation.objects.filter(
            asset_list_id=asset
        ).order_by('-dpca_date').first()
        
        detail_record_data = {
            'dpca_date': depreciation_date,
            'dpca_value': Decimal(str(depreciation_data['monthly_depreciation'])),
            'dpca_no_of_days': depreciation_data['days_count'],
            'remaining_value': Decimal(str(depreciation_data['remaining_value'])),
            'accumulated_dpca': Decimal(str(depreciation_data['new_accumulated'])),
            'dpca_desc': description,
            'dpca_ac_yesno': 'N',
            'dpca_datetime': current_time,
            'Record_Status': 'C',
        }
        
        if validated_user_id:
            detail_record_data['Maker_Id_id'] = validated_user_id
            detail_record_data['Maker_DT_Stamp'] = current_time
        
        if existing_record:
            for key, value in detail_record_data.items():
                setattr(existing_record, key, value)
            existing_record.save()
            detail_record_id = existing_record.ald_id
            operation_type = "UPDATE"
        else:
            detail_record_data['asset_list_id'] = asset
            detail_record = FA_Asset_List_Depreciation.objects.create(**detail_record_data)
            detail_record_id = detail_record.ald_id
            operation_type = "INSERT"
        
        return {
            'main_record_id': main_record.aldm_id,
            'detail_record_id': detail_record_id,
            'detail_operation': operation_type,
            'success': True,
            'user_id_used': validated_user_id
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f"History recording error: {str(e)}"
        }


def get_depreciation_history(asset_list_id, limit=None):
    """
    ດຶງປະຫວັດການຫັກຄ່າເສື່ອມລາຄາ
    """
    try:
        # ດຶງຈາກຕາຕະລາງຫຼັກ
        query = FA_Asset_List_Depreciation_Main.objects.filter(
            asset_list_id=asset_list_id
        ).order_by('-dpca_date')
        
        if limit:
            query = query[:limit]
        
        history = []
        for record in query:
            history.append({
                'aldm_id': record.aldm_id,
                'year': record.dpca_year,
                'month': record.dpca_month,
                'date': record.dpca_date.strftime('%d/%m/%Y'),
                'depreciation_value': float(record.dpca_value or 0),
                'days_count': record.dpca_no_of_days,
                'remaining_value': float(record.remaining_value or 0),
                'accumulated_dpca': float(record.accumulated_dpca or 0),
                'description': record.dpca_desc,
                'is_accounted': record.dpca_ac_yesno == 'Y',
                'account_date': record.dpca_ac_date.strftime('%d/%m/%Y') if record.dpca_ac_date else None,
                'created_datetime': record.dpca_datetime.strftime('%d/%m/%Y %H:%M:%S') if record.dpca_datetime else None,
                'record_status': record.Record_Status
            })
        
        return {
            'success': True,
            'history': history,
            'total_records': len(history)
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f"Get history error: {str(e)}"
        }

def mark_depreciation_as_accounted(aldm_id, user_id=None):
    """
    ໝາຍການຫັກຄ່າເສື່ອມລາຄາວ່າບັນຊີແລ້ວ - ແກ້ໄຂແລ້ວ
    """
    try:
        # ✅ ກວດສອບ user_id
        if user_id:
            validated_user_id = validate_user_id(user_id)
        else:
            validated_user_id = get_current_user_id()
        
        current_time = datetime.now()
        
        # ອັບເດດຕາຕະລາງຫຼັກ
        main_record = FA_Asset_List_Depreciation_Main.objects.get(aldm_id=aldm_id)
        main_record.dpca_ac_yesno = 'Y'
        main_record.dpca_ac_date = current_time.date()
        
        # ✅ ເພີ່ມ user ຖ້າມີ
        if validated_user_id:
            main_record.dpca_ac_by = validated_user_id
            main_record.Checker_Id_id = validated_user_id
            main_record.Checker_DT_Stamp = current_time
        
        main_record.save()
        
        # ອັບເດດຕາຕະລາງລາຍລະອຽດທີ່ກ່ຽວຂ້ອງ
        update_data = {
            'dpca_ac_yesno': 'Y',
            'dpca_ac_date': current_time.date(),
        }
        
        # ✅ ເພີ່ມ user ຖ້າມີ
        if validated_user_id:
            update_data['dpca_ac_by'] = validated_user_id
            update_data['Checker_Id_id'] = validated_user_id
            update_data['Checker_DT_Stamp'] = current_time
        
        FA_Asset_List_Depreciation.objects.filter(
            asset_list_id=main_record.asset_list_id,
            dpca_date=main_record.dpca_date,
            dpca_value=main_record.dpca_value
        ).update(**update_data)
        
        return {
            'success': True,
            'message': f'ໝາຍບັນຊີສຳເລັດ - Record ID: {aldm_id}',
            'user_id_used': validated_user_id
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f"Mark as accounted error: {str(e)}"
        }

# =====================================
# Main Calculation Function  
# =====================================

def calculate_depreciation_schedule(mapping_id):
    """
    ຟັງຊັ້ນຄິດຄ່າເສື່ອມລາຄາ - ວິທີແກ້: 90k → 0
    """
    try:
        try:
            accounting_method = FA_Accounting_Method.objects.get(mapping_id=mapping_id)
        except FA_Accounting_Method.DoesNotExist:
            return {"error": f"ບໍ່ພົບ mapping_id: {mapping_id}"}
        
        try:
            if accounting_method.asset_list_id:
                asset = accounting_method.asset_list_id
            elif accounting_method.ref_id:
                asset = FA_Asset_Lists.objects.get(asset_list_id=accounting_method.ref_id)
            else:
                return {"error": "ບໍ່ມີຂໍ້ມູນ asset_list_id ຫຼື ref_id"}
        except FA_Asset_Lists.DoesNotExist:
            return {"error": f"ບໍ່ພົບຊັບສິນ: {accounting_method.ref_id}"}
        
        if not asset.asset_value:
            return {"error": "ບໍ່ມີມູນຄ່າຊັບສິນ"}
        if not asset.asset_useful_life:
            return {"error": "ບໍ່ມີອາຍຸການໃຊ້ງານ"}
        if not accounting_method.transaction_date:
            return {"error": "ບໍ່ມີວັນທີເລີ່ມຕົ້ນ"}
        
        original_asset_value = float(asset.asset_value)
        original_salvage_value = float(asset.asset_salvage_value or 0)
        total_depreciable = float(asset.accu_dpca_value_total or 0)
        useful_life = int(asset.asset_useful_life)
        accu_dpca_value_total=int(asset.accu_dpca_value_total)
        start_date = accounting_method.transaction_date
        
        virtual_asset_value = total_depreciable
        virtual_salvage_value = 0
        
        end_date = start_date + relativedelta(years=useful_life) - timedelta(days=1)
        total_days = (end_date - start_date + timedelta(days=1)).days
        
        depreciable_amount = virtual_asset_value - virtual_salvage_value
        daily_depreciation = depreciable_amount / total_days
        
        current_count = int(asset.C_dpac or 0)
        total_months = useful_life * 12
        remaining_months = total_months - current_count
        can_depreciate = current_count < total_months
        is_completed = current_count >= total_months
        
        # ຄິດຄ່າເສື່ອມລາຄາສຳລັບຕົວຢ່າງເດືອນຕ່າງໆໂດຍໃຊ້ຈຳນວນມື້ຕົວຈິງ
        monthly_examples = {}
        current_date = start_date
        for month_offset in range(3):  # ສະແດງຕົວຢ່າງ 3 ເດືອນ
            month_start = current_date + relativedelta(months=month_offset)
            month_end = datetime(month_start.year, month_start.month,
                               get_last_day_of_month(month_start.year, month_start.month)).date()
            if month_end > end_date:
                month_end = end_date
            days_in_month = (month_end - month_start + timedelta(days=1)).days
            monthly_depreciation = daily_depreciation * days_in_month
            monthly_examples[f"month_{month_offset + 1}"] = {
                'period': f"{month_start.strftime('%d/%m/%Y')} - {month_end.strftime('%d/%m/%Y')}",
                'days': days_in_month,
                'depreciation': round(monthly_depreciation, 2)
            }
        
        history_result = get_depreciation_history(asset.asset_list_id, limit=5)
        
        result = {
            'asset_info': {
                'asset_id': asset.asset_list_id,
                'asset_name': asset.asset_spec or 'N/A',
                'original_asset_value': original_asset_value,
                'original_salvage_value': original_salvage_value,
                'virtual_asset_value': virtual_asset_value,
                'virtual_salvage_value': virtual_salvage_value,
                'useful_life': useful_life,
                'depreciation_method': asset.dpca_type or 'SL',
                'calculation_note': '🎯 ໃຊ້ accu_dpca_value_total ຄຳນວນເພື່ອໃຫ້ Remaining = 0'
            },
            'calculation_info': {
                'start_date': start_date.strftime('%d/%m/%Y'),
                'end_date': end_date.strftime('%d/%m/%Y'),
                'total_days': total_days,
                'depreciable_amount': round(depreciable_amount, 2),
                'daily_depreciation': round(daily_depreciation, 2),
                'final_target_value': 0,
                'calculation_method': f'ຫັກ {virtual_asset_value:,.0f} ກີບ ໃນ {total_days} ວັນ → Remaining = 0',
                'logic_explanation': {
                    'step1': f'ເອົາ accu_dpca_value_total = {total_depreciable:,.0f} ກີບ',
                    'step2': f'ຄຳນວນເປັນມື້ = {total_depreciable:,.0f} ÷ {total_days} = {daily_depreciation:.2f} ກີບ/ມື້',
                    'step3': f'ຫັກຄົບແລ້ວ: Accumulated = {total_depreciable:,.0f}, Remaining = 0'
                }
            },
            'depreciation_status': {
                'total_months': total_months,
                'current_count': current_count,
                'remaining_months': remaining_months,
                'can_depreciate': can_depreciate,
                'is_completed': is_completed,
                'completion_percentage': round((current_count / total_months) * 100, 2),
                'status_message': get_status_message_90k_to_zero(current_count, total_months, total_depreciable)
            },
            'monthly_examples': monthly_examples,  # ໃຊ້ຈຳນວນມື້ຕົວຈິງ
            'accounting_method': {
                'mapping_id': accounting_method.mapping_id,
                'ref_id': accounting_method.ref_id,
                'transaction_date': accounting_method.transaction_date.strftime('%d/%m/%Y')
            },
            'depreciation_history': history_result if history_result['success'] else []
        }
        
        return result
        
    except Exception as e:
        return {"error": f"General error: {str(e)}"}

    
def get_status_message_90k_to_zero(current_count, total_months, target_accumulated):
    """ສ້າງຂໍ້ຄວາມສະຖານະ - ສຳລັບ 90k → 0"""
    if current_count >= total_months:
        return f"✅ ຫັກຄົບ {target_accumulated:,.0f} ກີບ! ມູນຄ່າຄົງເຫຼືອ = 0 ({current_count}/{total_months} ເດືອນ)"
    elif current_count == 0:
        return f"🆕 ຍັງບໍ່ໄດ້ເລີ່ມຫັກ (0/{total_months} ເດືອນ) - ຈະຫັກ {target_accumulated:,.0f} ກີບ → 0"
    else:
        remaining = total_months - current_count
        return f"⏳ ກຳລັງຫັກ ({current_count}/{total_months} ເດືອນ) - ເຫຼືອ {remaining} ເດືອນ ເພື່ອຫັກຄົບ {target_accumulated:,.0f} ກີບ → 0"


def get_status_message(current_count, total_months):
    """ສ້າງຂໍ້ຄວາມສະຖານະ"""
    if current_count >= total_months:
        return f"✅ ຫັກຄົບຖ້ວນແລ້ວ! ({current_count}/{total_months} ເດືອນ)"
    elif current_count == 0:
        return f"🆕 ຍັງບໍ່ໄດ້ເລີ່ມຫັກ (0/{total_months} ເດືອນ)"
    else:
        remaining = total_months - current_count
        return f"⏳ ກຳລັງຫັກ ({current_count}/{total_months} ເດືອນ) - ເຫຼືອ {remaining} ເດືອນ"

def process_monthly_depreciation(mapping_id, user_id=None):
    """ຫັກຄ່າເສື່ອມລາຄາ 1 ເດືອນ - ວິທີ Vue.js: ໃຊ້ຈຳນວນມື້ຕົວຈິງ, ຮັບປະກັນມູນຄ່າສະສົມຄົບ depreciable_amount"""
    try:
        # ກວດສອບສະຖານະກ່ອນ
        calc_result = calculate_depreciation_schedule(mapping_id)
        if 'error' in calc_result:
            return calc_result
        
        if not calc_result['depreciation_status']['can_depreciate']:
            return {
                "error": "ຫັກຄົບມູນຄ່າທີ່ສາມາດຫັກເສື່ອມໄດ້ແລ້ວ! ມູນຄ່າຄົງເຫຼືອ = salvage_value",
                "current_status": calc_result['depreciation_status']
            }
        
        # ດຶງຂໍ້ມູນ
        accounting_method = FA_Accounting_Method.objects.get(mapping_id=mapping_id)
        if accounting_method.asset_list_id:
            asset = accounting_method.asset_list_id
        else:
            asset = FA_Asset_Lists.objects.get(asset_list_id=accounting_method.ref_id)
        
   
        current_count = int(asset.C_dpac or 0)
        next_month = current_count + 1
        
        start_date = accounting_method.transaction_date
        useful_life = int(asset.asset_useful_life)
        total_months = useful_life * 12
        end_date = start_date + relativedelta(years=useful_life) - timedelta(days=1)
        
        # ✅ ຂໍ້ມູນພື້ນຖານ (ໃຊ້ Decimal ເພື່ອຄວາມແມ່ນຍຳ)
        asset_value = Decimal(str(asset.asset_value or 0))  
        accu_dpca_value_total = Decimal(str(asset.accu_dpca_value_total))
        salvage_value = Decimal(str(asset.asset_salvage_value or 0))  
        depreciable_amount = asset_value - salvage_value  
        
        # ຄ່າເສື່ອມຕໍ່ປີ ແລະ ຕໍ່ເດືອນ
        annual_depreciation = depreciable_amount / Decimal(str(useful_life))
        monthly_depreciation = (annual_depreciation / Decimal('12')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        # ✅ ກວດສອບວ່າເປັນເດືອນສຸດທ້າຍບໍ່
        is_last_month = (next_month == total_months)
        
        # ຄິດວັນທີ່ຂອງເດືອນທີ່ຈະຫັກ
        month_start_date = start_date + relativedelta(months=current_count)
        
        if next_month == 1:
            # ເດືອນທຳອິດ
            month_actual_start = start_date
            month_end = datetime(month_start_date.year, month_start_date.month,
                               get_last_day_of_month(month_start_date.year, month_start_date.month)).date()
        else:
            # ເດືອນອື່ນໆ
            month_actual_start = datetime(month_start_date.year, month_start_date.month, 1).date()
            month_end = datetime(month_start_date.year, month_start_date.month,
                               get_last_day_of_month(month_start_date.year, month_start_date.month)).date()
        
        # ກວດສອບວ່າເປັນເດືອນສຸດທ້າຍບໍ
        if month_end > end_date:
            month_end = end_date
        
        # ✅ ຄິດຈຳນວນມື້ຕົວຈິງ
        days_in_month = (month_end - month_actual_start + timedelta(days=1)).days
        total_days_in_month = get_last_day_of_month(month_start_date.year, month_start_date.month)
        
        # ✅ ການຄິດຄ່າເສື່ອມລາຄາໃໝ່ (ຕາມວິທີ Vue.js)
        old_accumulated = Decimal(str(asset.asset_accu_dpca_value or 0))
        
        if next_month == 1:
            # 🎯 ງວດທຳອິດ: ມູນຄ່າຕົ້ນງວດ
            setup_value = (monthly_depreciation * Decimal(str(days_in_month)) / Decimal(str(total_days_in_month))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            monthly_depreciation_value = setup_value
            end_value = (monthly_depreciation - setup_value).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            new_accumulated = monthly_depreciation_value
            new_remaining = accu_dpca_value_total - new_accumulated
            calculation_note = f"ງວດທຳອິດ - ມູນຄ່າຕົ້ນງວດ = ({monthly_depreciation:,.2f} × {days_in_month}) ÷ {total_days_in_month} = {monthly_depreciation_value:,.2f} ກີບ"
            
            print(f"🎯 ງວດທຳອິດ (ເດືອນທີ່ {next_month}):")
            print(f"   - ວັນໃຊ້ຈິງ: {days_in_month}/{total_days_in_month} ມື້")
            print(f"   - ຄ່າເສື່ອມຕໍ່ເດືອນ: {monthly_depreciation:,.2f}")
            print(f"   - ມູນຄ່າຕົ້ນງວດ: {setup_value:,.2f}")
            print(f"   - ມູນຄ່າທ້າຍງວດ: {end_value:,.2f}")
            print(f"   - Accumulated: {new_accumulated:,.2f}")
            print(f"   - Remaining: {new_remaining:,.2f}")
            
        elif is_last_month:
            # 🎯 ງວດສຸດທ້າຍ: ຄ່າເສື່ອມ = ມູນຄ່າທີ່ເຫຼືອຈົນກວ່າຈະຄົບ depreciable_amount
            remaining_to_depreciate = depreciable_amount - old_accumulated
            monthly_depreciation_value = remaining_to_depreciate.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            new_accumulated = old_accumulated + monthly_depreciation_value
            new_remaining = accu_dpca_value_total - new_accumulated
            end_value = Decimal('0')  # ບໍ່ມີມູນຄ່າທ້າຍງວດໃນເດືອນສຸດທ້າຍ
            calculation_note = f"ງວດສຸດທ້າຍ - ຫັກຄົບ {depreciable_amount:,.0f} ກີບ (ຄ່າເສື່ອມ = {monthly_depreciation_value:,.2f})"
            
            print(f"🎯 ງວດສຸດທ້າຍ (ເດືອນທີ່ {next_month}):")
            print(f"   - ເປົ້າໝາຍ: ຫັກຄົບ {depreciable_amount:,.0f} ກີບ")
            print(f"   - ຫັກມາແລ້ວ: {old_accumulated:,.2f}")
            print(f"   - ຄ່າເສື່ອມເດືອນນີ້: {monthly_depreciation_value:,.2f}")
            print(f"   - Accumulated: {new_accumulated:,.2f}")
            print(f"   - Remaining: {new_remaining:,.2f}")
            
        else:
         
            monthly_depreciation_value = (monthly_depreciation * Decimal(str(days_in_month)) / Decimal(str(total_days_in_month))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            new_accumulated = old_accumulated + monthly_depreciation_value
            new_remaining = accu_dpca_value_total - new_accumulated
            end_value = Decimal('0')  
            calculation_note = f"ງວດປົກກະຕິ - ຄ່າເສື່ອມ = ({monthly_depreciation:,.2f} × {days_in_month}) ÷ {total_days_in_month} = {monthly_depreciation_value:,.2f}"
            
            print(f"🎯 ງວດປົກກະຕິ (ເດືອນທີ່ {next_month}):")
            print(f"   - ວັນໃຊ້ຈິງ: {days_in_month}/{total_days_in_month} ມື້")
            print(f"   - ຄ່າເສື່ອມເດືອນນີ້: {monthly_depreciation_value:,.2f}")
            print(f"   - Accumulated: {new_accumulated:,.2f}")
            print(f"   - Remaining: {new_remaining:,.2f}")
        
        # 📝 ກວດສອບຄວາມຖືກຕ້ອງ
        if new_accumulated > depreciable_amount:
            monthly_depreciation_value = (monthly_depreciation_value - (new_accumulated - depreciable_amount)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            new_accumulated = depreciable_amount
            new_remaining = asset_value - new_accumulated
            calculation_note += f" | ປັບປ່ຽນເພື່ອໃຫ້ accumulated = {depreciable_amount:,.0f}"
        
        # 📝 ເກັບປະຫວັດ
        history_data = {
            'month_number': next_month,
            'month_year': f"{get_month_name_la(month_actual_start.month)} {month_actual_start.year}",
            'period_start': month_actual_start,
            'period_end': month_end,
            'days_count': days_in_month,
            'total_days_in_month': total_days_in_month,
            'monthly_depreciation': float(monthly_depreciation_value),
            'setup_value': float(setup_value) if next_month == 1 else None,
            'end_value': float(end_value) if next_month == 1 else None,
            'old_accumulated': float(old_accumulated),
            'new_accumulated': float(new_accumulated),
            'remaining_value': float(new_remaining)
        }
        
        
        history_result = create_depreciation_history(asset, history_data, user_id)
        
        if not history_result['success']:
            return {"error": f"ບັນທຶກປະຫວັດຜິດພາດ: {history_result['error']}"}
        
      
        asset.C_dpac = str(next_month)
        asset.asset_accu_dpca_value = new_accumulated
        asset.asset_value_remain = new_remaining
        asset.asset_latest_date_dpca = datetime.now().date()
        asset.save()
        
        return {
            'success': True,
            'depreciation_processed': {
                'month_number': next_month,
                'month_year': f"{get_month_name_la(month_actual_start.month)} {month_actual_start.year}",
                'period': f"{month_actual_start.strftime('%d/%m/%Y')} - {month_end.strftime('%d/%m/%Y')}",
                'days_count': days_in_month,
                'total_days_in_month': total_days_in_month,
                'monthly_depreciation': float(monthly_depreciation_value),
                'setup_value': float(setup_value) if next_month == 1 else None,
                'end_value': float(end_value) if next_month == 1 else None,
                'old_accumulated': float(old_accumulated),
                'new_accumulated': float(new_accumulated),
                'remaining_value': float(new_remaining),
                'is_final_month': is_last_month,
                'calculation_note': calculation_note,
                'target_achieved': f"ຫັກຄົບ {depreciable_amount:,.0f} ກີບ, Remaining = {salvage_value:,.0f}" if is_last_month else None
            },
            'history_records': {
                'main_record_id': history_result['main_record_id'],
                'detail_record_id': history_result['detail_record_id']
            },
            'updated_status': {
                'C_dpac': next_month,
                'total_months': total_months,
                'remaining_months': total_months - next_month,
                'is_completed': next_month >= total_months,
                'final_achieved': new_accumulated >= depreciable_amount and new_remaining <= salvage_value if is_last_month else None
            }
        }
        
    except Exception as e:
        return {"error": f"Process error: {str(e)}"}

# =====================================
# Bulk Processing Functions
# =====================================

def get_depreciable_assets():
    """ຫາລາຍການຊັບສິນທີ່ສາມາດຫັກໄດ້"""
    try:
        # ດຶງ accounting methods ທັງໝົດທີ່ມີການເຊື່ອມຕໍ່ກັບ assets
        accounting_methods = FA_Accounting_Method.objects.all()
        depreciable_items = []
        
        for method in accounting_methods:
            try:
                # ດຶງຂໍ້ມູນ asset
                if method.asset_list_id:
                    asset = method.asset_list_id
                elif method.ref_id:
                    asset = FA_Asset_Lists.objects.get(asset_list_id=method.ref_id)
                else:
                    continue
                
                # ກວດສອບວ່າຫັກໄດ້ບໍ
                if asset.asset_value and asset.asset_useful_life:
                    current_count = int(asset.C_dpac or 0)
                    total_months = int(asset.asset_useful_life) * 12
                    can_depreciate = current_count < total_months
                    
                    item_info = {
                        'mapping_id': method.mapping_id,
                        'asset_id': asset.asset_list_id,
                        'asset_name': asset.asset_spec or 'N/A',
                        'asset_value': float(asset.asset_value),
                        'current_count': current_count,
                        'total_months': total_months,
                        'remaining_months': total_months - current_count,
                        'can_depreciate': can_depreciate,
                        'completion_percentage': round((current_count / total_months) * 100, 2),
                        'status': get_status_message(current_count, total_months)
                    }
                    depreciable_items.append(item_info)
                    
            except Exception as e:
                continue  # ຂ້າມລາຍການທີ່ມີບັນຫາ
        
        # ແຍກລາຍການທີ່ຫັກໄດ້ ແລະ ຫັກບໍ່ໄດ້
        can_depreciate_items = [item for item in depreciable_items if item['can_depreciate']]
        cannot_depreciate_items = [item for item in depreciable_items if not item['can_depreciate']]
        
        return {
            'summary': {
                'total_items': len(depreciable_items),
                'can_depreciate': len(can_depreciate_items),
                'cannot_depreciate': len(cannot_depreciate_items)
            },
            'items': depreciable_items,
            'depreciable_items': can_depreciate_items,
            'completed_items': cannot_depreciate_items
        }
        
    except Exception as e:
        return {"error": f"Get depreciable assets error: {str(e)}"}

def process_bulk_depreciation(mapping_ids, check_only=False, user_id=None):
    """ຫັກຄ່າເສື່ອມລາຄາຫຼາຍລາຍການພ້ອມກັນ + ບັນທຶກປະຫວັດ - ແກ້ໄຂແລ້ວ"""
    try:
        results = []
        success_count = 0
        error_count = 0
        
        # ✅ ກວດສອບ user_id ໃນຕອນເລີ່ມຕົ້ນ
        if user_id:
            validated_user_id = validate_user_id(user_id)
            if not validated_user_id:
                print(f"Warning: User ID {user_id} ບໍ່ມີຢູ່ - ຈະດຳເນີນການໂດຍບໍ່ມີ user")
        else:
            validated_user_id = get_current_user_id()
        
        for mapping_id in mapping_ids:
            # ✅ ແຕ່ລະ mapping_id ໃຊ້ transaction ແຍກ
            try:
                with transaction.atomic():
                    if check_only:
                        # ແຕ່ກວດສອບເທົ່ານັ້ນ
                        calc_result = calculate_depreciation_schedule(mapping_id)
                        if 'error' in calc_result:
                            results.append({
                                'mapping_id': mapping_id,
                                'status': 'error',
                                'message': calc_result['error']
                            })
                            error_count += 1
                        else:
                            can_depreciate = calc_result['depreciation_status']['can_depreciate']
                            results.append({
                                'mapping_id': mapping_id,
                                'status': 'ready' if can_depreciate else 'completed',
                                'asset_name': calc_result['asset_info']['asset_name'],
                                'can_depreciate': can_depreciate,
                                'current_count': calc_result['depreciation_status']['current_count'],
                                'total_months': calc_result['depreciation_status']['total_months'],
                                'message': calc_result['depreciation_status']['status_message']
                            })
                            if can_depreciate:
                                success_count += 1
                    else:
                        # ຫັກຈິງໆ + ບັນທຶກປະຫວັດ
                        process_result = process_monthly_depreciation(mapping_id, validated_user_id)
                        if 'error' in process_result:
                            results.append({
                                'mapping_id': mapping_id,
                                'status': 'error',
                                'message': process_result['error']
                            })
                            error_count += 1
                        else:
                            results.append({
                                'mapping_id': mapping_id,
                                'status': 'success',
                                'message': f"ຫັກເດືອນທີ່ {process_result['depreciation_processed']['month_number']} ສຳເລັດ",
                                'depreciation_processed': process_result['depreciation_processed'],
                                'history_records': process_result.get('history_records', {})
                            })
                            success_count += 1
                            
            except Exception as e:
                results.append({
                    'mapping_id': mapping_id,
                    'status': 'error',
                    'message': f"Processing error: {str(e)}"
                })
                error_count += 1
        
        return {
            'summary': {
                'total_items': len(mapping_ids),
                'success_count': success_count,
                'error_count': error_count,
                'check_only': check_only,
                'user_id_used': validated_user_id
            },
            'details': results
        }
        
    except Exception as e:
        return {"error": f"Bulk processing error: {str(e)}"}

# =====================================
# ✅ SQL ສຳລັບກວດສອບ/ສ້າງ Users:
# =====================================
"""
-- ກວດສອບວ່າມີ user ຫຍັງຢູ່ບ້າງ:
SELECT user_id, username FROM SAMCSYS_mttb_users;

-- ຖ້າບໍ່ມີ user ໃດເລີຍ ໃຫ້ສ້າງ user ທົດລອງ:
INSERT INTO SAMCSYS_mttb_users (user_id, username, password, email, is_active) 
VALUES (1, 'admin', 'admin123', 'admin@example.com', 1);

-- ຫຼື ຫາ user_id ທີ່ມີຢູ່ແລ້ວ:
SELECT MIN(user_id) as first_user_id FROM SAMCSYS_mttb_users WHERE is_active = 1;
"""
# =====================================
# API ຄົບທຸກອັນໃນໂຕດຽວ - ເພີ່ມ History Management
# =====================================

@csrf_exempt
def calculate_depreciation_api(request):
    """
    API ຄິດຄ່າເສື່ອມລາຄາຄົບໃນໂຕດຽວ - ມີການເກັບປະຫວັດ
    
    Actions:
    - calculate: ຄິດຄ່າເສື່ອມລາຄາ + ສະຖານະ + ປະຫວັດ (ຕ້ອງມີ mapping_id)
    - process: ຫັກຄ່າເສື່ອມລາຄາ 1 ເດືອນ + ບັນທຶກປະຫວັດ (ຕ້ອງມີ mapping_id)
    - status: ເບິ່ງສະຖານະປັດຈຸບັນ (ຕ້ອງມີ mapping_id)
    - bulk_list: ລາຍການຊັບສິນທີ່ຫັກໄດ້ (ບໍ່ຕ້ອງ parameters)
    - bulk_check: ກວດສອບລາຍການກ່ອນຫັກ (ຕ້ອງມີ mapping_ids)
    - bulk_process: ຫັກລາຍການທີ່ເລືອກ + ບັນທຶກປະຫວັດ (ຕ້ອງມີ mapping_ids)
    - bulk_process_all: ຫັກທຸກລາຍການພ້ອມກັນ + ບັນທຶກປະຫວັດ (ບໍ່ຕ້ອງ parameters)
    - get_history: ດຶງປະຫວັດການຫັກຄ່າເສື່ອມລາຄາ (ຕ້ອງມີ asset_list_id)
    - mark_accounted: ໝາຍການຫັກວ່າບັນຊີແລ້ວ (ຕ້ອງມີ aldm_id)
    """
    try:
        # ກວດສອບ method
        if request.method not in ['POST', 'GET']:
            return JsonResponse({'error': 'ໃຊ້ POST ຫຼື GET method'})
        
        # ດຶງຂໍ້ມູນ
        if request.method == 'POST':
            if not request.body:
                return JsonResponse({'error': 'ບໍ່ມີ request body'})
            
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError as e:
                return JsonResponse({'error': f'JSON error: {str(e)}'})
            
            mapping_id = data.get('mapping_id')
            mapping_ids = data.get('mapping_ids', [])
            asset_list_id = data.get('asset_list_id')
            aldm_id = data.get('aldm_id')
            user_id = data.get('user_id')
            action = data.get('action', 'calculate')  # default: calculate
        else:  # GET
            mapping_id = request.GET.get('mapping_id')
            mapping_ids_str = request.GET.get('mapping_ids', '')
            mapping_ids = mapping_ids_str.split(',') if mapping_ids_str else []
            asset_list_id = request.GET.get('asset_list_id')
            aldm_id = request.GET.get('aldm_id')
            user_id = request.GET.get('user_id')
            action = request.GET.get('action', 'calculate')
        
        # ✅ ກວດສອບ parameters ຕາມ action ທີ່ຖືກຕ້ອງ
        
        # Actions ທີ່ຕ້ອງມີ mapping_id
        if action in ['calculate', 'process', 'status']:
            if not mapping_id:
                return JsonResponse({
                    'error': 'ໃສ່ mapping_id',
                    'example': {
                        'POST': '{"mapping_id": 19, "action": "calculate"}',
                        'GET': '?mapping_id=19&action=calculate'
                    },
                    'actions_need_mapping_id': ['calculate', 'process', 'status']
                })
        
        # Actions ທີ່ຕ້ອງມີ mapping_ids
        if action in ['bulk_check', 'bulk_process']:
            if not mapping_ids:
                return JsonResponse({
                    'error': 'ໃສ່ mapping_ids',
                    'example': {
                        'POST': '{"action": "bulk_check", "mapping_ids": [19, 20, 21]}',
                        'GET': '?action=bulk_check&mapping_ids=19,20,21'
                    },
                    'actions_need_mapping_ids': ['bulk_check', 'bulk_process']
                })
        
        # Actions ທີ່ຕ້ອງມີ asset_list_id
        if action in ['get_history']:
            if not asset_list_id:
                return JsonResponse({
                    'error': 'ໃສ່ asset_list_id',
                    'example': {
                        'POST': '{"action": "get_history", "asset_list_id": 101}',
                        'GET': '?action=get_history&asset_list_id=101'
                    }
                })
        
        # Actions ທີ່ຕ້ອງມີ aldm_id
        if action in ['mark_accounted']:
            if not aldm_id:
                return JsonResponse({
                    'error': 'ໃສ່ aldm_id',
                    'example': {
                        'POST': '{"action": "mark_accounted", "aldm_id": 1, "user_id": 1}',
                        'GET': '?action=mark_accounted&aldm_id=1&user_id=1'
                    }
                })
        
        # Actions ທີ່ບໍ່ຕ້ອງ parameters: bulk_list, bulk_process_all
        
        # ✅ ເອີ້ນໃຊ້ຟັງຊັ້ນຕາມ action
        if action == 'calculate':
            # ຄິດຄ່າເສື່ອມລາຄາ + ສະຖານະ + ປະຫວັດ
            result = calculate_depreciation_schedule(mapping_id)
            
        elif action == 'process':
            # ຫັກຄ່າເສື່ອມລາຄາ 1 ເດືອນ + ບັນທຶກປະຫວັດ
            result = process_monthly_depreciation(mapping_id, user_id)
            
        elif action == 'status':
            # ເບິ່ງສະຖານະເທົ່ານັ້ນ
            calc_result = calculate_depreciation_schedule(mapping_id)
            if 'error' in calc_result:
                result = calc_result
            else:
                result = {
                    'asset_info': calc_result['asset_info'],
                    'depreciation_status': calc_result['depreciation_status'],
                    'depreciation_history': calc_result.get('depreciation_history', [])
                }
                
        elif action == 'bulk_list':
            # ລາຍການຊັບສິນທີ່ຫັກໄດ້ - ບໍ່ຕ້ອງ parameters
            result = get_depreciable_assets()
        elif action == 'get_monthly_due':
            # ລາຍການທີ່ຕ້ອງຫັກໃນເດືອນ
            month = data.get('month') if request.method == 'POST' else request.GET.get('month')
            year = data.get('year') if request.method == 'POST' else request.GET.get('year')
            if month:
                month = int(month)
            if year:
                year = int(year)
            result = get_depreciation_due_this_month(month, year)
        elif action == 'get_next_months_due':
            # ລາຍການທີ່ຕ້ອງຫັກໃນອີກ 3 ເດືອນຂ້າງໜ້າ
            months_ahead = data.get('months_ahead', 3) if request.method == 'POST' else int(request.GET.get('months_ahead', 3))
            result = get_next_few_months_due(months_ahead)
        elif action == 'process_monthly_due':
            # ຫັກທຸກລາຍການທີ່ຕ້ອງຫັກໃນເດືອນ
            month = data.get('month') if request.method == 'POST' else request.GET.get('month')
            year = data.get('year') if request.method == 'POST' else request.GET.get('year')
            if month:
                month = int(month)
            if year:
                year = int(year)
            with transaction.atomic():
                result = process_monthly_due_depreciation(month, year, user_id)
        elif action == 'bulk_check':
            # ກວດສອບລາຍການກ່ອນຫັກ
            result = process_bulk_depreciation(mapping_ids, check_only=True, user_id=user_id)
            
        elif action == 'bulk_process':
            # ຫັກລາຍການທີ່ເລືອກ + ບັນທຶກປະຫວັດ
            with transaction.atomic():
                result = process_bulk_depreciation(mapping_ids, check_only=False, user_id=user_id)
                
        elif action == 'bulk_process_all':
            # ຫັກທຸກລາຍການທີ່ຫັກໄດ້ + ບັນທຶກປະຫວັດ - ບໍ່ຕ້ອງ parameters
            depreciable_assets = get_depreciable_assets()
            if 'error' in depreciable_assets:
                return JsonResponse(depreciable_assets, status=400)
            
            # ດຶງ mapping_ids ທີ່ຫັກໄດ້
            available_ids = [
                item['mapping_id'] 
                for item in depreciable_assets['depreciable_items']
            ]
            
            if not available_ids:
                return JsonResponse({
                    'success': True,
                    'message': 'ບໍ່ມີລາຍການທີ່ຕ້ອງຫັກ',
                    'data': {
                        'summary': {
                            'total_items': 0,
                            'success_count': 0,
                            'error_count': 0
                        },
                        'details': []
                    }
                })
            
            with transaction.atomic():
                result = process_bulk_depreciation(available_ids, check_only=False, user_id=user_id)
        
        elif action == 'get_history':
            # ດຶງປະຫວັດການຫັກຄ່າເສື່ອມລາຄາ
            limit = data.get('limit') if request.method == 'POST' else request.GET.get('limit')
            if limit:
                limit = int(limit)
            result = get_depreciation_history(asset_list_id, limit)
        
        elif action == 'mark_accounted':
            # ໝາຍການຫັກວ່າບັນຊີແລ້ວ
            result = mark_depreciation_as_accounted(aldm_id, user_id)
                
        else:
            return JsonResponse({
                'error': f'action "{action}" ບໍ່ຖືກຕ້ອງ',
                'valid_actions': {
                    'need_mapping_id': ['calculate', 'process', 'status'],
                    'need_mapping_ids': ['bulk_check', 'bulk_process'],
                    'need_asset_list_id': ['get_history'],
                    'need_aldm_id': ['mark_accounted'],
                    'no_parameters': ['bulk_list', 'bulk_process_all']
                },
                'examples': {
                    'single': '{"mapping_id": 19, "action": "calculate"}',
                    'bulk_check': '{"action": "bulk_check", "mapping_ids": [19, 20]}',
                    'bulk_all': '{"action": "bulk_process_all", "user_id": 1}',
                    'history': '{"action": "get_history", "asset_list_id": 101, "limit": 10}',
                    'account': '{"action": "mark_accounted", "aldm_id": 1, "user_id": 1}'
                }
            })
        
        # ກວດສອບຜົນລັບ
        if isinstance(result, dict) and 'error' in result:
            return JsonResponse(result, status=400)
        
        return JsonResponse({
            'success': True,
            'action': action,
            'data': result,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        import traceback
        error_details = {
            'error': str(e),
            'type': type(e).__name__,
            'traceback': traceback.format_exc()
        }
        print("API Error Details:", error_details)
        return JsonResponse(error_details, status=500)

# =====================================
# Monthly Depreciation Due Functions
# =====================================

def get_depreciation_due_this_month(target_month=None, target_year=None):
    """
    ຫາລາຍການຊັບສິນທີ່ຕ້ອງຫັກໃນເດືອນທີ່ກຳນົດ
    
    Args:
        target_month: ເດືອນທີ່ຕ້ອງການກວດສອບ (1-12) - ຖ້າບໍ່ໃສ່ໃຊ້ເດືອນປັດຈຸບັນ
        target_year: ປີທີ່ຕ້ອງການກວດສອບ - ຖ້າບໍ່ໃສ່ໃຊ້ປີປັດຈຸບັນ
    """
    try:
        current_date = datetime.now()
        
        # ຖ້າບໍ່ໃສ່ໃຊ້ເດືອນ/ປີປັດຈຸບັນ
        if not target_month:
            target_month = current_date.month
        if not target_year:
            target_year = current_date.year
            
        # ວັນທີ່ເລີ່ມຕົ້ນແລະສິ້ນສຸດຂອງເດືອນ
        month_start = datetime(target_year, target_month, 1).date()
        month_end = datetime(target_year, target_month, 
                           get_last_day_of_month(target_year, target_month)).date()
        
        # ດຶງລາຍການທີ່ຄວນຫັກ
        accounting_methods = FA_Accounting_Method.objects.all()
        due_items = []
        overdue_items = []
        up_to_date_items = []
        
        for method in accounting_methods:
            try:
                # ດຶງຂໍ້ມູນ asset
                if method.asset_list_id:
                    asset = method.asset_list_id
                elif method.ref_id:
                    asset = FA_Asset_Lists.objects.get(asset_list_id=method.ref_id)
                else:
                    continue
                
                # ກວດສອບວ່າຫັກໄດ້ບໍ
                if not (asset.asset_value and asset.asset_useful_life):
                    continue
                
                current_count = int(asset.C_dpac or 0)
                useful_life = int(asset.asset_useful_life)
                total_months = useful_life * 12
                start_date = method.transaction_date
                
                # ຖ້າຫັກຄົບແລ້ວ ຂ້າມ
                if current_count >= total_months:
                    continue
                
                # ຄິດວ່າເດືອນຕໍ່ໄປຄວນຫັກເມື່ອໃດ
                next_month_number = current_count + 1
                
                # ຄິດວັນທີ່ທີ່ຄວນຫັກເດືອນຕໍ່ໄປ
                if next_month_number == 1:
                    # ເດືອນທຳອິດ - ເລີ່ມຈາກວັນທີເລີ່ມຊັບສິນ
                    due_date = start_date
                else:
                    # ເດືອນອື່ນໆ - ເລີ່ມຕົ້ນເດືອນ
                    due_date = (start_date + relativedelta(months=current_count)).replace(day=1)
                
                # ຄິດວັນທີ່ສິ້ນສຸດການຫັກເດືອນນັ້ນ
                if next_month_number == 1:
                    due_end_date = datetime(start_date.year, start_date.month,
                                          get_last_day_of_month(start_date.year, start_date.month)).date()
                else:
                    month_calc = start_date + relativedelta(months=current_count)
                    due_end_date = datetime(month_calc.year, month_calc.month,
                                          get_last_day_of_month(month_calc.year, month_calc.month)).date()
                
                # ຄິດຄ່າເສື່ອມລາຄາທີ່ຄວນຫັກ
                calc_result = calculate_depreciation_schedule(method.mapping_id)
                if 'error' in calc_result:
                    continue
                
                daily_depreciation = calc_result['calculation_info']['daily_depreciation']
                
                if next_month_number == 1:
                    days_count = (due_end_date - due_date + timedelta(days=1)).days
                else:
                    days_count = get_last_day_of_month(due_end_date.year, due_end_date.month)
                
                expected_depreciation = daily_depreciation * days_count
                
                # ສ້າງຂໍ້ມູນລາຍການ
                item_data = {
                    'mapping_id': method.mapping_id,
                    'asset_id': asset.asset_list_id,
                    'asset_name': asset.asset_spec or 'N/A',
                    'asset_value': float(asset.asset_value),
                    'current_month': next_month_number,
                    'total_months': total_months,
                    'due_date': due_date.strftime('%d/%m/%Y'),
                    'due_end_date': due_end_date.strftime('%d/%m/%Y'),
                    'days_count': days_count,
                    'expected_depreciation': round(expected_depreciation, 2),
                    'last_depreciation_date': asset.asset_latest_date_dpca.strftime('%d/%m/%Y') if asset.asset_latest_date_dpca else 'ຍັງບໍ່ໄດ້ຫັກ',
                    'status_category': '',
                    'due_month_year': f"{get_month_name_la(due_date.month)} {due_date.year}",
                    'completion_percentage': round((current_count / total_months) * 100, 2)
                }
                
                # ຈັດປະເພດຕາມສະຖານະ
                if due_date <= month_end and due_end_date >= month_start:
                    # ຕ້ອງຫັກໃນເດືອນນີ້
                    if due_end_date < current_date.date():
                        item_data['status_category'] = 'overdue'
                        item_data['status_message'] = f"⚠️ ຄ້າງຫັກ! ຄວນຫັກແລ້ວໃນ {item_data['due_month_year']}"
                        overdue_items.append(item_data)
                    else:
                        item_data['status_category'] = 'due'
                        item_data['status_message'] = f"📅 ຕ້ອງຫັກໃນ {item_data['due_month_year']}"
                        due_items.append(item_data)
                elif due_date > month_end:
                    # ຍັງບໍ່ຮອດເວລາ
                    item_data['status_category'] = 'future'
                    item_data['status_message'] = f"⏭️ ຈະຫັກໃນ {item_data['due_month_year']}"
                    # ບໍ່ເພີ່ມໃນລາຍການ due
                else:
                    # ອັບເດດແລ້ວ
                    item_data['status_category'] = 'up_to_date'
                    item_data['status_message'] = f"✅ ອັບເດດແລ້ວ"
                    up_to_date_items.append(item_data)
                    
            except Exception as e:
                print(f"Error processing mapping_id {method.mapping_id}: {str(e)}")
                continue
        
        # ຈັດລຽງຕາມລຳດັບຄວາມສຳຄັນ
        overdue_items.sort(key=lambda x: x['due_date'])
        due_items.sort(key=lambda x: x['due_date'])
        
        return {
            'success': True,
            'target_period': {
                'month': target_month,
                'year': target_year,
                'month_name_la': get_month_name_la(target_month),
                'period': f"{month_start.strftime('%d/%m/%Y')} - {month_end.strftime('%d/%m/%Y')}"
            },
            'summary': {
                'total_due': len(due_items),
                'total_overdue': len(overdue_items),
                'total_up_to_date': len(up_to_date_items),
                'total_checked': len(due_items) + len(overdue_items) + len(up_to_date_items)
            },
            'overdue_items': overdue_items,  # ຄ້າງຫັກ
            'due_items': due_items,          # ຕ້ອງຫັກໃນເດືອນນີ້
            'up_to_date_items': up_to_date_items[:5],  # ອັບເດດແລ້ວ (5 ອັນທຳອິດ)
            'all_items_needing_attention': overdue_items + due_items
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f"Get monthly due error: {str(e)}"
        }

def get_next_few_months_due(months_ahead=3):
    """
    ຫາລາຍການທີ່ຕ້ອງຫັກໃນອີກ 3 ເດືອນຂ້າງໜ້າ
    """
    try:
        current_date = datetime.now()
        results = []
        
        for i in range(months_ahead):
            target_date = current_date + relativedelta(months=i)
            monthly_result = get_depreciation_due_this_month(
                target_month=target_date.month,
                target_year=target_date.year
            )
            
            if monthly_result['success']:
                results.append({
                    'month': target_date.month,
                    'year': target_date.year,
                    'month_name': get_month_name_la(target_date.month),
                    'due_count': monthly_result['summary']['total_due'],
                    'overdue_count': monthly_result['summary']['total_overdue'],
                    'items': monthly_result['all_items_needing_attention'][:5]  # ສະແດງ 5 ອັນທຳອິດ
                })
        
        return {
            'success': True,
            'period_summary': results,
            'total_months_checked': months_ahead
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f"Get next months due error: {str(e)}"
        }

def process_monthly_due_depreciation(target_month=None, target_year=None, user_id=None):
    """
    ຫັກຄ່າເສື່ອມລາຄາທຸກລາຍການທີ່ຕ້ອງຫັກໃນເດືອນນັ້ນ
    """
    try:
        # ຫາລາຍການທີ່ຕ້ອງຫັກ
        due_result = get_depreciation_due_this_month(target_month, target_year)
        
        if not due_result['success']:
            return due_result
        
        # ລາຍການທີ່ຕ້ອງຫັກ (ລວມຄ້າງຫັກ)
        items_to_process = due_result['all_items_needing_attention']
        
        if not items_to_process:
            return {
                'success': True,
                'message': f"ບໍ່ມີລາຍການທີ່ຕ້ອງຫັກໃນ {due_result['target_period']['month_name_la']} {due_result['target_period']['year']}",
                'target_period': due_result['target_period'],
                'summary': {
                    'total_items': 0,
                    'success_count': 0,
                    'error_count': 0
                },
                'details': []
            }
        
        # ດຶງ mapping_ids
        mapping_ids = [item['mapping_id'] for item in items_to_process]
        
        # ຫັກທຸກລາຍການ
        with transaction.atomic():
            process_result = process_bulk_depreciation(mapping_ids, check_only=False, user_id=user_id)
        
        # ສ້າງຜົນລັບ
        return {
            'success': True,
            'message': f"ຫັກຄ່າເສື່ອມລາຄາໃນ {due_result['target_period']['month_name_la']} {due_result['target_period']['year']} ສຳເລັດ",
            'target_period': due_result['target_period'],
            'processing_result': process_result
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f"Process monthly due error: {str(e)}"
        }

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def setup_default_eod_functions(request):
    """
    Setup default EOD functions
    """
    try:
        from .eod_helpers import create_default_eod_functions
        
        success, message = create_default_eod_functions()
        
        if success:
            return Response({
                'message': message
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'error': message
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            'error': f'ເກີດຂໍ້ຜິດພາດ: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def validate_eod_prerequisites_view(request):
    """
    Validate EOD prerequisites
    """
    try:
        from .eod_helpers import validate_eod_prerequisites
        
        is_valid, issues = validate_eod_prerequisites()
        
        return Response({
            'can_start_eod': is_valid,
            'issues': issues,
            'message': 'ພ້ອມເລີ່ມ EOD' if is_valid else 'ມີບັນຫາທີ່ຕ້ອງແກ້ໄຂກ່ອນ'
        })
        
    except Exception as e:
        return Response({
            'can_start_eod': False,
            'issues': [f'ເກີດຂໍ້ຜິດພາດ: {str(e)}'],
            'message': 'ບໍ່ສາມາດກວດສອບໄດ້'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Store Procedures 
from django.db import connection
def run_trial_balance_proc(ac_ccy_id: str, date_start: str, date_end: str):
    with connection.cursor() as cursor:
        # Use parameterized SQL to prevent SQL injection
        sql = """
            DECLARE @return_value INT;
            EXEC @return_value = dbo.Somtop_Trail_Balance_By_Currency_Temp_NewTest_ACTB
                @ac_ccy_id = %s,
                @DateStart = %s,
                @DateEnd = %s;
            SELECT @return_value AS return_value;
        """
        cursor.execute(sql, [ac_ccy_id, date_start, date_end])
        row = cursor.fetchone()
        return row[0] if row else None


from django.db import connection
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def trial_balance_view(request):
    ac_ccy_id = request.data.get("ac_ccy_id")
    date_start = request.data.get("date_start")
    date_end = request.data.get("date_end")

    if not all([ac_ccy_id, date_start, date_end]):
        return Response({
            "status": "error",
            "message": "Missing required parameters: ac_ccy_id, date_start, or date_end."
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        logger.info(f"[TrialBalance] Executing stored procedure for ccy_id={ac_ccy_id} from {date_start} to {date_end}")

        with connection.cursor() as cursor:
            query = """
                EXEC dbo.Somtop_Trail_Balance_By_Currency_Temp_NewTest_ACTB
                    @ac_ccy_id = %s,
                    @DateStart = %s,
                    @DateEnd = %s
            """
            cursor.execute(query, [ac_ccy_id, date_start, date_end])
            columns = [col[0] for col in cursor.description]
            result = [dict(zip(columns, row)) for row in cursor.fetchall()]

        logger.info(f"[TrialBalance] Procedure completed successfully. Rows fetched: {len(result)}")

        return Response({
            "status": "success",
            "count": len(result),
            "data": result
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.exception(f"[TrialBalance] Error executing stored procedure: {str(e)}")
        return Response({
            "status": "error",
            "message": "Internal Server Error: " + str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)