from django.db import models

# Create your models here.
class STTB_MDdulesInfo(models.Model):
    M_Id = models.CharField(max_length=50)
    M_NameL = models.CharField(max_length=250)
    M_NameE = models.CharField(max_length=250)
    class Meta:
        verbose_name_plural='MDdulesInfo'
    def __str__(self):
        return self.M_NameL

class MTTB_Function_Description(models.Model):
    Function_Id = models.CharField(max_length=15,unique=True)
    Function_Desc = models.CharField(max_length=500,null=True, blank=True)
    Main_Menu = models.CharField(max_length=250,blank=True)
    Sub_Menu = models.CharField(max_length=250,blank=True)
    All_Link = models.CharField(max_length=500,blank=True)
    M_Id = models.ForeignKey(STTB_MDdulesInfo,null=True , blank=True, on_delete=models.CASCADE)
    Function_Status = models.CharField(max_length=1,blank=True)
    class Meta:
        ordering=['id']
        verbose_name_plural = 'Function_Description'
    def __str__(self):
        return self.Function_Id

class STTB_Dates(models.Model):
    DateID = models.AutoField(primary_key=True)
    InsertToday = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    Prev_Wroking_Day = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    Next_working_Day = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    eod_time = models.CharField(max_length=1)
    class Meta:
        ordering=['DateID']  # Change from 'id' to 'DateID'
        verbose_name_plural='EndOfDateInfo'
    def __str__(self):
        return str(self.DateID)


class MTTB_User(models.Model):
    User_Id = models.CharField(max_length=10,unique=True)
    User_Name = models.CharField(max_length=250)
    User_Password = models.CharField(max_length=250)
    User_Email = models.CharField(max_length=250,null=True,blank=True)
    User_Mobile = models.CharField(max_length=15,null=True,blank=True)
    # Use string reference for circular dependency
    Div_Id = models.ForeignKey('MTTB_Divisions', null=True, blank=True, on_delete=models.CASCADE)
    User_Status = models.BooleanField(default=True)
    InsertDate = models.DateTimeField(auto_now_add=True)
    UpdateDate = models.DateTimeField(auto_now=True)
    # Rename duplicate foreign keys with unique related_name
    Maker_Id = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='created_users')
    Maker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Checker_Id = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='checked_users')
    Checker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Auth_Status = models.CharField(max_length=1,null=True,blank=True)
    Once_Auth = models.CharField(max_length=1,null=True,blank=True)
    # Fix reference to Role_Master
    Role_ID = models.ForeignKey('MTTB_Role_Master', null=True, blank=True, on_delete=models.CASCADE)
    class Meta:
        ordering=['-id']
        verbose_name_plural='UsersRgith'
    def __str__(self):
        return self.User_Name
    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_full_name(self):
        return self.User_Name or self.User_Id

    def get_short_name(self):
        return self.User_Name or self.User_Id

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    def __str__(self):
        return self.User_Id

class MTTB_Divisions(models.Model):
    Div_Id = models.CharField(max_length=20, unique=True)
    Div_NameL = models.CharField(max_length=250,null=True,blank=True)
    Div_NameE = models.CharField(max_length=250,null=True,blank=True)
    Record_Status = models.CharField(max_length=1,null=True,blank=True)
    # Rename duplicate foreign keys with unique related_name
    Maker_Id = models.ForeignKey(MTTB_User, null=True, blank=True, on_delete=models.CASCADE, related_name='created_divisions')
    Maker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Checker_Id = models.ForeignKey(MTTB_User, null=True, blank=True, on_delete=models.CASCADE, related_name='checked_divisions')
    Checker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Auth_Status = models.CharField(max_length=1, null=True, blank=True)
    Once_Auth = models.CharField(max_length=1,null=True,blank=True)
    class Meta:
        verbose_name_plural='DivisionInfo'
    def __str__(self):
        return self.Div_Id  # Fixed from Div_ID to Div_Id
    
