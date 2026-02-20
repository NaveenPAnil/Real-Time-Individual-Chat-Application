from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required

from .models import ChatRoom, Message
from django.shortcuts import get_object_or_404, render
from accounts.models import User


User = get_user_model()


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@login_required
def chat_room(request, user_id):
    # ... existing code ...
    other_user = get_object_or_404(User, id=user_id)
    user1, user2 = sorted([request.user, other_user], key=lambda u: str(u.id))
    room, created = ChatRoom.objects.get_or_create(user1=user1, user2=user2)
    Message.objects.filter(room=room, sender=other_user, is_read=False).update(is_read=True)
    chat_messages = Message.objects.filter(room=room)

    return render(request, "chat/chat_room.html", {
        "room": room,
        "chat_messages": chat_messages,
        "other_user": other_user
    })

@login_required
def upload_file(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        room_id = request.POST.get('room_id')
        room = get_object_or_404(ChatRoom, id=room_id)
        
        message = Message.objects.create(
            room=room,
            sender=request.user,
            file=file,
            content=""
        )
        
        return JsonResponse({
            'success': True,
            'file_url': message.file.url,
            'message_id': str(message.id)
        })
    return JsonResponse({'success': False, 'error': 'Invalid request'})
