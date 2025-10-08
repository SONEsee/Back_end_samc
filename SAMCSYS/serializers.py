import re
from django.contrib.auth.hashers import make_password
from django.core.validators import EmailValidator
from rest_framework import serializers
from .models import MTTB_Users, MTTB_Divisions, MTTB_Role_Master

class DivisionSerializer(serializers.ModelSerializer):
    """Serializer for Division with additional info"""
    user_count = serializers.SerializerMethodField()
    
    class Meta:
        model = MTTB_Divisions
        fields = [
            'div_id', 'division_name_la', 'division_name_en', 
            'Record_Status', 'user_count'
        ]
    
    def get_user_count(self, obj):
        """Get count of active users in this division"""
        return MTTB_Users.objects.filter(
            div_id=obj, 
            User_Status='E'
        ).count()

class RoleMasterSerializer(serializers.ModelSerializer):
    """Serializer for Role Master with additional info"""
    user_count = serializers.SerializerMethodField()
    
    class Meta:
        model = MTTB_Role_Master
        fields = [
            'role_id', 'role_name_la', 'role_name_en', 
            'record_Status', 'user_count'
        ]
    
    def get_user_count(self, obj):
        """Get count of active users with this role"""
        return MTTB_Users.objects.filter(
            Role_ID=obj, 
            User_Status='E'
        ).count()
from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from django.core.validators import EmailValidator
from django.utils import timezone
import re


class MTTBUserSerializer(serializers.ModelSerializer):
    """
    Simplified User serializer with proper password handling
    """
    # Nested read-only representations
    division = DivisionSerializer(source='div_id', read_only=True)
    role = RoleMasterSerializer(source='Role_ID', read_only=True)

    # Writable PK fields
    div_id = serializers.PrimaryKeyRelatedField(
        queryset=MTTB_Divisions.objects.filter(Record_Status='O'),
        write_only=True, 
        required=True,
        error_messages={
            'required': 'ກະລຸນາເລືອກພະແນກ',
            'does_not_exist': 'ພະແນກທີ່ເລືອກບໍ່ຖືກຕ້ອງ',
        }
    )
    
    Role_ID = serializers.PrimaryKeyRelatedField(
        queryset=MTTB_Role_Master.objects.filter(record_Status='O'),
        write_only=True, 
        required=True,
        error_messages={
            'required': 'ກະລຸນາເລືອກສິດການນຳໃຊ້',
            'does_not_exist': 'ສິດການນຳໃຊ້ທີ່ເລືອກບໍ່ຖືກຕ້ອງ',
        }
    )

    # Password field (write-only)
    user_password = serializers.CharField(
        write_only=True,
        required=True,
        min_length=6,
        max_length=50,
        error_messages={
            'required': 'ກະລຸນາປ້ອນລະຫັດຜ່ານ',
            'min_length': 'ລະຫັດຜ່ານຕ້ອງມີຢ່າງໜ້ອຍ 6 ຕົວອັກສອນ',
            'max_length': 'ລະຫັດຜ່ານບໍ່ຄວນເກີນ 50 ຕົວອັກສອນ',
        }
    )

    # Profile picture URL
    profile_picture_url = serializers.SerializerMethodField()

    class Meta:
        model = MTTB_Users
        fields = [
            'user_id', 'user_name', 'user_password',
            'user_email', 'user_mobile', 'User_Status',
            'div_id', 'division', 'Role_ID', 'role',
            'profile_picture', 'profile_picture_url',
            'InsertDate', 'UpdateDate',
            'Auth_Status', 'Once_Auth'
        ]
        extra_kwargs = {
            'user_id': {
                'required': True,
                'error_messages': {
                    'required': 'ກະລຸນາປ້ອນລະຫັດຜູ້ໃຊ້',
                    'blank': 'ລະຫັດຜູ້ໃຊ້ບໍ່ສາມາດຫວ່າງເປົ່າໄດ້',
                }
            },
            'user_name': {
                'required': True,
                'error_messages': {
                    'required': 'ກະລຸນາປ້ອນຊື່ຜູ້ໃຊ້',
                    'blank': 'ຊື່ຜູ້ໃຊ້ບໍ່ສາມາດຫວ່າງເປົ່າໄດ້',
                }
            },
            'user_email': {
                'required': False,
                'allow_blank': True,
            },
            'user_mobile': {
                'required': True,
                'error_messages': {
                    'required': 'ກະລຸນາປ້ອນເບີໂທລະສັບ',
                }
            },
            'profile_picture': {
                'required': False,
                'allow_null': True,
            },
        }

    def get_profile_picture_url(self, obj):
        """Get full URL for profile picture"""
        if obj.profile_picture:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.profile_picture.url)
            return obj.profile_picture.url
        return None

    def validate_user_id(self, value):
        """Validate user ID"""
        if not value:
            raise serializers.ValidationError("ກະລຸນາປ້ອນລະຫັດຜູ້ໃຊ້")
        
        if len(value) < 3 or len(value) > 20:
            raise serializers.ValidationError(
                "ລະຫັດຜູ້ໃຊ້ຕ້ອງມີ 3-20 ຕົວອັກສອນ"
            )
        
        if not re.match(r'^[a-zA-Z0-9_]+$', value):
            raise serializers.ValidationError(
                "ລະຫັດຜູ້ໃຊ້ສາມາດໃຊ້ໄດ້ພຽງຕົວອັກສອນ, ຕົວເລກ ແລະ _"
            )
        
        return value.upper()

    def validate_user_name(self, value):
        """Validate username"""
        if not value:
            raise serializers.ValidationError("ກະລຸນາປ້ອນຊື່ຜູ້ໃຊ້")
        
        if len(value) < 3 or len(value) > 100:
            raise serializers.ValidationError(
                "ຊື່ຜູ້ໃຊ້ຕ້ອງມີ 3-100 ຕົວອັກສອນ"
            )
        
        return value.strip()

    def validate_user_email(self, value):
        """Validate email format"""
        if value:
            validator = EmailValidator()
            try:
                validator(value)
            except:
                raise serializers.ValidationError("ຮູບແບບອີເມວບໍ່ຖືກຕ້ອງ")
        return value

    def validate_user_mobile(self, value):
        """Validate mobile number"""
        if value:
            digits_only = re.sub(r'\D', '', value)
            
            if len(digits_only) < 8 or len(digits_only) > 15:
                raise serializers.ValidationError(
                    "ເບີໂທລະສັບຕ້ອງມີ 8-15 ຕົວເລກ"
                )
        
        return value

    def validate_user_password(self, value):
        """Validate password"""
        if not value:
            raise serializers.ValidationError("ກະລຸນາປ້ອນລະຫັດຜ່ານ")
        
        if len(value) < 6:
            raise serializers.ValidationError(
                "ລະຫັດຜ່ານຕ້ອງມີຢ່າງໜ້ອຍ 6 ຕົວອັກສອນ"
            )
        
        if len(value) > 50:
            raise serializers.ValidationError(
                "ລະຫັດຜ່ານບໍ່ຄວນເກີນ 50 ຕົວອັກສອນ"
            )
        
        return value

    def create(self, validated_data):
        """Create user with hashed password"""
        # Extract password before creating user
        password = validated_data.pop('user_password', None)
        
        # Set default values
        validated_data.setdefault('User_Status', 'E')
        validated_data.setdefault('Auth_Status', 'U')
        validated_data.setdefault('Once_Auth', 'N')
        
        # Create user instance
        user = MTTB_Users(**validated_data)
        
        # Hash and set password
        if password:
            user.user_password = make_password(password)
        
        # Save user
        user.save()
        
        return user

    def update(self, instance, validated_data):
        """Update user"""
        password = validated_data.pop('user_password', None)
        
        # Update fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Update password if provided
        if password:
            instance.user_password = make_password(password)
            instance.pwd_changed_on = timezone.now().date()
        
        instance.save()
        return instance

