from django.shortcuts import render
from .serializers import SignUpSerializer
from rest_framework.generics import CreateAPIView
from .models import CustomUser
from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework.exceptions import ValidationError
# Create your views here.``


class SignUpView(CreateAPIView):
    serializer_class = SignUpSerializer
    queryset = CustomUser.objects.all()
    

class Verifyview(APIView):
    permission_classes = [permissions.IsAuthenticated,]
    
    def post(self, request):
        code = request.data.get('code', None)
        if code is None:
            data= {
                'success':False,
                'message':'Kod yubormadingiz'
            }
            raise ValidationError(data)
        
        