from django.db import models

# Create your models here.    
class STTB_ModulesInfo(models.Model):
    module_Id = models.CharField(primary_key=True,max_length=20)
    module_name_la = models.CharField(max_length=250)
    module_name_en = models.CharField(max_length=250)
    module_icon = models.CharField(max_length=255, null=True, blank=True)  
    module_order = models.CharField(max_length=3, null=True, blank=True) 
    Record_Status = models.CharField(max_length=1, default='C')  
    Maker_Id = models.CharField(max_length=30, null=True, blank=True)
    Maker_DT_Stamp = models.DateTimeField(auto_now_add=True )
    Checker_Id = models.CharField(max_length=30, null=True, blank=True)
    Checker_DT_Stamp = models.DateTimeField(auto_now=True, null=True, blank=True)
    Auth_Status = models.CharField(max_length=1, null=True, blank=True, default='U')
    Once_Auth = models.CharField(max_length=1,null=True,blank=True, default='N')
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
    Record_Status = models.CharField(max_length=1, default='C') 
    Maker_Id = models.CharField(max_length=20, null=True, blank=True)
    Maker_DT_Stamp = models.DateTimeField(auto_now_add=True)
    Checker_Id = models.CharField(max_length=20, null=True, blank=True)
    Checker_DT_Stamp = models.DateTimeField(auto_now=True, null=True, blank=True)
    Auth_Status = models.CharField(max_length=1, null=True, blank=True, default='U')
    Once_Auth = models.CharField(max_length=1,null=True,blank=True, default='N')
    class Meta:
        verbose_name_plural = 'MAIN_MENU'
 
class MTTB_SUB_MENU(models.Model):
    sub_menu_id = models.CharField(primary_key=True, max_length=20)
    menu_id = models.ForeignKey('MTTB_MAIN_MENU', null=True, blank=True, on_delete=models.CASCADE)
    sub_menu_name_la = models.CharField(max_length=250)
    sub_menu_name_en = models.CharField(max_length=250)
    sub_menu_icon = models.CharField(max_length=250, null=True, blank=True)
    sub_menu_order = models.CharField(max_length=3,null=True,blank=True)
    sub_menu_urls = models.CharField(max_length=100, null=True, blank=True)
    Record_Status = models.CharField(max_length=1, default='C') 
    Maker_Id = models.CharField(max_length=20, null=True, blank=True)
    Maker_DT_Stamp = models.DateTimeField(auto_now_add=True)
    Checker_Id = models.CharField(max_length=20, null=True, blank=True)
    Checker_DT_Stamp = models.DateTimeField(auto_now=True, null=True, blank=True)
    Auth_Status = models.CharField(max_length=1, null=True, blank=True, default='U')
    Once_Auth = models.CharField(max_length=1,null=True,blank=True, default='N')
    class Meta:
        verbose_name_plural = 'SUB_MENU'
    
