from django.db import models

# Create your models here.    
class STTB_ModulesInfo(models.Model):
    module_Id = models.CharField(primary_key=True,max_length=20)
    module_name_la = models.CharField(max_length=250)
    module_name_en = models.CharField(max_length=250)
    module_icon = models.CharField(max_length=255, null=True, blank=True)  
    module_order = models.CharField(max_length=3, null=True, blank=True)  
    is_active = models.CharField(max_length=1)  
    created_by = models.CharField(max_length=30, null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True )
    modified_by = models.CharField(max_length=30, null=True, blank=True)
    modified_date = models.DateTimeField(auto_now=True, null=True, blank=True)
    class Meta:
        verbose_name_plural='ModulesInfo'
    def __str__(self):
        return self.MODULE_NAMEL
    
class MTTB_MAIN_MENU(models.Model):
    menu_id = models.CharField(primary_key=True, max_length=20)
    module_Id = models.ForeignKey('STTB_ModulesInfo', null=True, blank=True, on_delete=models.CASCADE, verbose_name='module_Id')
    menu_name_la = models.CharField(max_length=250,null=True,blank=True)
    menu_name_en = models.CharField(max_length=250,null=True,blank=True)
    menu_icon = models.CharField(max_length=250, null=True, blank=True)
    menu_order = models.CharField(max_length=3,null=True,blank=True)
    is_active = models.BooleanField(default=False)
    created_by = models.CharField(max_length=20, null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_by = models.CharField(max_length=20, null=True, blank=True)
    modified_date = models.DateTimeField(auto_now=True, null=True, blank=True)
    class Meta:
        verbose_name_plural = 'MAIN_MENU'
 
class MTTB_SUB_MENU(models.Model):
    sub_menu_id = models.CharField(primary_key=True, max_length=20)
    menu_id = models.ForeignKey('MTTB_MAIN_MENU', null=True, blank=True, on_delete=models.CASCADE)
    sub_menu_name_la = models.CharField(max_length=250)
    sub_menu_name_en = models.CharField(max_length=250)
    sub_menu_icon = models.CharField(max_length=250, null=True, blank=True)
    sub_menu_order = models.CharField(max_length=3,null=True,blank=True)
    is_active = models.BooleanField(default=False)
    created_by = models.CharField(max_length=20, null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_by = models.CharField(max_length=20, null=True, blank=True)
    modified_date = models.DateTimeField(auto_now=True, null=True, blank=True)
    class Meta:
        verbose_name_plural = 'SUB_MENU'
    
class MTTB_Function_Desc(models.Model):
    function_id = models.CharField(primary_key=True, max_length=20, verbose_name='Function_Id')
    sub_menu_id = models.ForeignKey('MTTB_SUB_MENU', null=True, blank=True, on_delete=models.CASCADE)
    description_la = models.CharField(max_length=200)
    description_en = models.CharField(max_length=200, null=True, blank=True)
    all_link = models.CharField(max_length=200, null=True, blank=True)
    eod_function = models.CharField(max_length=1, null=True, blank=True)
    function_order = models.IntegerField(null=True, blank=True)
    is_active = models.CharField(max_length=1, null=True, blank=True)
    created_by = models.CharField(max_length=30, null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    modified_by = models.CharField(max_length=30, null=True, blank=True)
    modified_date = models.DateTimeField(auto_now=False, null=True, blank=True)
    class Meta:
        ordering=['function_id']
        verbose_name_plural = 'Function_Description'
    def __str__(self):
        return self.function_id

class MTTB_Users(models.Model):
    STATUS_CHOICES = [
        ('E', 'Enabled'),
        ('D', 'Disabled'),
    ]

    user_id = models.CharField(primary_key=True, max_length=20)
    div_id = models.ForeignKey('MTTB_Divisions', null=True, blank=True, on_delete=models.CASCADE)
    Role_ID = models.ForeignKey('MTTB_Role_Master', null=True, blank=True, on_delete=models.CASCADE)
    user_name = models.CharField(max_length=250)
    user_password = models.CharField(max_length=250)
    user_email = models.CharField(max_length=250, null=True, blank=True)
    user_mobile = models.CharField(max_length=15, null=True, blank=True)

    # Changed from BooleanField to CharField with choices
    User_Status = models.CharField(
        max_length=1,
        choices=STATUS_CHOICES,
        default='E',
    )

    pwd_changed_on = models.DateField(null=True, blank=True)
    InsertDate = models.DateTimeField(auto_now_add=True)
    UpdateDate = models.DateTimeField(auto_now=True)
    Maker_Id = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.CASCADE, related_name='created_userss'
    )
    Maker_DT_Stamp = models.DateTimeField(null=True, blank=True)
    Checker_Id = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.CASCADE, related_name='checked_userss'
    )
    Checker_DT_Stamp = models.DateTimeField(null=True, blank=True)
    Auth_Status = models.CharField(max_length=1, null=True, blank=True)
    Once_Auth = models.CharField(max_length=1, null=True, blank=True)

    class Meta:
        verbose_name_plural = 'UsersRgith'

    def __str__(self):
        return self.user_name
    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_full_name(self):
        return self.user_name or self.user_id

    def get_short_name(self):
        return self.user_name or self.user_id

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True
    # ────────────────────────────────────────────
    
class STTB_Dates(models.Model):
    date_id = models.AutoField(primary_key=True)
    insertToday = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    prev_Wroking_Day = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    next_working_Day = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    eod_time = models.CharField(max_length=1)
    class Meta:
        ordering=['date_id']  # Change from 'id' to 'DateID'
        verbose_name_plural='EndOfDateInfo'
    def __str__(self):
        return str(self.date_id)

class MTTB_Divisions(models.Model):
    div_id = models.CharField(primary_key=True, max_length=20)
    division_name_la = models.CharField(max_length=250,null=True,blank=True)
    division_name_en = models.CharField(max_length=250,null=True,blank=True)
    record_Status = models.CharField(max_length=1,null=True,blank=True)
    Maker_Id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='created_division')
    Maker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Checker_Id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='checked_division')
    Checker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Auth_Status = models.CharField(max_length=1, null=True, blank=True)
    Once_Auth = models.CharField(max_length=1,null=True,blank=True)
    class Meta:
        verbose_name_plural='DivisionsInfo'
    def __str__(self):
        return self.div_id  # Fixed from Div_ID to Div_Id

