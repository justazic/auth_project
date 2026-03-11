from rest_framework import serializers
from .models import CODE_VERIFY, CodeVerify, CustomUser, DONE, VIA_EMAIL, VIA_PHONE
from rest_framework.exceptions import ValidationError
from baseapp.utility import check_email_or_phone
from django.core.mail import send_mail
from conf import settings
from django.db.models import Q

class SignUpSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only = True, required=False)
    user_auth_type = serializers.CharField(read_only= True, required=False)
    user_status = serializers.CharField(read_only= True, required=False)

    def __init__(self, *args, **kwargs):
        super(SignUpSerializer, self).__init__(*args, **kwargs)
        self.fields['email_phone_number'] = serializers.CharField(required=True, write_only=True)
    
    class Meta:
        model = CustomUser
        fields = ['id', 'user_auth_type', 'user_status']
    
    def validate(self, data):
        data = self.auth_validate(data)
        return data 
        
        
        
    def create(self, validated_data):
        user = super(SignUpSerializer, self).create(validated_data)
        code = user.create_verify_code(user.user_auth_type)
        
        if user.user_auth_type == VIA_EMAIL:
            send_mail(
                "Tasdiqlash kodi",
                f"Sizning kodingiz: {code}",
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
        elif user.user_auth_type == VIA_PHONE:
            print(f"TEL: {user.phone_number} | KOD: {code}")

        return user
    
        
    @staticmethod
    def auth_validate(data):
        user_input = data.get('email_phone_number')
        check_user = check_email_or_phone(user_input)
        print(check_user, '-----------------------------------------')
        if check_user == 'email':
            data = {
                'email': user_input,
                'user_auth_type': VIA_EMAIL
            }
        elif check_user == 'phone':
            data = {
                'phone_number': user_input,
                'user_auth_type': VIA_PHONE
            }
        else:
            data= {
                'success': False,
                'message': "Email yoki telefon kiritishingiz kerak"
            }
            raise ValidationError(data)
        return data
    
    def validate_email_phone_number(self, data):
        user_input = data
        
        if user_input is None:
            data= {
                'success': False,
                'message': "Email yoki telefon kiritishingiz kerak"
            }
            raise ValidationError(data)
        user  = CustomUser.objects.filter(Q(phone_number = user_input) | Q(email = user_input)).exists()
        
        if user:
            data= {
                'success': False,
                'message': "Email yoki telefon bizda mavjud"
            }
            raise ValidationError(data)
        return data
        
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.update(instance.token())
        return data
    