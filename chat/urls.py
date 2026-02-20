from django.urls import path, include
from . import views

urlpatterns = [
    path('chat/<uuid:user_id>/', views.chat_room, name='chat_room'),
    path('chat/upload/', views.upload_file, name='upload_file'),
]
