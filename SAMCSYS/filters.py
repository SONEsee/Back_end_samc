# ໃນໄຟລ໌ filters.py
from django_filters import rest_framework as filters
from .models import DETB_JRNL_LOG_MASTER

class JournalLogARDFilter(filters.FilterSet):
    # ປ່ຽນ fin_cycle ເປັນ NumberFilter ເພື່ອເປີດກວ້າງ
    fin_cycle = filters.NumberFilter(
        field_name='fin_cycle',
        lookup_expr='exact'
    )
    
    # ຟີວເຕີ້ອື່ນໆ
    Ccy_cd = filters.CharFilter(field_name='Ccy_cd', lookup_expr='exact')
    Auth_Status = filters.CharFilter(field_name='Auth_Status', lookup_expr='exact')
    Reference_No = filters.CharFilter(field_name='Reference_No', lookup_expr='icontains')
    
    class Meta:
        model = DETB_JRNL_LOG_MASTER
        fields = ['fin_cycle', 'Ccy_cd', 'Auth_Status', 'Reference_No']