class STTB_Current_Users(models.Model):
    User_Id = models.ForeignKey(MTTB_User,null=True,blank=True, on_delete=models.CASCADE)
    Host_UserLogin = models.CharField(max_length=255)
    Start_time = models.DateTimeField(auto_now_add=True,null=True,blank=True)
    class Meta:
        verbose_name_plural='Current_UserInfo'
    def __str__(self):
        return str(self.User_Id)

class MTTB_Role_Master(models.Model):
    Role_Id = models.CharField(max_length=20,unique=True)
    Role_NameL = models.CharField(max_length=250, null=True,blank=True)
    Role_NameE = models.CharField(max_length=250, null=True, blank=True)
    Record_Status = models.CharField(max_length=1,null=True,blank=True)
    Maker_Id = models.ForeignKey(MTTB_User, null=True, blank=True, on_delete=models.CASCADE, related_name='created_roles')
    Maker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Checker_Id = models.ForeignKey(MTTB_User, null=True, blank=True, on_delete=models.CASCADE, related_name='checked_roles')
    Checker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Auth_Status = models.CharField(max_length=1, null=True, blank=True)
    Once_Auth = models.CharField(max_length=1,null=True,blank=True)
    class Meta:
        verbose_name_plural='Role_MasterInfo'
    def __str__(self):
        return self.Role_Id  # Fixed from role_Id to Role_Id

class MTTB_Role_Detail(models.Model):
    Role_Id = models.ForeignKey(MTTB_Role_Master, null=True,blank=True, on_delete=models.CASCADE)
    Function_Id = models.ForeignKey(MTTB_Function_Description,null=True,blank=True, on_delete=models.CASCADE)
    New_Detail = models.IntegerField(default=0)
    Del_Detail = models.IntegerField(default=0)
    Edit_Detail = models.IntegerField(default=0)
    Auth_Detail = models.IntegerField(default=0)
    class Meta:
        verbose_name_plural='Role_Detail'
        
class MTTB_Ccy_DEFN(models.Model):
    Ccy_Code = models.CharField(max_length=20 , unique=True)
    Ccy_NameL = models.CharField(max_length=250, null=True,blank=True)
    Ccy_NameL = models.CharField(max_length=250, null=True,blank=True)
    Country = models.CharField(max_length=20,null=True,blank=True) 
    Ccy_Decimals = models.IntegerField(default=0)
    ALT_Ccy_Code = models.CharField(max_length=2,null=True, blank=True)
    Record_Status = models.CharField(max_length=1,null=True,blank=True)
    Maker_Id = models.ForeignKey(MTTB_User, null=True, blank=True, on_delete=models.CASCADE, related_name='created_Ccy_DEFN')
    Maker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Checker_Id = models.ForeignKey(MTTB_User, null=True, blank=True, on_delete=models.CASCADE, related_name='checked_Ccy_DEFN')
    Checker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Auth_Status = models.CharField(max_length=1, null=True, blank=True)
    Once_Auth = models.CharField(max_length=1,null=True,blank=True)
    class Meta:
        verbose_name_plural='Currency_DEFN_Info'

class MTTB_EXC_Rate(models.Model):
    CCy_Code = models.ForeignKey(MTTB_Ccy_DEFN, null=True,blank =True , on_delete=models.CASCADE)
    Buy_Rate = models.IntegerField(default=0)
    Sale_Rate = models.IntegerField(default=0)
    INT_Auth_Status = models.CharField(max_length=1,null=True,blank=True)
    Maker_Id = models.ForeignKey(MTTB_User, null=True, blank=True, on_delete=models.CASCADE, related_name='created_Exc_Rate')
    Maker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Checker_Id = models.ForeignKey(MTTB_User, null=True, blank=True, on_delete=models.CASCADE, related_name='checked_Exc_Rate')
    Checker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Auth_Status = models.CharField(max_length=1, null=True, blank=True)
    class Meta:
        verbose_name_plural='ExchangeRate'

