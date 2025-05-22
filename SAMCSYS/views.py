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
from django.utils import timezone
from .models import MTTB_Users
from .serializers import MTTBUserSerializer

class MTTBUserViewSet(viewsets.ModelViewSet):
    queryset = MTTB_Users.objects.select_related('div_id', 'Role_ID').all()
    serializer_class = MTTBUserSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [AllowAny()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        # request.user is your MTTB_Users instance via JWTAuthentication
        maker = self.request.user if self.request.user.is_authenticated else None
        # pass Maker_Id and Maker_DT_Stamp into serializer.save()
        serializer.save(
            Maker_Id=maker,
            Maker_DT_Stamp=timezone.now()
        )

    def perform_update(self, serializer):
        checker = self.request.user if self.request.user.is_authenticated else None
        # set Checker_Id and Checker_DT_Stamp
        serializer.save(
            Checker_Id=checker,
            Checker_DT_Stamp=timezone.now()
        )

@api_view(["POST"])
@permission_classes([AllowAny])
def login_view(request):
    uid = request.data.get("user_name")
    pwd = request.data.get("user_password")
    if not uid or not pwd:
        return Response({"error": "User_Name and User_Password required"},
                        status=status.HTTP_400_BAD_REQUEST)

    hashed = _hash(pwd)
    try:
        user = MTTB_Users.objects.select_related('div_id', 'Role_ID').get(
            user_name=uid, user_password=hashed
        )
    except MTTB_Users.DoesNotExist:
        return Response({"error": "Invalid credentials"},
                        status=status.HTTP_401_UNAUTHORIZED)

    # 1) Create tokens
    refresh = RefreshToken.for_user(user)
    access  = refresh.access_token

    # 2) Serialize your user data
    data = MTTBUserSerializer(user).data

    # 3) Manually add full division & role info
    if user.div_id:
        data['division'] = {
            'div_id': user.Div_Id.Div_Id,
            'Div_NameL': user.Div_Id.Div_NameL,
            'Div_NameE': user.Div_Id.Div_NameE,
            'Record_Status': user.Div_Id.Record_Status,
        }
    else:
        data['division'] = None

    if user.Role_ID:
        data['role'] = {
            'role_id': user.Role_ID.role_id,
            'role_name_la': user.Role_ID.role_name_la,
            'role_name_en': user.Role_ID.role_name_en,
            'record_Status': user.Role_ID.record_Status,
        }
    else:
        data['role'] = None

    # 4) Return tokens + full payload
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


from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import MTTB_Role_Detail
from .serializers import RoleDetailSerializer

class MTTBRoleDetailViewSet(viewsets.ModelViewSet):
    """
    CRUD for Role_Detail records.
    """
    queryset = MTTB_Role_Detail.objects.select_related(
        'role_id', 'function_id'
    ).all()
    serializer_class = RoleDetailSerializer

    def get_permissions(self):
        # Allow open creation; require auth for all others
        if self.request.method == 'POST':
            return [AllowAny()]
        return [IsAuthenticated()]


# Function Loop Sidebar Menu

from collections import OrderedDict
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import (
    MTTB_Users,
    MTTB_Role_Detail,
    MTTB_Function_Desc,
    MTTB_SUB_MENU,
    MTTB_MAIN_MENU,
    STTB_ModulesInfo,
)
from .serializers import ModuleSerializer  # if you added them

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def sidebar_for_user(request, user_id):
    """
    GET /api/users/{user_id}/sidebar/
    Returns modules → main menus → sub menus → functions with permissions.
    """
    # 1) Load user & role
    user = get_object_or_404(MTTB_Users, user_id=user_id)
    role = user.Role_ID
    # print("User:", user.user_id, "Role:", user.Role_ID)

    if not role:
        return Response([])  # no role, no sidebar

    # 2) Fetch all role_detail for this role, with joins down to module
    details = (
        MTTB_Role_Detail.objects
          .filter(role_id=role)
          .select_related(
              'function_id',
              'function_id__sub_menu_id',
              'function_id__sub_menu_id__menu_id',
              'function_id__sub_menu_id__menu_id__module_Id'
          )
    )

    # 3) Build nested dict: module → main_menu → sub_menu → [functions]
    modules = OrderedDict()
    for det in details:
        func  = det.function_id
        sub   = func.sub_menu_id
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
                'sub_menu_id':    sub.sub_menu_id,
                'sub_menu_name_la': sub.sub_menu_name_la,
                'sub_menu_name_en': sub.sub_menu_name_en,
                'sub_menu_icon':   sub.sub_menu_icon,
                'sub_menu_order':  sub.sub_menu_order,
                'sub_menu_urls':   sub.sub_menu_urls,
                'is_active':       sub.is_active,
                'functions':       []
            }

        # Finally, append the function + its permission flags
        sm_group[sm_key]['functions'].append({
            'function_id':    func.function_id,
            'description_la': func.description_la,
            'description_en': func.description_en,
            'permissions': {
                'new':    det.New_Detail,
                'delete': det.Del_Detail,
                'edit':   det.Edit_Detail,
                'auth':   det.Auth_Detail,
            }  
        })

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

    # 5) (Optional) validate with serializer
    # serialized = ModuleSerializer(result, many=True)
    # return Response(serialized.data)

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
    MTTB_Function_Desc,
    MTTB_SUB_MENU,
    MTTB_MAIN_MENU,
    STTB_ModulesInfo,
)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def role_sidebar(request, role_id):
    """
    GET /api/role/<role_id>/sidebar/
    Returns modules → main menus → sub menus → functions with permissions.
    """
    # 1) Load role
    role = get_object_or_404(MTTB_Role_Master, role_id=role_id)

    # 2) Pull in every detail → function → sub_menu → main_menu → module
    details = (
        MTTB_Role_Detail.objects
        .filter(role_id=role)
        .select_related(
            'function_id',
            'function_id__sub_menu_id',
            'function_id__sub_menu_id__menu_id',
            'function_id__sub_menu_id__menu_id__module_Id'
        )
        .order_by(
            'function_id__sub_menu_id__menu_id__module_Id__module_order',
            'function_id__sub_menu_id__menu_id__menu_order',
            'function_id__sub_menu_id__sub_menu_order',
            'function_id__function_order'
        )
    )

    # 3) Group into nested dicts
    modules = OrderedDict()
    for det in details:
        func = det.function_id
        sub  = func.sub_menu_id
        main = sub.menu_id
        mod  = main.module_Id

        # ensure all links exist
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
                'is_active':        sub.is_active,
                'functions':        []
            }

        # Function level
        sm_group[sub.sub_menu_id]['functions'].append({
            'function_id':    func.function_id,
            'description_la': func.description_la,
            'description_en': func.description_en,
            'permissions': {
                'new':    det.New_Detail,
                'delete': det.Del_Detail,
                'edit':   det.Edit_Detail,
                'auth':   det.Auth_Detail,
            }
        })

    # 4) Convert nested OrderedDicts to lists
    sidebar = []
    for mod in modules.values():
        main_menus = []
        for mm in mod['main_menus'].values():
            mm['sub_menus'] = list(mm['sub_menus'].values())
            main_menus.append(mm)
        mod['main_menus'] = main_menus
        sidebar.append(mod)

    return Response(sidebar, status=status.HTTP_200_OK)


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

