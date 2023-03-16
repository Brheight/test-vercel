from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from .models import Room

class RoomSerializer(ModelSerializer):
    class Meta:
        model = Room
        fields = ('id', 'code', 'host', 'guest_can_pause' , 'votes_to_skip', 'created_at' )
class CreateRoomSerializer(ModelSerializer):
    class Meta:
        model = Room
        fields = ('id','guest_can_pause', 'votes_to_skip' )
        
class UpdateRoomSerializer(ModelSerializer):
    code = serializers.CharField(validators = [])
    
    class Meta:
        model = Room
        fields = ('id','guest_can_pause', 'votes_to_skip', 'code' )