# Simplified serializers for dropdown/selection purposes
class DivisionChoiceSerializer(serializers.ModelSerializer):
    """Lightweight serializer for division choices"""
    class Meta:
        model = MTTB_Divisions
        fields = ['div_id', 'division_name_en', 'division_name_la']

class RoleChoiceSerializer(serializers.ModelSerializer):
    """Lightweight serializer for role choices"""
    class Meta:
        model = MTTB_Role_Master
        fields = ['role_id', 'role_name_en', 'role_name_la']

class UserSummarySerializer(serializers.ModelSerializer):
    """Lightweight serializer for user listings"""
    division_name = serializers.CharField(source='div_id.division_name_en', read_only=True)
    role_name = serializers.CharField(source='Role_ID.role_name_en', read_only=True)
    
    class Meta:
        model = MTTB_Users
        fields = [
            'user_id', 'user_name', 'user_email', 'User_Status',
            'division_name', 'role_name', 'Auth_Status'
        ]

from .models import MTTB_Divisions
class MTTBDivisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MTTB_Divisions
        # include every field on your model
        fields = '__all__'
        read_only_fields = (
            'Maker_DT_Stamp',
            'Checker_DT_Stamp',
        )

from .models import MTTB_Role_Master
class MTTBRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = MTTB_Role_Master
        fields = '__all__'
        read_only_fields = (
            'Maker_DT_Stamp',
            'Checker_DT_Stamp',
        )

from .models import MTTB_Role_Detail
class RoleDetailSerializer(serializers.ModelSerializer):
    sub_menu_name_la = serializers.CharField(source='sub_menu_id.sub_menu_name_la', read_only=True)
    sub_menu_name_en = serializers.CharField(source='sub_menu_id.sub_menu_name_en', read_only=True)
    menu_name_la = serializers.CharField(source='sub_menu_id.menu_id.menu_name_la', read_only=True)
    
    class Meta:
        model = MTTB_Role_Detail
        fields = '__all__'
        
    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Include sub menu and main menu information if available
        if instance.sub_menu_id:
            data['sub_menu_info'] = {
                'sub_menu_id': instance.sub_menu_id.sub_menu_id,
                'sub_menu_name_la': instance.sub_menu_id.sub_menu_name_la,
                'sub_menu_name_en': instance.sub_menu_id.sub_menu_name_en,
                'sub_menu_urls': instance.sub_menu_id.sub_menu_urls,
            }
            if instance.sub_menu_id.menu_id:
                data['menu_info'] = {
                    'menu_id': instance.sub_menu_id.menu_id.menu_id,
                    'menu_name_la': instance.sub_menu_id.menu_id.menu_name_la,
                    'menu_name_en': instance.sub_menu_id.menu_id.menu_name_en,
                }
        return data

from .models import (
    MTTB_Role_Detail,
    MTTB_Function_Desc,
    STTB_ModulesInfo,
)
from .models import STTB_ModulesInfo
class STTBModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = STTB_ModulesInfo
        fields = ['M_Id', 'M_NameL', 'M_NameE']

from .models import MTTB_Function_Desc
class FunctionDescriptionSerializer(serializers.ModelSerializer):
    M_Id = STTBModuleSerializer(read_only=True)

    class Meta:
        model = MTTB_Function_Desc
        fields = [
            'function_id',
            'Function_Desc',
            'Main_Menu',
            'Sub_Menu',
            'All_Link',
            'M_Id',
            'Function_Status',
        ]



class FunctionPermSerializer(serializers.Serializer):
    function_id    = serializers.CharField()
    description_la = serializers.CharField()
    description_en = serializers.CharField()
    permissions    = serializers.DictField()

class SubMenuSerializer(serializers.Serializer):
    sub_menu_id    = serializers.CharField()
    sub_menu_name_la = serializers.CharField()
    sub_menu_name_en = serializers.CharField()
    sub_menu_icon  = serializers.CharField(allow_null=True)
    sub_menu_order = serializers.CharField()
    Record_Status      = serializers.BooleanField()
    functions      = FunctionPermSerializer(many=True)

class MainMenuSerializer(serializers.Serializer):
    menu_id        = serializers.CharField()
    menu_name_la   = serializers.CharField()
    menu_name_en   = serializers.CharField()
    menu_icon      = serializers.CharField(allow_null=True)
    menu_order     = serializers.CharField()
    Record_Status      = serializers.BooleanField()
    SubMenuSerializer = SubMenuSerializer(many=True)

class ModuleSerializer(serializers.Serializer):
    module_Id      = serializers.CharField()
    module_name_la = serializers.CharField()
    module_name_en = serializers.CharField()
    module_icon    = serializers.CharField(allow_null=True)
    module_order   = serializers.CharField()
    Record_Status      = serializers.CharField()
    main_menus     = MainMenuSerializer(many=True)


from .models import MTTB_MAIN_MENU
class MainMenu_detail(serializers.ModelSerializer):
    class Meta:
        model = MTTB_MAIN_MENU
        fields = ['menu_id', 'menu_name_la', 'menu_name_en']
    
from .models import MTTB_SUB_MENU
class SubMenu_detail(serializers.ModelSerializer):
    class Meta:
        model = MTTB_SUB_MENU
        fields = ['sub_menu_id', 'sub_menu_name_la', 'sub_menu_name_en']

from .models import STTB_ModulesInfo
class ModulesInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = STTB_ModulesInfo
        fields = '__all__'
        read_only_fields = ('Maker_Id', 'Maker_DT_Stamp')

from .models import STTB_ModulesInfo
class STTBModuleSerializers(serializers.ModelSerializer):
    class Meta:
        model = STTB_ModulesInfo
        fields = ['module_Id', 'module_name_la', 'module_name_en']

class MainMenuSerializer(serializers.ModelSerializer):
    module = STTBModuleSerializers(source='module_Id', read_only=True)
    class Meta:
        model = MTTB_MAIN_MENU
        fields = '__all__'
        read_only_fields = ('Maker_Id', 'Maker_DT_Stamp')

class SubMenuSerializer(serializers.ModelSerializer):
    menu = MainMenu_detail(source='menu_id',read_only=True)
    class Meta:
        model = MTTB_SUB_MENU
        fields = '__all__'
        read_only_fields = ('Maker_Id', 'Maker_DT_Stamp',)

class FunctionDescSerializer(serializers.ModelSerializer):
    sub_menu = SubMenu_detail(source='sub_menu_id', read_only=True)
    class Meta:
        model = MTTB_Function_Desc
        fields = '__all__'
        read_only_fields = ('Maker_Id', 'Maker_DT_Stamp', 'Checker_Id', 'Checker_DT_Stamp')

from .models import MTTB_Ccy_DEFN

class CcyDefnSerializer(serializers.ModelSerializer):
    class Meta:
        model = MTTB_Ccy_DEFN
        fields = '__all__'
        read_only_fields = ('Maker_DT_Stamp', 'Checker_DT_Stamp')

from .models import MTTB_EXC_Rate, MTTB_EXC_Rate_History
from rest_framework import serializers
from .models import MTTB_EXC_Rate

class ExcRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MTTB_EXC_Rate
        fields = [
            'id', 
            'ccy_code', 
            'Buy_Rate', 
            'Sale_Rate', 
            'INT_Auth_Status', 
            'Auth_Status',
            'value_date',  # Include this field
            'Maker_Id', 
            'Checker_Id',
            'Maker_DT_Stamp', 
            'Checker_DT_Stamp'
        ]
        read_only_fields = ['id', 'Maker_DT_Stamp', 'Checker_DT_Stamp']

class ExcRateHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MTTB_EXC_Rate_History
        fields = '__all__'
        read_only_fields = ('Maker_DT_Stamp', 'Checker_DT_Stamp')


from rest_framework import serializers
from .models import MTTB_GLMaster
from rest_framework import serializers
from .models import MTTB_GLSub
class GLSubSerializer(serializers.ModelSerializer):
    class Meta:
        model = MTTB_GLSub
        fields = '__all__'
        read_only_fields = ('Maker_DT_Stamp', 'Checker_DT_Stamp')

class GLMasterSerializer(serializers.ModelSerializer):
    # children = GLSubSerializer(many=True, source='glsub_set')
    
    class Meta:
        model = MTTB_GLMaster
        fields = '__all__'
        read_only_fields = ('Maker_DT_Stamp', 'Checker_DT_Stamp')



# class GLSubSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = MTTB_GLSub
#         fields = '__all__'
#         read_only_fields = ('Maker_DT_Stamp', 'Checker_DT_Stamp')

from .models import MTTB_EMPLOYEE,MTTB_LCL_Holiday,MTTB_Divisions,MTTB_Users
from SAMCSYS.serializers import DivisionSerializer

class UserSerial(serializers.ModelSerializer):
    class Meta:
        model = MTTB_Users
        fields = ['user_id', 'user_name']

# class MTTB_EMPLOYEESerializer(serializers.ModelSerializer):
#     user_id = UserSerial(source='user_id',read_only=True)
#     division_id = serializers.SerializerMethodField()  

#     class Meta:
#         model = MTTB_EMPLOYEE
#         fields = '__all__'
from rest_framework import serializers
from .models import MTTB_EMPLOYEE, MTTB_Users, MTTB_Divisions

class EmployeeSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user_id.user_name', read_only=True)
    division_name_la = serializers.CharField(source='div_id.division_name_la', read_only=True)
    employee_photo = serializers.ImageField(required=False, allow_null=True)
    employee_signature = serializers.ImageField(required=False, allow_null=True)
    
    class Meta:
        model = MTTB_EMPLOYEE
        fields = [
            'employee_id', 'user_id', 'user_name', 'employee_name_la', 'employee_name_en',
            'gender', 'date_of_birth', 'national_id', 'address_la', 'address_en',
            'phone_number', 'email', 'position_code', 'div_id', 'division_name_la',
            'employee_photo', 'employee_signature', 'hire_date', 'employment_status',
            'Record_Status', 'Maker_Id', 'Maker_DT_Stamp', 'Checker_Id', 'Checker_DT_Stamp',
            'Auth_Status', 'Once_Auth'
        ]
        read_only_fields = ['Record_Status', 'Maker_Id', 'Maker_DT_Stamp', 'Checker_Id', 'Checker_DT_Stamp', 'Auth_Status', 'Once_Auth']

    def validate_user_id(self, value):
        if value and not MTTB_Users.objects.filter(user_id=value.user_id, User_Status='E').exists():
            raise serializers.ValidationError("Invalid or inactive user_id")
        return value

    def validate_division_id(self, value):
        if value and not MTTB_Divisions.objects.filter(div_id=value.div_id, record_Status='O').exists():
            raise serializers.ValidationError("Invalid or inactive div_id")
        return value

    def validate(self, data):
        if not data.get('employee_name_la'):
            raise serializers.ValidationError({"employee_name_la": "This field is required"})
        if not data.get('div_id'):
            raise serializers.ValidationError({"div_id": "This field is required"})
        return data

from rest_framework import serializers
from .models import MTTB_LCL_Holiday, MTTB_Users

class MTTB_LCL_HolidaySerializer(serializers.ModelSerializer):
    # Read-only fields for displaying user information
    maker_username = serializers.CharField(source='Maker_Id.username', read_only=True)
    checker_username = serializers.CharField(source='Checker_Id.username', read_only=True)
    
    class Meta:
        model = MTTB_LCL_Holiday
        fields = [
            'lcl_holiday_id',
            'HYear',
            'HMonth',
            'HDate',
            'Holiday_List',
            'Record_Status',
            'Maker_Id',
            'maker_username',
            'Maker_DT_Stamp',
            'Checker_Id',
            'checker_username',
            'Checker_DT_Stamp',
            'Auth_Status',
            'Once_Auth'
        ]
        read_only_fields = ['Maker_Id', 'Maker_DT_Stamp', 'Checker_Id', 'Checker_DT_Stamp']


from rest_framework import serializers
from .models import MTTB_Fin_Cycle

class FinCycleSerializer(serializers.ModelSerializer):
    class Meta:
        model = MTTB_Fin_Cycle
        fields = '__all__'
        read_only_fields = ('Maker_DT_Stamp', 'Checker_DT_Stamp')

from rest_framework import serializers
from .models import MTTB_Per_Code

class PerCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MTTB_Per_Code
        fields = '__all__'


from rest_framework import serializers
from .models import MTTB_USER_ACCESS_LOG, MTTB_USER_ACTIVITY_LOG


from .models import MTTB_Users
class UserAccessLogSerializer(serializers.ModelSerializer):
    user = MTTBUserSerializer(source='user_id', read_only=True)
    division = DivisionSerializer(source='div_id', read_only=True)

    class Meta:
        model = MTTB_USER_ACCESS_LOG
        fields = '__all__'
        read_only_fields = ('login_datetime', 'logout_datetime')

class UserActivityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = MTTB_USER_ACTIVITY_LOG
        fields = '__all__'
        read_only_fields = ('activity_datetime',)



class RoleDetailSerializer(serializers.ModelSerializer):
    # Rename writable fields to match model field names
    fuu_details = SubMenuSerializer(source='sub_menu_id', read_only=True)
    role_detail = RoleMasterSerializer(source='role_id', read_only=True)
    role_id = serializers.PrimaryKeyRelatedField(
        queryset=MTTB_Role_Master.objects.all()
    )
    sub_menu_id = serializers.PrimaryKeyRelatedField(
        queryset=MTTB_SUB_MENU.objects.all()
    )

    class Meta:
        model = MTTB_Role_Detail
        fields = '__all__'

from .models import MTTB_TRN_Code

class MTTB_TRN_CodeSerializer(serializers.ModelSerializer):   # Read-only fields for user information
    maker_username = serializers.CharField(source='Maker_Id.username', read_only=True)
    checker_username = serializers.CharField(source='Checker_Id.username', read_only=True)
    
    class Meta:
        model = MTTB_TRN_Code
        fields = [
            'trn_code',
            'trn_Desc_la',
            'trn_Desc_en',
            'Record_Status',
            'Maker_Id',
            'maker_username',
            'Maker_DT_Stamp',
            'Checker_Id',
            'checker_username',
            'Checker_DT_Stamp',
            'Auth_Status',
            'Once_Auth'
        ]
        read_only_fields = ['Maker_Id', 'Maker_DT_Stamp', 'Checker_Id', 'Checker_DT_Stamp']


from rest_framework import serializers
from .models import MTTB_ProvinceInfo, MTTB_DistrictInfo, MTTB_VillageInfo

class ProvinceDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = MTTB_ProvinceInfo
        fields = ['pro_id', 'pro_code', 'pro_name_e', 'pro_name_l']

