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

