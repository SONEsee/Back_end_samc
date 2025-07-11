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
    # sub_menu_id = models.ForeignKey('MTTB_SUB_MENU', null=True, blank=True, on_delete=models.CASCADE)
    description_la = models.CharField(max_length=200)
    description_en = models.CharField(max_length=200, null=True, blank=True)
    # all_link = models.CharField(max_length=200, null=True, blank=True)
    eod_function = models.CharField(max_length=1, null=True, blank=True, default='N')
    function_order = models.IntegerField(null=True, blank=True)
    Record_Status = models.CharField(max_length=1, null=True, blank=True, default='Y')
    Maker_Id = models.ForeignKey(
        'MTTB_Users', null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='created_functions'
    )
    Maker_DT_Stamp = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    Checker_Id = models.ForeignKey(
        'MTTB_Users', null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='checked_functions'
    )
    Checker_DT_Stamp = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['function_id']
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


# class MTTB_Users(models.Model):
#     STATUS_CHOICES = [
#         ('E', 'Enabled'),
#         ('D', 'Disabled'),
#     ]

#     user_id = models.CharField(primary_key=True, max_length=20)
#     div_id = models.ForeignKey(
#         'MTTB_Divisions', null=True, blank=True, on_delete=models.CASCADE
#     )
#     Role_ID = models.ForeignKey(
#         'MTTB_Role_Master', null=True, blank=True, on_delete=models.CASCADE
#     )
#     user_name = models.CharField(max_length=250, unique=True)
#     user_password = models.CharField(max_length=250)
#     user_email = models.CharField(max_length=250, null=True, blank=True)
#     user_mobile = models.CharField(max_length=15, null=True, blank=True)

#     # New field to upload a profile picture
#     profile_picture = models.ImageField(
#         upload_to='profile_pictures/', null=True, blank=True
#     )

#     User_Status = models.CharField(
#         max_length=1,
#         choices=STATUS_CHOICES,
#         default='E',
#     )

#     pwd_changed_on = models.DateField(null=True, blank=True)
#     InsertDate = models.DateTimeField(auto_now_add=True)
#     UpdateDate = models.DateTimeField(auto_now=True)
#     Maker_Id = models.ForeignKey(
#         'self', null=True, blank=True,
#         on_delete=models.CASCADE,
#         related_name='created_userss'
#     )
#     Maker_DT_Stamp = models.DateTimeField(auto_now_add=True, null=True, blank=True)
#     Checker_Id = models.ForeignKey(
#         'self', null=True, blank=True,
#         on_delete=models.CASCADE,
#         related_name='checked_userss'
#     )
#     Checker_DT_Stamp = models.DateTimeField(null=True, blank=True)
#     Auth_Status = models.CharField(max_length=1, null=True, blank=True, default='U')
#     Once_Auth = models.CharField(max_length=1, null=True, blank=True, default='N')

#     class Meta:
#         verbose_name_plural = 'UsersRgith'
#         db_table = 'SAMCSYS_mttb_users'

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


from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models