class MTTB_Function_Desc(models.Model):
    function_id = models.CharField(primary_key=True, max_length=20, verbose_name='Function_Id')
    sub_menu_id = models.ForeignKey('MTTB_SUB_MENU', null=True, blank=True, on_delete=models.CASCADE)
    description_la = models.CharField(max_length=200)
    description_en = models.CharField(max_length=200, null=True, blank=True)
    # all_link = models.CharField(max_length=200, null=True, blank=True)
    eod_function = models.CharField(max_length=1, null=True, blank=True, default='N')
    function_order = models.IntegerField(null=True, blank=True)
    is_active = models.CharField(max_length=1, null=True, blank=True, default='Y')
    created_by = models.CharField(max_length=30, null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    modified_by = models.CharField(max_length=30, null=True, blank=True)
    modified_date = models.DateTimeField(auto_now=False, null=True, blank=True)
    class Meta:
        ordering=['function_id']
        verbose_name_plural = 'Function_Description'
    def __str__(self):
        return self.function_id

# class MTTB_Users(models.Model):
#     STATUS_CHOICES = [
#         ('E', 'Enabled'),
#         ('D', 'Disabled'),
#     ]

#     user_id = models.CharField(primary_key=True, max_length=20)
#     div_id = models.ForeignKey('MTTB_Divisions', null=True, blank=True, on_delete=models.CASCADE)
#     Role_ID = models.ForeignKey('MTTB_Role_Master', null=True, blank=True, on_delete=models.CASCADE)
#     user_name = models.CharField(max_length=250)
#     user_password = models.CharField(max_length=250)
#     user_email = models.CharField(max_length=250, null=True, blank=True)
#     user_mobile = models.CharField(max_length=15, null=True, blank=True)

#     # Changed from BooleanField to CharField with choices
#     User_Status = models.CharField(
#         max_length=1,
#         choices=STATUS_CHOICES,
#         default='E',
#     )

#     pwd_changed_on = models.DateField(null=True, blank=True)
#     InsertDate = models.DateTimeField(auto_now_add=True)
#     UpdateDate = models.DateTimeField(auto_now=True)
#     Maker_Id = models.ForeignKey(
#         'self', null=True, blank=True, on_delete=models.CASCADE, related_name='created_userss'
#     )
#     Maker_DT_Stamp = models.DateTimeField(auto_now_add=True,null=True, blank=True)
#     Checker_Id = models.ForeignKey(
#         'self', null=True, blank=True, on_delete=models.CASCADE, related_name='checked_userss'
#     )
#     Checker_DT_Stamp = models.DateTimeField(null=True, blank=True)
#     Auth_Status = models.CharField(max_length=1, null=True, blank=True)
#     Once_Auth = models.CharField(max_length=1, null=True, blank=True)

#     class Meta:
#         verbose_name_plural = 'UsersRgith'

#     def __str__(self):
#         return self.user_name
#     @property
#     def is_authenticated(self):
#         return True

#     @property
#     def is_anonymous(self):
#         return False

#     def get_full_name(self):
#         return self.user_name or self.user_id

#     def get_short_name(self):
#         return self.user_name or self.user_id

#     def has_perm(self, perm, obj=None):
#         return True

#     def has_module_perms(self, app_label):
#         return True
#     # ────────────────────────────────────────────


class MTTB_Users(models.Model):
    STATUS_CHOICES = [
        ('E', 'Enabled'),
        ('D', 'Disabled'),
    ]

    user_id = models.CharField(primary_key=True, max_length=20)
    div_id = models.ForeignKey(
        'MTTB_Divisions', null=True, blank=True, on_delete=models.CASCADE
    )
    Role_ID = models.ForeignKey(
        'MTTB_Role_Master', null=True, blank=True, on_delete=models.CASCADE
    )
    user_name = models.CharField(max_length=250, unique=True)
    user_password = models.CharField(max_length=250)
    user_email = models.CharField(max_length=250, null=True, blank=True)
    user_mobile = models.CharField(max_length=15, null=True, blank=True)

    # New field to upload a profile picture
    profile_picture = models.ImageField(
        upload_to='profile_pictures/', null=True, blank=True
    )

    User_Status = models.CharField(
        max_length=1,
        choices=STATUS_CHOICES,
        default='E',
    )

    pwd_changed_on = models.DateField(null=True, blank=True)
    InsertDate = models.DateTimeField(auto_now_add=True)
    UpdateDate = models.DateTimeField(auto_now=True)
    Maker_Id = models.ForeignKey(
        'self', null=True, blank=True,
        on_delete=models.CASCADE,
        related_name='created_userss'
    )
    Maker_DT_Stamp = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    Checker_Id = models.ForeignKey(
        'self', null=True, blank=True,
        on_delete=models.CASCADE,
        related_name='checked_userss'
    )
    Checker_DT_Stamp = models.DateTimeField(null=True, blank=True)
    Auth_Status = models.CharField(max_length=1, null=True, blank=True, default='U')
    Once_Auth = models.CharField(max_length=1, null=True, blank=True, default='N')

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


class MTTB_USER_ACCESS_LOG(models.Model):
    log_id = models.AutoField(primary_key=True)  
    user_id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE)   
    login_datetime = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    logout_datetime = models.DateTimeField(null=True, blank=True)
    session_id = models.CharField(max_length=100, null=True, blank=True)
    ip_address = models.CharField(max_length=45,null=True, blank=True)
    user_agent = models.CharField(max_length=255, null=True, blank=True)
    login_status = models.CharField(max_length=1)
    logout_type = models.CharField(max_length=1, null=True, blank=True)
    remarks = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name_plural='USER_ACCESS_LOG'

class MTTB_USER_ACTIVITY_LOG(models.Model):
    activity_id = models.AutoField(primary_key=True) 
    user_id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE) 
    session_id = models.CharField(max_length=100)
    activity_datetime = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    module_id = models.CharField(max_length=10)
    function_id = models.CharField(max_length=20)
    action_type = models.CharField(max_length=20)
    record_id = models.CharField(max_length=100, null=True, blank=True)
    old_values = models.TextField(null=True, blank=True) 
    new_values = models.TextField(null=True, blank=True) 
    ip_address = models.GenericIPAddressField(null=True, blank=True)

class Meta:
        verbose_name_plural='USER_ACTIVITY_LOG'


    
class STTB_Dates(models.Model):
    date_id = models.AutoField(primary_key=True)
    Start_Date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
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
    record_Status = models.CharField(max_length=1,null=True,blank=True, default='C')
    Maker_Id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='created_division')
    Maker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Checker_Id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='checked_division')
    Checker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Auth_Status = models.CharField(max_length=1, null=True, blank=True, default='U')
    Once_Auth = models.CharField(max_length=1,null=True,blank=True, default='N')
    class Meta:
        verbose_name_plural='DivisionsInfo'
    def __str__(self):
        return self.div_id  # Fixed from Div_ID to Div_Id

class MTTB_Role_Master(models.Model):
    role_id = models.CharField(primary_key=True,max_length=20)
    role_name_la = models.CharField(max_length=250, null=True,blank=True)
    role_name_en = models.CharField(max_length=250, null=True, blank=True)
    record_Status = models.CharField(max_length=1,null=True,blank=True, default='C')
    Maker_Id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='created_roles')
    Maker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Checker_Id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='checked_roles')
    Checker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Auth_Status = models.CharField(max_length=1, null=True, blank=True, default='U')
    Once_Auth = models.CharField(max_length=1,null=True,blank=True, default='N')
    class Meta:
        verbose_name_plural='Role_MasterInfo'
    def __str__(self):
        return self.role_id  


class MTTB_Role_Detail(models.Model):
    role_id = models.ForeignKey(MTTB_Role_Master, null=True,blank=True, on_delete=models.CASCADE)
    sub_menu_id = models.ForeignKey(MTTB_SUB_MENU, null=True,blank=True, on_delete=models.CASCADE)
    New_Detail = models.IntegerField(default=0)
    Del_Detail = models.IntegerField(default=0)
    Edit_Detail = models.IntegerField(default=0)
    Auth_Detail = models.IntegerField(default=0)
    View_Detail = models.IntegerField(default=0)
    class Meta:
        verbose_name_plural='Role_Detail'
        unique_together = ('role_id', 'sub_menu_id')