class MTTB_Role_Master(models.Model):
    role_id = models.CharField(primary_key=True,max_length=20)
    role_name_la = models.CharField(max_length=250, null=True,blank=True)
    role_name_en = models.CharField(max_length=250, null=True, blank=True)
    record_Status = models.CharField(max_length=1,null=True,blank=True)
    Maker_Id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='created_roles')
    Maker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Checker_Id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='checked_roles')
    Checker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Auth_Status = models.CharField(max_length=1, null=True, blank=True)
    Once_Auth = models.CharField(max_length=1,null=True,blank=True)
    class Meta:
        verbose_name_plural='Role_MasterInfo'
    def __str__(self):
        return self.role_id  # Fixed from role_Id to Role_Id


class MTTB_Role_Detail(models.Model):
    role_id = models.ForeignKey(MTTB_Role_Master, null=True,blank=True, on_delete=models.CASCADE)
    function_id = models.ForeignKey(MTTB_Function_Desc, null=True,blank=True, on_delete=models.CASCADE)
    New_Detail = models.IntegerField(default=0)
    Del_Detail = models.IntegerField(default=0)
    Edit_Detail = models.IntegerField(default=0)
    Auth_Detail = models.IntegerField(default=0)
    class Meta:
        verbose_name_plural='Role_Detail'



class STTB_Current_Users(models.Model):
    user_id = models.ForeignKey(MTTB_Users,null=True,blank=True, on_delete=models.CASCADE)
    Host_UserLogin = models.CharField(max_length=255)
    Start_time = models.DateTimeField(auto_now_add=True,null=True,blank=True)
    class Meta:
        verbose_name_plural='Current_UserInfo'
    def __str__(self):
        return str(self.user_id)

    
