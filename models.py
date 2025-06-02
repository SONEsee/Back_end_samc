# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Districtinfo(models.Model):
    dis_sys_id = models.AutoField(db_column='Dis_sys_ID')  # Field name made lowercase.
    proid = models.CharField(db_column='ProID', max_length=10, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    disid = models.CharField(db_column='DisID', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    discode = models.CharField(db_column='DisCode', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    disnamee = models.CharField(db_column='DisNameE', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    disnamel = models.CharField(db_column='DisNameL', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    userid = models.IntegerField(db_column='UserID', blank=True, null=True)  # Field name made lowercase.
    dateinsert = models.DateTimeField(db_column='DateInsert', blank=True, null=True)  # Field name made lowercase.
    dateupdate = models.DateTimeField(db_column='DateUpdate', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'DistrictInfo'


class Provinceinfo(models.Model):
    pro_sys_id = models.AutoField(db_column='Pro_sys_id')  # Field name made lowercase.
    proid = models.CharField(db_column='ProID', max_length=10, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    procode = models.CharField(db_column='ProCode', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    pronamee = models.CharField(db_column='ProNameE', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    pronamel = models.CharField(db_column='ProNameL', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    dateinsert = models.DateTimeField(db_column='DateInsert', blank=True, null=True)  # Field name made lowercase.
    dateupdate = models.DateTimeField(db_column='DateUpdate', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'ProvinceInfo'


class SamcsysActbDairyLog(models.Model):
    ac_entry_sr_no = models.AutoField(primary_key=True)
    module = models.CharField(max_length=2, db_collation='SQL_Latin1_General_CP1_CI_AS')
    trn_ref_no = models.CharField(max_length=16, db_collation='SQL_Latin1_General_CP1_CI_AS')
    event_sr_no = models.IntegerField()
    event = models.CharField(max_length=4, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    ac_no = models.CharField(max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS')
    ac_ccy = models.CharField(max_length=3, db_collation='SQL_Latin1_General_CP1_CI_AS')
    drcr_ind = models.CharField(max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS')
    trn_code = models.CharField(max_length=3, db_collation='SQL_Latin1_General_CP1_CI_AS')
    fcy_amount = models.DecimalField(max_digits=22, decimal_places=3, blank=True, null=True)
    exch_rate = models.DecimalField(max_digits=24, decimal_places=1, blank=True, null=True)
    lcy_amount = models.DecimalField(max_digits=22, decimal_places=3, blank=True, null=True)
    external_ref_no = models.CharField(max_length=16, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    addl_text = models.CharField(max_length=255, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    trn_dt = models.DateField(blank=True, null=True)
    type = models.CharField(max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    category = models.CharField(max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    value_dt = models.DateField(blank=True, null=True)
    financial_cycle = models.CharField(max_length=9, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    period_code = models.CharField(max_length=3, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    user_id = models.CharField(max_length=12, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    maker_dt_stamp = models.DateTimeField(db_column='Maker_DT_Stamp', blank=True, null=True)  # Field name made lowercase.
    auth_id = models.CharField(max_length=12, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    checker_dt_stamp = models.DateTimeField(db_column='Checker_DT_Stamp', blank=True, null=True)  # Field name made lowercase.
    auth_status = models.CharField(db_column='Auth_Status', max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    product = models.CharField(max_length=4, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    entry_seq_no = models.IntegerField(blank=True, null=True)
    delete_stat = models.CharField(max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'SAMCSYS_actb_dairy_log'


class SamcsysActbDairyLogHistory(models.Model):
    ac_entry_sr_no = models.AutoField(primary_key=True)
    module = models.CharField(max_length=2, db_collation='SQL_Latin1_General_CP1_CI_AS')
    trn_ref_no = models.CharField(max_length=16, db_collation='SQL_Latin1_General_CP1_CI_AS')
    event_sr_no = models.IntegerField()
    event = models.CharField(max_length=4, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    ac_no = models.CharField(max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS')
    ac_ccy = models.CharField(max_length=3, db_collation='SQL_Latin1_General_CP1_CI_AS')
    drcr_ind = models.CharField(max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS')
    trn_code = models.CharField(max_length=3, db_collation='SQL_Latin1_General_CP1_CI_AS')
    fcy_amount = models.DecimalField(max_digits=22, decimal_places=3, blank=True, null=True)
    exch_rate = models.DecimalField(max_digits=24, decimal_places=1, blank=True, null=True)
    lcy_amount = models.DecimalField(max_digits=22, decimal_places=3, blank=True, null=True)
    external_ref_no = models.CharField(max_length=16, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    addl_text = models.CharField(max_length=255, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    trn_dt = models.DateField(blank=True, null=True)
    type = models.CharField(max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    category = models.CharField(max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    value_dt = models.DateField(blank=True, null=True)
    financial_cycle = models.CharField(max_length=9, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    period_code = models.CharField(max_length=3, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    user_id = models.CharField(max_length=12, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    maker_dt_stamp = models.DateTimeField(db_column='Maker_DT_Stamp', blank=True, null=True)  # Field name made lowercase.
    auth_id = models.CharField(max_length=12, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    checker_dt_stamp = models.DateTimeField(db_column='Checker_DT_Stamp', blank=True, null=True)  # Field name made lowercase.
    auth_status = models.CharField(db_column='Auth_Status', max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    product = models.CharField(max_length=4, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    entry_seq_no = models.IntegerField(blank=True, null=True)
    delete_stat = models.CharField(max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'SAMCSYS_actb_dairy_log_history'


class SamcsysBalancesheetAcc(models.Model):
    no = models.AutoField(primary_key=True)
    report_number = models.CharField(max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    description = models.CharField(max_length=2500, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    formula = models.TextField(db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    pvalue = models.TextField(db_column='Pvalue', db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    mvalue = models.TextField(db_column='Mvalue', db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'SAMCSYS_balancesheet_acc'


class SamcsysBalancesheetMfi(models.Model):
    no = models.AutoField(primary_key=True)
    report_number = models.CharField(max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    description = models.CharField(max_length=2500, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    formula = models.TextField(db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    pvalue = models.TextField(db_column='Pvalue', db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    mvalue = models.TextField(db_column='Mvalue', db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'SAMCSYS_balancesheet_mfi'


class SamcsysDetbJrnlLog(models.Model):
    reference_no = models.AutoField(db_column='Reference_No', primary_key=True)  # Field name made lowercase.
    ccy_cd = models.CharField(db_column='Ccy_cd', max_length=3, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    amount = models.DecimalField(db_column='Amount', max_digits=22, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    lcy_amount = models.DecimalField(db_column='Lcy_Amount', max_digits=22, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    dr_cr = models.CharField(db_column='Dr_cr', max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    account = models.CharField(db_column='Account', max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    txn_code = models.CharField(db_column='Txn_code', max_length=3, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    value_date = models.DateTimeField(db_column='Value_date', blank=True, null=True)  # Field name made lowercase.
    exch_rate = models.DecimalField(db_column='Exch_rate', max_digits=24, decimal_places=12, blank=True, null=True)  # Field name made lowercase.
    fin_cycle = models.CharField(max_length=9, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    period_code = models.CharField(db_column='Period_code', max_length=3, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    addl_text = models.CharField(db_column='Addl_text', max_length=255, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    maker_dt_stamp = models.DateTimeField(db_column='Maker_DT_Stamp', blank=True, null=True)  # Field name made lowercase.
    checker_dt_stamp = models.DateTimeField(db_column='Checker_DT_Stamp', blank=True, null=True)  # Field name made lowercase.
    auth_status = models.CharField(db_column='Auth_Status', max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    checker_id = models.ForeignKey('SamcsysMttbUsers', models.DO_NOTHING, db_column='Checker_Id_id', blank=True, null=True)  # Field name made lowercase.
    maker_id = models.ForeignKey('SamcsysMttbUsers', models.DO_NOTHING, db_column='Maker_Id_id', related_name='samcsysdetbjrnllog_maker_id_set', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'SAMCSYS_detb_jrnl_log'


class SamcsysDetbJrnlLogHist(models.Model):
    reference_no = models.AutoField(db_column='Reference_No', primary_key=True)  # Field name made lowercase.
    ccy_cd = models.CharField(db_column='Ccy_cd', max_length=3, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    amount = models.DecimalField(db_column='Amount', max_digits=22, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    lcy_amount = models.DecimalField(db_column='Lcy_Amount', max_digits=22, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    dr_cr = models.CharField(db_column='Dr_cr', max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    account = models.CharField(db_column='Account', max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    txn_code = models.CharField(db_column='Txn_code', max_length=3, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    value_date = models.DateTimeField(db_column='Value_date', blank=True, null=True)  # Field name made lowercase.
    exch_rate = models.DecimalField(db_column='Exch_rate', max_digits=24, decimal_places=12, blank=True, null=True)  # Field name made lowercase.
    fin_cycle = models.CharField(max_length=9, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    period_code = models.CharField(db_column='Period_code', max_length=3, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    addl_text = models.CharField(db_column='Addl_text', max_length=255, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    maker_dt_stamp = models.DateTimeField(db_column='Maker_DT_Stamp', blank=True, null=True)  # Field name made lowercase.
    checker_dt_stamp = models.DateTimeField(db_column='Checker_DT_Stamp', blank=True, null=True)  # Field name made lowercase.
    auth_status = models.CharField(db_column='Auth_Status', max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    checker_id = models.ForeignKey('SamcsysMttbUsers', models.DO_NOTHING, db_column='Checker_Id_id', blank=True, null=True)  # Field name made lowercase.
    maker_id = models.ForeignKey('SamcsysMttbUsers', models.DO_NOTHING, db_column='Maker_Id_id', related_name='samcsysdetbjrnlloghist_maker_id_set', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'SAMCSYS_detb_jrnl_log_hist'


class SamcsysDistrictinfo(models.Model):
    dis_sys_id = models.AutoField(primary_key=True)
    dis_id = models.CharField(max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    dis_code = models.CharField(max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    dis_name_e = models.CharField(max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    dis_name_l = models.CharField(max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    user_id = models.IntegerField(blank=True, null=True)
    date_insert = models.DateTimeField(blank=True, null=True)
    date_update = models.DateTimeField(blank=True, null=True)
    pro_id = models.ForeignKey('SamcsysProvinceinfo', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'SAMCSYS_districtinfo'


class SamcsysDistrictinfoNew(models.Model):
    dis_id = models.CharField(primary_key=True, max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS')
    dis_code = models.CharField(max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    dis_name_e = models.CharField(max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    dis_name_l = models.CharField(max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    user_id = models.IntegerField(blank=True, null=True)
    date_insert = models.DateTimeField(blank=True, null=True)
    date_update = models.DateTimeField(blank=True, null=True)
    pro_id = models.ForeignKey('SamcsysProvinceinfoNew', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'SAMCSYS_districtinfo_new'


class SamcsysIncomestatementAcc(models.Model):
    no = models.AutoField(primary_key=True)
    report_number = models.CharField(max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    description = models.CharField(max_length=2500, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    formula = models.TextField(db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    pvalue = models.TextField(db_column='Pvalue', db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    mvalue = models.TextField(db_column='Mvalue', db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'SAMCSYS_incomestatement_acc'


class SamcsysIncomestatementMfi(models.Model):
    no = models.AutoField(primary_key=True)
    report_number = models.CharField(max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    description = models.CharField(max_length=2500, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    formula = models.TextField(db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    pvalue = models.TextField(db_column='Pvalue', db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    mvalue = models.TextField(db_column='Mvalue', db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'SAMCSYS_incomestatement_mfi'


class SamcsysMonthlyreport(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    gl_code = models.ForeignKey('SamcsysMttbGlmaster', models.DO_NOTHING, blank=True, null=True)
    desc = models.TextField(db_column='Desc', db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    ccy_code = models.ForeignKey('SamcsysMttbCcyDefn', models.DO_NOTHING, db_column='CCy_Code_id', blank=True, null=True)  # Field name made lowercase.
    fin_year = models.ForeignKey('SamcsysMttbFinCycle', models.DO_NOTHING, blank=True, null=True)
    period_code = models.ForeignKey('SamcsysMttbPerCode', models.DO_NOTHING, blank=True, null=True)
    category = models.CharField(max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    op_dr = models.DecimalField(db_column='OP_DR', max_digits=25, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    op_cr = models.DecimalField(db_column='OP_CR', max_digits=25, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    mo_dr = models.DecimalField(db_column='Mo_DR', max_digits=25, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    mo_cr = models.DecimalField(db_column='Mo_CR', max_digits=25, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    cl_dr = models.DecimalField(db_column='Cl_DR', max_digits=25, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    cl_cr = models.DecimalField(db_column='Cl_CR', max_digits=25, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    op_dr_lcy = models.DecimalField(db_column='OP_DR_lcy', max_digits=25, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    op_cr_lcy = models.DecimalField(db_column='OP_CR_lcy', max_digits=25, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    mo_dr_lcy = models.DecimalField(db_column='Mo_DR_lcy', max_digits=25, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    mo_cr_lcy = models.DecimalField(db_column='Mo_CR_lcy', max_digits=25, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    cl_dr_lcy = models.DecimalField(db_column='Cl_DR_lcy', max_digits=25, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    cl_cr_lcy = models.DecimalField(db_column='Cl_CR_lcy', max_digits=25, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    insertdate = models.DateTimeField(db_column='InsertDate', blank=True, null=True)  # Field name made lowercase.
    updatedate = models.DateTimeField(db_column='UpdateDate', blank=True, null=True)  # Field name made lowercase.
    userid = models.IntegerField(db_column='UserID', blank=True, null=True)  # Field name made lowercase.
    msegment = models.CharField(db_column='MSegment', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'SAMCSYS_monthlyreport'


class SamcsysMttbCcyDefn(models.Model):
    ccy_code = models.CharField(primary_key=True, max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS')
    ccy_name_la = models.CharField(db_column='Ccy_Name_la', max_length=250, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    ccy_name_en = models.CharField(db_column='Ccy_Name_en', max_length=250, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    country = models.CharField(db_column='Country', max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    ccy_decimals = models.DecimalField(db_column='Ccy_Decimals', max_digits=12, decimal_places=2)  # Field name made lowercase.
    alt_ccy_code = models.CharField(db_column='ALT_Ccy_Code', max_length=2, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    record_status = models.CharField(db_column='Record_Status', max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    maker_dt_stamp = models.DateTimeField(db_column='Maker_DT_Stamp', blank=True, null=True)  # Field name made lowercase.
    checker_dt_stamp = models.DateTimeField(db_column='Checker_DT_Stamp', blank=True, null=True)  # Field name made lowercase.
    auth_status = models.CharField(db_column='Auth_Status', max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    once_auth = models.CharField(db_column='Once_Auth', max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    checker_id = models.ForeignKey('SamcsysMttbUsers', models.DO_NOTHING, db_column='Checker_Id_id', blank=True, null=True)  # Field name made lowercase.
    maker_id = models.ForeignKey('SamcsysMttbUsers', models.DO_NOTHING, db_column='Maker_Id_id', related_name='samcsysmttbccydefn_maker_id_set', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'SAMCSYS_mttb_ccy_defn'


class SamcsysMttbDataEntry(models.Model):
    data_entry_id = models.CharField(primary_key=True, max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS')
    jrn_rekey_required = models.CharField(db_column='JRN_REKEY_REQUIRED', max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    jrn_rekey_value_date = models.CharField(db_column='JRN_REKEY_VALUE_DATE', max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    jrn_rekey_amount = models.CharField(db_column='JRN_REKEY_AMOUNT', max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    jrn_rekey_txn_code = models.CharField(db_column='JRN_REKEY_TXN_CODE', max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    back_value = models.IntegerField(db_column='BACK_VALUE')  # Field name made lowercase.
    mod_no = models.IntegerField(db_column='MOD_NO')  # Field name made lowercase.
    record_status = models.CharField(db_column='Record_Status', max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    maker_dt_stamp = models.DateTimeField(db_column='Maker_DT_Stamp', blank=True, null=True)  # Field name made lowercase.
    checker_dt_stamp = models.DateTimeField(db_column='Checker_DT_Stamp', blank=True, null=True)  # Field name made lowercase.
    auth_status = models.CharField(db_column='Auth_Status', max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    once_auth = models.CharField(db_column='Once_Auth', max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    checker_id = models.ForeignKey('SamcsysMttbUsers', models.DO_NOTHING, db_column='Checker_Id_id', blank=True, null=True)  # Field name made lowercase.
    maker_id = models.ForeignKey('SamcsysMttbUsers', models.DO_NOTHING, db_column='Maker_Id_id', related_name='samcsysmttbdataentry_maker_id_set', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'SAMCSYS_mttb_data_entry'


class SamcsysMttbDivisions(models.Model):
    div_id = models.CharField(primary_key=True, max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS')
    division_name_la = models.CharField(max_length=250, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    division_name_en = models.CharField(max_length=250, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    record_status = models.CharField(db_column='record_Status', max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    maker_dt_stamp = models.DateTimeField(db_column='Maker_DT_Stamp', blank=True, null=True)  # Field name made lowercase.
    checker_dt_stamp = models.DateTimeField(db_column='Checker_DT_Stamp', blank=True, null=True)  # Field name made lowercase.
    auth_status = models.CharField(db_column='Auth_Status', max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    once_auth = models.CharField(db_column='Once_Auth', max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    checker_id = models.ForeignKey('SamcsysMttbUsers', models.DO_NOTHING, db_column='Checker_Id_id', blank=True, null=True)  # Field name made lowercase.
    maker_id = models.ForeignKey('SamcsysMttbUsers', models.DO_NOTHING, db_column='Maker_Id_id', related_name='samcsysmttbdivisions_maker_id_set', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'SAMCSYS_mttb_divisions'


class SamcsysMttbEmployee(models.Model):
    employee_id = models.CharField(primary_key=True, max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS')
    employee_name_la = models.CharField(max_length=250, db_collation='SQL_Latin1_General_CP1_CI_AS')
    employee_name_en = models.CharField(max_length=250, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    gender = models.CharField(max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    national_id = models.CharField(max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    address_la = models.CharField(max_length=255, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    address_en = models.CharField(max_length=255, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    phone_number = models.CharField(max_length=15, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    email = models.CharField(max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    position_code = models.CharField(max_length=10, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    div_id = models.ForeignKey(SamcsysMttbDivisions, models.DO_NOTHING, blank=True, null=True)
    employee_photo = models.CharField(max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    employee_signature = models.CharField(max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    hire_date = models.DateField(blank=True, null=True)
    employment_status = models.CharField(max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS')
    record_stat = models.CharField(max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    maker_dt_stamp = models.DateTimeField(db_column='Maker_DT_Stamp', blank=True, null=True)  # Field name made lowercase.
    checker_dt_stamp = models.DateTimeField(db_column='Checker_DT_Stamp', blank=True, null=True)  # Field name made lowercase.
    auth_status = models.CharField(db_column='Auth_Status', max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    once_auth = models.CharField(db_column='Once_Auth', max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    checker_id = models.ForeignKey('SamcsysMttbUsers', models.DO_NOTHING, db_column='Checker_Id_id', blank=True, null=True)  # Field name made lowercase.
    maker_id = models.ForeignKey('SamcsysMttbUsers', models.DO_NOTHING, db_column='Maker_Id_id', related_name='samcsysmttbemployee_maker_id_set', blank=True, null=True)  # Field name made lowercase.
    user_id = models.ForeignKey('SamcsysMttbUsers', models.DO_NOTHING, related_name='samcsysmttbemployee_user_id_set', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'SAMCSYS_mttb_employee'


class SamcsysMttbEocMaintain(models.Model):
    eoc_id = models.AutoField(primary_key=True)
    module_id = models.CharField(max_length=2, db_collation='SQL_Latin1_General_CP1_CI_AS')
    function_id = models.CharField(max_length=8, db_collation='SQL_Latin1_General_CP1_CI_AS')
    eoc_seq_no = models.IntegerField()
    eoc_type = models.CharField(max_length=3, db_collation='SQL_Latin1_General_CP1_CI_AS')
    record_stat = models.CharField(max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS')
    mod_no = models.IntegerField(blank=True, null=True)
    maker_dt_stamp = models.DateTimeField(db_column='Maker_DT_Stamp', blank=True, null=True)  # Field name made lowercase.
    checker_dt_stamp = models.DateTimeField(db_column='Checker_DT_Stamp', blank=True, null=True)  # Field name made lowercase.
    auth_status = models.CharField(db_column='Auth_Status', max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    once_auth = models.CharField(db_column='Once_Auth', max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    checker_id = models.ForeignKey('SamcsysMttbUsers', models.DO_NOTHING, db_column='Checker_Id_id', blank=True, null=True)  # Field name made lowercase.
    maker_id = models.ForeignKey('SamcsysMttbUsers', models.DO_NOTHING, db_column='Maker_Id_id', related_name='samcsysmttbeocmaintain_maker_id_set', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'SAMCSYS_mttb_eoc_maintain'


class SamcsysMttbExcRate(models.Model):
    id = models.BigAutoField(primary_key=True)
    buy_rate = models.DecimalField(db_column='Buy_Rate', max_digits=12, decimal_places=2)  # Field name made lowercase.
    sale_rate = models.DecimalField(db_column='Sale_Rate', max_digits=12, decimal_places=2)  # Field name made lowercase.
    int_auth_status = models.CharField(db_column='INT_Auth_Status', max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    maker_dt_stamp = models.DateTimeField(db_column='Maker_DT_Stamp', blank=True, null=True)  # Field name made lowercase.
    checker_dt_stamp = models.DateTimeField(db_column='Checker_DT_Stamp', blank=True, null=True)  # Field name made lowercase.
    auth_status = models.CharField(db_column='Auth_Status', max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    ccy_code = models.ForeignKey(SamcsysMttbCcyDefn, models.DO_NOTHING, blank=True, null=True)
    checker_id = models.ForeignKey('SamcsysMttbUsers', models.DO_NOTHING, db_column='Checker_Id_id', blank=True, null=True)  # Field name made lowercase.
    maker_id = models.ForeignKey('SamcsysMttbUsers', models.DO_NOTHING, db_column='Maker_Id_id', related_name='samcsysmttbexcrate_maker_id_set', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'SAMCSYS_mttb_exc_rate'


class SamcsysMttbExcRateHistory(models.Model):
    id = models.BigAutoField(primary_key=True)
    buy_rate = models.DecimalField(db_column='Buy_Rate', max_digits=12, decimal_places=2)  # Field name made lowercase.
    sale_rate = models.DecimalField(db_column='Sale_Rate', max_digits=12, decimal_places=2)  # Field name made lowercase.
    int_auth_status = models.CharField(db_column='INT_Auth_Status', max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    maker_dt_stamp = models.DateTimeField(db_column='Maker_DT_Stamp', blank=True, null=True)  # Field name made lowercase.
    checker_dt_stamp = models.DateTimeField(db_column='Checker_DT_Stamp', blank=True, null=True)  # Field name made lowercase.
    auth_status = models.CharField(db_column='Auth_Status', max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    ccy_code = models.ForeignKey(SamcsysMttbCcyDefn, models.DO_NOTHING, blank=True, null=True)
    checker_id = models.ForeignKey('SamcsysMttbUsers', models.DO_NOTHING, db_column='Checker_Id_id', blank=True, null=True)  # Field name made lowercase.
    maker_id = models.ForeignKey('SamcsysMttbUsers', models.DO_NOTHING, db_column='Maker_Id_id', related_name='samcsysmttbexcratehistory_maker_id_set', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'SAMCSYS_mttb_exc_rate_history'


class SamcsysMttbFinCycle(models.Model):
    fin_cycle = models.CharField(primary_key=True, max_length=10, db_collation='SQL_Latin1_General_CP1_CI_AS')
    cycle_desc = models.CharField(db_column='cycle_Desc', max_length=250, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    startdate = models.DateTimeField(db_column='StartDate', blank=True, null=True)  # Field name made lowercase.
    enddate = models.DateTimeField(db_column='EndDate', blank=True, null=True)  # Field name made lowercase.
    record_status = models.CharField(db_column='Record_Status', max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    maker_dt_stamp = models.DateTimeField(db_column='Maker_DT_Stamp', blank=True, null=True)  # Field name made lowercase.
    checker_dt_stamp = models.DateTimeField(db_column='Checker_DT_Stamp', blank=True, null=True)  # Field name made lowercase.
    auth_status = models.CharField(db_column='Auth_Status', max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    once_auth = models.CharField(db_column='Once_Auth', max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    checker_id = models.ForeignKey('SamcsysMttbUsers', models.DO_NOTHING, db_column='Checker_Id_id', blank=True, null=True)  # Field name made lowercase.
    maker_id = models.ForeignKey('SamcsysMttbUsers', models.DO_NOTHING, db_column='Maker_Id_id', related_name='samcsysmttbfincycle_maker_id_set', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'SAMCSYS_mttb_fin_cycle'


class SamcsysMttbFunctionDesc(models.Model):
    function_id = models.CharField(primary_key=True, max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS')
    description_la = models.CharField(max_length=200, db_collation='SQL_Latin1_General_CP1_CI_AS')
    description_en = models.CharField(max_length=200, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    eod_function = models.CharField(max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    function_order = models.IntegerField(blank=True, null=True)
    is_active = models.CharField(max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    created_by = models.CharField(max_length=30, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    created_date = models.DateTimeField(blank=True, null=True)
    modified_by = models.CharField(max_length=30, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    modified_date = models.DateTimeField(blank=True, null=True)
    sub_menu_id = models.ForeignKey('SamcsysMttbSubMenu', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'SAMCSYS_mttb_function_desc'


class SamcsysMttbGlmaster(models.Model):
    glid = models.AutoField(primary_key=True)
    gl_code = models.CharField(unique=True, max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    gl_desc_la = models.CharField(db_column='gl_Desc_la', max_length=250, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    gl_desc_en = models.CharField(db_column='gl_Desc_en', max_length=250, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    gltype = models.CharField(db_column='glType', max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    category = models.CharField(max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    retal = models.CharField(max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    ccy_res = models.CharField(db_column='ccy_Res', max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    res_ccy = models.CharField(db_column='Res_ccy', max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    allow_backperiodentry = models.CharField(db_column='Allow_BackPeriodEntry', max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    pl_split_reqd = models.CharField(db_column='pl_Split_ReqD', max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    record_status = models.CharField(db_column='Record_Status', max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    maker_dt_stamp = models.DateTimeField(db_column='Maker_DT_Stamp', blank=True, null=True)  # Field name made lowercase.
    checker_dt_stamp = models.DateTimeField(db_column='Checker_DT_Stamp', blank=True, null=True)  # Field name made lowercase.
    auth_status = models.CharField(db_column='Auth_Status', max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    once_auth = models.CharField(db_column='Once_Auth', max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    checker_id = models.ForeignKey('SamcsysMttbUsers', models.DO_NOTHING, db_column='Checker_Id_id', blank=True, null=True)  # Field name made lowercase.
    maker_id = models.ForeignKey('SamcsysMttbUsers', models.DO_NOTHING, db_column='Maker_Id_id', related_name='samcsysmttbglmaster_maker_id_set', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'SAMCSYS_mttb_glmaster'


class SamcsysMttbGlsub(models.Model):
    glsub_id = models.AutoField(primary_key=True)
    glsub_code = models.CharField(max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    glsub_desc_la = models.CharField(db_column='glsub_Desc_la', max_length=250, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    glsub_desc_en = models.CharField(db_column='glsub_Desc_en', max_length=250, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    record_status = models.CharField(db_column='Record_Status', max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    maker_dt_stamp = models.DateTimeField(db_column='Maker_DT_Stamp', blank=True, null=True)  # Field name made lowercase.
    checker_dt_stamp = models.DateTimeField(db_column='Checker_DT_Stamp', blank=True, null=True)  # Field name made lowercase.
    auth_status = models.CharField(db_column='Auth_Status', max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    once_auth = models.CharField(db_column='Once_Auth', max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    gl_code = models.ForeignKey(SamcsysMttbGlmaster, models.DO_NOTHING, blank=True, null=True)
    checker_id = models.ForeignKey('SamcsysMttbUsers', models.DO_NOTHING, db_column='Checker_Id_id', blank=True, null=True)  # Field name made lowercase.
    maker_id = models.ForeignKey('SamcsysMttbUsers', models.DO_NOTHING, db_column='Maker_Id_id', related_name='samcsysmttbglsub_maker_id_set', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'SAMCSYS_mttb_glsub'


class SamcsysMttbLclHoliday(models.Model):
    lcl_holiday_id = models.CharField(primary_key=True, max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS')
    hyear = models.CharField(db_column='HYear', max_length=4, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    hmonth = models.CharField(db_column='HMonth', max_length=10, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    hdate = models.DateTimeField(db_column='HDate', blank=True, null=True)  # Field name made lowercase.
    holiday_list = models.CharField(db_column='Holiday_List', max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    record_status = models.CharField(db_column='Record_Status', max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    maker_dt_stamp = models.DateTimeField(db_column='Maker_DT_Stamp', blank=True, null=True)  # Field name made lowercase.
    checker_dt_stamp = models.DateTimeField(db_column='Checker_DT_Stamp', blank=True, null=True)  # Field name made lowercase.
    auth_status = models.CharField(db_column='Auth_Status', max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    once_auth = models.CharField(db_column='Once_Auth', max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    checker_id = models.ForeignKey('SamcsysMttbUsers', models.DO_NOTHING, db_column='Checker_Id_id', blank=True, null=True)  # Field name made lowercase.
    maker_id = models.ForeignKey('SamcsysMttbUsers', models.DO_NOTHING, db_column='Maker_Id_id', related_name='samcsysmttblclholiday_maker_id_set', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'SAMCSYS_mttb_lcl_holiday'


class SamcsysMttbMainMenu(models.Model):
    menu_id = models.CharField(primary_key=True, max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS')
    menu_name_la = models.CharField(max_length=250, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    menu_name_en = models.CharField(max_length=250, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    menu_icon = models.CharField(max_length=250, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    menu_order = models.CharField(max_length=3, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    is_active = models.CharField(max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS')
    created_by = models.CharField(max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    created_date = models.DateTimeField()
    modified_by = models.CharField(max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    modified_date = models.DateTimeField(blank=True, null=True)
    module_id = models.ForeignKey('SamcsysSttbModulesinfo', models.DO_NOTHING, db_column='module_Id_id', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'SAMCSYS_mttb_main_menu'


class SamcsysMttbPerCode(models.Model):
    period_code = models.CharField(primary_key=True, max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS')
    pc_startdate = models.DateTimeField(db_column='PC_StartDate', blank=True, null=True)  # Field name made lowercase.
    pc_enddate = models.DateTimeField(db_column='PC_EndDate', blank=True, null=True)  # Field name made lowercase.
    fin_cycle = models.ForeignKey(SamcsysMttbFinCycle, models.DO_NOTHING, db_column='Fin_cycle_id', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'SAMCSYS_mttb_per_code'


class SamcsysMttbRoleDetail(models.Model):
    id = models.BigAutoField(primary_key=True)
    new_detail = models.IntegerField(db_column='New_Detail')  # Field name made lowercase.
    del_detail = models.IntegerField(db_column='Del_Detail')  # Field name made lowercase.
    edit_detail = models.IntegerField(db_column='Edit_Detail')  # Field name made lowercase.
    auth_detail = models.IntegerField(db_column='Auth_Detail')  # Field name made lowercase.
    role_id = models.ForeignKey('SamcsysMttbRoleMaster', models.DO_NOTHING, blank=True, null=True)
    sub_menu_id = models.ForeignKey('SamcsysMttbSubMenu', models.DO_NOTHING, blank=True, null=True)
    view_detail = models.IntegerField(db_column='View_Detail')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'SAMCSYS_mttb_role_detail'


class SamcsysMttbRoleMaster(models.Model):
    role_id = models.CharField(primary_key=True, max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS')
    role_name_la = models.CharField(max_length=250, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    role_name_en = models.CharField(max_length=250, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    record_status = models.CharField(db_column='record_Status', max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    maker_dt_stamp = models.DateTimeField(db_column='Maker_DT_Stamp', blank=True, null=True)  # Field name made lowercase.
    checker_dt_stamp = models.DateTimeField(db_column='Checker_DT_Stamp', blank=True, null=True)  # Field name made lowercase.
    auth_status = models.CharField(db_column='Auth_Status', max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    once_auth = models.CharField(db_column='Once_Auth', max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    checker_id = models.ForeignKey('SamcsysMttbUsers', models.DO_NOTHING, db_column='Checker_Id_id', blank=True, null=True)  # Field name made lowercase.
    maker_id = models.ForeignKey('SamcsysMttbUsers', models.DO_NOTHING, db_column='Maker_Id_id', related_name='samcsysmttbrolemaster_maker_id_set', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'SAMCSYS_mttb_role_master'


class SamcsysMttbSubMenu(models.Model):
    sub_menu_id = models.CharField(primary_key=True, max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS')
    sub_menu_name_la = models.CharField(max_length=250, db_collation='SQL_Latin1_General_CP1_CI_AS')
    sub_menu_name_en = models.CharField(max_length=250, db_collation='SQL_Latin1_General_CP1_CI_AS')
    sub_menu_icon = models.CharField(max_length=250, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    sub_menu_order = models.CharField(max_length=3, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    is_active = models.CharField(max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS')
    created_by = models.CharField(max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    created_date = models.DateTimeField()
    modified_by = models.CharField(max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    modified_date = models.DateTimeField(blank=True, null=True)
    menu_id = models.ForeignKey(SamcsysMttbMainMenu, models.DO_NOTHING, blank=True, null=True)
    sub_menu_urls = models.CharField(max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'SAMCSYS_mttb_sub_menu'


class SamcsysMttbTrnCode(models.Model):
    trn_code = models.CharField(primary_key=True, max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS')
    trn_desc_la = models.CharField(db_column='trn_Desc_la', max_length=250, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    trn_desc_en = models.CharField(db_column='trn_Desc_en', max_length=250, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    record_status = models.CharField(db_column='Record_Status', max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    maker_dt_stamp = models.DateTimeField(db_column='Maker_DT_Stamp', blank=True, null=True)  # Field name made lowercase.
    checker_dt_stamp = models.DateTimeField(db_column='Checker_DT_Stamp', blank=True, null=True)  # Field name made lowercase.
    auth_status = models.CharField(db_column='Auth_Status', max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    once_auth = models.CharField(db_column='Once_Auth', max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    checker_id = models.ForeignKey('SamcsysMttbUsers', models.DO_NOTHING, db_column='Checker_Id_id', blank=True, null=True)  # Field name made lowercase.
    maker_id = models.ForeignKey('SamcsysMttbUsers', models.DO_NOTHING, db_column='Maker_Id_id', related_name='samcsysmttbtrncode_maker_id_set', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'SAMCSYS_mttb_trn_code'


class SamcsysMttbUserAccessLog(models.Model):
    log_id = models.AutoField(primary_key=True)
    login_datetime = models.DateTimeField(blank=True, null=True)
    logout_datetime = models.DateTimeField(blank=True, null=True)
    session_id = models.CharField(max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    ip_address = models.CharField(max_length=45, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    user_agent = models.CharField(max_length=255, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    login_status = models.CharField(max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS')
    logout_type = models.CharField(max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    remarks = models.CharField(max_length=255, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    user_id = models.ForeignKey('SamcsysMttbUsers', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'SAMCSYS_mttb_user_access_log'


class SamcsysMttbUserActivityLog(models.Model):
    activity_id = models.AutoField(primary_key=True)
    session_id = models.CharField(max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS')
    activity_datetime = models.DateTimeField(blank=True, null=True)
    module_id = models.CharField(max_length=10, db_collation='SQL_Latin1_General_CP1_CI_AS')
    function_id = models.CharField(max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS')
    action_type = models.CharField(max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS')
    record_id = models.CharField(max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    old_values = models.TextField(db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    new_values = models.TextField(db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    ip_address = models.CharField(max_length=39, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    user_id = models.ForeignKey('SamcsysMttbUsers', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'SAMCSYS_mttb_user_activity_log'


class SamcsysMttbUsers(models.Model):
    user_id = models.CharField(primary_key=True, max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS')
    user_name = models.CharField(unique=True, max_length=250, db_collation='SQL_Latin1_General_CP1_CI_AS')
    user_password = models.CharField(max_length=250, db_collation='SQL_Latin1_General_CP1_CI_AS')
    user_email = models.CharField(max_length=250, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    user_mobile = models.CharField(max_length=15, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    user_status = models.CharField(db_column='User_Status', max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    pwd_changed_on = models.DateField(blank=True, null=True)
    insertdate = models.DateTimeField(db_column='InsertDate')  # Field name made lowercase.
    updatedate = models.DateTimeField(db_column='UpdateDate')  # Field name made lowercase.
    maker_dt_stamp = models.DateTimeField(db_column='Maker_DT_Stamp', blank=True, null=True)  # Field name made lowercase.
    checker_dt_stamp = models.DateTimeField(db_column='Checker_DT_Stamp', blank=True, null=True)  # Field name made lowercase.
    auth_status = models.CharField(db_column='Auth_Status', max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    once_auth = models.CharField(db_column='Once_Auth', max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    checker_id = models.ForeignKey('self', models.DO_NOTHING, db_column='Checker_Id_id', blank=True, null=True)  # Field name made lowercase.
    maker_id = models.ForeignKey('self', models.DO_NOTHING, db_column='Maker_Id_id', related_name='samcsysmttbusers_maker_id_set', blank=True, null=True)  # Field name made lowercase.
    role_id = models.ForeignKey(SamcsysMttbRoleMaster, models.DO_NOTHING, db_column='Role_ID_id', blank=True, null=True)  # Field name made lowercase.
    div_id = models.ForeignKey(SamcsysMttbDivisions, models.DO_NOTHING, blank=True, null=True)
    profile_picture = models.CharField(max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'SAMCSYS_mttb_users'


class SamcsysProvinceinfo(models.Model):
    pro_sys_id = models.AutoField(primary_key=True)
    pro_id = models.CharField(max_length=10, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    pro_code = models.CharField(max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    pro_name_e = models.CharField(max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    pro_name_l = models.CharField(max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    date_insert = models.DateTimeField(blank=True, null=True)
    date_update = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'SAMCSYS_provinceinfo'


class SamcsysProvinceinfoNew(models.Model):
    pro_id = models.CharField(primary_key=True, max_length=10, db_collation='SQL_Latin1_General_CP1_CI_AS')
    pro_code = models.CharField(max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    pro_name_e = models.CharField(max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    pro_name_l = models.CharField(max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    date_insert = models.DateTimeField(blank=True, null=True)
    date_update = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'SAMCSYS_provinceinfo_new'


class SamcsysSttbCurrentUsers(models.Model):
    id = models.BigAutoField(primary_key=True)
    host_userlogin = models.CharField(db_column='Host_UserLogin', max_length=255, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    start_time = models.DateTimeField(db_column='Start_time', blank=True, null=True)  # Field name made lowercase.
    user_id = models.ForeignKey(SamcsysMttbUsers, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'SAMCSYS_sttb_current_users'


class SamcsysSttbDates(models.Model):
    date_id = models.AutoField(primary_key=True)
    inserttoday = models.DateTimeField(db_column='insertToday', blank=True, null=True)  # Field name made lowercase.
    prev_wroking_day = models.DateTimeField(db_column='prev_Wroking_Day', blank=True, null=True)  # Field name made lowercase.
    next_working_day = models.DateTimeField(db_column='next_working_Day', blank=True, null=True)  # Field name made lowercase.
    eod_time = models.CharField(max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS')

    class Meta:
        managed = False
        db_table = 'SAMCSYS_sttb_dates'


class SamcsysSttbEocDailyLog(models.Model):
    ac_entry_sr_no = models.AutoField(primary_key=True)
    module = models.CharField(max_length=2, db_collation='SQL_Latin1_General_CP1_CI_AS')
    trn_ref_no = models.CharField(max_length=15, db_collation='SQL_Latin1_General_CP1_CI_AS')
    event_sr_no = models.IntegerField(blank=True, null=True)
    event = models.CharField(max_length=4, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    ac_no = models.CharField(max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS')
    ac_ccy = models.CharField(max_length=3, db_collation='SQL_Latin1_General_CP1_CI_AS')
    drcr_ind = models.CharField(max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS')
    trn_code = models.CharField(max_length=3, db_collation='SQL_Latin1_General_CP1_CI_AS')
    fcy_amount = models.DecimalField(max_digits=22, decimal_places=3, blank=True, null=True)
    exch_rate = models.DecimalField(max_digits=24, decimal_places=1, blank=True, null=True)
    lcy_amount = models.DecimalField(max_digits=22, decimal_places=3, blank=True, null=True)
    external_ref_no = models.CharField(max_length=16, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    addl_text = models.CharField(max_length=255, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    trn_dt = models.DateField(blank=True, null=True)
    type = models.CharField(max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    category = models.CharField(max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    value_dt = models.DateField(blank=True, null=True)
    financial_cycle = models.CharField(max_length=9, db_collation='SQL_Latin1_General_CP1_CI_AS')
    period_code = models.CharField(max_length=3, db_collation='SQL_Latin1_General_CP1_CI_AS')
    user_id = models.CharField(max_length=12, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    maker_dt_stamp = models.DateTimeField(db_column='Maker_DT_Stamp', blank=True, null=True)  # Field name made lowercase.
    auth_id = models.CharField(max_length=12, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    checker_dt_stamp = models.DateTimeField(db_column='Checker_DT_Stamp', blank=True, null=True)  # Field name made lowercase.
    auth_status = models.CharField(db_column='Auth_Status', max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    product = models.CharField(max_length=4, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    entry_seq_no = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'SAMCSYS_sttb_eoc_daily_log'


class SamcsysSttbEocStatus(models.Model):
    eoc_stt_id = models.AutoField(primary_key=True)
    eoc_seq_no = models.IntegerField(blank=True, null=True)
    module_id = models.CharField(max_length=2, db_collation='SQL_Latin1_General_CP1_CI_AS')
    function_id = models.CharField(max_length=8, db_collation='SQL_Latin1_General_CP1_CI_AS')
    eoc_type = models.CharField(max_length=3, db_collation='SQL_Latin1_General_CP1_CI_AS')
    eod_date = models.DateTimeField(blank=True, null=True)
    eoc_status = models.CharField(max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS')
    error = models.CharField(max_length=550, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'SAMCSYS_sttb_eoc_status'


class SamcsysSttbGlBal(models.Model):
    gl_bal_id = models.AutoField(primary_key=True)
    gl_code = models.ForeignKey(SamcsysMttbGlmaster, models.DO_NOTHING, blank=True, null=True)
    ccy_code = models.ForeignKey(SamcsysMttbCcyDefn, models.DO_NOTHING, db_column='CCy_Code_id', blank=True, null=True)  # Field name made lowercase.
    fin_year = models.ForeignKey(SamcsysMttbFinCycle, models.DO_NOTHING, blank=True, null=True)
    period_code = models.ForeignKey(SamcsysMttbPerCode, models.DO_NOTHING, blank=True, null=True)
    category = models.CharField(max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    dr_mov = models.DecimalField(max_digits=25, decimal_places=2, blank=True, null=True)
    cr_mov = models.DecimalField(max_digits=25, decimal_places=2, blank=True, null=True)
    dr_mov_lcy = models.DecimalField(max_digits=25, decimal_places=2, blank=True, null=True)
    cr_mov_lcy = models.DecimalField(max_digits=25, decimal_places=2, blank=True, null=True)
    dr_bal = models.DecimalField(max_digits=25, decimal_places=2, blank=True, null=True)
    cr_bal = models.DecimalField(max_digits=25, decimal_places=2, blank=True, null=True)
    dr_bal_lcy = models.DecimalField(max_digits=25, decimal_places=2, blank=True, null=True)
    cr_bal_lcy = models.DecimalField(max_digits=25, decimal_places=2, blank=True, null=True)
    open_dr_bal = models.DecimalField(max_digits=25, decimal_places=2, blank=True, null=True)
    open_cr_bal = models.DecimalField(max_digits=25, decimal_places=2, blank=True, null=True)
    open_dr_bal_lcy = models.DecimalField(max_digits=25, decimal_places=2, blank=True, null=True)
    open_cr_bal_lcy = models.DecimalField(max_digits=25, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'SAMCSYS_sttb_gl_bal'


class SamcsysSttbGlSubBal(models.Model):
    gl_sub_bal_id = models.AutoField(primary_key=True)
    ccy_code = models.ForeignKey(SamcsysMttbCcyDefn, models.DO_NOTHING, db_column='CCy_Code_id', blank=True, null=True)  # Field name made lowercase.
    fin_year = models.ForeignKey(SamcsysMttbFinCycle, models.DO_NOTHING, blank=True, null=True)
    period_code = models.ForeignKey(SamcsysMttbPerCode, models.DO_NOTHING, blank=True, null=True)
    dr_mov = models.DecimalField(max_digits=25, decimal_places=2, blank=True, null=True)
    cr_mov = models.DecimalField(max_digits=25, decimal_places=2, blank=True, null=True)
    dr_mov_lcy = models.DecimalField(max_digits=25, decimal_places=2, blank=True, null=True)
    cr_mov_lcy = models.DecimalField(max_digits=25, decimal_places=2, blank=True, null=True)
    dr_bal = models.DecimalField(max_digits=25, decimal_places=2, blank=True, null=True)
    cr_bal = models.DecimalField(max_digits=25, decimal_places=2, blank=True, null=True)
    dr_bal_lcy = models.DecimalField(max_digits=25, decimal_places=2, blank=True, null=True)
    cr_bal_lcy = models.DecimalField(max_digits=25, decimal_places=2, blank=True, null=True)
    open_dr_bal = models.DecimalField(max_digits=25, decimal_places=2, blank=True, null=True)
    open_cr_bal = models.DecimalField(max_digits=25, decimal_places=2, blank=True, null=True)
    open_dr_bal_lcy = models.DecimalField(max_digits=25, decimal_places=2, blank=True, null=True)
    open_cr_bal_lcy = models.DecimalField(max_digits=25, decimal_places=2, blank=True, null=True)
    gl_sub = models.ForeignKey(SamcsysMttbGlsub, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'SAMCSYS_sttb_gl_sub_bal'


class SamcsysSttbModulesinfo(models.Model):
    module_id = models.CharField(db_column='module_Id', primary_key=True, max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    module_name_la = models.CharField(max_length=250, db_collation='SQL_Latin1_General_CP1_CI_AS')
    module_name_en = models.CharField(max_length=250, db_collation='SQL_Latin1_General_CP1_CI_AS')
    module_icon = models.CharField(max_length=255, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    module_order = models.CharField(max_length=3, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    is_active = models.CharField(max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS')
    created_by = models.CharField(max_length=30, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    created_date = models.DateTimeField()
    modified_by = models.CharField(max_length=30, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    modified_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'SAMCSYS_sttb_modulesinfo'


class SamcsysVillageinfoNew(models.Model):
    vil_id = models.CharField(primary_key=True, max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS')
    vil_code = models.CharField(max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    vil_name_e = models.CharField(max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    vil_name_l = models.CharField(max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    user_id = models.IntegerField(blank=True, null=True)
    date_insert = models.DateTimeField(blank=True, null=True)
    date_update = models.DateTimeField(blank=True, null=True)
    vbol_code = models.CharField(max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    vbol_name = models.TextField(db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    dis_id = models.ForeignKey(SamcsysDistrictinfoNew, models.DO_NOTHING, blank=True, null=True)
    pro_id = models.ForeignKey(SamcsysProvinceinfoNew, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'SAMCSYS_villageinfo_new'


class Villageinfo(models.Model):
    proid = models.IntegerField(db_column='ProID', blank=True, null=True)  # Field name made lowercase.
    disid = models.CharField(db_column='DisID', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    vilid = models.AutoField(db_column='VilID')  # Field name made lowercase.
    vilcode = models.CharField(db_column='VilCode', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    vilnamee = models.CharField(db_column='VilNameE', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    vilnamel = models.CharField(db_column='VilNameL', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    userid = models.IntegerField(db_column='UserID', blank=True, null=True)  # Field name made lowercase.
    dateinsert = models.DateTimeField(db_column='DateInsert', blank=True, null=True)  # Field name made lowercase.
    dateupdate = models.DateTimeField(db_column='DAteUpdate', blank=True, null=True)  # Field name made lowercase.
    vbolcode = models.CharField(db_column='VBOLCode', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    vbolname = models.TextField(db_column='VBOLName', db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'VillageInfo'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150, db_collation='SQL_Latin1_General_CP1_CI_AS')

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255, db_collation='SQL_Latin1_General_CP1_CI_AS')
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS')

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128, db_collation='SQL_Latin1_General_CP1_CI_AS')
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150, db_collation='SQL_Latin1_General_CP1_CI_AS')
    first_name = models.CharField(max_length=150, db_collation='SQL_Latin1_General_CP1_CI_AS')
    last_name = models.CharField(max_length=150, db_collation='SQL_Latin1_General_CP1_CI_AS')
    email = models.CharField(max_length=254, db_collation='SQL_Latin1_General_CP1_CI_AS')
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    object_repr = models.CharField(max_length=200, db_collation='SQL_Latin1_General_CP1_CI_AS')
    action_flag = models.SmallIntegerField()
    change_message = models.TextField(db_collation='SQL_Latin1_General_CP1_CI_AS')
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS')
    model = models.CharField(max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS')

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255, db_collation='SQL_Latin1_General_CP1_CI_AS')
    name = models.CharField(max_length=255, db_collation='SQL_Latin1_General_CP1_CI_AS')
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40, db_collation='SQL_Latin1_General_CP1_CI_AS')
    session_data = models.TextField(db_collation='SQL_Latin1_General_CP1_CI_AS')
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'
