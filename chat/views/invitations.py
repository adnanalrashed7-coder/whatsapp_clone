from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from ..models import RoomInvitation, ChatRoom, Message
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