class MTTB_UserManager(BaseUserManager):
    def create_user(self, user_id, user_name, password=None, **extra_fields):
        if not user_id:
            raise ValueError('The User ID must be set')
        user = self.model(user_id=user_id, user_name=user_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, user_id, user_name, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(user_id, user_name, password, **extra_fields)

class MTTB_Users(AbstractBaseUser, PermissionsMixin):
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

    USERNAME_FIELD = 'user_name'
    REQUIRED_FIELDS = ['user_id']
    objects = MTTB_UserManager()
    class Meta:
        verbose_name_plural = 'UsersRgith'
        db_table = 'SAMCSYS_mttb_users'

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

# class MTTB_USER_ACCESS_LOG(models.Model):
#     log_id = models.AutoField(primary_key=True)  
#     user_id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE)   
#     login_datetime = models.DateTimeField(auto_now_add=True, null=True, blank=True)
#     logout_datetime = models.DateTimeField(null=True, blank=True)
#     session_id = models.CharField(max_length=100, null=True, blank=True)
#     ip_address = models.CharField(max_length=45,null=True, blank=True)
#     user_agent = models.CharField(max_length=255, null=True, blank=True)
#     login_status = models.CharField(max_length=1)
#     logout_type = models.CharField(max_length=1, null=True, blank=True)
#     remarks = models.CharField(max_length=255, null=True, blank=True)

#     class Meta:
#         verbose_name_plural='USER_ACCESS_LOG'
class MTTB_USER_ACCESS_LOG(models.Model):
    # Your existing fields...
    log_id = models.AutoField(primary_key=True)  
    user_id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE)   
    login_datetime = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    logout_datetime = models.DateTimeField(null=True, blank=True)
    session_id = models.CharField(max_length=100, null=True, blank=True)
    ip_address = models.CharField(max_length=45,null=True, blank=True)
    user_agent = models.CharField(max_length=255, null=True, blank=True)
    login_status = models.CharField(
        max_length=1,
        choices=[
            ('S', 'Success'),
            ('F', 'Failed'),
            ('A', 'Admin Action'),
        ]
    )
    logout_type = models.CharField(
        max_length=1, 
        null=True, 
        blank=True,
        choices=[
            ('U', 'User Initiated'),
            ('F', 'Force Logout'),
            ('T', 'Timeout'),
            ('S', 'System'),
        ]
    )
    remarks = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name_plural='USER_ACCESS_LOG'
        db_table = 'mttb_user_access_log'
        indexes = [
            models.Index(fields=['user_id', 'logout_datetime']),
            models.Index(fields=['session_id']),
            models.Index(fields=['login_datetime']),
        ]

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
    prev_Working_Day = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    next_working_Day = models.DateTimeField(auto_now_add=False, null=True, blank=True)
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
    Record_Status = models.CharField(max_length=1,null=True,blank=True, default='C')
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
    Record_Status = models.CharField(max_length=1, null=True, blank=True, default='C')
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
    mod_no = models.IntegerField(null=True, blank=True)
    outstanding = models.CharField(max_length=20,null=True,blank=True)
    post_side = models.CharField(max_length=20,null=True,blank=True)
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
    Reference_No = models.CharField(max_length=30, null=True, blank=True)
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
    Reference_sub_No = models.CharField(max_length=35, null=True, blank=True)
    comments = models.CharField(max_length=1000, null=True, blank=True)
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
    trn_ref_sub_no = models.CharField(max_length=35, null=True, blank=True)
    event_sr_no = models.BigIntegerField(default=0, null=True, blank=True)
    event = models.CharField(max_length=4, null=True, blank=True)
    ac_no = models.ForeignKey(MTTB_GLSub,null=True,blank=True,on_delete=models.CASCADE)
    ac_no_full = models.CharField(max_length=40, null=True, blank=True)
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
    external_ref_no = models.CharField(max_length=30, null=True, blank=True)
    addl_text = models.CharField(max_length=255, null=True, blank=True)
    addl_sub_text = models.CharField(max_length=255, null=True, blank=True)
    trn_dt = models.DateField(null=True, blank=True)
    glid = models.ForeignKey(MTTB_GLMaster,null=True,blank=True,on_delete=models.CASCADE)
    glType = models.CharField(max_length=1, null=True, blank=True)
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
    Reference_No = models.CharField(max_length=30, null=True, blank=True)
    Reference_sub_No = models.CharField(max_length=35, null=True, blank=True)
    comments = models.CharField(max_length=255, null=True, blank=True)
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
    trn_ref_sub_no = models.CharField(max_length=35, null=True, blank=True)
    event_sr_no = models.BigIntegerField(default=0, null=True, blank=True)
    event = models.CharField(max_length=4, null=True, blank=True)
    ac_no = models.ForeignKey(MTTB_GLSub,null=True,blank=True,on_delete=models.CASCADE)
    ac_no_full = models.CharField(max_length=40, null=True, blank=True)
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
    external_ref_no = models.CharField(max_length=30, null=True, blank=True)
    addl_text = models.CharField(max_length=255, null=True, blank=True)
    addl_sub_text = models.CharField(max_length=255, null=True, blank=True)
    trn_dt = models.DateField(null=True, blank=True)
    glid = models.ForeignKey(MTTB_GLMaster,null=True,blank=True,on_delete=models.CASCADE)
    glType = models.CharField(max_length=1, null=True, blank=True)
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
    module_id = models.ForeignKey('STTB_ModulesInfo', null=True, blank=True, on_delete=models.CASCADE)
    function_id = models.ForeignKey('MTTB_Function_Desc', null=True, blank=True, on_delete=models.CASCADE)
    eoc_seq_no = models.IntegerField(default=0)                
    eoc_type = models.CharField(max_length=3)          
    Record_Status = models.CharField(max_length=1, default='C')  
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
    # module_id = models.ForeignKey('STTB_ModulesInfo', null=True, blank=True, on_delete=models.CASCADE)
    # function_id = models.ForeignKey('MTTB_Function_Desc', null=True, blank=True, on_delete=models.CASCADE)
    eoc_id = models.ForeignKey(MTTB_EOC_MAINTAIN, null=True, blank=True, on_delete=models.CASCADE)
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
    trn_ref_sub_no = models.CharField(max_length=35, null=True, blank=True)
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
    addl_sub_text = models.CharField(max_length=255, null=True, blank=True)
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
    UserID = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='created_monthlyreport')
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