class MTTB_EMPLOYEE(models.Model):
    employee_id = models.CharField(max_length=20, primary_key=True)
    user_id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE) 
    employee_name_la = models.CharField(max_length=250)
    employee_name_en = models.CharField(max_length=250, null=True, blank=True)
    gender = models.CharField(max_length=1, choices=[('F', 'Female'), ('M', 'Male')], null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    national_id = models.CharField(max_length=20, null=True, blank=True)
    address_la = models.CharField(max_length=255, null=True, blank=True)
    address_en = models.CharField(max_length=255, null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    email = models.CharField(max_length=100, null=True, blank=True)
    position_code = models.CharField(max_length=10, null=True, blank=True)
    div_id = models.ForeignKey(MTTB_Divisions, null=True, blank=True, on_delete=models.CASCADE)
    employee_photo = models.ImageField(upload_to='employee_photos/', null=True, blank=True)
    employee_signature = models.ImageField(upload_to='employee_signatures/', null=True, blank=True)
    hire_date = models.DateField(max_length=10,null=True, blank=True)
    employment_status = models.CharField(max_length=1, default='A')
    record_stat = models.CharField(max_length=1 ,null=True,blank=True, default='C')
    Maker_Id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='created_employee')
    Maker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Checker_Id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='checked_employee')
    Checker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Auth_Status = models.CharField(max_length=1, null=True, blank=True, default='U')
    Once_Auth = models.CharField(max_length=1,null=True,blank=True, default='N')
    class Meta:
        verbose_name_plural='EMPLOYEE'

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
    Record_Status = models.CharField(max_length=1,null=True,blank=True, default='C')
    Maker_Id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='created_Ccy_DEFN')
    Maker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Checker_Id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='checked_Ccy_DEFN')
    Checker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Auth_Status = models.CharField(max_length=1, null=True, blank=True, default='U')
    Once_Auth = models.CharField(max_length=1,null=True,blank=True, default='N')
    class Meta:
        verbose_name_plural='Currency_DEFN_Info'

class MTTB_EXC_Rate(models.Model):
    ccy_code = models.ForeignKey(MTTB_Ccy_DEFN, null=True,blank =True , on_delete=models.CASCADE)
    Buy_Rate = models.DecimalField(max_digits=12,decimal_places=2)
    Sale_Rate = models.DecimalField(max_digits=12,decimal_places=2)
    INT_Auth_Status = models.CharField(max_length=1,null=True,blank=True, default='U')
    Maker_Id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='created_Exc_Rate')
    Maker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Checker_Id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='checked_Exc_Rate')
    Checker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Auth_Status = models.CharField(max_length=1, null=True, blank=True, default='U')
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
    Auth_Status = models.CharField(max_length=1, null=True, blank=True, default='U')
    class Meta:
        verbose_name_plural='ExchangeRate_History'
        
class MTTB_TRN_Code(models.Model):
    trn_code = models.CharField(primary_key=True,max_length=20)
    trn_Desc_la = models.CharField(max_length=250,null=True, blank=True)
    trn_Desc_en = models.CharField(max_length=250,null=True, blank=True)
    Record_Status = models.CharField(max_length=1,null=True,blank=True, default='C')
    Maker_Id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='created_Trn_Code')
    Maker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Checker_Id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='checked_Trn_Code')
    Checker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Auth_Status = models.CharField(max_length=1, null=True, blank=True, default='U')
    Once_Auth = models.CharField(max_length=1,null=True,blank=True, default='N')
    class Meta:
        verbose_name_plural ='TrnCode'
        
class MTTB_LCL_Holiday(models.Model):
    lcl_holiday_id = models.CharField(primary_key=True,max_length=20)
    HYear = models.CharField(max_length=4,null=True,blank=True)
    HMonth = models.CharField(max_length=10,null=True,blank=True)
    HDate = models.DateTimeField(auto_now=True,null=True,blank=True)
    Holiday_List = models.CharField(max_length=31,null=True,blank=True)
    Record_Status = models.CharField(max_length=1,null=True,blank=True, default='C')
    Maker_Id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='created_TLCL_Holiday')
    Maker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Checker_Id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='checked_TLCL_Holiday')
    Checker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Auth_Status = models.CharField(max_length=1, null=True, blank=True, default='U')
    Once_Auth = models.CharField(max_length=1,null=True,blank=True, default='N')
    class Meta:
        verbose_name_plural ='LCL_Holiday'
        
class MTTB_GLMaster(models.Model):
    glid  = models.AutoField(primary_key=True)
    gl_code  = models.CharField(max_length=20,null=True, blank=True, unique=True)
    gl_Desc_la = models.CharField(max_length=250,null=True,blank=True)
    gl_Desc_en = models.CharField(max_length=250,null=True,blank=True)
    glType = models.CharField(max_length=1,null=True ,blank=True)
    category = models.CharField(max_length=1 ,null=True,blank=True)
    CategoryType = models.CharField(max_length=1,null=True,blank=True)
    retal = models.CharField(max_length=1,null=True,blank=True)
    ccy_Res = models.CharField(max_length=1,null=True,blank=True)
    Res_ccy = models.ForeignKey(MTTB_Ccy_DEFN,null=True,blank=True,on_delete=models.CASCADE)
    Allow_BackPeriodEntry = models.CharField(max_length=1,null=True,blank=True)
    pl_Split_ReqD = models.CharField(max_length=1,null=True,blank=True)
    Record_Status = models.CharField(max_length=1,null=True,blank=True, default='C')
    Maker_Id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='created_GLMaster')
    Maker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Checker_Id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='checked_GLMaster')
    Checker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Auth_Status = models.CharField(max_length=1, null=True, blank=True, default='U')
    Once_Auth = models.CharField(max_length=1,null=True,blank=True, default='N')
    class Meta:
        verbose_name_plural ='GLMaster'
        
