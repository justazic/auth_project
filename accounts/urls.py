from django.urls import path
from .views import SignUpView, Verifyview

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('verify/', Verifyview.as_view(), name='verify'),
]