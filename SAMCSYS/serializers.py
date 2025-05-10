import hashlib
from rest_framework import serializers
from .models import MTTB_User

class MTTBUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = MTTB_User
        fields = [
            "id",
            "User_Id",
            "User_Name",
            "User_Password",
            "User_Email",
            "User_Mobile",
            "Div_Id",
            "User_Status",
            "Maker_Id",
            "Maker_DT_Stamp",
            "Checker_Id",
            "Checker_DT_Stamp",
            "Auth_Status",
            "Once_Auth",
            "Role_ID",
            "InsertDate",
            "UpdateDate",
        ]
        extra_kwargs = {
            "User_Password": {"write_only": True}
        }

    def _hash(self, raw_password):
        return hashlib.md5(raw_password.encode("utf-8")).hexdigest()

    def create(self, validated_data):
        raw = validated_data.pop("User_Password")
        validated_data["User_Password"] = self._hash(raw)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if "User_Password" in validated_data:
            raw = validated_data.pop("User_Password")
            validated_data["User_Password"] = self._hash(raw)
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
    MTTB_Function_Description,
    STTB_MDdulesInfo,
)

class STTBModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = STTB_MDdulesInfo
        fields = ['M_Id', 'M_NameL', 'M_NameE']


class FunctionDescriptionSerializer(serializers.ModelSerializer):
    M_Id = STTBModuleSerializer(read_only=True)

    class Meta:
        model = MTTB_Function_Description
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
        queryset=MTTB_Function_Description.objects.all()
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