class MTTB_GLSub(models.Model):
    glsub_id = models.AutoField(primary_key=True)
    gl_code = models.ForeignKey(MTTB_GLMaster,null=True,blank=True,on_delete=models.CASCADE)    
    glsub_code = models.CharField(max_length=20,null=True ,blank=True)
    glsub_Desc_la = models.CharField(max_length=250,null=True,blank=True)
    glsub_Desc_en = models.CharField(max_length=250,null=True,blank=True)
    Record_Status = models.CharField(max_length=1,null=True,blank=True, default='C')
    Maker_Id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='created_GL_sub')
    Maker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Checker_Id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='checked_GL_sub')
    Checker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Auth_Status = models.CharField(max_length=1, null=True, blank=True, default='U')
    Once_Auth = models.CharField(max_length=1,null=True,blank=True, default='N')
    class Meta:
        verbose_name_plural='GLSub'
    def __str__(self):
        return self.glsub_code or str(self.glsub_id)

class MTTB_Fin_Cycle(models.Model):
    fin_cycle = models.CharField(primary_key=True,max_length=10)
    cycle_Desc = models.CharField(max_length=250,null=True,blank=True)
    StartDate = models.DateTimeField(auto_now=False, null=True, blank=True)
    EndDate = models.DateTimeField(auto_now=False, null=True, blank=True)
    Record_Status = models.CharField(max_length=1,null=True,blank=True, default='C')
    Maker_Id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='created_Fin_Cycle')
    Maker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Checker_Id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='checked_Fin_Cycle')
    Checker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Auth_Status = models.CharField(max_length=1, null=True, blank=True, default='U')
    Once_Auth = models.CharField(max_length=1,null=True,blank=True, default='N')
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
    BACK_VALUE = models.CharField(max_length=1,null=True,blank=True)
    MOD_NO = models.CharField(max_length=1,null=True,blank=True)
    Record_Status = models.CharField(max_length=1,null=True,blank=True, default='C')
    Maker_Id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='created_DATA_Entry')
    Maker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Checker_Id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='checked_DATA_Entry')
    Checker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Auth_Status = models.CharField(max_length=1, null=True, blank=True, default='U')
    Once_Auth = models.CharField(max_length=1,null=True,blank=True, default='N')
    class Meta:
        verbose_name_plural = 'DaTa_Entry'

class DETB_JRNL_LOG_MASTER(models.Model):
    JRNLLog_id = models.AutoField(primary_key=True)
    module_id = models.ForeignKey(STTB_ModulesInfo,null=True,blank=True,on_delete=models.CASCADE)
    Reference_No = models.CharField(max_length=20, null=True, blank=True)
    Ccy_cd = models.ForeignKey(MTTB_Ccy_DEFN,null=True,blank=True,on_delete=models.CASCADE)
    Fcy_Amount = models.DecimalField(max_digits=22, decimal_places=3, null=True, blank=True)
    Lcy_Amount = models.DecimalField(max_digits=22, decimal_places=3, null=True, blank=True)
    Txn_code = models.ForeignKey(MTTB_TRN_Code,null=True,blank=True,on_delete=models.CASCADE)
    Value_date = models.DateTimeField(auto_now=False,null=True , blank=True)
    Exch_rate = models.DecimalField(max_digits=24, decimal_places=12, null=True, blank=True)
    fin_cycle = models.ForeignKey(MTTB_Fin_Cycle,null=True,blank=True,on_delete=models.CASCADE)
    Period_code = models.ForeignKey(MTTB_Per_Code,null=True,blank=True,on_delete=models.CASCADE)
    Addl_text = models.CharField(max_length=255, null=True, blank=True)
    Maker_Id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='created_JRNL_LOG_MASTER')
    Maker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Checker_Id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='checked_JRNL_LOG_MASTER')
    Checker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Auth_Status = models.CharField(max_length=1, null=True, blank=True, default='U')
    entry_seq_no = models.IntegerField(null=True, blank=True)
    delete_stat = models.CharField(max_length=1, null=True, blank=True)
    class Meta:
        verbose_name_plural = 'DETB_JRNL_LOG_MASTER'