class ProvinceSerializer(serializers.ModelSerializer):
    class Meta:
        model = MTTB_ProvinceInfo
        fields = '__all__'

class DistrictDetailSerializer(serializers.ModelSerializer):
    pro_detail = serializers.SerializerMethodField()

    class Meta:
        model = MTTB_DistrictInfo
        fields = ['dis_id', 'dis_code', 'dis_name_e', 'dis_name_l', 'pro_id', 'pro_detail']

    def get_pro_detail(self, obj):
        try:
            province = MTTB_ProvinceInfo.objects.get(pro_id=obj.pro_id)
            return ProvinceDetailSerializer(province).data
        except MTTB_ProvinceInfo.DoesNotExist:
            return None

class DistrictSerializer(serializers.ModelSerializer):
    pro_detail = serializers.SerializerMethodField()

    class Meta:
        model = MTTB_DistrictInfo
        fields = '__all__'
        read_only_fields = ('user_id', 'date_insert', 'date_update')

    def get_pro_detail(self, obj):
        try:
            province = MTTB_ProvinceInfo.objects.get(pro_id=obj.pro_id)
            return ProvinceDetailSerializer(province).data
        except MTTB_ProvinceInfo.DoesNotExist:
            return None

class VillageSerializer(serializers.ModelSerializer):
    dis_detail = serializers.SerializerMethodField()

    class Meta:
        model = MTTB_VillageInfo
        fields = '__all__'
        read_only_fields = ('user_id', 'date_insert', 'date_update')

    def get_dis_detail(self, obj):
        try:
            district = MTTB_DistrictInfo.objects.get(dis_code=obj.dis_id)
            return DistrictDetailSerializer(district).data
        except MTTB_DistrictInfo.DoesNotExist:
            return None


from rest_framework import serializers
from .models import MTTB_DATA_Entry

class MTTB_DATA_EntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = MTTB_DATA_Entry
        fields = '__all__'

from rest_framework import serializers
from .models import (
    DETB_JRNL_LOG, MTTB_Ccy_DEFN, MTTB_GLSub, MTTB_TRN_Code,
    MTTB_Fin_Cycle, MTTB_Per_Code, MTTB_Users
)

class CcySerializer(serializers.ModelSerializer):
    class Meta:
        model = MTTB_Ccy_DEFN
        fields = '__all__'

class GLSubSerializer(serializers.ModelSerializer):
    class Meta:
        model = MTTB_GLSub
        fields = '__all__'
class TransactionSerializer(serializers.Serializer):
    glsub_code = serializers.CharField(max_length=20)
    transaction_side = serializers.CharField(max_length=2)
    
    # def validate(self, data):
    #     validate_glsub_selection(data['glsub_code'], data['transaction_side'])
        # return data
class TrnCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MTTB_TRN_Code
        fields = '__all__'

class FinCycleSerializer(serializers.ModelSerializer):
    class Meta:
        model = MTTB_Fin_Cycle
        fields = '__all__'

class PerCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MTTB_Per_Code
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = MTTB_Users
        fields = ['id', 'username']  

class UserSerializers(serializers.ModelSerializer):
    class Meta:
        model = MTTB_Users
        fields = '__all__'  


# serializers.py
from rest_framework import serializers
from django.db import transaction
from decimal import Decimal
from .models import (
    DETB_JRNL_LOG, MTTB_GLSub, MTTB_Ccy_DEFN, MTTB_TRN_Code, 
    MTTB_Fin_Cycle, MTTB_Per_Code, MTTB_Users, STTB_ModulesInfo,
    MTTB_EXC_Rate
)

class JRNLLogSerializer(serializers.ModelSerializer):
    # Read-only fields for display
    currency_name = serializers.CharField(source='Ccy_cd.Ccy_Name_la', read_only=True)
    account_code = serializers.CharField(source='Account.glsub_code', read_only=True)
    account_name = serializers.CharField(source='Account.glsub_Desc_la', read_only=True)
    transaction_name = serializers.CharField(source='Txn_code.trn_Desc_la', read_only=True)
    maker_name = serializers.CharField(source='Maker_Id.user_name', read_only=True)
    checker_name = serializers.CharField(source='Checker_Id.user_name', read_only=True)
    
    class Meta:
        model = DETB_JRNL_LOG
        fields = '__all__'
        read_only_fields = ('JRNLLog_id', 'Maker_DT_Stamp', 'Checker_DT_Stamp')

    def validate_Reference_No(self, value):
        """
        Remove unique validation since Reference_No can be shared
        across multiple entries in the same transaction
        """
        # You can add other validation logic here if needed
        # For example, check format or length
        if len(value) > 30:
            raise serializers.ValidationError("Reference number too long.")
        
        return value

    def validate(self, data):
        """Custom validation for journal entries"""
        # Keep existing validation logic
        if data.get('Fcy_Amount', 0) <= 0:
            raise serializers.ValidationError("Foreign currency amount must be greater than 0.")
        
        if data.get('Lcy_Amount', 0) <= 0:
            raise serializers.ValidationError("Local currency amount must be greater than 0.")
        
        if data.get('Dr_cr') not in ['D', 'C']:
            raise serializers.ValidationError("Dr_cr must be 'D' for Debit or 'C' for Credit.")
        
        if data.get('Exch_rate', 0) <= 0:
            raise serializers.ValidationError("Exchange rate must be greater than 0.")
        
        return data
    

class JournalEntryBatchSerializer(serializers.Serializer):
    """Serializer for batch journal entry creation"""
    Reference_No = serializers.CharField(max_length=30)
    Reference_sub_No = serializers.CharField(max_length=35, required=False, allow_blank=True)
    Ccy_cd = serializers.CharField(max_length=20)
    Txn_code = serializers.CharField(max_length=20)
    Value_date = serializers.DateTimeField()
    Account_no = serializers.CharField(max_length=30, required=False, allow_blank=True)
    Addl_text = serializers.CharField(max_length=255, required=False, allow_blank=True)
    fin_cycle = serializers.CharField(max_length=10, required=False)
    Period_code = serializers.CharField(max_length=20, required=False)
    module_id = serializers.CharField(max_length=20, required=False)
    
    entries = serializers.ListField(
        child=serializers.DictField(),
        min_length=1
    )
    
    def validate_entries(self, entries):
        """Validate journal entries for balanced transaction"""
        total_debit = Decimal('0.00')
        total_credit = Decimal('0.00')
        
        for entry in entries:
            if not entry.get('Account'):
                raise serializers.ValidationError("Each entry must have an Account.")
            
            if not entry.get('Amount') or Decimal(str(entry['Amount'])) <= 0:
                raise serializers.ValidationError("Each entry must have a positive Amount.")
            
            dr_cr = entry.get('Dr_cr')
            amount = Decimal(str(entry['Amount']))
            
            if dr_cr == 'D':
                total_debit += amount
            elif dr_cr == 'C':
                total_credit += amount
            else:
                raise serializers.ValidationError("Each entry must specify Dr_cr as 'D' or 'C'.")
        
        if abs(total_debit - total_credit) > Decimal('0.01'):
            raise serializers.ValidationError(
                f"Transaction is not balanced. Debit: {total_debit}, Credit: {total_credit}"
            )
        
        return entries
    

from rest_framework import serializers
from .models import DETB_JRNL_LOG_MASTER

class DETB_JRNL_LOG_MASTER_Serializer(serializers.ModelSerializer):
    maker_name = serializers.CharField(source='Maker_Id.user_name', read_only=True)
    checker_name = serializers.CharField(source='Checker_Id.user_name', read_only=True)
    class Meta:
        model = DETB_JRNL_LOG_MASTER
        fields = '__all__'

