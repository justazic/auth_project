from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from baseapp.models import BaseModel
from datetime import datetime, timedelta
from conf.settings import EMAIL_EXPIRATION_TIME, PHONE_EXPIRATION_TIME
import random
import uuid
from rest_framework_simplejwt.tokens import RefreshToken
# Create your models here.


ORDINARY_USER, ADMIN, MANAGER = ('ordinary_user','admin', 'manager')
NEW, CODE_VERIFY, DONE, PHOTO_DONE = ('new', 'code_verify', 'done', 'photo_done')
VIA_EMAIL, VIA_PHONE = ('via_email', 'via_phone')


class CustomUser(AbstractUser, BaseModel):
    USER_ROLES = (
        (ORDINARY_USER, ORDINARY_USER),
        (ADMIN, ADMIN),
        (MANAGER, MANAGER)        
    )
    USER_STATUS = (
        (NEW, NEW),
        (CODE_VERIFY, CODE_VERIFY),
        (DONE, DONE),
        (PHOTO_DONE, PHOTO_DONE),
    )
    USER_AUTH_TYPE = (
        (VIA_EMAIL, VIA_EMAIL),
        (VIA_PHONE, VIA_PHONE),
    )
    
    user_role = models.CharField(max_length=20, choices=USER_ROLES, default=ORDINARY_USER)
    user_auth_type = models.CharField(max_length=20, choices=USER_AUTH_TYPE)
    user_status = models.CharField(max_length=20, choices=USER_STATUS, default=NEW)
    email = models.EmailField(blank=True, null=True, unique=True)
    phone_number = models.CharField(max_length=13, blank=True, null=True, unique=True)
    photo = models.ImageField(upload_to='users/', validators=[FileExtensionValidator(allowed_extensions=['png', 'jpg', 'heic'])])

    def __str__(self):
        return self.username
    
    def create_verify_code(self, verify_type):
        code = "".join([str(random.randint(0, 9)) for _ in range(4)])
        
        CodeVerify.objects.create(
            user=self,
            verify_type=verify_type,
            code=code
        )
        return code
    
    
    def create_code(self, verify_type):
        code = ''.join([str(random.randint(1000))[-1] for _ in range(4)])
        
        CodeVerify.objects.create(
            user=self,
            verify_type=verify_type,
            code=code
        )
        return code
    
    def check_username(self):
        if not self.username:
            temp_username = 'username' + uuid.uuid4().__str__().split('-')[-1]
            while CustomUser.objects.filter(username=temp_username).exists():
                temp_username = temp_username + str(random.randint(10))
            self.username = temp_username         
            
    def check_email(self):
        if self.email:
            self.email = self.email.lower()    
        
    def check_pass(self):
        if not self.password:
            temp_pass = 'password' + uuid.uuid4().__str__().split('-')[-1]
            self.password = temp_pass
            
    def hash_pass(self):
        if not self.password.startswith("pbkdf2_sha256"):
            self.set_password(self.password)
    
    def token(self):
        refresh = RefreshToken.for_user(self)
        data = {
            'refresh' : str(refresh),
            'access': str(refresh.access_token)
        }
        return data
    
    def clean(self):
        self.check_email()
        self.check_username()
        self.check_pass()
        self.hash_pass()
    
    def save(self, *args, **kwargs):
        
        self.clean()
        super(CustomUser, self).save(*args, **kwargs)
        
    
class CodeVerify(BaseModel):
    VERIFY_TYPE = (
        (VIA_EMAIL, VIA_EMAIL),
        (VIA_PHONE, VIA_PHONE),
    )
    code = models.CharField(max_length=4, blank=True, null=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='codes')
    verify_type = models.CharField(max_length=20, choices=VERIFY_TYPE)
    is_active = models.BooleanField(default=False)
    expiration_time = models.DateTimeField()
    
    def __str__(self):
        return f"{self.user.username} | {self.code}"
    
    def save(self, *args, **kwargs):
        if self.verify_type == VIA_EMAIL:
            self.expiration_time = datetime.now() + timedelta(minutes=EMAIL_EXPIRATION_TIME)
        else:
            self.expiration_time = datetime.now() + timedelta(minutes=PHONE_EXPIRATION_TIME)
        super().save(*args, **kwargs)