class MainMenuViewSet(viewsets.ModelViewSet):
    queryset = MTTB_MAIN_MENU.objects.select_related('module_Id').all().order_by('menu_order')
    serializer_class = MainMenuSerializer
    permission_classes = [IsAuthenticated]

class SubMenuViewSet(viewsets.ModelViewSet):
    queryset = MTTB_SUB_MENU.objects.select_related('menu_id').all().order_by('sub_menu_order')
    serializer_class = SubMenuSerializer
    permission_classes = [IsAuthenticated]

class FunctionDescViewSet(viewsets.ModelViewSet):
    queryset = MTTB_Function_Desc.objects.select_related('sub_menu_id').all().order_by('function_order')
    serializer_class = FunctionDescSerializer
    permission_classes = [IsAuthenticated]

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
    CRUD for General Ledger Master records.
    """
    queryset = MTTB_GLMaster.objects.select_related('Maker_Id', 'Checker_Id').filter(glType='5').all().order_by('gl_code')
    serializer_class = GLMasterSerializer

    def get_permissions(self):
        # Allow unauthenticated creation (e.g. bootstrap), require auth otherwise
        if self.request.method == 'POST':
            return [AllowAny()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        maker = self.request.user if self.request.user and self.request.user.is_authenticated else None
        gl = serializer.save(
            Maker_Id=maker,
            Maker_DT_Stamp=timezone.now()
        )
        return gl

    def perform_update(self, serializer):
        checker = self.request.user if self.request.user and self.request.user.is_authenticated else None
        gl = serializer.save(
            Checker_Id=checker,
            Checker_DT_Stamp=timezone.now()
        )
        return gl
    
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

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import MTTB_EMPLOYEE,MTTB_LCL_Holiday
from .serializers import MTTB_EMPLOYEESerializer,MTTB_LCL_HolidaySerializer

class MTTB_EMPLOYEEViewSet(viewsets.ModelViewSet):
    queryset = MTTB_EMPLOYEE.objects.all().order_by('employee_id')
    serializer_class = MTTB_EMPLOYEESerializer
    permission_classes = [IsAuthenticated]

class MTTB_LCL_HolidayViewSet(viewsets.ModelViewSet):
    queryset = MTTB_LCL_Holiday.objects.all().order_by('lcl_holiday_id')
    serializer_class = MTTB_LCL_HolidaySerializer
    permission_classes = [IsAuthenticated]

