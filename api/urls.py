from django.urls import path
from .views import *


urlpatterns = [
    path('', index),
    path('room', RoomView.as_view()),
    path('create-room', CreateRoomView.as_view()),
    path('get-room', GetRoom.as_view() ),
    path('join-room', JoinRoom.as_view()),
    path('user-in-room', UserInRoom.as_view()),
    path('update-room', UpdateRoom.as_view())
]