class MTTB_EXC_Rate_History(models.Model):
    CCy_Code = models.ForeignKey(MTTB_Ccy_DEFN, null=True,blank =True , on_delete=models.CASCADE)
    Buy_Rate = models.IntegerField(default=0)
    Sale_Rate = models.IntegerField(default=0)
    INT_Auth_Status = models.CharField(max_length=1,null=True,blank=True)
    Maker_Id = models.ForeignKey(MTTB_User, null=True, blank=True, on_delete=models.CASCADE, related_name='created_Exc_RateHistory')
    Maker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Checker_Id = models.ForeignKey(MTTB_User, null=True, blank=True, on_delete=models.CASCADE, related_name='checked_Exc_Rate_History')
    Checker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Auth_Status = models.CharField(max_length=1, null=True, blank=True)
    class Meta:
        verbose_name_plural='ExchangeRate_History'
        
class MTTB_TRN_Code(models.Model):
    Trn_code = models.CharField(max_length=20,unique=True)
    Trn_Desc = models.CharField(max_length=150,null=True, blank=True)
    Record_Status = models.CharField(max_length=1,null=True,blank=True)
    Maker_Id = models.ForeignKey(MTTB_User, null=True, blank=True, on_delete=models.CASCADE, related_name='created_Trn_Code')
    Maker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Checker_Id = models.ForeignKey(MTTB_User, null=True, blank=True, on_delete=models.CASCADE, related_name='checked_Trn_Code')
    Checker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Auth_Status = models.CharField(max_length=1, null=True, blank=True)
    Once_Auth = models.CharField(max_length=1,null=True,blank=True)
    class Meta:
        verbose_name_plural ='TrnCode'
        
class MTTB_LCL_Holiday(models.Model):
    HYear = models.CharField(max_length=4,null=True,blank=True)
    HMonth = models.CharField(max_length=10,null=True,blank=True)
    HDate = models.DateTimeField(auto_now=True,null=True,blank=True)
    Holiday_List = models.CharField(max_length=1,null=True,blank=True)
    Record_Status = models.CharField(max_length=1,null=True,blank=True)
    Maker_Id = models.ForeignKey(MTTB_User, null=True, blank=True, on_delete=models.CASCADE, related_name='created_TLCL_Holiday')
    Maker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Checker_Id = models.ForeignKey(MTTB_User, null=True, blank=True, on_delete=models.CASCADE, related_name='checked_TLCL_Holiday')
    Checker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Auth_Status = models.CharField(max_length=1, null=True, blank=True)
    Once_Auth = models.CharField(max_length=1,null=True,blank=True)
    class Meta:
        verbose_name_plural ='LCL_Holiday'
class MTTB_GLMaster(models.Model):
    glid  = models.AutoField(primary_key=True)
    gl_code  = models.CharField(max_length=10,null=True, blank=True)
    gl_Desc = models.CharField(max_length=250,null=True,blank=True)
    glTpe = models.CharField(max_length=1,null=True ,blank=True)
    category = models.CharField(max_length=1 ,null=True,blank=True)
    retal = models.CharField(max_length=1,null=True,blank=True)
    ccy_Res = models.CharField(max_length=1,null=True,blank=True)
    Res_ccy = models.CharField(max_length=1 , null =True,blank=True)
    Allow_BackPeriodEntry = models.CharField(max_length=1,null=True,blank=True)
    pl_Split_ReqD = models.CharField(max_length=1,null=True,blank=True)
    Record_Status = models.CharField(max_length=1,null=True,blank=True)
    Maker_Id = models.ForeignKey(MTTB_User, null=True, blank=True, on_delete=models.CASCADE, related_name='created_GLMaster')
    Maker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Checker_Id = models.ForeignKey(MTTB_User, null=True, blank=True, on_delete=models.CASCADE, related_name='checked_GLMaster')
    Checker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Auth_Status = models.CharField(max_length=1, null=True, blank=True)
    Once_Auth = models.CharField(max_length=1,null=True,blank=True)
    class Meta:
        verbose_name_plural ='GLMaster'
        
