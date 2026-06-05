from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from ..models import RoomInvitation, ChatRoom, Message, FriendRequest, Friendship
from accounts.models import CustomUser

@login_required
def invite_user(request, room_id):
    """دعوة مستخدم إلى غرفة خاصة"""
    try:
        room = get_object_or_404(ChatRoom, id=room_id)
        
        # التحقق من الصلاحيات
        if not (room.created_by == request.user or room.admins.filter(id=request.user.id).exists()):
            messages.error(request, 'ليس لديك صلاحية لدعوة مستخدمين إلى هذه الغرفة')
            return redirect('chat:manage_room', room_id=room_id)
        
        if request.method == 'POST':
            email = request.POST.get('email', '').strip().lower()
            
            if not email:
                messages.error(request, 'يرجى إدخال بريد إلكتروني')
                return redirect('chat:manage_room', room_id=room_id)
            
            try:
                invited_user = CustomUser.objects.get(email=email)
                
                # التحقق من عدم دعوة المستخدم لنفسه
                if invited_user == request.user:
                    messages.warning(request, 'لا يمكنك دعوة نفسك')
                    return redirect('chat:manage_room', room_id=room_id)
                
                # التحقق من عدم وجود دعوة سابقة
                existing_invitation = RoomInvitation.objects.filter(
                    room=room,
                    invited_user=invited_user,
                    is_accepted=False,
                    is_declined=False,
                    expires_at__gt=timezone.now()
                ).exists()
                
                if existing_invitation:
                    messages.warning(request, 'تم إرسال دعوة سابقة لهذا المستخدم ولا تزال فعالة')
                    return redirect('chat:manage_room', room_id=room_id)
                
                # التحقق من أن المستخدم ليس عضو بالفعل
                if room.participants.filter(id=invited_user.id).exists():
                    messages.warning(request, 'المستخدم عضو بالفعل في الغرفة')
                    return redirect('chat:manage_room', room_id=room_id)
                
                # إنشاء الدعوة
                invitation = RoomInvitation.objects.create(
                    room=room,
                    invited_by=request.user,
                    invited_user=invited_user,
                    expires_at=timezone.now() + timezone.timedelta(days=7)
                )
                
                # إرسال بريد إلكتروني
                try:
                    send_invitation_email(invitation, request)
                    messages.success(request, f'تم إرسال دعوة إلى {email} بنجاح')
                except Exception as e:
                    # الدعوة تم إنشاؤها ولكن فشل إرسال البريد
                    messages.warning(request, f'تم إنشاء الدعوة ولكن فشل إرسال البريد: {str(e)}')
                
            except CustomUser.DoesNotExist:
                messages.error(request, f'المستخدم بالبريد {email} غير موجود في النظام')
            except Exception as e:
                messages.error(request, f'حدث خطأ غير متوقع: {str(e)}')
        
        return redirect('chat:manage_room', room_id=room_id)
        
    except Exception as e:
        print(f"Error in invite_user: {e}")
        messages.error(request, f'حدث خطأ في إنشاء الدعوة: {str(e)}')
        return redirect('chat:manage_room', room_id=room_id)


@login_required
def user_directory(request):
    """عرض دليل المستخدمين وطلبات الصداقة وقائمة الأصدقاء."""
    users = CustomUser.objects.exclude(id=request.user.id).order_by('email')
    now = timezone.now()

    pending_sent = FriendRequest.objects.filter(sender=request.user, status='pending', expires_at__gt=now)
    pending_received = FriendRequest.objects.filter(receiver=request.user, status='pending', expires_at__gt=now)
    friends = Friendship.get_friends(request.user)

    friend_entries = []
    for friend in friends:
        friend_entries.append({
            'user': friend,
            'private_room': ChatRoom.objects.filter(
                name=ChatRoom.get_private_chat_name(request.user, friend),
                room_type='private'
            ).first()
        })

    user_entries = []
    for user in users:
        is_friend = Friendship.be_friends(request.user, user)
        outgoing_request = pending_sent.filter(receiver=user).first()
        incoming_request = pending_received.filter(sender=user).first()
        private_room = None

        if is_friend:
            private_room = ChatRoom.objects.filter(
                name=ChatRoom.get_private_chat_name(request.user, user),
                room_type='private'
            ).first()

        user_entries.append({
            'user': user,
            'is_friend': is_friend,
            'outgoing_request': outgoing_request,
            'incoming_request': incoming_request,
            'private_room': private_room,
        })

    return render(request, 'chat/user_directory.html', {
        'users': user_entries,
        'friends': friends,
        'friend_entries': friend_entries,
        'pending_received': pending_received,
        'pending_sent': pending_sent,
    })


@login_required
def send_friend_request(request, user_id):
    if request.method != 'POST':
        return redirect('chat:user_directory')

    invited_user = get_object_or_404(CustomUser, id=user_id)

    if invited_user == request.user:
        messages.warning(request, 'لا يمكنك إرسال طلب صداقة إلى نفسك')
        return redirect('chat:user_directory')

    if Friendship.be_friends(request.user, invited_user):
        room = ChatRoom.get_or_create_private_chat(request.user, invited_user)
        return redirect('chat:room_detail', room_id=room.id)

    now = timezone.now()
    existing_request = FriendRequest.objects.filter(
        sender=request.user,
        receiver=invited_user,
        status='pending',
        expires_at__gt=now
    ).first()

    if existing_request:
        messages.warning(request, 'لقد أرسلت بالفعل طلب صداقة لهذا المستخدم، انتظر الموافقة.')
        return redirect('chat:user_directory')

    incoming_request = FriendRequest.objects.filter(
        sender=invited_user,
        receiver=request.user,
        status='pending',
        expires_at__gt=now
    ).first()

    if incoming_request:
        room = incoming_request.accept()
        messages.success(request, 'تم قبول طلب الصداقة الموجود بالفعل بينكما')
        return redirect('chat:room_detail', room_id=room.id)

    FriendRequest.objects.create(
        sender=request.user,
        receiver=invited_user,
        expires_at=timezone.now() + timezone.timedelta(days=30)
    )
    messages.success(request, 'تم إرسال طلب الصداقة بنجاح')
    return redirect('chat:user_directory')


