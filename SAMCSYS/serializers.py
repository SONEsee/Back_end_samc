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