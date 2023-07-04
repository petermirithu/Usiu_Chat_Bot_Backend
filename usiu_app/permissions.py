
from django.conf import settings
from rest_framework import permissions
from rest_framework import exceptions
import traceback

class isAuthorized(permissions.BasePermission):

    def has_permission(self, request, view):                      
        try:                        
            token = request.headers["Authorization"].replace("Bearer ", "")                                                                                       
            try:                                               
                return True
            except:                                      
                raise exceptions.AuthenticationFailed()            
        except:                        
            raise exceptions.NotAuthenticated()                       