@login_required
def my_friend_requests(request):
    incoming = FriendRequest.objects.filter(receiver=request.user).order_by('-created_at')
    outgoing = FriendRequest.objects.filter(sender=request.user).order_by('-created_at')
    return render(request, 'chat/friend_requests.html', {
        'incoming_requests': incoming,
        'outgoing_requests': outgoing,
    })


@login_required
def accept_friend_request(request, token):
    friend_request = get_object_or_404(FriendRequest, token=token, receiver=request.user)

    if not friend_request.is_active():
        messages.error(request, 'هذا الطلب غير صالح بعد الآن')
        return redirect('chat:my_friend_requests')

    room = friend_request.accept()
    messages.success(request, 'تم قبول طلب الصداقة وتم إنشاء الدردشة الخاصة')
    return redirect('chat:room_detail', room_id=room.id)


@login_required
def decline_friend_request(request, token):
    friend_request = get_object_or_404(FriendRequest, token=token, receiver=request.user)

    if friend_request.is_active():
        friend_request.decline()
        messages.info(request, 'تم رفض طلب الصداقة')

    return redirect('chat:my_friend_requests')


def send_invitation_email(invitation, request):
    """إرسال بريد دعوة"""
    try:
        current_site = get_current_site(request)
        subject = f'دعوة للانضمام إلى غرفة الدردشة: {invitation.room.name}'
        
        # تحميل القالب وإرسال البريد
        message = render_to_string('chat/invitation_email.html', {
            'invitation': invitation,
            'domain': current_site.domain,
            'protocol': 'https' if request.is_secure() else 'http'
        })
        
        email = EmailMessage(
            subject=subject,
            body=message,
            from_email='ADALChat <adnanalrashed7@gmail.com>',
            to=[invitation.invited_user.email]
        )
        email.content_subtype = "html"
        
        # إرسال البريد
        email.send()
        print(f"✅ تم إرسال بريد الدعوة إلى: {invitation.invited_user.email}")
        return True
        
    except Exception as e:
        print(f"❌ فشل إرسال بريد الدعوة: {str(e)}")
        import traceback
        print(f"❌ تفاصيل الخطأ: {traceback.format_exc()}")
        return False

@login_required
def accept_invitation(request, token):
    """قبول دعوة الانضمام إلى غرفة"""
    try:
        invitation = get_object_or_404(RoomInvitation, token=token, invited_user=request.user)
        
        if invitation.is_expired():
            messages.error(request, 'انتهت صلاحية الدعوة')
            return redirect('chat:home')
        
        if invitation.is_accepted:
            messages.info(request, 'لقد قبلت هذه الدعوة مسبقاً')
            return redirect('chat:room_detail', room_id=invitation.room.id)
        
        if invitation.is_declined:
            messages.error(request, 'لقد رفضت هذه الدعوة مسبقاً')
            return redirect('chat:home')
        
        # إضافة المستخدم إلى الغرفة
        invitation.room.participants.add(request.user)
        invitation.is_accepted = True
        invitation.save()
        
        # إنشاء رسالة نظام
        Message.objects.create(
            room=invitation.room,
            sender=request.user,
            content=f'انضم {request.user.email} إلى الغرفة',
            message_type='system'
        )
        
        messages.success(request, f'تم الانضمام إلى غرفة {invitation.room.name}')
        return redirect('chat:room_detail', room_id=invitation.room.id)
        
    except Exception as e:
        messages.error(request, 'رابط الدعوة غير صالح')
        return redirect('chat:home')

@login_required
def decline_invitation(request, token):
    """رفض دعوة الانضمام إلى غرفة"""
    try:
        invitation = get_object_or_404(RoomInvitation, token=token, invited_user=request.user)
        
        if not invitation.is_accepted and not invitation.is_declined:
            invitation.is_declined = True
            invitation.save()
            Message.objects.create(
                room=invitation.room,
                sender=request.user,
                content=f'{request.user.email} رفضت دعوتك للدردشة الخاصة',
                message_type='system'
            )
            messages.info(request, 'تم رفض الدعوة')
        
        return redirect('chat:home')
        
    except Exception as e:
        messages.error(request, 'رابط الدعوة غير صالح')
        return redirect('chat:home')

@login_required
def my_invitations(request):
    """عرض الدعوات الواردة للمستخدم"""
    invitations = RoomInvitation.objects.filter(
        invited_user=request.user,
        is_accepted=False,
        is_declined=False
    ).filter(expires_at__gt=timezone.now()).select_related('room', 'invited_by')
    
    return render(request, 'chat/my_invitations.html', {
        'invitations': invitations
    })

@login_required
def check_invitation(request, token):
    """صفحة للتحقق من صحة الدعوة"""
    try:
        invitation = get_object_or_404(RoomInvitation, token=token)
        
        context = {
            'invitation': invitation,
            'is_valid': not invitation.is_expired() and not invitation.is_accepted and not invitation.is_declined,
            'is_expired': invitation.is_expired(),
            'is_accepted': invitation.is_accepted,
            'is_declined': invitation.is_declined,
        }
        
        return render(request, 'chat/check_invitation.html', context)
        
    except Exception as e:
        messages.error(request, 'رابط الدعوة غير صالح')
        return redirect('chat:home')