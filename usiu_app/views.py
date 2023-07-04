
from datetime import datetime
import uuid
import json
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from .permissions import isAuthorized

@api_view(['POST'])
@permission_classes([isAuthorized])
def register_user(request):
    data = json.loads(request.body)
    try:                        
        return Response("Account Created successfully", status=status.HTTP_201_CREATED)
    except:    
        # Unmuted to see full error !!!!!!!!!
        # print("**********************************************************")
        # print(traceback.format_exc())           
        # print("**********************************************************")     
        return Response("Error while creating an account", status=status.HTTP_400_BAD_REQUEST)