class DETB_JRNL_LOG_MASTER_AC_Serializer(serializers.ModelSerializer):
    maker_name = serializers.CharField(source='Maker_Id.user_name', read_only=True)
    checker_name = serializers.CharField(source='Checker_Id.user_name', read_only=True)
    jrnl_log_ac = serializers.SerializerMethodField()

    class Meta:
        model = DETB_JRNL_LOG_MASTER
        fields = '__all__'

    def get_jrnl_log_ac(self, obj):
        jrnl_log = DETB_JRNL_LOG.objects.filter(Reference_No=obj.Reference_No).first()
        if jrnl_log:
            return {
                "JRNLLog_id": jrnl_log.JRNLLog_id,
                "Ac_relatives": jrnl_log.Ac_relatives
            }
        return None

from rest_framework import serializers
from .models import DETB_JRNL_LOG_MASTER

class DETB_JRNL_LOG_MASTER_ListSerializer(serializers.ModelSerializer):
    """Optimized serializer for list view with only essential fields"""
    maker_name = serializers.CharField(source='Maker_Id.user_name', read_only=True)
    module_name_la = serializers.CharField(source='module_id.module_name_la', read_only=True)
    ccy_code = serializers.CharField(source='Ccy_cd.ccy_code', read_only=True)
    
    class Meta:
        model = DETB_JRNL_LOG_MASTER
        fields = [
            'JRNLLog_id', 'Reference_No', 'Auth_Status', 'module_id',
            'Ccy_cd', 'Fcy_Amount', 'Lcy_Amount', 'Txn_code', 
            'Addl_text', 'Value_date', 'Maker_Id', 'maker_name',
            'module_name_la', 'ccy_code'
        ]

class DETB_JRNL_LOG_MASTER_DetailSerializer(serializers.ModelSerializer):
    """Full serializer for detail view"""
    maker_name = serializers.CharField(source='Maker_Id.user_name', read_only=True)
    checker_name = serializers.CharField(source='Checker_Id.user_name', read_only=True)
    
    class Meta:
        model = DETB_JRNL_LOG_MASTER
        fields = '__all__'
#----------------------Asset---------------------------------------- 
from rest_framework import serializers
from .models import (FA_Asset_Type,FA_Chart_Of_Asset,FA_Suppliers,FA_Location,FA_Expense_Category,FA_Asset_Lists,FA_Asset_List_Depreciation_Main,
    FA_Asset_List_Disposal,FA_Asset_Expense,FA_Transfer_Logs,FA_Asset_Photos,FA_Maintenance_Logs,FA_Asset_List_Depreciation,
    FA_Accounting_Method, MasterCode, MasterType, FA_Asset_List_Depreciation_InMonth)

class AssetTypeDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = FA_Asset_Type
        fields = '__all__'

class AssetTypeDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = FA_Asset_Type
        fields = ['type_code', 'type_name_la', 'type_name_en', 'is_tangible']

class AssetListDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = FA_Asset_Lists
        fields = ['asset_list_id', 'asset_spec','asset_list_code','asset_serial_no','asset_tag']

# class FAAssetTypeSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = FA_Asset_Type
#         fields = '__all__'

class MasterTypeDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = MasterType
        fields = ['M_id', 'M_code', 'M_name_la', 'M_name_en', 'M_detail', 'Status']

class MasterCodeDetail_Serializer(serializers.ModelSerializer):
    class Meta:
        model = MasterCode
        fields = ['MC_id', 'M_id', 'MC_code', 'MC_name_la', 'MC_name_en']

class FAChartOfAssetDetailSerializer(serializers.ModelSerializer):
    asset_type_detail = AssetTypeDetailsSerializer(source='asset_type_id', read_only=True)

    class Meta:
        model = FA_Chart_Of_Asset
        fields = ['coa_id', 'asset_code', 'asset_name_en', 'asset_name_la', 'asset_type_detail']


class ChartOfAssetDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = FA_Chart_Of_Asset
        fields = ['coa_id', 'asset_code', 'asset_name_en', 'asset_name_la']

class MasterCodeDetailSerializer(serializers.ModelSerializer):
    chart_detail = serializers.SerializerMethodField()

    class Meta:
        model = MasterCode
        fields = ['MC_code', 'MC_name_la', 'MC_name_en', 'M_id_id', 'chart_detail']

    def get_chart_detail(self, obj):
        """
        use this connect on FA_Chart_Of_Asset from field M_id_id (isn't FK)
        """
        if not obj.M_id_id:
            return None
        chart = FA_Chart_Of_Asset.objects.filter(coa_id=obj.M_id_id).first()
        if chart:
            return ChartOfAssetDetailSerializer(chart).data
        return None

class FAAssetTypeSerializer(serializers.ModelSerializer):
    mastercode_detail = serializers.SerializerMethodField()

    class Meta:
        model = FA_Asset_Type
        fields = '__all__'

    def get_mastercode_detail(self, obj):
        """
        use this connect on MasterCode from is_tangible (isn't FK)
        """
        if not obj.is_tangible:
            return None
        mc = MasterCode.objects.filter(MC_code=obj.is_tangible).first()
        if mc:
            return MasterCodeDetailSerializer(mc).data
        return None
    
class SuppliersDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = FA_Suppliers
        fields = ['supplier_id', 'supplier_code', 'supplier_name']

class FASuppliersSerializer(serializers.ModelSerializer):
    class Meta:
        model = FA_Suppliers
        fields = '__all__'

class LocationDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = FA_Location
        fields = ['location_id', 'location_code', 'location_name_en', 'location_name_la']

class FALocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = FA_Location
        fields = '__all__'

class FAExpenseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = FA_Expense_Category
        fields = '__all__'

#change on chart serial
from rest_framework import serializers
from django.db import transaction
from django.utils import timezone

class FAAssetListSerializer(serializers.ModelSerializer):
    asset_id_detail = FAChartOfAssetDetailSerializer(source='asset_type_id', read_only=True)
    location_detail = LocationDetailSerializer(source='asset_location_id', read_only=True)
    supplier_detail = SuppliersDetailSerializer(source='supplier_id', read_only=True)
    division_detail = DivisionSerializer(source='division', read_only=True)
    type_of_pay_detail = serializers.SerializerMethodField()
    asset_status_detail = serializers.SerializerMethodField()

    class Meta:
        model = FA_Asset_Lists
        fields = '__all__'

    def get_type_of_pay_detail(self, obj):
        if hasattr(self, '_type_of_pay_cache') and obj.type_of_pay in self._type_of_pay_cache:
            return self._type_of_pay_cache[obj.type_of_pay]

        from .models import MasterCode
        mc = MasterCode.objects.filter(MC_code=obj.type_of_pay).first()
        result = MasterCodeDetail_Serializer(mc).data if mc else None

        if not hasattr(self, '_type_of_pay_cache'):
            self._type_of_pay_cache = {}
        self._type_of_pay_cache[obj.type_of_pay] = result
        return result

    def get_asset_status_detail(self, obj):
        if hasattr(self, '_asset_status_cache') and obj.asset_status in self._asset_status_cache:
            return self._asset_status_cache[obj.asset_status]

        from .models import MasterCode
        mc = MasterCode.objects.filter(MC_code=obj.asset_status).first()
        result = MasterCodeDetail_Serializer(mc).data if mc else None

        if not hasattr(self, '_asset_status_cache'):
            self._asset_status_cache = {}
        self._asset_status_cache[obj.asset_status] = result
        return result




