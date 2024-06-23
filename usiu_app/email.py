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

def send_user_feedback_message(first_name, last_name, feedback, recipient_email ):
    try:        
        message1 = f"Greetings {first_name},\n\nWe wanted to personally express our gratitude for taking the time to provide feedback on our app. Your input is valuable to us as it helps us improve and enhance the user experience.\n\nIf you encounter any further issues or have additional feedback to share, please don't hesitate to reach out. Your continued support and engagement are vital to our success, and we're always here to listen and assist.\n\nWith kind regards,\nYour USIU Chat Bot Team."
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [recipient_email, ]
        # Send to user feedback
        send_mail('Thank you for the Feedback', message1, email_from, recipient_list )
        # Send to developer 
        message2 = f"Greetings,\n\n{first_name} who is a user of the USIU Chat Bot App has sent you some feedback. Please find more details below:-\n\nFrom: {first_name} {last_name}\nEmail: {recipient_email}\nMessage: {feedback}\n\nWith kind regards,\nYour USIU Chat Bot Team."
        send_mail('You have a new Feedback from: '+first_name, message2, email_from, ["nickydanic852@gmail.com", ])
        return "done"
    except:
        return "error"      
