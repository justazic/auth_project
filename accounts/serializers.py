from rest_framework import serializers
from .models import CODE_VERIFY, CodeVerify, CustomUser, DONE, VIA_EMAIL, VIA_PHONE
from rest_framework.exceptions import ValidationError
from baseapp.utility import check_email_or_phone
from django.core.mail import send_mail
from conf import settings

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
        user_input = data.get('email_phone_number')
        check_user = check_email_or_phone(user_input)
        
        if check_user == 'email':
            if CustomUser.objects.filter(email=user_input).exists():
                raise ValidationError({
                    "success": False,
                    "message": "Bu email royxatdan otilgan!"
                })
            data.update({
                'email': user_input,
                'user_auth_type': VIA_EMAIL
            })
            
        elif check_user == 'phone':
            if CustomUser.objects.filter(phone_number=user_input).exists():
                raise ValidationError({
                    "success": False,
                    "message": "Bu telefon raqami royxatdan otilgan!"
                })
            data.update({
                'phone_number': user_input,
                'user_auth_type': VIA_PHONE
            })
            
        return data
        
    def create(self, validated_data):
        validated_data.pop('email_phone_number', None)
        
        if 'email' in validated_data:
            validated_data['username'] = validated_data['email']
        elif 'phone_number' in validated_data:
            validated_data['username'] = validated_data['phone_number']
            validated_data['email'] = None 

        user = CustomUser.objects.create_user(**validated_data)
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