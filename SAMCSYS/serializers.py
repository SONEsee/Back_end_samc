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
            'user_password': {'write_only': True}
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
            'Function_Id',
            'Function_Desc',
            'Main_Menu',
            'Sub_Menu',
            'All_Link',
            'M_Id',
            'Function_Status',
        ]



class RoleDetailSerializer(serializers.ModelSerializer):
    # Writable fields for foreign keys
    Role_Id = serializers.PrimaryKeyRelatedField(
        queryset=MTTB_Role_Master.objects.all()
    )
    Function_Id = serializers.PrimaryKeyRelatedField(
        queryset=MTTB_Function_Desc.objects.all()
    )

    class Meta:
        model = MTTB_Role_Detail
        fields = [
            'id',
            'Role_Id',
            'Function_Id',
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

from .models import STTB_ModulesInfo
class ModulesInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = STTB_ModulesInfo
        fields = '__all__'

class MainMenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = MTTB_MAIN_MENU
        fields = '__all__'

class SubMenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = MTTB_SUB_MENU
        fields = '__all__'

class FunctionDescSerializer(serializers.ModelSerializer):
    class Meta:
        model = MTTB_Function_Desc
        fields = '__all__'

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