class FA_Asset_Type(models.Model):
    type_id = models.AutoField(primary_key=True)
    is_tangible = models.CharField(max_length=1, null=True, blank=True, default='N')
    type_code = models.CharField(max_length=10,null=True, blank=True, unique=True)
    type_name_la = models.CharField(max_length=100, null=True, blank=True)
    type_name_en = models.CharField(max_length=100, null=True, blank=True)
    Record_Status = models.CharField(max_length=1,null=True,blank=True, default='C')
    Maker_Id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='created_asset_type')
    Maker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Checker_Id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='checked_asset_type')
    Checker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)

    class Meta:
        verbose_name_plural = 'AssestType'

class FA_Chart_Of_Asset(models.Model):
    coa_id = models.AutoField(primary_key=True)
    asset_code = models.CharField(max_length=50,null=True, blank=True, unique=True)
    asset_name_la = models.CharField(max_length=255, null=True, blank=True)
    asset_name_en = models.CharField(max_length=255, null=True, blank=True)
    asset_type_id = models.ForeignKey(FA_Asset_Type, null=True, blank=True, on_delete=models.CASCADE)
    Record_Status = models.CharField(max_length=1,null=True,blank=True, default='C')
    Maker_Id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='created_chart_of_asset')
    Maker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Checker_Id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='checked_chart_of_asset')
    Checker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)

    class Meta:
        verbose_name_plural = 'ChartOfAsset'

class FA_Suppliers(models.Model):
    supplier_id = models.AutoField(primary_key=True)
    supplier_code = models.CharField(max_length=20,null=True, blank=True, unique=True)
    supplier_name = models.CharField(max_length=100, null=True, blank=True)
    contact_person = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    email = models.CharField(max_length=100, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    tax_id = models.CharField(max_length=20, null=True, blank=True)
    bank_account = models.CharField(max_length=50, null=True, blank=True)
    bank_name = models.CharField(max_length=100, null=True, blank=True)
    supplier_type = models.CharField(max_length=50, null=True, blank=True) 
    credit_limit = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)  
    payment_terms = models.CharField(max_length=100, null=True, blank=True) 
    Record_Status = models.CharField(max_length=1,null=True,blank=True, default='C')
    Maker_Id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='created_asset_suppliers')
    Maker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Checker_Id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='checked_asset_suppliers')
    Checker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)

    class Meta:
        verbose_name_plural = 'AssetSuppliers'

class FA_Location(models.Model):
    location_id = models.AutoField(primary_key=True)
    location_code = models.CharField(max_length=20,null=True, blank=True, unique=True)
    location_name_la = models.CharField(max_length=255, null=True, blank=True)
    location_name_en = models.CharField(max_length=255, null=True, blank=True)
    parent_location_id = models.IntegerField(null=True, blank=True) 
    location_type = models.CharField(max_length=50, null=True, blank=True)  
    phone = models.CharField(max_length=20, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    responsible_person = models.CharField(max_length=100, null=True, blank=True)  
    remarks = models.TextField(null=True, blank=True)  
    Record_Status = models.CharField(max_length=1,null=True,blank=True, default='C')
    Maker_Id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='created_asset_locations')
    Maker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Checker_Id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='checked_asset_locations')
    Checker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)

    class Meta:
        verbose_name_plural = 'AssetLocations'

