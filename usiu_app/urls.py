from django.urls import path
from .views import *

urlpatterns = [                
  path('register_user', register_user, name='register_user'),    
  path('login_user', login_user, name='login_user'),      
  path('resend_verification_code', resend_verification_code, name='resend_verification_code'),      
  path('verify_verification_code', verify_verification_code, name='verify_verification_code'),        
  path('send_question', send_question, name='send_question'),        
]