class DETB_JRNL_LOG(models.Model):
    JRNLLog_id = models.AutoField(primary_key=True)
    module_id = models.ForeignKey(STTB_ModulesInfo,null=True,blank=True,on_delete=models.CASCADE)
    Reference_No = models.CharField(max_length=30, null=True, blank=True)
    Ccy_cd = models.ForeignKey(MTTB_Ccy_DEFN,null=True,blank=True,on_delete=models.CASCADE)
    Fcy_Amount = models.DecimalField(max_digits=22, decimal_places=3, null=True, blank=True)
    Lcy_Amount = models.DecimalField(max_digits=22, decimal_places=3, null=True, blank=True)
    fcy_dr = models.DecimalField(max_digits=22, decimal_places=3, null=True, blank=True)
    fcy_cr = models.DecimalField(max_digits=22, decimal_places=3, null=True, blank=True)
    lcy_dr = models.DecimalField(max_digits=22, decimal_places=3, null=True, blank=True)
    lcy_cr = models.DecimalField(max_digits=22, decimal_places=3, null=True, blank=True)
    Dr_cr = models.CharField(max_length=1)
    Account = models.ForeignKey(MTTB_GLSub,null=True,blank=True,on_delete=models.CASCADE)
    Account_no = models.CharField(max_length=30, null=True, blank=True)
    Ac_relatives = models.CharField(max_length=50, null=True, blank=True)
    Txn_code = models.ForeignKey(MTTB_TRN_Code,null=True,blank=True,on_delete=models.CASCADE)
    Value_date = models.DateTimeField(auto_now=False,null=True , blank=True)
    Exch_rate = models.DecimalField(max_digits=24, decimal_places=12, null=True, blank=True)
    fin_cycle = models.ForeignKey(MTTB_Fin_Cycle,null=True,blank=True,on_delete=models.CASCADE)
    Period_code = models.ForeignKey(MTTB_Per_Code,null=True,blank=True,on_delete=models.CASCADE)
    Addl_text = models.CharField(max_length=255, null=True, blank=True)
    Addl_sub_text = models.CharField(max_length=255, null=True, blank=True)
    Maker_Id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='created_JRNL_LOG')
    Maker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Checker_Id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='checked_JRNL_LOG')
    Checker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Auth_Status = models.CharField(max_length=1, null=True, blank=True, default='U')
    class Meta:
        verbose_name_plural = 'JRNL_LOG'
        # Optional: Prevent duplicate entries for same reference + account + dr_cr
        unique_together = [
            ['Reference_No', 'Account', 'Dr_cr', 'Fcy_Amount']
        ]
        # OR use constraints (Django 2.2+)
        constraints = [
            models.UniqueConstraint(
                fields=['Reference_No', 'Account', 'Dr_cr', 'Fcy_Amount'],
                name='unique_journal_entry'
            )
        ]

class ACTB_DAIRY_LOG(models.Model):
    ac_entry_sr_no = models.AutoField(primary_key=True)
    module = models.ForeignKey(STTB_ModulesInfo,null=True,blank=True,on_delete=models.CASCADE)
    trn_ref_no = models.ForeignKey(DETB_JRNL_LOG,null=True,blank=True,on_delete=models.CASCADE)
    event_sr_no = models.BigIntegerField(default=0, null=True, blank=True)
    event = models.CharField(max_length=4, null=True, blank=True)
    ac_no = models.ForeignKey(MTTB_GLSub,null=True,blank=True,on_delete=models.CASCADE)
    ac_relative = models.CharField(max_length=50, null=True, blank=True)
    ac_ccy = models.ForeignKey(MTTB_Ccy_DEFN,null=True,blank=True,on_delete=models.CASCADE)
    drcr_ind = models.CharField(max_length=1)
    trn_code = models.ForeignKey(MTTB_TRN_Code,null=True,blank=True,on_delete=models.CASCADE)
    fcy_amount = models.DecimalField(max_digits=22, decimal_places=3, null=True, blank=True)
    exch_rate = models.DecimalField(max_digits=24, decimal_places=1, null=True, blank=True)
    lcy_amount = models.DecimalField(max_digits=22, decimal_places=3, null=True, blank=True)
    fcy_dr = models.DecimalField(max_digits=22, decimal_places=3, null=True, blank=True)
    fcy_cr = models.DecimalField(max_digits=22, decimal_places=3, null=True, blank=True)
    lcy_dr = models.DecimalField(max_digits=22, decimal_places=3, null=True, blank=True)
    lcy_cr = models.DecimalField(max_digits=22, decimal_places=3, null=True, blank=True)
    external_ref_no = models.CharField(max_length=16, null=True, blank=True)
    addl_text = models.CharField(max_length=255, null=True, blank=True)
    trn_dt = models.DateField(null=True, blank=True)
    type = models.ForeignKey(MTTB_GLMaster,null=True,blank=True,on_delete=models.CASCADE)
    category = models.CharField(max_length=1, null=True, blank=True)
    value_dt = models.DateField(null=True, blank=True)
    financial_cycle = models.ForeignKey(MTTB_Fin_Cycle,null=True,blank=True,on_delete=models.CASCADE)
    period_code = models.ForeignKey(MTTB_Per_Code,null=True,blank=True,on_delete=models.CASCADE)
    user_id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='created_DAILY_LOG')
    Maker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    auth_id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='checker_DAILY_LOG')
    Checker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Auth_Status = models.CharField(max_length=1, null=True, blank=True, default='U')
    product = models.CharField(max_length=4, null=True, blank=True)
    entry_seq_no = models.IntegerField(null=True, blank=True)
    delete_stat = models.CharField(max_length=1, null=True, blank=True)

    class Meta:
        verbose_name_plural = 'DAILY_LOG'

