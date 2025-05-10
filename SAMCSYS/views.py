# Create your views here.
import hashlib
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import MTTB_User
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
#     queryset = MTTB_User.objects.all()
#     serializer_class = MTTBUserSerializer

#     # allow unauthenticated user to create an account
#     def get_permissions(self):
#         if self.request.method == "POST":
#             return [AllowAny()]
#         return super().get_permissions()


def _hash(raw_password):
    return hashlib.md5(raw_password.encode("utf-8")).hexdigest()

class MTTBUserViewSet(viewsets.ModelViewSet):
    queryset = MTTB_User.objects.all()
    serializer_class = MTTBUserSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [AllowAny()]
        return super().get_permissions()


@api_view(["POST"])
@permission_classes([AllowAny])
def login_view(request):
    uid = request.data.get("User_Name")
    pwd = request.data.get("User_Password")
    if not uid or not pwd:
        return Response({"error": "User_Name and User_Password required"},
                        status=status.HTTP_400_BAD_REQUEST)

    hashed = _hash(pwd)
    try:
        user = MTTB_User.objects.get(User_Name=uid, User_Password=hashed)
    except MTTB_User.DoesNotExist:
        return Response({"error": "Invalid credentials"},
                        status=status.HTTP_401_UNAUTHORIZED)

    # 1) Create tokens
    refresh = RefreshToken.for_user(user)
    access = refresh.access_token

    # 2) Serialize your user data
    data = MTTBUserSerializer(user).data

    # 3) Return tokens + user info
    return Response({
        "message": "Login successful",
        "refresh": str(refresh),
        "access": str(access),
        "user": data
    })


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
    queryset = MTTB_Divisions.objects.all().order_by('Div_Id')
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
            Auth_Status='P',     # pending by default
        )

    def perform_update(self, serializer):
        # Stamp the checker on updates
        serializer.save(
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
    queryset = MTTB_Role_Master.objects.all().order_by('Role_Id')
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
            Auth_Status='P'
        )

    def perform_update(self, serializer):
        # Stamp checker and timestamp
        serializer.save(
            Checker_DT_Stamp=timezone.now()
        )


from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import MTTB_Role_Detail
from .serializers import RoleDetailSerializer

class MTTBRoleDetailViewSet(viewsets.ModelViewSet):
    """
    CRUD for Role_Detail records.
    """
    queryset = MTTB_Role_Detail.objects.select_related(
        'Role_Id', 'Function_Id'
    ).all()
    serializer_class = RoleDetailSerializer

    def get_permissions(self):
        # Allow open creation; require auth for all others
        if self.request.method == 'POST':
            return [AllowAny()]
        return [IsAuthenticated()]
