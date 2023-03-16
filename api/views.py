from django.shortcuts import render
from rest_framework import generics, status
from .serializer import RoomSerializer, CreateRoomSerializer, UpdateRoomSerializer
from .models import Room
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import JsonResponse
import logging    # first of all import the module
logging.basicConfig(filename="std.log",
format='%(asctime)s %(message)s',
filemode='w')

#Let us Create an object
logger=logging.getLogger()

#Now we are going to Set the threshold of logger to DEBUG
logger.setLevel(logging.DEBUG)
logger.info('why')
# Create your views here.

from datetime import datetime

class Comment:
    def __init__(self, email, content, created=None):
        self.email = email
        self.content = content
        self.created = created or datetime.now()

comment = Comment(email='leila@example.com', content='foo bar')

from rest_framework import serializers

class CommentSerializer(serializers.Serializer):
    email = serializers.EmailField()
    content = serializers.CharField(max_length=200)
    created = serializers.DateTimeField()
    
    
serializer = CommentSerializer(comment)
serializer.data

from rest_framework.renderers import JSONRenderer

json = JSONRenderer().render(serializer.data)


import io
from rest_framework.parsers import JSONParser

stream = io.BytesIO(json)
data = JSONParser().parse(stream)


serializer = CommentSerializer(data=data)
serializer.is_valid()
# True
serializer.validated_data


class RoomView(generics.ListAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer

def index(response):
    return render(response, 'api/index.html', {})
    
    
    
class GetRoom(APIView):
    serializer_class = RoomSerializer
    lookup_url_kwarg = 'code'
    
    def get(self, request, format = None):
        code = request.GET.get(self.lookup_url_kwarg)
        if code != None:
            room = Room.objects.filter(code = code)
            if len(room) > 0 :
                data = RoomSerializer(room[0]).data
                data['is_host'] = self.request.session.session_key == room[0].host
                logger.info(data['is_host'])
                return Response(data, status = status.HTTP_200_OK)
            return Response({'Room Not Found':'Invalid Room Code'}, status = status.HTTP_404_NOT_FOUND)
        return Response({'Bad request':'Code parameter not found in request'}, status = status.HTTP_400_BAD_REQUEST)
                
    
class JoinRoom(APIView):
    lookup_url_kwarg ='code'
    
    def post(self, request, format = None):
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()
        code = request.data.get(self.lookup_url_kwarg)
        if code != None:
            room_result = Room.objects.filter(code = code)
            if len(room_result) > 0:
                room = room_result[0]
                self.request.session['room_code'] = code
                return Response({'message':'Room Joined!'}, status = status.HTTP_200_OK)
            return Response({'Bad Request':'Invalid Room Code!'}, status = status.HTTP_400_BAD_REQUEST)
        return Response({'Bad Request':'Invalid post data, did not find  code key'}, status = status.HTTP_400_BAD_REQUEST)
        
        
class CreateRoomView(APIView):
    serializer_class = CreateRoomSerializer
    
    def post(self, request, format =None):
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()
        serialize = self.serializer_class(data = request.data)
        logger.info('loggin request')
        
        if serialize.is_valid():
            
            guest_can_pause = serialize.data.get('guest_can_pause')
            votes_to_skip = serialize.data.get('votes_to_skip')
            logger.info('go -ing')
            host = self.request.session.session_key
            queryset = Room.objects.filter(host= host)
            if queryset.exists():
                room = queryset[0]
                #room.guest_can_pause = guest_can_pause
                room.votes_to_skip = votes_to_skip
                room.save(update_fields=['guest_can_pause', 'votes_to_skip'])
                self.request.session['room_code'] = room.code
                return Response(RoomSerializer(room).data, status=status.HTTP_200_OK)
                
            else:
                room = Room(host=host,votes_to_skip = votes_to_skip )
                room.save()
                self.request.session['room_code'] = room.code
                return Response(RoomSerializer(room).data, status=status.HTTP_200_OK)
        return Response({'Bad Request':'Invalid data...'}, status=status.HTTP_400_BAD_REQUEST)
                
class UserInRoom(APIView):
    def get(self, request, format = None):
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()
        data = {
            'code': self.request.session.get('room_code')
        }
        return JsonResponse(data, status = status.HTTP_200_OK)
                
                
class LeaveRoom(APIView):
    def post(self, request, format = None):
        if 'room_code' in self.request.session:
            self.request.session.pop('room_code')
            host_id = self.request.session.session_key
            room_results = Room.objects.filter(host = host_id)
            if len(room_results) > 0:
                room = room_result[0]
                room.delete()
                
        return Response({'Message':'Succes'}, status = status.HTTP_200_OK)
            
            
            
class UpdateRoom(APIView):
    serializer_class = UpdateRoomSerializer
    def patch(self, request, format=None):
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()
        serializer = self.serializer_class(data = request.data)
        if serializer.is_valid():
            guest_can_pause = serializer.data.get('guest_can_pause')
            votes_to_skip = serializer.data.get('votes_to_skip')
            code = serializer.data.get('code')
            queryset = Room.objects.filter(code = code)
            if not queryset.exists():
                return Response({'msg':'Room not found'}, status = status.HTTP_404_NOT_FOUND )
            room = queryset[0]
            user_id = self.request.session.session_key
            if room.host != user_id:
                return Response({'msg':'You are not the host of this room.'}, status = status.HTTP_403_FORBIDDEN)
            room.guest_can_pause = guest_can_pause
            room.votes_to_skip = votes_to_skip
            room.save(update_fields=['guest_can_pause', 'votes_to_skip'])
            return Response(RoomSerializer(room).data, status = status.HTTP_200_OK)
        return Response({'Bad Request':'Invalid Data!'}, status = status.HTTP_400_BAD_REQUEST)