class DETB_JRNL_LOG_HIST(models.Model):
    JRNLLog_id_his = models.AutoField(primary_key=True)
    Reference_No = models.CharField(max_length=20, null=True, blank=True)
    module_id = models.ForeignKey(STTB_ModulesInfo,null=True,blank=True,on_delete=models.CASCADE)
    Ccy_cd = models.ForeignKey(MTTB_Ccy_DEFN,null=True,blank=True,on_delete=models.CASCADE)
    Fcy_Amount = models.DecimalField(max_digits=22, decimal_places=3, null=True, blank=True)
    Lcy_Amount = models.DecimalField(max_digits=22, decimal_places=3, null=True, blank=True)
    fcy_dr = models.DecimalField(max_digits=22, decimal_places=3, null=True, blank=True)
    fcy_cr = models.DecimalField(max_digits=22, decimal_places=3, null=True, blank=True)
    lcy_dr = models.DecimalField(max_digits=22, decimal_places=3, null=True, blank=True)
    lcy_cr = models.DecimalField(max_digits=22, decimal_places=3, null=True, blank=True)
    Dr_cr = models.CharField(max_length=1)
    Account = models.ForeignKey(MTTB_GLSub,null=True,blank=True,on_delete=models.CASCADE)
    Account_no = models.CharField(max_length=30, null=True, blank=True)
    Ac_relatives = models.CharField(max_length=50, null=True, blank=True)
    Txn_code = models.ForeignKey(MTTB_TRN_Code,null=True,blank=True,on_delete=models.CASCADE)
    Value_date = models.DateTimeField(auto_now=False,null=True , blank=True)
    Exch_rate = models.DecimalField(max_digits=24, decimal_places=12, null=True, blank=True)
    fin_cycle = models.ForeignKey(MTTB_Fin_Cycle,null=True,blank=True,on_delete=models.CASCADE)
    Period_code = models.ForeignKey(MTTB_Per_Code,null=True,blank=True,on_delete=models.CASCADE)
    Addl_text = models.CharField(max_length=255, null=True, blank=True)
    Addl_sub_text = models.CharField(max_length=255, null=True, blank=True)
    Maker_Id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='created_JRNL_LOG_HIST')
    Maker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Checker_Id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='checked_JRNL_LOG_HIST')
    Checker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Auth_Status = models.CharField(max_length=1, null=True, blank=True, default='U')
    class Meta:
        verbose_name_plural = 'JRNL_LOG_HIST'

class ACTB_DAIRY_LOG_HISTORY(models.Model):
    ac_entry_sr_no = models.AutoField(primary_key=True)
    module = models.ForeignKey(STTB_ModulesInfo,null=True,blank=True,on_delete=models.CASCADE)
    trn_ref_no = models.ForeignKey(DETB_JRNL_LOG,null=True,blank=True,on_delete=models.CASCADE)
    event_sr_no = models.BigIntegerField(default=0, null=True, blank=True)
    event = models.CharField(max_length=4, null=True, blank=True)
    ac_no = models.ForeignKey(MTTB_GLSub,null=True,blank=True,on_delete=models.CASCADE)
    ac_relative = models.CharField(max_length=50, null=True, blank=True)
    ac_ccy = models.ForeignKey(MTTB_Ccy_DEFN,null=True,blank=True,on_delete=models.CASCADE)
    drcr_ind = models.CharField(max_length=1)
    trn_code = models.ForeignKey(MTTB_TRN_Code,null=True,blank=True,on_delete=models.CASCADE)
    fcy_amount = models.DecimalField(max_digits=22, decimal_places=3, null=True, blank=True)
    exch_rate = models.DecimalField(max_digits=24, decimal_places=1, null=True, blank=True)
    lcy_amount = models.DecimalField(max_digits=22, decimal_places=3, null=True, blank=True)
    fcy_dr = models.DecimalField(max_digits=22, decimal_places=3, null=True, blank=True)
    fcy_cr = models.DecimalField(max_digits=22, decimal_places=3, null=True, blank=True)
    lcy_dr = models.DecimalField(max_digits=22, decimal_places=3, null=True, blank=True)
    lcy_cr = models.DecimalField(max_digits=22, decimal_places=3, null=True, blank=True)
    external_ref_no = models.CharField(max_length=16, null=True, blank=True)
    addl_text = models.CharField(max_length=255, null=True, blank=True)
    trn_dt = models.DateField(null=True, blank=True)
    type = models.ForeignKey(MTTB_GLMaster,null=True,blank=True,on_delete=models.CASCADE)
    category = models.CharField(max_length=1, null=True, blank=True)
    value_dt = models.DateField(null=True, blank=True)
    financial_cycle = models.ForeignKey(MTTB_Fin_Cycle,null=True,blank=True,on_delete=models.CASCADE)
    period_code = models.ForeignKey(MTTB_Per_Code,null=True,blank=True,on_delete=models.CASCADE)
    user_id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='created_DAILY_LOG_HISTORY')
    Maker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    auth_id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='checker_DAILY_LOG_HISTORY')
    Checker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Auth_Status = models.CharField(max_length=1, null=True, blank=True, default='U')
    product = models.CharField(max_length=4, null=True, blank=True)
    entry_seq_no = models.IntegerField(null=True, blank=True)
    delete_stat = models.CharField(max_length=1, null=True, blank=True)

    class Meta:
        verbose_name_plural = 'DAILY_LOG_HISTORY'

class MTTB_EOC_MAINTAIN(models.Model):
    eoc_id = models.AutoField(primary_key=True)
    module_id = models.CharField(max_length=2)         
    function_id = models.CharField(max_length=8)      
    eoc_seq_no = models.IntegerField(default=0)                
    eoc_type = models.CharField(max_length=3)          
    record_stat = models.CharField(max_length=1, default='C')  
    mod_no = models.IntegerField(null=True, blank=True)    
    Maker_Id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='created_EOC_MAINTAIN')
    Maker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Checker_Id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='checked_EOC_MAINTAIN')
    Checker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Auth_Status = models.CharField(max_length=1, null=True, blank=True, default='U')
    Once_Auth = models.CharField(max_length=1,null=True,blank=True, default='N')      

    class Meta:
        verbose_name_plural = 'EOC_MAINTAIN'