class MTTB_Ccy_DEFN(models.Model):
    ccy_code = models.CharField(primary_key=True,max_length=20)
    Ccy_Name_la = models.CharField(max_length=250, null=True,blank=True)
    Ccy_Name_en = models.CharField(max_length=250, null=True,blank=True)
    Country = models.CharField(max_length=20,null=True,blank=True) 
    Ccy_Decimals = models.DecimalField(max_digits=12,decimal_places=2)
    ALT_Ccy_Code = models.CharField(max_length=2,null=True, blank=True)
    Record_Status = models.CharField(max_length=1,null=True,blank=True)
    Maker_Id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='created_Ccy_DEFN')
    Maker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Checker_Id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='checked_Ccy_DEFN')
    Checker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Auth_Status = models.CharField(max_length=1, null=True, blank=True)
    Once_Auth = models.CharField(max_length=1,null=True,blank=True)
    class Meta:
        verbose_name_plural='Currency_DEFN_Info'

class MTTB_EXC_Rate(models.Model):
    ccy_code = models.ForeignKey(MTTB_Ccy_DEFN, null=True,blank =True , on_delete=models.CASCADE)
    Buy_Rate = models.DecimalField(max_digits=12,decimal_places=2)
    Sale_Rate = models.DecimalField(max_digits=12,decimal_places=2)
    INT_Auth_Status = models.CharField(max_length=1,null=True,blank=True)
    Maker_Id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='created_Exc_Rate')
    Maker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Checker_Id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='checked_Exc_Rate')
    Checker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Auth_Status = models.CharField(max_length=1, null=True, blank=True)
    class Meta:
        verbose_name_plural='ExchangeRate'

class MTTB_EXC_Rate_History(models.Model):
    ccy_code = models.ForeignKey(MTTB_Ccy_DEFN, null=True,blank =True , on_delete=models.CASCADE)
    Buy_Rate = models.DecimalField(max_digits=12,decimal_places=2)
    Sale_Rate = models.DecimalField(max_digits=12,decimal_places=2)
    INT_Auth_Status = models.CharField(max_length=1,null=True,blank=True)
    Maker_Id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='created_Exc_RateHistory')
    Maker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Checker_Id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='checked_Exc_Rate_History')
    Checker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Auth_Status = models.CharField(max_length=1, null=True, blank=True)
    class Meta:
        verbose_name_plural='ExchangeRate_History'
        
class MTTB_TRN_Code(models.Model):
    trn_code = models.CharField(primary_key=True,max_length=20)
    trn_Desc_la = models.CharField(max_length=250,null=True, blank=True)
    trn_Desc_en = models.CharField(max_length=250,null=True, blank=True)
    Record_Status = models.CharField(max_length=1,null=True,blank=True)
    Maker_Id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='created_Trn_Code')
    Maker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Checker_Id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='checked_Trn_Code')
    Checker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Auth_Status = models.CharField(max_length=1, null=True, blank=True)
    Once_Auth = models.CharField(max_length=1,null=True,blank=True)
    class Meta:
        verbose_name_plural ='TrnCode'
        
class MTTB_LCL_Holiday(models.Model):
    lcl_holiday_id = models.CharField(primary_key=True,max_length=20)
    HYear = models.CharField(max_length=4,null=True,blank=True)
    HMonth = models.CharField(max_length=10,null=True,blank=True)
    HDate = models.DateTimeField(auto_now=True,null=True,blank=True)
    Holiday_List = models.CharField(max_length=1,null=True,blank=True)
    Record_Status = models.CharField(max_length=1,null=True,blank=True)
    Maker_Id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='created_TLCL_Holiday')
    Maker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Checker_Id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='checked_TLCL_Holiday')
    Checker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Auth_Status = models.CharField(max_length=1, null=True, blank=True)
    Once_Auth = models.CharField(max_length=1,null=True,blank=True)
    class Meta:
        verbose_name_plural ='LCL_Holiday'
        