class FA_Expense_Category (models.Model):
    ec_id = models.AutoField(primary_key=True)
    category_code = models.CharField(max_length=20,null=True, blank=True, unique=True)
    category_name_la = models.CharField(max_length=255, null=True, blank=True)
    category_name_en = models.CharField(max_length=255, null=True, blank=True)
    is_capitalized_default = models.CharField(max_length=1, null=True, blank=True, default='N') 
    default_gl_account = models.CharField(max_length=50, null=True, blank=True)  
    required_approval = models.CharField(max_length=1, null=True, blank=True, default='Y')  
    approval_limit = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True) 
    Record_Status = models.CharField(max_length=1,null=True,blank=True, default='C')
    Maker_Id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='created_expense_category')
    Maker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Checker_Id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='checked_expense_category')
    Checker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)

    class Meta:
        verbose_name_plural = 'ExpenseCategory'

# class FA_Asset_List(models.Model):
#     asset_list_id = models.AutoField(primary_key=True)
#     asset_list_code = models.CharField(max_length=20, null=True, blank=True, unique=True)
#     asset_type_id = models.ForeignKey(FA_Chart_Of_Asset, null=True, blank=True, on_delete=models.CASCADE)
#     asset_serial_no = models.CharField(max_length=50, null=True, blank=True, unique=True)
#     asset_tag = models.CharField(max_length=50, null=True, blank=True, unique=True)
#     asset_location_id = models.ForeignKey(FA_Location, null=True, blank=True, on_delete=models.CASCADE)
#     asset_spec = models.TextField(null=True, blank=True)
#     asset_date = models.DateField(null=True, blank=True)
#     asset_currency = models.CharField(max_length=5, null=True, blank=True)
#     asset_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
#     asset_status  = models.CharField(max_length=20, null=True, blank=True, default='ACTIVE')  
#     warranty_end_date = models.DateField(null=True, blank=True)
#     supplier_id = models.ForeignKey(FA_Suppliers, null=True, blank=True, on_delete=models.CASCADE)
#     has_depreciation = models.CharField(max_length=1, null=True, blank=True, default='Y')  # Y or N
#     dpca_type = models.CharField(max_length=20, null=True, blank=True)
#     dpca_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  
#     asset_useful_life = models.IntegerField(null=True, blank=True)  
#     asset_salvage_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True) 
#     dpca_start_date = models.DateField(null=True, blank=True)  
#     dpca_end_date = models.DateField(null=True, blank=True) 
#     asset_accu_dpca_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)  
#     asset_value_remain = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)  
#     asset_latest_date_dpca = models.DateField(null=True, blank=True)  
#     asset_disposal_date = models.DateField(null=True, blank=True)  
#     asset_ac_yesno = models.CharField(max_length=1, null=True, blank=True, default='N')  
#     asset_ac_date = models.DateField(null=True, blank=True) 
#     asset_ac_datetime = models.DateTimeField(auto_now=False, null=True, blank=True)  
#     aaset_ac_by = models.IntegerField(null=True, blank=True)
#     Record_Status = models.CharField(max_length=1,null=True,blank=True, default='C')
#     Maker_Id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='created_asset_list')
#     Maker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
#     Checker_Id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='checked_asset_list')
#     Checker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)

#     class Meta:
#         verbose_name_plural = 'AssestList'

