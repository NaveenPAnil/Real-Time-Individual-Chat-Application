from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from accounts.models import User
from base.models import BaseModel


class ChatRoom(BaseModel):
    user1 = models.ForeignKey(User, related_name='chats_initiated', on_delete=models.CASCADE)
    user2 = models.ForeignKey(User, related_name='chats_received', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user1.email} - {self.user2.email}"

    class Meta:
        db_table = 'chat_chat_room'
        verbose_name = _('chat_room')
        verbose_name_plural = _('chat_rooms')
        unique_together = ('user1', 'user2')


class Message(BaseModel):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to='chat_files/', blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sender.email}"

    class Meta:
        db_table = 'chat_message'
        verbose_name = _('message')
        verbose_name_plural = _('messages')
        ordering = ['timestamp']