class MTTB_GLMaster(models.Model):
    glid  = models.AutoField(primary_key=True)
    gl_code  = models.CharField(max_length=20,null=True, blank=True)
    gl_Desc_la = models.CharField(max_length=250,null=True,blank=True)
    gl_Desc_en = models.CharField(max_length=250,null=True,blank=True)
    glType = models.CharField(max_length=1,null=True ,blank=True)
    category = models.CharField(max_length=1 ,null=True,blank=True)
    retal = models.CharField(max_length=1,null=True,blank=True)
    ccy_Res = models.CharField(max_length=1,null=True,blank=True)
    Res_ccy = models.CharField(max_length=1 , null =True,blank=True)
    Allow_BackPeriodEntry = models.CharField(max_length=1,null=True,blank=True)
    pl_Split_ReqD = models.CharField(max_length=1,null=True,blank=True)
    Record_Status = models.CharField(max_length=1,null=True,blank=True)
    Maker_Id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='created_GLMaster')
    Maker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Checker_Id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='checked_GLMaster')
    Checker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Auth_Status = models.CharField(max_length=1, null=True, blank=True)
    Once_Auth = models.CharField(max_length=1,null=True,blank=True)
    class Meta:
        verbose_name_plural ='GLMaster'
        
class MTTB_GLSub(models.Model):
    glsub_id = models.AutoField(primary_key=True)
    gl_code = models.ForeignKey(MTTB_GLMaster,null=True,blank=True,on_delete=models.CASCADE)
    glsub_code = models.CharField(max_length=20,null=True ,blank=True)
    glsub_Desc_la = models.CharField(max_length=250,null=True,blank=True)
    glsub_Desc_en = models.CharField(max_length=250,null=True,blank=True)
    Record_Status = models.CharField(max_length=1,null=True,blank=True)
    Maker_Id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='created_GL_sub')
    Maker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Checker_Id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='checked_GL_sub')
    Checker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Auth_Status = models.CharField(max_length=1, null=True, blank=True)
    Once_Auth = models.CharField(max_length=1,null=True,blank=True)
    class Meta:
        verbose_name_plural='GLSub'

class MTTB_Fin_Cycle(models.Model):
    fin_cycle = models.CharField(primary_key=True,max_length=10)
    cycle_Desc = models.CharField(max_length=250,null=True,blank=True)
    StartDate = models.DateTimeField(auto_now=False, null=True, blank=True)
    EndDate = models.DateTimeField(auto_now=False, null=True, blank=True)
    Record_Status = models.CharField(max_length=1,null=True,blank=True)
    Maker_Id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='created_Fin_Cycle')
    Maker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Checker_Id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='checked_Fin_Cycle')
    Checker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Auth_Status = models.CharField(max_length=1, null=True, blank=True)
    Once_Auth = models.CharField(max_length=1,null=True,blank=True)
    class Meta:
        verbose_name_plural ='FinCycle'
        
class MTTB_Per_Code(models.Model):
    period_code = models.CharField(primary_key=True,max_length=20)
    PC_StartDate  = models.DateTimeField(auto_now=False,null=True,blank=True)
    PC_EndDate = models.DateTimeField(auto_now=False,null=True , blank=True)  
    Fin_cycle = models.ForeignKey(MTTB_Fin_Cycle,null=True ,blank=True,on_delete=models.CASCADE)
    class Meta:
        verbose_name_plural ='PerCode'
        
class MTTB_DATA_Entry(models.Model):
    data_entry_id = models.CharField(primary_key=True,max_length=20)
    JRN_REKEY_REQUIRED = models.CharField(max_length=1,null=True,blank=True)
    JRN_REKEY_VALUE_DATE = models.CharField(max_length=1,null=True,blank=True)
    JRN_REKEY_AMOUNT = models.CharField(max_length=1,null=True,blank=True)
    JRN_REKEY_TXN_CODE = models.CharField(max_length=1,null=True,blank=True)
    BACK_VALUE = models.IntegerField(default=0)
    MOD_NO = models.IntegerField(default=0)
    Record_Status = models.CharField(max_length=1,null=True,blank=True)
    Maker_Id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='created_DATA_Entry')
    Maker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Checker_Id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='checked_DATA_Entry')
    Checker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Auth_Status = models.CharField(max_length=1, null=True, blank=True)
    Once_Auth = models.CharField(max_length=1,null=True,blank=True)
    class Meta:
        verbose_name_plural = 'DaTa_Entry'
        