class FA_Asset_Lists(models.Model):
    asset_list_id = models.CharField(primary_key=True, max_length=30)
    asset_list_code = models.CharField(max_length=20, null=True, blank=True, unique=True)
    asset_type_id = models.ForeignKey(FA_Chart_Of_Asset, null=True, blank=True, on_delete=models.CASCADE)
    asset_serial_no = models.CharField(max_length=50, null=True, blank=True, unique=True)
    asset_tag = models.CharField(max_length=50, null=True, blank=True, unique=True)
    asset_location_id = models.ForeignKey(FA_Location, null=True, blank=True, on_delete=models.CASCADE)
    asset_spec = models.TextField(null=True, blank=True)
    asset_date = models.DateField(null=True, blank=True)
    asset_currency = models.CharField(max_length=5, null=True, blank=True)
    asset_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    asset_status  = models.CharField(max_length=20, null=True, blank=True, default='UC')  
    warranty_end_date = models.DateField(null=True, blank=True)
    supplier_id = models.ForeignKey(FA_Suppliers, null=True, blank=True, on_delete=models.CASCADE)
    has_depreciation = models.CharField(max_length=1, null=True, blank=True, default='Y')  # Y or N
    dpca_type = models.CharField(max_length=20, null=True, blank=True)
    dpca_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  
    asset_useful_life = models.IntegerField(null=True, blank=True)  
    asset_salvage_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True) 
    dpca_start_date = models.DateField(null=True, blank=True)  
    dpca_end_date = models.DateField(null=True, blank=True) 
    accu_dpca_value_total = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    asset_accu_dpca_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)  
    asset_value_remain = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)  
    asset_value_remainMonth = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    asset_value_remainBegin = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    asset_value_remainLast = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    acc_no = models.CharField(max_length=30, null=True, blank=True)
    type_of_pay = models.CharField(max_length=30, null=True, blank=True)
    asset_latest_date_dpca = models.DateField(null=True, blank=True)  
    asset_disposal_date = models.DateField(null=True, blank=True)  
    asset_ac_yesno = models.CharField(max_length=1, null=True, blank=True, default='N')  
    asset_ac_date = models.DateField(null=True, blank=True) 
    asset_ac_datetime = models.DateTimeField(auto_now=False, null=True, blank=True)  
    asset_ac_by = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='ac_asset_lists')
    Record_Status = models.CharField(max_length=1,null=True,blank=True, default='C')
    Maker_Id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='created_asset_lists')
    Maker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Checker_Id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='checked_asset_lists')
    Checker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Auth_Status = models.CharField(max_length=1, null=True, blank=True, default='U')
    Auth_Status_ARC = models.CharField(max_length=1, null=True, blank=True, default='U')

    class Meta:
        verbose_name_plural = 'AssestLists'

class FA_Depreciation_Main (models.Model):
    dm_id = models.AutoField(primary_key=True)
    asset_id = models.ForeignKey(FA_Asset_Lists, null=True, blank=True, on_delete=models.CASCADE)
    dpca_type = models.CharField(max_length=20, null=True, blank=True) 
    dpca_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  
    dpca_useful_life = models.IntegerField(null=True, blank=True)  
    start_date = models.DateField(null=True, blank=True)  
    end_date = models.DateField(null=True, blank=True)  
    Record_Status = models.CharField(max_length=1,null=True,blank=True, default='C')
    Maker_Id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='created_depreciation_main')
    Maker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Checker_Id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='checked_depreciation_main')
    Checker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)

    class Meta:
        verbose_name_plural = 'DepreciationMain'

class FA_Depreciation_Sub (models.Model):
    ds_id = models.AutoField(primary_key=True)
    m_id = models.ForeignKey(FA_Depreciation_Main, null=True, blank=True, on_delete=models.CASCADE)
    round_no = models.IntegerField(null=True, blank=True) 
    dpca_date = models.DateField(null=True, blank=True) 
    dpca_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)  
    dpca_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True) 
    dpca_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True) 
    dpca_per_month = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)  
    dpca_yesno = models.CharField(max_length=1, null=True, blank=True, default='N')  
    period_year = models.CharField(max_length=4, null=True, blank=True) 
    period_month = models.CharField(max_length=7, null=True, blank=True)  
    Record_Status = models.CharField(max_length=1,null=True,blank=True, default='C')
    Maker_Id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='created_depreciation_sub')
    Maker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Checker_Id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='checked_depreciation_sub')
    Checker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    approve_by = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='approve_depreciation_sub')
    approve_datetime = models.DateTimeField(auto_now=False, null=True, blank=True) 

    class Meta:
        verbose_name_plural = 'DepreciationSub'

