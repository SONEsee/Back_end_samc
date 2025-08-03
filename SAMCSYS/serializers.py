import hashlib
from rest_framework import serializers
from .models import MTTB_Users
from .models import MTTB_Users, MTTB_Divisions, MTTB_Role_Master,STTB_ModulesInfo,MTTB_MAIN_MENU,MTTB_SUB_MENU,MTTB_Function_Desc
class DivisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MTTB_Divisions
        fields = ['div_id', 'division_name_la', 'division_name_en', 'Record_Status']

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
        fields = ['id', 'username']  # Adjust fields to match your model


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
        fields = ['type_code', 'type_name_la', 'type_name_en']

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

class FAAssetListSerializer(serializers.ModelSerializer):
    asset_id_detail = FAChartOfAssetDetailSerializer(source='asset_type_id', read_only=True)
    location_detail = LocationDetailSerializer(source='asset_location_id', read_only=True)
    supplier_detail = SuppliersDetailSerializer(source='supplier_id', read_only=True)
    type_of_pay_detail = serializers.SerializerMethodField()
    asset_status_detail = serializers.SerializerMethodField()

    class Meta:
        model = FA_Asset_Lists
        fields = '__all__'

    def get_type_of_pay_detail(self, obj):
        from .models import MasterCode
        mc = MasterCode.objects.filter(MC_code=obj.type_of_pay).first()
        if mc:
            return MasterCodeDetail_Serializer(mc).data
        return None

    def get_asset_status_detail(self, obj):
        from .models import MasterCode
        mc = MasterCode.objects.filter(MC_code=obj.asset_status).first()
        if mc:
            return MasterCodeDetail_Serializer(mc).data
        return None

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
    class Meta:
        model = FA_Transfer_Logs
        fields = '__all__'

class FAAssetPhotosSerializer(serializers.ModelSerializer):
    class Meta:
        model = FA_Asset_Photos
        fields = '__all__'

class FAMaintenanceLogsSerializer(serializers.ModelSerializer):
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
        try:
            # Access is_tangible from the related FA_Asset_Type
            is_tangible = obj.asset_type_id.is_tangible
            # Fetch MasterCode where MC_code matches is_tangible and M_id_id = '1003'
            master_code = MasterCode.objects.get(MC_code=is_tangible, M_id_id='1003')
            return MasterCodeSerializer(master_code).data
        except (MasterCode.DoesNotExist, AttributeError):
            return None  # Return None if no matching MasterCode or FA_Asset_Type is found
        

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