from django.conf import settings
from django.core.mail import send_mail

def send_welcome_message_with_code(first_name, verification_code, recipient_email ):
    try:
        subject = 'Welcome to the USIU Chat Bot'
        message = f'Greetings {first_name},\n\nWelcome to the USIU Chat Bot which is an AI assistant.\n\nYour verification code is:- {verification_code}.\n\nIn case of any inquiries, please do let us know anytime by replying to this email.\n\nWith kind regards,\nYour USIU Chat Bot Team.'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [recipient_email, ]
        send_mail( subject, message, email_from, recipient_list )
        return "done"
    except:
        return "error"

def send_reset_verification_code(first_name, verification_code, recipient_email ):
    try:
        subject = 'Password Reset Verification Code'
        message = f'Greetings {first_name},\n\nWe noticed that you wanted to reset your password.\n\nYour verification code is:- {verification_code}.\n\nIn case your not the one who triggered this email please change your password ASAP or if you have any inquiries, please do let us know anytime by replying to this email.\n\nWith kind regards,\nYour USIU Chat Bot Team.'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [recipient_email, ]
        send_mail( subject, message, email_from, recipient_list )
        return "done"
    except:
        return "error"    