class FA_Asset_List_Depreciation (models.Model):
    ald_id = models.AutoField(primary_key=True)
    asset_list_id = models.ForeignKey(FA_Asset_Lists, null=True, blank=True, on_delete=models.CASCADE)
    dpca_date = models.DateField(null=True, blank=True)  
    dpca_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True) 
    dpca_no_of_days = models.IntegerField(null=True, blank=True) 
    remaining_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    accumulated_dpca = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True) 
    dpca_desc = models.CharField(max_length=255, null=True, blank=True) 
    dpca_ac_yesno = models.CharField(max_length=1, null=True, blank=True, default='N')  
    dpca_date = models.DateField(null=True, blank=True)  
    dpca_datetime = models.DateTimeField(auto_now=False, null=True, blank=True)  
    dpca_ac_by = models.IntegerField(null=True, blank=True) 
    Record_Status = models.CharField(max_length=1,null=True,blank=True, default='C')
    Maker_Id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='created_asset_list_depreciation')
    Maker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Checker_Id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='checked_asset_list_depreciation')
    Checker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)

    class Meta:
        verbose_name_plural = 'AssestListDepreciation'

class FA_Asset_List_Disposal(models.Model):
    alds_id = models.AutoField(primary_key=True)
    asset_list_id = models.ForeignKey(FA_Asset_Lists, null=True, blank=True, on_delete=models.CASCADE)
    disposal_date = models.DateField(null=True, blank=True)  
    disposal_type = models.CharField(max_length=20, null=True, blank=True)  
    disposal_by = models.IntegerField(null=True, blank=True) 
    disposal_purpose = models.CharField(max_length=255, null=True, blank=True)  
    disposal_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    disposal_proceeds = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True) 
    disposal_cost = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)  
    gain_loss = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True) 
    buyer_name = models.CharField(max_length=100, null=True, blank=True)  
    disposal_reason = models.CharField(max_length=255, null=True, blank=True)  
    disposal_ac_yesno = models.CharField(max_length=1, null=True, blank=True, default='N') 
    disposal_ac_date = models.DateField(null=True, blank=True)  
    disposal_ac_datetime = models.DateTimeField(auto_now=False, null=True, blank=True) 
    disposal_ac_by = models.IntegerField(null=True, blank=True)   
    Record_Status = models.CharField(max_length=1,null=True,blank=True, default='C')
    Maker_Id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='created_asset_list_disposal')
    Maker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Checker_Id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='checked_asset_list_disposal')
    Checker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)

    class Meta:
        verbose_name_plural = 'AssestListDisposal'

class FA_Asset_Expense(models.Model):
    ae_id = models.AutoField(primary_key=True)
    asset_list_id = models.ForeignKey(FA_Asset_Lists, null=True, blank=True, on_delete=models.CASCADE)
    expense_type = models.CharField(max_length=50, null=True, blank=True)  
    expense_date = models.DateField(null=True, blank=True)  
    expense_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True) 
    currency_code = models.CharField(max_length=5, null=True, blank=True)  
    exchange_rate = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)  
    expense_amount_base = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True) 
    vendore_id = models.ForeignKey(FA_Suppliers, null=True, blank=True, on_delete=models.CASCADE)  
    invoice_no = models.CharField(max_length=50, null=True, blank=True) 
    invoice_date = models.DateField(null=True, blank=True)  
    expense_description = models.TextField(null=True, blank=True)  
    is_capitalized = models.CharField(max_length=1, null=True, blank=True, default='N')  
    warranty_coverd = models.CharField(max_length=1, null=True, blank=True, default='N')  
    downtime_hours = models.IntegerField(null=True, blank=True)  
    expense_status = models.CharField(max_length=20, null=True, blank=True, default='PENDING')  
    approved_by = models.IntegerField(null=True, blank=True) 
    approved_date = models.DateField(null=True, blank=True)  
    payment_date = models.DateField(null=True, blank=True) 
    is_posted = models.CharField(max_length=1, null=True, blank=True, default='N')  
    posted_by = models.IntegerField(null=True, blank=True)  
    posted_date = models.DateField(null=True, blank=True)  
    journal_entry_id = models.IntegerField(null=True, blank=True)  
    notes = models.TextField(null=True, blank=True)  
    Record_Status = models.CharField(max_length=1,null=True,blank=True, default='C')
    Maker_Id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='created_asset_expense')
    Maker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Checker_Id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='checked_asset_expense')
    Checker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)

    class Meta:
        verbose_name_plural = 'AssestExpense'