# class FAAssetListSerializer(serializers.ModelSerializer):
#     asset_id_detail = FAChartOfAssetDetailSerializer(source='asset_type_id', read_only=True)
#     location_detail = LocationDetailSerializer(source='asset_location_id', read_only=True)
#     supplier_detail = SuppliersDetailSerializer(source='supplier_id', read_only=True)
#     type_of_pay_detail = serializers.SerializerMethodField()
#     asset_status_detail = serializers.SerializerMethodField()

#     class Meta:
#         model = FA_Asset_Lists
#         fields = '__all__'

#     def get_type_of_pay_detail(self, obj):
#         from .models import MasterCode
#         mc = MasterCode.objects.filter(MC_code=obj.type_of_pay).first()
#         if mc:
#             return MasterCodeDetail_Serializer(mc).data
#         return None

#     def get_asset_status_detail(self, obj):
#         from .models import MasterCode
#         mc = MasterCode.objects.filter(MC_code=obj.asset_status).first()
#         if mc:
#             return MasterCodeDetail_Serializer(mc).data
#         return None

# class FADepreciationMainSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = FA_Depreciation_Main
#         fields = '__all__'

# class FADepreciationSubSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = FA_Depreciation_Sub
#         fields = '__all__'

class FAAssetListDepreciationMainSerializer(serializers.ModelSerializer):
    asset_list_id_detail = AssetListDetailsSerializer(source='asset_list_id', read_only=True)
    class Meta:
        model = FA_Asset_List_Depreciation_Main
        fields = '__all__'

class FAAssetListDepreciationSerializer(serializers.ModelSerializer):
    asset_list_id_detail = AssetListDetailsSerializer(source='asset_list_id', read_only=True)
    class Meta:
        model = FA_Asset_List_Depreciation
        fields = '__all__'

class FAAssetListDisposalSerializer(serializers.ModelSerializer):
    class Meta:
        model = FA_Asset_List_Disposal
        fields = '__all__'

class FAAssetExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = FA_Asset_Expense
        fields = '__all__'

class FATransferLogsSerializer(serializers.ModelSerializer):
    asset_list_id_detail = AssetListDetailsSerializer(source='asset_list_id', read_only=True)
    from_location_detail = LocationDetailSerializer(source='from_location_id', read_only=True)
    to_location_detail = LocationDetailSerializer(source='to_location_id', read_only=True)
    
    # ເພີ່ມ field division ເພື່ອຮັບຂໍ້ມູນຈາກ frontend (ແຕ່ບໍ່ບັນທຶກໃນ FA_Transfer_Logs)
    division = serializers.PrimaryKeyRelatedField(
        queryset=MTTB_Divisions.objects.all(),
        required=False,
        allow_null=True,
        write_only=True  # ໃຊ້ສຳລັບຮັບຂໍ້ມູນຈາກ frontend ເທົ່ານັ້ນ
    )
    
    class Meta:
        model = FA_Transfer_Logs
        fields = '__all__'
    
    def create(self, validated_data):
        # ດຶງ division ອອກຈາກ validated_data ກ່ອນສ້າງ record
        division = validated_data.pop('division', None)
        
        # ສ້າງ FA_Transfer_Logs record ໂດຍບໍ່ມີ division field
        instance = super().create(validated_data)
        
        # ເກັບ division ໄວ້ເພື່ອໃຊ້ໃນ ViewSet
        instance._division_for_asset_update = division
        
        return instance
    
    def create(self, validated_data):
        # ດຶງ division ອອກຈາກ validated_data ກ່ອນສ້າງ FA_Transfer_Logs record
        division = validated_data.pop('division', None)
        
        # ສ້າງ FA_Transfer_Logs record ໂດຍບໍ່ມີ division field
        instance = super().create(validated_data)
        
        # ເກັບ division ໄວ້ເພື່ອໃຊ້ໃນ ViewSet
        instance._division_for_asset_update = division
        
        return instance
    
    def create(self, validated_data):
        # ດຶງ division ອອກຈາກ validated_data ກ່ອນສ້າງ FA_Transfer_Logs record
        division = validated_data.pop('division', None)
        
        # ສ້າງ FA_Transfer_Logs record ໂດຍບໍ່ມີ division field
        instance = super().create(validated_data)
        
        # ເກັບ division ໄວ້ເພື່ອໃຊ້ໃນ ViewSet
        instance._division_for_asset_update = division
        
        return instance

class FAAssetPhotosSerializer(serializers.ModelSerializer):
    class Meta:
        model = FA_Asset_Photos
        fields = '__all__'

class FAMaintenanceLogsSerializer(serializers.ModelSerializer):
    asset_list_id_detail = AssetListDetailsSerializer(source='asset_list_id', read_only=True)
    supplier_detail = SuppliersDetailSerializer(source='supplier_id', read_only=True)
    class Meta:
        model = FA_Maintenance_Logs
        fields = '__all__'

class FAAccountingMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = FA_Accounting_Method
        fields = '__all__'

class FAAssetListDepreciationInMonthSerializer(serializers.ModelSerializer):
    class Meta:
        model = FA_Asset_List_Depreciation_InMonth
        fields = '__all__'


from rest_framework import serializers
from .models import MTTB_EOC_MAINTAIN, STTB_ModulesInfo, MTTB_Function_Desc, MTTB_Users

class EOCMaintainSerializer(serializers.ModelSerializer):
    # Read-only fields for user information
    maker_name = serializers.CharField(source='Maker_Id.username', read_only=True)
    checker_name = serializers.CharField(source='Checker_Id.username', read_only=True)
    module_name = serializers.CharField(source='module_id.module_name', read_only=True)
    function_name = serializers.CharField(source='function_id.description_la', read_only=True)
    
    class Meta:
        model = MTTB_EOC_MAINTAIN
        fields = '__all__'
        read_only_fields = ('eoc_id', 'Maker_Id', 'Maker_DT_Stamp', 'Checker_Id', 'Checker_DT_Stamp')

    def validate(self, data):
        """Custom validation logic"""
        if data.get('eoc_type') and len(data['eoc_type']) > 3:
            raise serializers.ValidationError("eoc_type ບໍ່ສາມາດເກີນ 3 ຕົວອັກສອນ")
        
        if data.get('record_stat') and data['record_stat'] not in ['C', 'O']:
            raise serializers.ValidationError("record_stat ຕ້ອງເປັນ 'C' ຫຼື 'O' ເທົ່ານັ້ນ")
            
        return data
    
from rest_framework import serializers
from .models import MasterType, MasterCode

class MasterTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MasterType
        fields = ['M_id', 'M_code', 'M_name_la', 'M_name_en', 'M_detail', 'Status']

class MasterCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MasterCode
        fields = ['MC_id', 'M_id', 'MC_code', 'MC_name_la', 'MC_name_en', 'MC_detail', 'Status', 'BOL_code', 'BOL_name']

from rest_framework import serializers
from .models import FA_Chart_Of_Asset, MasterCode
from .serializers import AssetTypeDetailSerializer, MasterCodeSerializer
class FAChartOfAssetSerializer(serializers.ModelSerializer):
    asset_type_detail = AssetTypeDetailSerializer(source='asset_type_id', read_only=True)
    tangible_detail = serializers.SerializerMethodField()

    class Meta:
        model = FA_Chart_Of_Asset
        fields = '__all__'

    def get_tangible_detail(self, obj):
        if not obj.asset_type_id or not obj.asset_type_id.is_tangible:
            return None

        is_tangible = obj.asset_type_id.is_tangible
        if not hasattr(self, '_master_code_cache'):
            self._master_code_cache = {}

        if is_tangible in self._master_code_cache:
            return self._master_code_cache[is_tangible]

        try:
            master_code = MasterCode.objects.get(MC_code=is_tangible, M_id_id='1003')
            result = MasterCodeSerializer(master_code).data
            self._master_code_cache[is_tangible] = result
            return result
        except MasterCode.DoesNotExist:
            return None

