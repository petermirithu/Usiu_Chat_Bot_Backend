from .models import *
import random
import traceback
from datetime import datetime,timedelta

def check_if_email_taken(email):
    try:
        found = Users.objects.get(email=email)
        return True
    except Users.DoesNotExist:
        return False    

def generate_verification_code(user_id):
    try:          
        numbers = list("123456789")
        length = 6
        random.shuffle(numbers)
        list_of_numbers = []
        for i in range(length):
            list_of_numbers.append(random.choice(numbers))
        
        random.shuffle(list_of_numbers)
        code = "".join(list_of_numbers)             

        verification_obj = VerificationCodes(
            user_id=user_id,
            code=code,                                        
            created_at=datetime.now()
        )
        verification_obj.save()  

        return code
    except:
        # Unmuted to see full error !!!!!!!!!
        print("**********************************************************")
        print(traceback.format_exc())           
        print("**********************************************************")     
        return "error"

def verify_verification_code(user_id, code):
    try:                 
        verification_code=VerificationCodes.objects.get(user_id=user_id, code=code)
        time_now = datetime.now()        
        code_expires_at = verification_code.created_at + timedelta(hours=1)                

        if time_now < code_expires_at:
            VerificationCodes.objects.filter(user_id=user_id, code=code).update(used=True)                        
            return "code okay"                                
        else:
            return "code expired"                                
    except VerificationCodes.DoesNotExist:
        return "code invalid"