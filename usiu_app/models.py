from mongoengine import *
import datetime

# Create your models here.
class Users(Document):     
    first_name=StringField(required=True)
    last_name=StringField(required=True)
    email=StringField(required=True)
    password=StringField(required=True)    
    verified = BooleanField(default=False)
    auth_token=StringField()
    created_at=DateTimeField(required=True)
    updated_at=DateTimeField(default=datetime.datetime.utcnow)

class VerificationCodes(Document):
    user_id = ReferenceField(Users, reverse_delete_rule=CASCADE)
    code = StringField(required=True)    
    used = BooleanField(default=False)
    created_at = DateTimeField(required=True)

class Sessions(Document):  
    user_id = ReferenceField(Users, reverse_delete_rule=CASCADE)      
    created_at = DateTimeField(required=True)        
    date_modified = DateTimeField(default=datetime.datetime.utcnow)

class Messages(Document):  
    session_id = ReferenceField(Sessions, reverse_delete_rule=CASCADE)  
    human = StringField(required=True)            
    ai = StringField(required=True)                        
    created_at = DateTimeField(required=True)        
    date_modified = DateTimeField(default=datetime.datetime.utcnow)