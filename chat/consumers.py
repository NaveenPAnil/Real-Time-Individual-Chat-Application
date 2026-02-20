import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ChatRoom, Message
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        # We accept first to give the client a stable connection while we validate
        await self.accept()
        
        user = self.scope["user"]
        print(f"WS Connect attempt by: {user} (Anonymous: {user.is_anonymous})")

        if user.is_anonymous:
            print("WS Rejecting: User is anonymous")
            await self.close()
            return

        # Update online status
        await self.update_user_status(user, True)

        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f"chat_{self.room_id}"

        # Use a single sync_to_async call to handle DB logic
        membership_valid = await self.check_room_membership(user)
        
        if not membership_valid:
            # We already updated status to True, but if membership fails we disconnect
            # and status update in disconnect will handle it.
            await self.close()
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # Mark messages as read immediately when connecting
        await self.mark_messages_as_read(user)

        # Notify the room that messages have been read
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'messages_read',
                'user_id': str(user.id)
            }
        )
        print(f"WS Connected successfully to {self.room_group_name}")

    async def disconnect(self, close_code):
        user = self.scope["user"]
        if not user.is_anonymous:
            await self.update_user_status(user, False)

        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
        print(f"WS Disconnected code: {close_code}")

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data.get('type', 'chat_message')
            user = self.scope['user']

            if message_type == 'chat_message':
                message_text = data.get('message', '').strip()
                file_url = data.get('file_url')
                message_id = data.get('message_id')

                if file_url and message_id:
                    # Message already saved, just broadcast
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'chat_message',
                            'message': message_text,
                            'file_url': file_url,
                            'sender': user.email,
                            'sender_id': str(user.id),
                            'timestamp': 'Just now',
                            'message_id': message_id
                        }
                    )
                elif message_text:
                    message_obj = await self.save_message(user, message_text)
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'chat_message',
                            'message': message_text,
                            'sender': user.email,
                            'sender_id': str(user.id),
                            'timestamp': timezone.localtime(message_obj.timestamp).strftime('%H:%M'),
                            'message_id': str(message_obj.id)
                        }
                    )

            elif message_type == 'mark_read':
                await self.mark_messages_as_read(user)
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'messages_read',
                        'user_id': str(user.id)
                    }
                )
            elif message_type == 'typing':
                is_typing = data.get('typing', False)
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'user_typing',
                        'user_id': str(user.id),
                        'typing': is_typing
                    }
                )
            elif message_type == 'delete_message':
                message_id = data.get('message_id')
                if await self.delete_message_from_db(user, message_id):
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'message_deleted',
                            'message_id': message_id
                        }
                    )
        except Exception as e:
            print(f"WS Receive Error: {e}")

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'file_url': event.get('file_url'),
            'sender': event['sender'],
            'sender_id': event['sender_id'],
            'timestamp': event.get('timestamp', 'Just now'),
            'message_id': event.get('message_id')
        }))

    async def messages_read(self, event):
        await self.send(text_data=json.dumps({
            'type': 'messages_read',
            'user_id': event['user_id']
        }))

    async def user_typing(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user_typing',
            'user_id': event['user_id'],
            'typing': event['typing']
        }))

    async def message_deleted(self, event):
        await self.send(text_data=json.dumps({
            'type': 'message_deleted',
            'message_id': event['message_id']
        }))

    @database_sync_to_async
    def check_room_membership(self, user):

        try:
            # select_related helps fetch the users in the same query
            room = ChatRoom.objects.select_related('user1', 'user2').get(id=self.room_id)
            if user == room.user1 or user == room.user2:
                print(f"WS Room Membership Valid: {user.email}")
                return True
            print(f"WS Room Membership Invalid: {user.email}")
            return False
        except Exception as e:
            print(f"WS Membership Check Error: {e}")
            return False

    @database_sync_to_async
    def save_message(self, user, message):
        room = ChatRoom.objects.get(id=self.room_id)
        return Message.objects.create(
            room=room,
            sender=user,
            content=message
        )

    @database_sync_to_async
    def mark_messages_as_read(self, user):
        room = ChatRoom.objects.get(id=self.room_id)
        Message.objects.filter(room=room).exclude(sender=user).update(is_read=True)

    @database_sync_to_async
    def delete_message_from_db(self, user, message_id):
        try:
            # Only sender can delete their own message
            msg = Message.objects.get(id=message_id, sender=user)
            msg.delete()
            return True
        except Message.DoesNotExist:
            print(f"WS Delete Error: Message {message_id} not found or not owned by {user}")
            return False
        except Exception as e:
            print(f"WS Delete Error: {e}")
            return False

    @database_sync_to_async
    def update_user_status(self, user, is_online):
        User.objects.filter(id=user.id).update(
            is_online=is_online,
            last_seen=timezone.now()
        )