class STTB_EOC_STATUS(models.Model):
    eoc_stt_id = models.AutoField(primary_key=True)
    eoc_seq_no = models.IntegerField(null=True, blank=True)        
    module_id = models.CharField(max_length=2)                   
    function_id = models.CharField(max_length=8)                   
    eoc_type = models.CharField(max_length=3)                     
    eod_date = models.DateTimeField(auto_now=False, null=True, blank=True)         
    eoc_status = models.CharField(max_length=1)                   
    error = models.CharField(max_length=550, null=True, blank=True)       

    class Meta:
        verbose_name_plural = 'EOC_STATUS'

class STTB_EOC_DAILY_LOG(models.Model):
    ac_entry_sr_no = models.AutoField(primary_key=True)
    module = models.CharField(max_length=2)
    trn_ref_no = models.CharField(max_length=15)
    event_sr_no = models.IntegerField(null=True, blank=True)
    event = models.CharField(max_length=4, null=True, blank=True)
    ac_no = models.CharField(max_length=20)
    ac_ccy = models.CharField(max_length=3)
    drcr_ind = models.CharField(max_length=1)
    trn_code = models.CharField(max_length=3)
    fcy_amount = models.DecimalField(max_digits=22, decimal_places=3, null=True, blank=True)
    exch_rate = models.DecimalField(max_digits=24, decimal_places=1, null=True, blank=True)
    lcy_amount = models.DecimalField(max_digits=22, decimal_places=3, null=True, blank=True)
    external_ref_no = models.CharField(max_length=16, null=True, blank=True)
    addl_text = models.CharField(max_length=255, null=True, blank=True)
    trn_dt = models.DateField(null=True, blank=True)
    type = models.CharField(max_length=1, null=True, blank=True)
    category = models.CharField(max_length=1, null=True, blank=True)
    value_dt = models.DateField(null=True, blank=True)
    financial_cycle = models.CharField(max_length=9)
    period_code = models.CharField(max_length=3)
    user_id = models.CharField(max_length=12, null=True, blank=True)
    Maker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    auth_id = models.CharField(max_length=12, null=True, blank=True)
    Checker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Auth_Status = models.CharField(max_length=1, null=True, blank=True, default='U')
    product = models.CharField(max_length=4, null=True, blank=True)
    entry_seq_no = models.IntegerField(null=True, blank=True)       

    class Meta:
        verbose_name_plural = 'EOC_DAILY_LOG'

class STTB_GL_BAL(models.Model):
    gl_bal_id = models.AutoField(primary_key=True)
    gl_code = models.ForeignKey(MTTB_GLMaster,null=True,blank=True,on_delete=models.CASCADE)
    CCy_Code = models.ForeignKey(MTTB_Ccy_DEFN,null=True,blank=True,on_delete=models.CASCADE)
    fin_year = models.ForeignKey(MTTB_Fin_Cycle,null=True,blank=True,on_delete=models.CASCADE)
    period_code = models.ForeignKey(MTTB_Per_Code,null=True,blank=True,on_delete=models.CASCADE)
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
    gl_sub_bal_id = models.AutoField(primary_key=True)
    gl_sub = models.ForeignKey(MTTB_GLSub,null=True,blank=True,on_delete=models.CASCADE)
    CCy_Code = models.ForeignKey(MTTB_Ccy_DEFN,null=True,blank=True,on_delete=models.CASCADE)
    fin_year = models.ForeignKey(MTTB_Fin_Cycle,null=True,blank=True,on_delete=models.CASCADE)
    period_code = models.ForeignKey(MTTB_Per_Code,null=True,blank=True,on_delete=models.CASCADE)
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

class Balancesheet_acc(models.Model):
    no = models.AutoField(primary_key=True)
    report_number = models.CharField(max_length=50, null=True, blank=True)
    description = models.CharField(max_length=2500, null=True, blank=True)
    formula = models.TextField(null=True, blank=True)
    Pvalue = models.TextField(null=True, blank=True)
    Mvalue = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name_plural = 'balancesheet_acc'

class Balancesheet_mfi(models.Model):
    no = models.AutoField(primary_key=True)
    report_number = models.CharField(max_length=50, null=True, blank=True)
    description = models.CharField(max_length=2500, null=True, blank=True)
    formula = models.TextField(null=True, blank=True)
    Pvalue = models.TextField(null=True, blank=True)
    Mvalue = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name_plural = 'balancesheet_mfi'

class Incomestatement_acc(models.Model):
    no = models.AutoField(primary_key=True)
    report_number = models.CharField(max_length=50, null=True, blank=True)
    description = models.CharField(max_length=2500, null=True, blank=True)
    formula = models.TextField(null=True, blank=True)
    Pvalue = models.TextField(null=True, blank=True)
    Mvalue = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name_plural = 'incomestatement_acc'

class Incomestatement_mfi(models.Model):
    no = models.AutoField(primary_key=True)
    report_number = models.CharField(max_length=50, null=True, blank=True)
    description = models.CharField(max_length=2500, null=True, blank=True)
    formula = models.TextField(null=True, blank=True)
    Pvalue = models.TextField(null=True, blank=True)
    Mvalue = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name_plural = 'incomestatement_mfi'

