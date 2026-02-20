from django.contrib import admin

# Register your models here.
from chat.models import ChatRoom, Message


class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ('user1', 'user2')


class MessageAdmin(admin.ModelAdmin):
    list_display = ('room', 'sender', 'timestamp', 'is_read')


admin.site.register(Message, MessageAdmin)
admin.site.register(ChatRoom, ChatRoomAdmin)