class GLSubDisplaySerializer(serializers.ModelSerializer):
    outstanding = serializers.CharField(source='gl_code.outstanding', read_only=True)
    gl_code = serializers.CharField(source='gl_code.gl_code', read_only=True)
    gl_Desc_la = serializers.CharField(source='gl_code.gl_Desc_la', read_only=True)
    gl_Desc_en = serializers.CharField(source='gl_code.gl_Desc_en', read_only=True)

    class Meta:
        model = MTTB_GLSub
        fields = [
            'glsub_id', 'glsub_code', 'glsub_Desc_la', 'glsub_Desc_en',
            'outstanding', 'gl_code', 'gl_Desc_la', 'gl_Desc_en',
            'Record_Status', 'Maker_Id', 'Maker_DT_Stamp', 'Checker_Id',
            'Checker_DT_Stamp', 'Auth_Status', 'Once_Auth'
        ]

from rest_framework import serializers
from .models import Dairy_Report

class DairyReportSerializer(serializers.ModelSerializer):
    CCy_Code_display = serializers.CharField(source='CCy_Code.ccy_code', read_only=True)
    Fin_year_display = serializers.CharField(source='Fin_year.fin_year', read_only=True)
    Period_code_display = serializers.CharField(source='Period_code.period_code', read_only=True)
    Maker_display = serializers.CharField(source='Maker_Id.username', read_only=True)

    class Meta:
        model = Dairy_Report
        fields = '__all__'
        read_only_fields = ('DP_ID', 'InsertDate', 'UpdateDate')

    def validate(self, data):
        """
        Custom validation for the dairy report data
        """
        # Add any custom validation logic here
        if data.get('StartDate') and data.get('EndDate'):
            if data['StartDate'] > data['EndDate']:
                raise serializers.ValidationError({
                    'EndDate': 'ວັນທີສິ້ນສຸດຕ້ອງບໍ່ນ້ອຍກວ່າວັນທີເລີ່ມຕົ້ນ'
                })
        
        return data
    

from rest_framework import serializers
from .models import CompanyProfileInfo

class CompanyProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyProfileInfo
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

    def validate_name_la(self, value):
        if not value or len(value.strip()) < 2:
            raise serializers.ValidationError("ຊື່ບໍລິສັດເປັນພາສາລາວຕ້ອງມີຢ່າງນ້ອຍ 2 ຕົວອັກສອນ")
        return value.strip()
    

    def validate_email(self, value):
        if value and not value.strip():
            return None
        return value
    
# newww
from rest_framework import serializers
from .models import FA_Asset_Audit
from .serializers import AssetListDetailsSerializer,DivisionSerializer

class FAAssetAuditSerializer(serializers.ModelSerializer):
    asset_list_id_detail = AssetListDetailsSerializer(source='asset_list_id', read_only=True)
    division_id_detail = DivisionSerializer(source='department_id', read_only=True)
    class Meta:
        model = FA_Asset_Audit 
        fields = '__all__'


# IImplement End of Journal Validation

from rest_framework import serializers
from .models import (
    STTB_Dates, MTTB_EOC_MAINTAIN, STTB_EOC_DAILY_LOG,
    MTTB_Function_Desc, MTTB_LCL_Holiday
)


class EODDateSerializer(serializers.ModelSerializer):
    """
    Serializer for STTB_Dates model
    """
    start_date_formatted = serializers.SerializerMethodField()
    prev_working_day_formatted = serializers.SerializerMethodField()
    next_working_day_formatted = serializers.SerializerMethodField()
    eod_status = serializers.SerializerMethodField()
    
    class Meta:
        model = STTB_Dates
        fields = [
            'date_id', 'Start_Date', 'prev_Working_Day', 'next_working_Day',
            'eod_time', 'Maker_Id', 'Maker_DT_Stamp', 'Checker_Id', 'Checker_DT_Stamp',
            'start_date_formatted', 'prev_working_day_formatted', 
            'next_working_day_formatted', 'eod_status'
        ]
    
    def get_start_date_formatted(self, obj):
        return obj.Start_Date.strftime('%Y-%m-%d') if obj.Start_Date else None
    
    def get_prev_working_day_formatted(self, obj):
        return obj.prev_Working_Day.strftime('%Y-%m-%d') if obj.prev_Working_Day else None
    
    def get_next_working_day_formatted(self, obj):
        return obj.next_working_Day.strftime('%Y-%m-%d') if obj.next_working_Day else None
    
    def get_eod_status(self, obj):
        return 'ສຳເລັດແລ້ວ' if obj.eod_time == 'Y' else 'ລໍຖ້າດຳເນີນການ'


class EODFunctionSerializer(serializers.ModelSerializer):
    """
    Serializer for EOD Functions
    """
    function_description = serializers.CharField(source='function_id.description_la', read_only=True)
    module_name = serializers.CharField(source='module_id.module_id', read_only=True)
    is_active = serializers.SerializerMethodField()
    
    class Meta:
        model = MTTB_EOC_MAINTAIN
        fields = [
            'eoc_seq_no', 'function_id', 'function_description',
            'module_id', 'module_name', 'Record_Status', 'Auth_Status',
            'is_active'
        ]
    
    def get_is_active(self, obj):
        return obj.Record_Status == 'O'


class EODExecutionLogSerializer(serializers.ModelSerializer):
    """
    Serializer for EOD Execution Logs
    """
    function_name = serializers.CharField(source='function_id.description_la', read_only=True)
    status_display = serializers.SerializerMethodField()
    
    class Meta:
        model = STTB_EOC_DAILY_LOG
        fields = [
            'log_id', 'function_id', 'function_name', 'processing_date',
            'execution_status', 'status_display', 'error_message',
            'executed_by', 'execution_time'
        ]
    
    def get_status_display(self, obj):
        status_map = {
            'SUCCESS': 'ສຳເລັດ',
            'FAILED': 'ລົ້ມເຫລວ',
            'ERROR': 'ຂໍ້ຜິດພາດ',
            'PENDING': 'ລໍຖ້າ'
        }
        return status_map.get(obj.execution_status, obj.execution_status)


class EODSubmissionSerializer(serializers.Serializer):
    """
    Serializer for EOD submission request
    """
    value_date = serializers.DateField(
        required=False,
        help_text='ວັນທີທີ່ຕ້ອງການປະມວນຜົນ EOD'
    )
    is_back_date = serializers.BooleanField(
        default=False,
        help_text='ກຳນົດວ່າເປັນການປະມວນຜົນຍ້ອນຫຼັງຫຼືບໍ່'
    )
    eod_id = serializers.IntegerField(
        required=False,
        help_text='EOD ID ສຳລັບການປະມວນຜົນຍ້ອນຫຼັງ'
    )
    
    def validate(self, data):
        """
        Validate EOD submission data
        """
        if data.get('is_back_date') and not data.get('eod_id'):
            raise serializers.ValidationError(
                'ຕ້ອງລະບຸ eod_id ສຳລັບການປະມວນຜົນຍ້ອນຫຼັງ'
            )
        
        if not data.get('is_back_date') and data.get('eod_id'):
            raise serializers.ValidationError(
                'eod_id ໃຊ້ສະເພາະການປະມວນຜົນຍ້ອນຫຼັງເທົ່ານັ້ນ'
            )
        
        return data