class FA_Transfer_Logs(models.Model):
    transfer_id = models.AutoField(primary_key=True)
    asset_list_id = models.ForeignKey(FA_Asset_Lists, null=True, blank=True, on_delete=models.CASCADE)
    transfer_date = models.DateField(null=True, blank=True)
    from_location_id = models.ForeignKey(FA_Location, null=True, blank=True, related_name='transfer_from_location', on_delete=models.CASCADE)
    to_location_id = models.ForeignKey(FA_Location, null=True, blank=True, related_name='transfer_to_location', on_delete=models.CASCADE)
    transfer_reason = models.TextField(null=True, blank=True)
    transfer_cost = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True) 
    condition_before = models.TextField(null=True, blank=True)  
    condition_after = models.TextField(null=True, blank=True)  
    transport_method = models.CharField(max_length=100, null=True, blank=True) 
    requested_by = models.IntegerField(null=True, blank=True)
    approved_by = models.IntegerField(null=True, blank=True)  
    received_by = models.IntegerField(null=True, blank=True)  
    handover_date = models.DateField(null=True, blank=True)  
    received_date = models.DateField(null=True, blank=True) 
    status = models.CharField(max_length=50, null=True, blank=True) 
    insurance_covered = models.CharField(max_length=1, null=True, blank=True, default='N')  
    estimated_arrival = models.DateField(null=True, blank=True)  
    actual_arrival = models.DateField(null=True, blank=True)  
    notes = models.TextField(null=True, blank=True)  
    Record_Status = models.CharField(max_length=1,null=True,blank=True, default='C')
    Maker_Id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='created_transfer_logs')
    Maker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Checker_Id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='checked_transfer_logs')
    Checker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)

    class Meta:
        verbose_name_plural = 'TransferLogs'

class FA_Asset_Photos(models.Model):
    ap_id = models.AutoField(primary_key=True)
    asset_list_id = models.ForeignKey(FA_Asset_Lists, null=True, blank=True, on_delete=models.CASCADE)
    photo_type = models.CharField(max_length=50, null=True, blank=True)  
    file_name = models.CharField(max_length=255, null=True, blank=True)  
    file_path = models.TextField(null=True, blank=True)  
    file_size = models.IntegerField(null=True, blank=True) 
    mime_type = models.CharField(max_length=100, null=True, blank=True) 
    description = models.TextField(null=True, blank=True)  
    taken_date = models.DateField(null=True, blank=True) 
    taken_by = models.IntegerField(null=True, blank=True)  
    is_primary = models.CharField(max_length=1, null=True, blank=True, default='N')  
    display_order = models.IntegerField(null=True, blank=True)   
    Record_Status = models.CharField(max_length=1,null=True,blank=True, default='C')
    Maker_Id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='created_asset_photos')
    Maker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Checker_Id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='checked_asset_photos')
    Checker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)

    class Meta:
        verbose_name_plural = 'AssetPhotos'


