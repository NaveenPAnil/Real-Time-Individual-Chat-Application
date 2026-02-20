from allauth.account.utils import complete_signup
from allauth.account.models import EmailAddress
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from chat.models import ChatRoom, Message
from .forms import UserForm
from django.contrib import messages, auth


# Create your views here.
from .models import User


def register_user(request):
    if request.user.is_authenticated:
        messages.warning(request, 'Already logged in!')
        return redirect('user_list')
    elif request.method == 'POST':
        print(request.POST)
        form = UserForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password']
            user = form.save(commit=False)
            user.set_password(password)
            user.save()

            # send verification email
            # mail_subject = 'Please activate your account'
            # email_template = 'accounts/emails/account_verification_email'
            complete_signup(
                request,
                user,
                settings.ACCOUNT_EMAIL_VERIFICATION,
                '/login/'  # redirect after confirmation
            )
            messages.success(request, "Account created successfully")
            return redirect('registerUser')
    else:
        form = UserForm()
    context = {
        'form': form,
    }
    return render(request, 'accounts/register.html', context)


def login(request):
    if request.user.is_authenticated:
        messages.warning(request, 'Already logged in!!')
        return redirect('user_list')
    elif request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(username=email, password=password)
        if user is not None:
            if not EmailAddress.objects.filter(user=user, verified=True).exists():
                messages.error(request, "Please verify your email first.")
                return redirect('login')

            from django.utils import timezone
            auth.login(request, user)
            user.is_online = True
            user.last_seen = timezone.now()
            user.save()
            messages.success(request, 'You are logged in..')
            return redirect('user_list')
        else:
            messages.error(request, 'Invalid login credentials! Try again..')
            return redirect('login')
    return render(request, 'accounts/login.html')


def logout(request):
    from django.utils import timezone
    user = request.user
    user.is_online = False
    user.last_seen = timezone.now()
    user.save()
    auth.logout(request)
    messages.info(request, 'Logout successfully')
    return redirect('login')


@login_required(login_url='login')
def user_list(request):
    users = User.objects.exclude(id=request.user.id).exclude(is_superadmin=True)
    
    # Add unread count for each user
    for user in users:
        # We need to find the room between request.user and 'user'
        user1, user2 = sorted([request.user, user], key=lambda u: str(u.id))
        room = ChatRoom.objects.filter(user1=user1, user2=user2).first()
        if room:
            user.unread_count = Message.objects.filter(room=room, sender=user, is_read=False).count()
        else:
            user.unread_count = 0

    context = {
        "users": users
    }
    return render(request, 'chat/user_list.html', context)

