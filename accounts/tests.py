from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from accounts.models import CustomUser, CodeVerify, VIA_EMAIL,VIA_PHONE, NEW

# Create your tests here.

class RegistrationTest(APITestCase):
    
    def setUp(self):
        self.signup_url = reverse('signup')
        self.email_data = {
            "email_phone_number": "testuser@gmail.com"
        }
        self.phone_data = {
            "email_phone_number": "+998901234567"
        }
        
    def test_signup_email(self):
        response = self.client.post(self.signup_url, self.email_data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['user_auth_type'], VIA_EMAIL)
        user = CustomUser.objects.get(email="testuser@gmail.com")
        self.assertEqual(user.user_status, NEW)
        self.assertTrue(CodeVerify.objects.filter(user=user).exists())
        
    def test_signup_phone(self):
        response = self.client.post(self.signup_url, self.phone_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user_auth_type'], VIA_PHONE)
        user = CustomUser.objects.get(phone_number="+998901234567")
        self.assertIsNotNone(user)
        
    def test_signup_existing_user(self):
        self.client.post(self.signup_url, self.email_data)
        response = self.client.post(self.signup_url, self.email_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.status_code, 400)

    def test_signup_invalid_input(self):
        invalid_data = {"email_phone_number": "not-an-email-or-phone"}
        response = self.client.post(self.signup_url, invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_verify_code_unauthenticated(self):
        verify_url = '/accounts/verify/' 
        response = self.client.post(verify_url, {"code": "1234"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)