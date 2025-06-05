import hashlib
from rest_framework import serializers
from .models import MTTB_Users
from .models import MTTB_Users, MTTB_Divisions, MTTB_Role_Master,STTB_ModulesInfo,MTTB_MAIN_MENU,MTTB_SUB_MENU,MTTB_Function_Desc
class DivisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MTTB_Divisions
        fields = ['div_id', 'division_name_la', 'division_name_en', 'record_Status']

class RoleMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = MTTB_Role_Master
        fields = ['role_id', 'role_name_la', 'role_name_en', 'record_Status']

class MTTBUserSerializer(serializers.ModelSerializer):
    # Nested read-only representations
    division = DivisionSerializer(source='div_id', read_only=True)
    role     = RoleMasterSerializer(source='Role_ID', read_only=True)

    # Writable PK fields
    div_id   = serializers.PrimaryKeyRelatedField(
        queryset=MTTB_Divisions.objects.all(), write_only=True, required=False
    )
    Role_ID  = serializers.PrimaryKeyRelatedField(
        queryset=MTTB_Role_Master.objects.all(), write_only=True, required=False
    )

    class Meta:
        model = MTTB_Users
        fields = [
            'user_id',
            'user_name',
            'user_password',
            'user_email',
            'user_mobile',
            'User_Status',
            'pwd_changed_on',
            'div_id',
            'division',
            'Role_ID',
            'role',
            'profile_picture',
            'InsertDate',
            'UpdateDate',
            'Maker_Id',
            'Maker_DT_Stamp',
            'Checker_Id',
            'Checker_DT_Stamp',
            'Auth_Status',
            'Once_Auth',
        ]
        extra_kwargs = {
            'user_password': {'write_only': True},
             'profile_picture': {'required': False, 'allow_null': True},
        }

    def _hash(self, raw_password):
        return hashlib.md5(raw_password.encode('utf-8')).hexdigest()

    def create(self, validated_data):
        raw_pwd = validated_data.pop('user_password')
        validated_data['user_password'] = self._hash(raw_pwd)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # If password is being updated, hash it
        raw = validated_data.get('user_password')
        if raw:
            validated_data['user_password'] = self._hash(raw)
        return super().update(instance, validated_data)

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
    is_active      = serializers.BooleanField()
    functions      = FunctionPermSerializer(many=True)

class MainMenuSerializer(serializers.Serializer):
    menu_id        = serializers.CharField()
    menu_name_la   = serializers.CharField()
    menu_name_en   = serializers.CharField()
    menu_icon      = serializers.CharField(allow_null=True)
    menu_order     = serializers.CharField()
    is_active      = serializers.BooleanField()
    SubMenuSerializer = SubMenuSerializer(many=True)

class ModuleSerializer(serializers.Serializer):
    module_Id      = serializers.CharField()
    module_name_la = serializers.CharField()
    module_name_en = serializers.CharField()
    module_icon    = serializers.CharField(allow_null=True)
    module_order   = serializers.CharField()
    is_active      = serializers.CharField()
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
        read_only_fields = ('created_by', 'created_date', 'modified_by', 'modified_date')

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
        read_only_fields = ('created_by', 'created_date', 'modified_by', 'modified_date')

class SubMenuSerializer(serializers.ModelSerializer):
    menu = MainMenu_detail(source='menu_id',read_only=True)
    class Meta:
        model = MTTB_SUB_MENU
        fields = '__all__'
        read_only_fields = ('created_by', 'created_date', 'modified_by', 'modified_date')

class FunctionDescSerializer(serializers.ModelSerializer):
    sub_menu = SubMenu_detail(source='sub_menu_id', read_only=True)
    class Meta:
        model = MTTB_Function_Desc
        fields = '__all__'
        read_only_fields = ('created_by', 'created_date', 'modified_by', 'modified_date')

from .models import MTTB_Ccy_DEFN

class CcyDefnSerializer(serializers.ModelSerializer):
    class Meta:
        model = MTTB_Ccy_DEFN
        fields = '__all__'
        read_only_fields = ('Maker_DT_Stamp', 'Checker_DT_Stamp')

from .models import MTTB_EXC_Rate, MTTB_EXC_Rate_History

class ExcRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MTTB_EXC_Rate
        fields = '__all__'
        read_only_fields = ('Maker_DT_Stamp', 'Checker_DT_Stamp')

class ExcRateHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MTTB_EXC_Rate_History
        fields = '__all__'
        read_only_fields = ('Maker_DT_Stamp', 'Checker_DT_Stamp')


from rest_framework import serializers
from .models import MTTB_GLMaster

class GLMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = MTTB_GLMaster
        fields = '__all__'
        read_only_fields = ('Maker_DT_Stamp', 'Checker_DT_Stamp')

from rest_framework import serializers
from .models import MTTB_GLSub

class GLSubSerializer(serializers.ModelSerializer):
    class Meta:
        model = MTTB_GLSub
        fields = '__all__'
        read_only_fields = ('Maker_DT_Stamp', 'Checker_DT_Stamp')

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
            'record_stat', 'Maker_Id', 'Maker_DT_Stamp', 'Checker_Id', 'Checker_DT_Stamp',
            'Auth_Status', 'Once_Auth'
        ]
        read_only_fields = ['record_stat', 'Maker_Id', 'Maker_DT_Stamp', 'Checker_Id', 'Checker_DT_Stamp', 'Auth_Status', 'Once_Auth']

    def validate_user_id(self, value):
        if value and not MTTB_Users.objects.filter(user_id=value.user_id, User_Status='E').exists():
            raise serializers.ValidationError("Invalid or inactive user_id")
        return value

    def validate_division_id(self, value):
        if value and not MTTB_Divisions.objects.filter(div_id=value.div_id, record_Status='C').exists():
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

