
from datetime import datetime,timedelta
import uuid
import json
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes

from usiu_app.Helpers import check_if_email_taken, generate_verification_code
from usiu_app.email import send_verification_code
from usiu_app.enc_decryption import check_password, encode_value, hash_password
from usiu_app.langchain_model import process_user_input
from usiu_app.models import Messages, Users, VerificationCodes, Sessions
from usiu_app.multi_threading import start_save_message_thread
from usiu_app.serializers import MessagesSerializer, SessionsSerializer, UsersSerializer
from .permissions import isAuthorized
from django.utils.timezone import now as getTimeNow
import traceback

# **************************************** Scripts ****************************************
# Users.objects.filter().delete()
# VerificationCodes.objects.filter().delete()

# Messages.objects.filter().delete()
# Sessions.objects.filter().delete()

@api_view(['POST'])
@permission_classes([])
def register_user(request):
    data = json.loads(request.body)
    try:             
        first_name = data['firstName']                  
        last_name = data['lastName']
        email = data['email']
        password = data['password'] 
                 
        taken=check_if_email_taken(email)
        if taken==True:            
            return Response('Email is already taken', status=status.HTTP_423_LOCKED)
        else:                                
            hashed_password = hash_password(password)                
            new_user = Users(
                        first_name=first_name,
                        last_name=last_name,
                        email=email,
                        password=str(hashed_password),                            
                        created_at=getTimeNow()
                        )
            new_user.save()

            verification_code = generate_verification_code()            
            verification_obj = VerificationCodes(
                user_id=new_user.id,
                code=verification_code,                                        
                created_at=datetime.now()
            )
            verification_obj.save()  

            send_code_results = send_verification_code(first_name, verification_code, email)
            send_code_results=""
            if send_code_results=="error":
                return Response("Error while sending your a verification code", status=status.HTTP_400_BAD_REQUEST)
            else:
                serialised_user = UsersSerializer(new_user, many=False)                                        
                return Response(serialised_user.data, status=status.HTTP_201_CREATED)
    except:    
        # Unmuted to see full error !!!!!!!!!
        print("**********************************************************")
        print(traceback.format_exc())           
        print("**********************************************************")     
        return Response("Error occured while creating an account", status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def resend_verification_code(request):
    data = json.loads(request.body)
    try:                 
        VerificationCodes.objects.get(user_id=data["userId"])
        verification_code = generate_verification_code()            
        VerificationCodes.objects.filter(user_id=data["userId"]).update(
            code=verification_code,            
            created_at=datetime.now()
        )
        user = Users.objects.get(id=data["userId"])               
        send_code_results = send_verification_code(user.first_name, verification_code, user.email)
        send_code_results=""
        if send_code_results=="error":
            return Response("Error while sending you a verification code", status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response("Verification code sent successfully", status=status.HTTP_201_CREATED)
    except:
        print("**********************************************************")
        print(traceback.format_exc())           
        print("**********************************************************")     
        return Response("Error while resending the verification code", status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
def update_user(request):
    data = json.loads(request.body)
    try:         
        Users.objects.filter(id=data["userId"]).update(first_name=data["firstName"],last_name=data["lastName"],email=data["email"])
        return Response("Successfully updated your profile", status=status.HTTP_200_OK)                        
    except:
        print("**********************************************************")
        print(traceback.format_exc())           
        print("**********************************************************")     
        return Response("Error while updating your user profile", status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['PUT'])
def change_user_password(request):
    data = json.loads(request.body)
    try:         
        user=Users.objects.get(id=data["userId"])
        if(check_password(data["oldPassword"], user.password) == True):                    
            hashed_password = hash_password(data["newPassword"])                            
            Users.objects.filter(id=data["userId"]).update(password=str(hashed_password))
            return Response("Successfully updated your password", status=status.HTTP_200_OK)                        
        else:
            return Response("invalidPassword", status=status.HTTP_400_BAD_REQUEST)                        
    except:
        print("**********************************************************")
        print(traceback.format_exc())           
        print("**********************************************************")     
        return Response("Error while updating your user profile", status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def verify_verification_code(request):
    data = json.loads(request.body)
    try:                 
        verification_code=VerificationCodes.objects.get(user_id=data["userId"], code=data["code"])
        time_now = datetime.now()        
        code_expires_at = verification_code.created_at + timedelta(hours=1)                

        if time_now < code_expires_at:
            VerificationCodes.objects.filter(user_id=data["userId"], code=data["code"]).update(used=True)
            Users.objects.filter(id=data["userId"]).update(verified=True)
            
            user = Users.objects.get(id=data["userId"])
            serialised_user = UsersSerializer(user, many=False)                                  
            
            now = getTimeNow()                   
            payload = {'id': serialised_user.data["id"],'loggedinAt': now.strftime("%m/%d/%Y, %H:%M:%S")}                    
            
            user.auth_token=encode_value(payload)                          
            serialised_user = UsersSerializer(user, many=False)                                                
            return Response(serialised_user.data, status=status.HTTP_200_OK)            
        else:                    
            return Response("Session expired", status=status.HTTP_400_BAD_REQUEST)        
    except VerificationCodes.DoesNotExist:
        return Response("Invalid verification code", status=status.HTTP_400_BAD_REQUEST)
    except:
        print("**********************************************************")
        print(traceback.format_exc())           
        print("**********************************************************")     
        return Response("Error while verifying the verification code", status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
def login_user(request):
    data = json.loads(request.body)
    try:
        email = data['email']
        password = data['password']                
        try:
            user = Users.objects.get(email=email)               
            if(check_password(password, user.password) == True):                    
                now = getTimeNow()   
                serialised_user = UsersSerializer(user, many=False)                                                                 
                payload = {'id': serialised_user.data["id"],'loggedinAt': now.strftime("%m/%d/%Y, %H:%M:%S")}                    
                user.auth_token=encode_value(payload)                                                             
                serialised_user = UsersSerializer(user, many=False)                                        
                return Response(serialised_user.data, status=status.HTTP_200_OK)
            else:
                return Response("invalidCredentials", status=status.HTTP_400_BAD_REQUEST)                                        
        except Users.DoesNotExist:            
            return Response("invalidCredentials", status=status.HTTP_400_BAD_REQUEST)                                                    
    except:
        # Unmuted to see full error !!!!!!!!!
        print("**********************************************************")
        print(traceback.format_exc())           
        print("**********************************************************")     
        return Response("An error occured while authenticating you", status=status.HTTP_400_BAD_REQUEST)                    
    
@api_view(['POST'])
@permission_classes([isAuthorized])
def send_question(request):    
    try:        
        user_id = request.data.get("userId")                                
        session_id = request.data.get("sessionId")  
        question = request.data.get("question")                                                                                
                                 
        if isinstance(question, str)==False or len(question) == 0:
            return Response("Seems like you sent an empty message :(", status=status.HTTP_200_OK)            
        else:
            bot_response=process_user_input(question, session_id, user_id)                         

            response={                            
                "_id": uuid.uuid4(),
                "text": bot_response["answer"],
                "sessionId": bot_response["session_id"]                                                        
            } 

            payload={
                "session_id": bot_response["session_id"],
                "user_id":user_id,
                "human":question,
                "ai":bot_response["answer"]                
            }
            
            if "experiencing technical difficulties" not in bot_response["answer"]:
                start_save_message_thread(payload)            

            return Response(response, status=status.HTTP_200_OK)
    except:
        # Unmuted to see full error !!!!!!!!!
        print("**********************************************************")
        print(traceback.format_exc())           
        print("**********************************************************")    
        return Response("An error occured while sending your question", status=status.HTTP_400_BAD_REQUEST)    

@api_view(['GET'])
@permission_classes([isAuthorized])
def fetch_conversations(request, user_id):    
    try:                     
        sessions = Sessions.objects.filter(user_id=user_id).order_by("-date_modified")
        serialised_sessions = SessionsSerializer(sessions, many=True)        
        results = []
        for session in serialised_sessions.data:                                    
            messages = Messages.objects.filter(session_id=session["id"])                           
            if len(messages)==0:
                Sessions.objects.filter(id=session["id"]).delete()
            else:                
                session["title"] = messages[0]["ai"]                                                        
                results.append(session)
        return Response(results, status=status.HTTP_200_OK)           
    except:
        # Unmuted to see full error !!!!!!!!!
        print("**********************************************************")
        print(traceback.format_exc())           
        print("**********************************************************")  
        return Response("An error occured while fetching your conversations", status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([isAuthorized])
def delete_conversation(request, session_id):    
    try:                     
        Sessions.objects.filter(id=session_id).delete()
        return Response("Successfully deleted the conversation", status=status.HTTP_200_OK)           
    except:
        # Unmuted to see full error !!!!!!!!!
        print("**********************************************************")
        print(traceback.format_exc())           
        print("**********************************************************")  
        return Response("An error occured while deleting your conversation", status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
@permission_classes([isAuthorized])
def fetch_conversation_history(request, session_id, from_index, to_index):    
    results={
        "chatPagination":{
            "fromIndex":to_index,
            "toIndex":to_index+10
        },
        "showLoadEarlier":False,
        "messages":[],
    }

    try:                                     
        session = Sessions.objects.get(id=session_id)
        serialised_session = SessionsSerializer(session, many=False)                                                    
        messages = Messages.objects.filter(session_id=session_id).order_by('-created_at')                
        
        remaining_messages_count = len(messages) - results["chatPagination"]["toIndex"]        
        if remaining_messages_count > 0:
            results["showLoadEarlier"]=True        
        else:
            results["showLoadEarlier"]=False
            results["chatPagination"]["fromIndex"]=0
            results["chatPagination"]["toIndex"]=10

        paginated_messages = messages[from_index:to_index]
        serialised_messages = MessagesSerializer(paginated_messages, many=True)                                    
        
        for message in serialised_messages.data:
            human_message={                 
                "_id": uuid.uuid4(),
                "text": message["human"],
                "sessionId": message["session_id"],                 
                "createdAt": message["created_at"],
                "user":{
                    "_id": serialised_session.data["user_id"]                                  
                }
            }              
            ai_message={     
                "_id": uuid.uuid4(),
                "text": message["ai"],
                "sessionId": message["session_id"],                 
                "createdAt": message["created_at"],
                "user":{
                    "_id": "sAIdi",
                    "name": 'sAIdi',                
                }               
            } 
            results["messages"].append(ai_message)                         
            results["messages"].append(human_message)                                   
        return Response(results, status=status.HTTP_200_OK)           
    except Sessions.DoesNotExist:
        return Response(results, status=status.HTTP_200_OK) 
    except:
        # Unmuted to see full error !!!!!!!!!
        print("**********************************************************")
        print(traceback.format_exc())           
        print("**********************************************************")      
        return Response("An error occured while fetching your conversation history", status=status.HTTP_400_BAD_REQUEST)