class FA_Maintenance_Logs(models.Model):
    maintenance_id = models.AutoField(primary_key=True)
    asset_list_id = models.ForeignKey(FA_Asset_Lists, null=True, blank=True, on_delete=models.CASCADE)
    maintenance_date = models.DateField(null=True, blank=True)
    maintenance_type = models.CharField(max_length=20, null=True, blank=True) 
    description = models.TextField(null=True, blank=True)
    cost = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    currency_id = models.CharField(max_length=5, null=True, blank=True, default='LAK')  
    technician = models.CharField(max_length=100, null=True, blank=True)  
    supplier_id = models.ForeignKey(FA_Suppliers, null=True, blank=True, on_delete=models.CASCADE)  
    next_maintenance_date = models.DateField(null=True, blank=True,  default='MEDIUM')  
    downtime_hours = models.IntegerField(null=True, blank=True) 
    severity_level = models.CharField(max_length=20, null=True, blank=True) 
    warranty_claim = models.CharField(max_length=1, null=True, blank=True, default='N')  
    status = models.CharField(max_length=50, null=True, blank=True, default='SCHEDULED') 
    completed_by = models.IntegerField(null=True, blank=True)  
    completed_date = models.DateField(null=True, blank=True)  
    notes = models.TextField(null=True, blank=True) 
    Record_Status = models.CharField(max_length=1,null=True,blank=True, default='C')
    Maker_Id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='created_maintenance_logs')
    Maker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Checker_Id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='checked_maintenance_logs')
    Checker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)

    class Meta:
        verbose_name_plural = 'MaintenanceLogs'

class FA_Accounting_Method(models.Model):
    mapping_id = models.AutoField(primary_key=True)
    ref_id = models.CharField(max_length=20, null=True, blank=True)  
    acc_type = models.CharField(max_length=50, null=True, blank=True)  
    asset_list_id = models.ForeignKey(FA_Asset_Lists, null=True, blank=True, on_delete=models.CASCADE)  
    debit_account_id = models.CharField(max_length=50, null=True, blank=True) 
    credit_account_id = models.CharField(max_length=50, null=True, blank=True) 
    amount_start = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)  
    amount_end = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)  
    transaction_date = models.DateField(null=True, blank=True)  
    description = models.TextField(null=True, blank=True)    
    Record_Status = models.CharField(max_length=1,null=True,blank=True, default='C')
    Maker_Id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='created_accounting_method')
    Maker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)
    Checker_Id = models.ForeignKey(MTTB_Users, null=True, blank=True, on_delete=models.CASCADE, related_name='checked_accounting_method')
    Checker_DT_Stamp = models.DateTimeField(auto_now=False, null=True, blank=True)

    class Meta:
        verbose_name_plural = 'AccountingMethod'


class MTTB_REVOKED_SESSIONS(models.Model):
    """Track revoked JWT sessions for force logout functionality"""
    id = models.AutoField(primary_key=True)
    jti = models.CharField(max_length=255, unique=True, db_index=True)
    user_id = models.ForeignKey(MTTB_Users, on_delete=models.CASCADE)
    revoked_at = models.DateTimeField(auto_now_add=True)
    revoked_by = models.ForeignKey(
        MTTB_Users, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='revoked_sessions'
    )
    reason = models.CharField(max_length=255, null=True, blank=True)
    ip_address = models.CharField(max_length=45, null=True, blank=True)
    class Meta:
        db_table = 'mttb_revoked_sessions'
        verbose_name_plural = 'Revoked Sessions'
        indexes = [
            models.Index(fields=['jti']),
            models.Index(fields=['user_id']),
            models.Index(fields=['revoked_at']),
        ]

class MasterType(models.Model):
    M_id = models.AutoField(primary_key=True)
    M_code = models.CharField(max_length=50, null=True, blank=True) 
    M_name_la = models.CharField(max_length=255, null=True, blank=True) 
    M_name_en = models.CharField(max_length=255, null=True, blank=True) 
    M_detail = models.TextField(null=True, blank=True)
    Status = models.CharField(max_length=20, null=True, blank=True)
    class Meta:
        verbose_name_plural = 'MasterType'

class MasterCode(models.Model):
    MC_id = models.AutoField(primary_key=True)
    M_id = models.ForeignKey(MasterType, null=True, blank=True, on_delete=models.CASCADE) 
    MC_code = models.CharField(max_length=50, null=True, blank=True) 
    MC_name_la = models.CharField(max_length=255, null=True, blank=True) 
    MC_name_en = models.CharField(max_length=255, null=True, blank=True) 
    MC_detail = models.TextField(null=True, blank=True)
    Status = models.CharField(max_length=20, null=True, blank=True)
    BOL_code = models.CharField(max_length=50, null=True, blank=True)
    BOL_name = models.CharField(max_length=255, null=True, blank=True)
    class Meta:
        verbose_name_plural = 'MasterCode'