class MonthlyReport(models.Model): 
    ID = models.AutoField(primary_key=True)
    gl_code = models.ForeignKey(MTTB_GLMaster,null=True,blank=True,on_delete=models.CASCADE)
    Desc = models.TextField(null=True, blank=True)
    CCy_Code = models.ForeignKey(MTTB_Ccy_DEFN,null=True,blank=True,on_delete=models.CASCADE)
    fin_year = models.ForeignKey(MTTB_Fin_Cycle,null=True,blank=True,on_delete=models.CASCADE)
    period_code = models.ForeignKey(MTTB_Per_Code,null=True,blank=True,on_delete=models.CASCADE)
    category = models.CharField(max_length=1, null=True, blank=True)
    OP_DR = models.DecimalField(max_digits=25, decimal_places=2, null=True, blank=True)
    OP_CR = models.DecimalField(max_digits=25, decimal_places=2, null=True, blank=True)
    Mo_DR = models.DecimalField(max_digits=25, decimal_places=2, null=True, blank=True)
    Mo_CR = models.DecimalField(max_digits=25, decimal_places=2, null=True, blank=True)
    Cl_DR = models.DecimalField(max_digits=25, decimal_places=2, null=True, blank=True)
    Cl_CR = models.DecimalField(max_digits=25, decimal_places=2, null=True, blank=True)
    OP_DR_lcy = models.DecimalField(max_digits=25, decimal_places=2, null=True, blank=True)
    OP_CR_lcy = models.DecimalField(max_digits=25, decimal_places=2, null=True, blank=True)
    Mo_DR_lcy = models.DecimalField(max_digits=25, decimal_places=2, null=True, blank=True)
    Mo_CR_lcy = models.DecimalField(max_digits=25, decimal_places=2, null=True, blank=True)
    Cl_DR_lcy = models.DecimalField(max_digits=25, decimal_places=2, null=True, blank=True)
    Cl_CR_lcy = models.DecimalField(max_digits=25, decimal_places=2, null=True, blank=True)
    InsertDate = models.DateTimeField(auto_now_add=True,null=True, blank=True)
    UpdateDate = models.DateTimeField(auto_now=True,null=True, blank=True)
    UserID = models.IntegerField(null=True, blank=True)
    MSegment = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        verbose_name_plural = 'MonthlyReport'  

class MTTB_ProvinceInfo(models.Model):
    pro_sys_id = models.AutoField(primary_key=True)
    pro_id = models.CharField(max_length=10,null=True, blank=True)
    pro_code = models.CharField(max_length=50,null=True, blank=True)
    pro_name_e = models.CharField(max_length=50,null=True, blank=True)
    pro_name_l = models.CharField(max_length=50,null=True, blank=True)
    date_insert = models.DateTimeField(auto_now_add=True,null=True, blank=True)
    date_update = models.DateTimeField(auto_now=True,null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Provinceinfo' 

class MTTB_DistrictInfo(models.Model):
    dis_sys_id = models.AutoField(primary_key=True)
    pro_id = models.CharField(max_length=10,null=True, blank=True) 
    dis_id = models.CharField(max_length=50,null=True, blank=True)
    dis_code = models.CharField(max_length=50,null=True, blank=True)
    dis_name_e = models.CharField(max_length=50,null=True, blank=True)
    dis_name_l = models.CharField(max_length=50,null=True, blank=True)
    user_id = models.CharField(max_length=50, null=True, blank=True)
    date_insert = models.DateTimeField(auto_now_add=True,null=True, blank=True)
    date_update = models.DateTimeField(auto_now=True,null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Districtinfo' 

class MTTB_VillageInfo(models.Model):
    vil_sys_id = models.AutoField(primary_key=True)
    pro_id = models.CharField(max_length=10,null=True, blank=True)
    dis_id = models.CharField(max_length=50,null=True, blank=True)
    vil_id = models.CharField(max_length=50,null=True, blank=True)
    vil_code = models.CharField(max_length=50,null=True, blank=True)
    vil_name_e = models.CharField(max_length=50,null=True, blank=True)
    vil_name_l = models.CharField(max_length=50,null=True, blank=True)
    user_id = models.CharField(max_length=50, null=True, blank=True)
    date_insert = models.DateTimeField(auto_now_add=True,null=True, blank=True)
    date_update = models.DateTimeField(auto_now=True,null=True, blank=True)
    vbol_code = models.CharField(max_length=50,null=True, blank=True)
    vbol_name = models.TextField(null=True, blank=True) 

    class Meta:
        verbose_name_plural = 'Villageinfo' 

class FA_asset_type(models.Model):
    id = models.AutoField(primary_key=True)
    IS_TANGIBLE_CHOICES = (
        ('Y', 'Yes'),
        ('N', 'No'),
    )
    is_tangible = models.CharField(max_length=1, choices=IS_TANGIBLE_CHOICES,null=True, blank=True)
    type_code = models.CharField(max_length=50, unique=True,null=True, blank=True)
    type_name_la = models.CharField(max_length=255, null=True, blank=True)
    type_name_en = models.CharField(max_length=255, null=True, blank=True)
    create_by = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='created_assest_type')
    create_datetime = models.DateTimeField(auto_now=False, null=True, blank=True)
    update_by = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='update_assest_type')
    update_datetime = models.DateTimeField(auto_now=False, null=True, blank=True)

    class Meta:
        verbose_name_plural = 'AssestType'
