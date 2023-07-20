from django.urls import path
from .views import *

urlpatterns = [                
  path('register_user', register_user, name='register_user'),    
  path('login_user', login_user, name='login_user'),      
  path('update_user', update_user, name='update_user'),      
  path('change_user_password', change_user_password, name='change_user_password'),      
  path('resend_verification_code', resend_verification_code, name='resend_verification_code'),      
  path('verify_verification_code', verify_verification_code, name='verify_verification_code'),        
  path('send_question', send_question, name='send_question'),        
  path('fetch_conversations/<str:user_id>', fetch_conversations, name='fetch_conversations'),      
  path('delete_conversation/<str:session_id>', delete_conversation, name='delete_conversation'),        
  path('fetch_conversation_history/<str:session_id>/<int:from_index>/<int:to_index>', fetch_conversation_history, name='fetch_conversation_history'),        
]