class MTTB_GLSub(models.Model):
    glid = models.AutoField(primary_key=True)
    glsub = models.CharField(max_length=20,null=True ,blank=True)
    glsub_Desc = models.CharField(max_length=250,null=True,blank=True)
    gl_code = models.ForeignKey(MTTB_GLMaster,null=True,blank=True,on_delete=models.CASCADE)
    Record_Status = models.CharField(max_length=1,null=True,blank=True)
    Maker_Id = models.ForeignKey(MTTB_User, null=True, blank=True, on_delete=models.CASCADE, related_name='created_GL_sub')
    Maker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Checker_Id = models.ForeignKey(MTTB_User, null=True, blank=True, on_delete=models.CASCADE, related_name='checked_GL_sub')
    Checker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Auth_Status = models.CharField(max_length=1, null=True, blank=True)
    Once_Auth = models.CharField(max_length=1,null=True,blank=True)
    class Meta:
        verbose_name_plural='GLSub'

class MTTB_Fin_Cycle(models.Model):
    Fin_cycle = models.CharField(max_length=10,unique=True)
    cycle_Desc = models.CharField(max_length=250,null=True,blank=True)
    StartDate = models.DateTimeField(auto_now=False, null=True, blank=True)
    EndDate = models.DateTimeField(auto_now=False, null=True, blank=True)
    Record_Status = models.CharField(max_length=1,null=True,blank=True)
    Maker_Id = models.ForeignKey(MTTB_User, null=True, blank=True, on_delete=models.CASCADE, related_name='created_Fin_Cycle')
    Maker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Checker_Id = models.ForeignKey(MTTB_User, null=True, blank=True, on_delete=models.CASCADE, related_name='checked_Fin_Cycle')
    Checker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Auth_Status = models.CharField(max_length=1, null=True, blank=True)
    Once_Auth = models.CharField(max_length=1,null=True,blank=True)
    class Meta:
        verbose_name_plural ='FinCycle'
        
class MTTB_Per_Code(models.Model):
    period_code = models.CharField(max_length=20,unique=True)
    PC_StartDate  = models.DateTimeField(auto_now=False,null=True,blank=True)
    PC_EndDate = models.DateTimeField(auto_now=False,null=True , blank=True)  
    Fin_cycle = models.ForeignKey(MTTB_Fin_Cycle,null=True ,blank=True,on_delete=models.CASCADE)
    class Meta:
        verbose_name_plural ='PerCode'
        
class MTTB_DATA_Entry(models.Model):
    JRN_REKEY_REQUIRED = models.CharField(max_length=1,null=True,blank=True)
    JRN_REKEY_VALUE_DATE = models.CharField(max_length=1,null=True,blank=True)
    JRN_REKEY_AMOUNT = models.CharField(max_length=1,null=True,blank=True)
    JRN_REKEY_TXN_CODE = models.CharField(max_length=1,null=True,blank=True)
    BACK_VALUE = models.IntegerField(default=0)
    MOD_NO = models.IntegerField(default=0)
    Record_Status = models.CharField(max_length=1,null=True,blank=True)
    Maker_Id = models.ForeignKey(MTTB_User, null=True, blank=True, on_delete=models.CASCADE, related_name='created_DATA_Entry')
    Maker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Checker_Id = models.ForeignKey(MTTB_User, null=True, blank=True, on_delete=models.CASCADE, related_name='checked_DATA_Entry')
    Checker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Auth_Status = models.CharField(max_length=1, null=True, blank=True)
    Once_Auth = models.CharField(max_length=1,null=True,blank=True)
    class Meta:
        verbose_name_plural = 'DATA_Entry'