class HolidaySerializer(serializers.ModelSerializer):
    """
    Serializer for Holiday Calendar
    """
    working_days_count = serializers.SerializerMethodField()
    holidays_count = serializers.SerializerMethodField()
    
    class Meta:
        model = MTTB_LCL_Holiday
        fields = [
            'HYear', 'HMonth', 'Holiday_List',
            'working_days_count', 'holidays_count'
        ]
    
    def get_working_days_count(self, obj):
        if obj.Holiday_List:
            return obj.Holiday_List.count('W')
        return 0
    
    def get_holidays_count(self, obj):
        if obj.Holiday_List:
            return obj.Holiday_List.count('H')
        return 0
    
from .models import STTB_Somtop_Trial_Balancesheet
class SomtopTrialBalancesheetSerializer(serializers.ModelSerializer):
    """
    Serializer for STTB_Somtop_Trial_Balancesheet model
    """
    class Meta:
        model = STTB_Somtop_Trial_Balancesheet
        fields = '__all__'
        read_only_fields = ('Maker_Id', 'Maker_DT_Stamp', 'Checker_Id', 'Checker_DT_Stamp')

from rest_framework import serializers
from .models import DETB_JRNL_LOG

class PreMainSerializer(serializers.Serializer):
    aldm_id = serializers.IntegerField()
    dpca_desc = serializers.CharField()

class DETB_JRNL_LOGSerializer_Asset(serializers.ModelSerializer):
    pre_main = serializers.SerializerMethodField()

    class Meta:
        model = DETB_JRNL_LOG
        fields = '__all__' 

    def get_pre_main(self, obj):
        return {
            "aldm_id": getattr(obj, 'aldm_id', None),
            "dpca_desc": getattr(obj, 'dpca_desc', None)
        }
class DETB_JRNL_LOG_MASTER_Serializer_dps(serializers.ModelSerializer):
    class Meta:
        model = DETB_JRNL_LOG_MASTER
        fields = '__all__'
from rest_framework import serializers
from decimal import Decimal
from .models import (
    DETB_JRNL_LOG, DETB_JRNL_LOG_HIST,
    MTTB_GLSub, MTTB_GLMaster, MTTB_TRN_Code,
    DETB_JRNL_LOG_MASTER, ACTB_DAIRY_LOG, ACTB_DAIRY_LOG_HISTORY
)

# Serializer ສຳລັບ DETB_JRNL_LOG
class JRNLLogSerializer(serializers.ModelSerializer):
    currency_name = serializers.CharField(source='Ccy_cd.Ccy_Name_la', read_only=True)
    account_code = serializers.CharField(source='Account.glsub_code', read_only=True)
    account_name = serializers.CharField(source='Account.glsub_Desc_la', read_only=True)
    transaction_name = serializers.CharField(source='Txn_code.trn_Desc_la', read_only=True)
    maker_name = serializers.CharField(source='Maker_Id.user_name', read_only=True)
    checker_name = serializers.CharField(source='Checker_Id.user_name', read_only=True)
    
    class Meta:
        model = DETB_JRNL_LOG
        fields = '__all__'
        read_only_fields = ('JRNLLog_id', 'Maker_DT_Stamp', 'Checker_DT_Stamp')

    def validate_Reference_No(self, value):
        if len(value) > 30:
            raise serializers.ValidationError("Reference number too long.")
        return value

    def validate(self, data):
        if data.get('Fcy_Amount', 0) <= 0:
            raise serializers.ValidationError("Foreign currency amount must be greater than 0.")
        if data.get('Lcy_Amount', 0) <= 0:
            raise serializers.ValidationError("Local currency amount must be greater than 0.")
        if data.get('Dr_cr') not in ['D', 'C']:
            raise serializers.ValidationError("Dr_cr must be 'D' for Debit or 'C' for Credit.")
        if data.get('Exch_rate', 0) <= 0:
            raise serializers.ValidationError("Exchange rate must be greater than 0.")
        return data

# Serializer ສຳລັບ DETB_JRNL_LOG_HIST
class JRNLLogHistSerializer(serializers.ModelSerializer):
    currency_name = serializers.CharField(source='Ccy_cd.Ccy_Name_la', read_only=True)
    account_code = serializers.CharField(source='Account.glsub_code', read_only=True)
    account_name = serializers.CharField(source='Account.glsub_Desc_la', read_only=True)
    transaction_name = serializers.CharField(source='Txn_code.trn_Desc_la', read_only=True)
    maker_name = serializers.CharField(source='Maker_Id.user_name', read_only=True)
    checker_name = serializers.CharField(source='Checker_Id.user_name', read_only=True)
    ac_relatives = serializers.CharField(source='Ac_relatives', read_only=True)

    class Meta:
        model = DETB_JRNL_LOG_HIST
        fields = '__all__'
        read_only_fields = ('JRNLLog_id', 'Maker_DT_Stamp', 'Checker_DT_Stamp')

    def validate_Reference_No(self, value):
        if len(value) > 30:
            raise serializers.ValidationError("Reference number too long.")
        return value

    def validate(self, data):
        if data.get('Fcy_Amount', 0) <= 0:
            raise serializers.ValidationError("Foreign currency amount must be greater than 0.")
        if data.get('Lcy_Amount', 0) <= 0:
            raise serializers.ValidationError("Local currency amount must be greater than 0.")
        if data.get('Dr_cr') not in ['D', 'C']:
            raise serializers.ValidationError("Dr_cr must be 'D' for Debit or 'C' for Credit.")
        if data.get('Exch_rate', 0) <= 0:
            raise serializers.ValidationError("Exchange rate must be greater than 0.")
        return data

# Serializer ສຳລັບ batch journal entries
class JournalEntryBatchSerializer(serializers.Serializer):
    Reference_No = serializers.CharField(max_length=30)
    Reference_sub_No = serializers.CharField(max_length=35, required=False, allow_blank=True)
    Ccy_cd = serializers.CharField(max_length=20)
    Txn_code = serializers.CharField(max_length=20)
    Value_date = serializers.DateTimeField()
    Account_no = serializers.CharField(max_length=30, required=False, allow_blank=True)
    Addl_text = serializers.CharField(max_length=255, required=False, allow_blank=True)
    fin_cycle = serializers.CharField(max_length=10, required=False)
    Period_code = serializers.CharField(max_length=20, required=False)
    module_id = serializers.CharField(max_length=20, required=False)
    
    entries = serializers.ListField(
        child=serializers.DictField(),
        min_length=1
    )
    
    def validate_entries(self, entries):
        total_debit = Decimal('0.00')
        total_credit = Decimal('0.00')
        for entry in entries:
            if not entry.get('Account'):
                raise serializers.ValidationError("Each entry must have an Account.")
            if not entry.get('Amount') or Decimal(str(entry['Amount'])) <= 0:
                raise serializers.ValidationError("Each entry must have a positive Amount.")
            dr_cr = entry.get('Dr_cr')
            amount = Decimal(str(entry['Amount']))
            if dr_cr == 'D':
                total_debit += amount
            elif dr_cr == 'C':
                total_credit += amount
            else:
                raise serializers.ValidationError("Each entry must specify Dr_cr as 'D' or 'C'.")
        if abs(total_debit - total_credit) > Decimal('0.01'):
            raise serializers.ValidationError(
                f"Transaction is not balanced. Debit: {total_debit}, Credit: {total_credit}"
            )
        return entries

