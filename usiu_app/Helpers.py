from .models import *
import random
from django.conf import settings

def check_if_email_taken(email):
    try:
        found = Users.objects.get(email=email)
        return True
    except Users.DoesNotExist:
        return False    

def generate_verification_code():
    try:          
        numbers = list("123456789")
        length = 6
        random.shuffle(numbers)
        password = []
        for i in range(length):
            password.append(random.choice(numbers))
        
        random.shuffle(password)
        return "".join(password) 
    except:
        return "error"