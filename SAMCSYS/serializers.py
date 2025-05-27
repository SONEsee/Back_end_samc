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



class RoleDetailSerializer(serializers.ModelSerializer):
    # Rename writable fields to match model field names
    role_id = serializers.PrimaryKeyRelatedField(
        queryset=MTTB_Role_Master.objects.all()
    )
    function_id = serializers.PrimaryKeyRelatedField(
        queryset=MTTB_Function_Desc.objects.all()
    )

    class Meta:
        model = MTTB_Role_Detail
        fields = [
            'role_id',
            'function_id',
            'New_Detail',
            'Del_Detail',
            'Edit_Detail',
            'Auth_Detail',
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

class MTTB_EMPLOYEESerializer(serializers.ModelSerializer):
    user_id = UserSerial(source='user_id',read_only=True)
    division_id = serializers.SerializerMethodField()  

    class Meta:
        model = MTTB_EMPLOYEE
        fields = '__all__'

    def get_division_id(self, obj):
        from SAMCSYS.serializers import DivisionSerializer
        from SAMCSYS.models import MTTB_Divisions
        try:
            division = MTTB_Divisions.objects.get(div_id=obj.division_id)
            return DivisionSerializer(division).data
        except MTTB_Divisions.DoesNotExist:
            return None

class MTTB_LCL_HolidaySerializer(serializers.ModelSerializer):
    class Meta:
        model = MTTB_LCL_Holiday
        fields = '__all__'


from rest_framework import serializers
from .models import MTTB_Fin_Cycle

class FinCycleSerializer(serializers.ModelSerializer):
    class Meta:
        model = MTTB_Fin_Cycle
        fields = '__all__'
        read_only_fields = ('Maker_DT_Stamp', 'Checker_DT_Stamp')

from rest_framework import serializers
from .models import MTTB_USER_ACCESS_LOG, MTTB_USER_ACTIVITY_LOG

class UserAccessLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = MTTB_USER_ACCESS_LOG
        fields = '__all__'
        read_only_fields = ('login_datetime', 'logout_datetime')

class UserActivityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = MTTB_USER_ACTIVITY_LOG
        fields = '__all__'
        read_only_fields = ('activity_datetime',)