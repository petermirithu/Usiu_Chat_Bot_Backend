from rest_framework_mongoengine import serializers
from usiu_app.models import *

class UsersSerializer(serializers.DocumentSerializer):
    class Meta:
        model=Users
        exclude=("password",)

class SessionsSerializer(serializers.DocumentSerializer):
    class Meta:
        model = Sessions  
        fields="__all__"   

class MessagesSerializer(serializers.DocumentSerializer):
    class Meta:
        model = Messages  
        fields="__all__" 