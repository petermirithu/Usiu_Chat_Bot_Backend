import ast
import hashlib
import bcrypt
import jwt
from django.conf import settings

# Password Section
def hash_password(password):    
    salt = bcrypt.gensalt(rounds=9)            
    sha_password=hashlib.sha256(password.encode(settings.ENCODE_ALGORITHM)).digest()    
    hashed = bcrypt.hashpw(sha_password,salt)        
    return hashed

def check_password(password,hashed):     
    sha_password=hashlib.sha256(password.encode(settings.ENCODE_ALGORITHM)).digest()    
    if bcrypt.checkpw(sha_password, ast.literal_eval(hashed)):        
        return True
    else:        
        return False  

# Token Section
def encode_value(payload):    
    encoded = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)    
    return encoded

def decode_value(encoded):    
    decoded = jwt.decode(encoded, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])                                         
    return decoded