class STTB_GL_BAL(models.Model):
    gl_code = models.ForeignKey(MTTB_GLMaster,null=True,blank=True,on_delete=models.CASCADE)
    CCy_Code = models.ForeignKey(MTTB_Ccy_DEFN, null=True,blank =True , on_delete=models.CASCADE)
    fin_year = models.CharField(max_length=9, null=True,blank =True) #no foreign table 
    period_code = models.ForeignKey(MTTB_Per_Code, null=True,blank =True , on_delete=models.CASCADE)
    category = models.CharField(max_length=1, null=True, blank=True)
    dr_mov = models.DecimalField(max_digits=25, decimal_places=2, null=True, blank=True)
    cr_mov = models.DecimalField(max_digits=25, decimal_places=2, null=True, blank=True)
    dr_mov_lcy = models.DecimalField(max_digits=25, decimal_places=2, null=True, blank=True)
    cr_mov_lcy = models.DecimalField(max_digits=25, decimal_places=2, null=True, blank=True)
    dr_bal = models.DecimalField(max_digits=25, decimal_places=2, null=True, blank=True)
    cr_bal = models.DecimalField(max_digits=25, decimal_places=2, null=True, blank=True)
    dr_bal_lcy = models.DecimalField(max_digits=25, decimal_places=2, null=True, blank=True)
    cr_bal_lcy = models.DecimalField(max_digits=25, decimal_places=2, null=True, blank=True)
    open_dr_bal = models.DecimalField(max_digits=25, decimal_places=2, null=True, blank=True)
    open_cr_bal = models.DecimalField(max_digits=25, decimal_places=2, null=True, blank=True)
    open_dr_bal_lcy = models.DecimalField(max_digits=25, decimal_places=2, null=True, blank=True)
    open_cr_bal_lcy = models.DecimalField(max_digits=25, decimal_places=2, null=True, blank=True)

    class Meta:
        verbose_name_plural = 'GL_BAL'

class STTB_GL_SUB_BAL(models.Model):
    gl_code = models.ForeignKey(MTTB_GLMaster,null=True,blank=True,on_delete=models.CASCADE)
    CCy_Code = models.ForeignKey(MTTB_Ccy_DEFN, null=True,blank =True , on_delete=models.CASCADE)
    fin_year = models.CharField(max_length=9, null=True,blank =True) #no foreign table 
    period_code = models.ForeignKey(MTTB_Per_Code, null=True,blank =True , on_delete=models.CASCADE)
    dr_mov = models.DecimalField(max_digits=25, decimal_places=2, null=True, blank=True)
    cr_mov = models.DecimalField(max_digits=25, decimal_places=2, null=True, blank=True)
    dr_mov_lcy = models.DecimalField(max_digits=25, decimal_places=2, null=True, blank=True)
    cr_mov_lcy = models.DecimalField(max_digits=25, decimal_places=2, null=True, blank=True)
    dr_bal = models.DecimalField(max_digits=25, decimal_places=2, null=True, blank=True)
    cr_bal = models.DecimalField(max_digits=25, decimal_places=2, null=True, blank=True)
    dr_bal_lcy = models.DecimalField(max_digits=25, decimal_places=2, null=True, blank=True)
    cr_bal_lcy = models.DecimalField(max_digits=25, decimal_places=2, null=True, blank=True)
    open_dr_bal = models.DecimalField(max_digits=25, decimal_places=2, null=True, blank=True)
    open_cr_bal = models.DecimalField(max_digits=25, decimal_places=2, null=True, blank=True)
    open_dr_bal_lcy = models.DecimalField(max_digits=25, decimal_places=2, null=True, blank=True)
    open_cr_bal_lcy = models.DecimalField(max_digits=25, decimal_places=2, null=True, blank=True)

    class Meta:
        verbose_name_plural = 'GL_SUB_BAL'

