from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q
from django.contrib import messages
import json
from ..models import ChatRoom, Message, RoomInvitation
from accounts.models import CustomUser
import uuid

@login_required
def chat_home(request):
    """الصفحة الرئيسية للدردشة مع قائمة الغرف"""
    try:
        # حساب الدعوات غير المقروءة
        unread_invitations_count = RoomInvitation.objects.filter(
            invited_user=request.user,
            is_accepted=False,
            is_declined=False,
            expires_at__gt=timezone.now()
        ).count()
        
        # إنشاء غرفة عامة افتراضية إذا لم تكن موجودة - مع إضافة المنشئ
        general_room, created = ChatRoom.objects.get_or_create(
            name='عام',
            room_type='public',
            defaults={
                'created_by': request.user, 
                'description': 'الغرفة العامة للدردشة'
            }
        )
        
        # التأكد من أن المنشئ مضاف كمشارك ومشرف
        general_room.ensure_creator_is_participant()
        
        # إذا تم إنشاء الغرفة الآن، أضف المنشئ كمشرف ومشارك
        if created:
            general_room.admins.add(request.user)
            general_room.participants.add(request.user)
            print(f"✅ تم إنشاء الغرفة العامة وإضافة المنشئ: {request.user.email}")
        else:
            # إذا كانت الغرفة موجودة مسبقاً، تأكد من إضافة المستخدم الحالي إذا لم يكن مضافاً
            if not general_room.participants.filter(id=request.user.id).exists():
                general_room.participants.add(request.user)
                print(f"✅ تم إضافة المستخدم الحالي إلى الغرفة العامة: {request.user.email}")
        
        # جلب الغرف المتاحة للمستخدم
        available_rooms = ChatRoom.objects.filter(
            Q(room_type='public') | 
            Q(participants=request.user) |
            Q(created_by=request.user)
        ).distinct().filter(is_active=True)
        
        # غرف المستخدم الخاصة (التي أنشأها)
        user_rooms = request.user.created_rooms.all()
        
        # تحضير بيانات الغرف مع الإحصائيات - بشكل آمن
        rooms_data = []
        for room in available_rooms:
            try:
                room_data = {
                    'id': str(room.id),
                    'name': room.name,
                    'description': room.description or 'لا يوجد وصف',
                    'type': room.room_type,
                    'created_by': room.created_by.email,
                    'is_owner': room.created_by == request.user,
                    'online_count': room.get_online_count(),
                    'message_count': room.message_set.count(),
                    'can_join': room.can_join(request.user)
                }
                rooms_data.append(room_data)
            except Exception as e:
                print(f"Error processing room {room.id}: {e}")
        
        # بيانات غرف المستخدم
        user_rooms_data = []
        for room in user_rooms:
            try:
                room_data = {
                    'id': str(room.id),
                    'name': room.name,
                    'description': room.description or 'لا يوجد وصف',
                    'type': room.room_type,
                    'created_by': room.created_by.email,
                    'is_owner': True,
                    'online_count': room.get_online_count(),
                    'message_count': room.message_set.count(),
                    'can_join': True
                }
                user_rooms_data.append(room_data)
            except Exception as e:
                print(f"Error processing user room {room.id}: {e}")
        
        # الغرف العامة فقط
        public_rooms_data = [room for room in rooms_data if room['type'] == 'public']
        
        context = {
            'available_rooms': available_rooms,
            'user_rooms': user_rooms,
            'rooms_data_json': json.dumps(rooms_data, ensure_ascii=False),
            'user_rooms_data_json': json.dumps(user_rooms_data, ensure_ascii=False),
            'public_rooms_data_json': json.dumps(public_rooms_data, ensure_ascii=False),
            'current_room': general_room,
            'unread_invitations_count': unread_invitations_count,
        }
        return render(request, 'chat/home.html', context)
        
    except Exception as e:
        print(f"Error in chat_home: {e}")
        messages.error(request, 'حدث خطأ في تحميل الغرف')
        return render(request, 'chat/home.html', {
            'rooms_data_json': '[]',
            'user_rooms_data_json': '[]',
            'public_rooms_data_json': '[]',
            'available_rooms': [],
            'user_rooms': [],
            'unread_invitations_count': 0
        })



@login_required
def room_detail(request, room_id):
    """تفاصيل غرفة دردشة محددة"""
    try:
        # محاولة تحويل room_id إلى UUID أولاً
        try:
            room_uuid = uuid.UUID(room_id)
            room = get_object_or_404(ChatRoom, id=room_uuid)
        except ValueError:
            room = get_object_or_404(ChatRoom, name=room_id)
        
        # التحقق من صلاحية الدخول
        if not room.can_join(request.user):
            messages.error(request, 'ليس لديك صلاحية للدخول إلى هذه الغرفة')
            return redirect('chat:home')
        
        # إضافة المستخدم إلى قائمة المتصلين
        room.add_online_user(request.user)
        
        # جلب آخر 100 رسالة
        messages_list = Message.objects.filter(
            room=room
        ).exclude(
            deleted_for=request.user
        ).select_related('sender', 'reply_to').order_by('-timestamp')[:100]
        
        # معلومات المستخدمين المتصلين
        online_users = room.get_online_users()
        online_count = room.get_online_count()
        
        # جلب جميع المشاركين في الغرفة مع حالة الاتصال
        participants = room.participants.all()
        participants_with_status = []
        
        for participant in participants:
            is_online = room.is_user_online(participant)
            participants_with_status.append({
                'user': participant,
                'is_online': is_online,
                'display_name': participant.email,  # سنحسن هذا لاحقاً
            })
        
        participants_count = participants.count()
        
        # التحقق من صلاحيات الإدارة
        is_room_admin = (
            room.admins.filter(id=request.user.id).exists() or 
            room.created_by == request.user
        )
        
        context = {
            'room': room,
            'room_id': str(room.id),
            'messages': reversed(messages_list),
            'online_users': online_users,
            'online_count': online_count,
            'participants': participants,
            'participants_with_status': participants_with_status,
            'participants_count': participants_count,
            'is_room_admin': is_room_admin,
        }
        return render(request, 'chat/rooms/room.html', context)
        
    except Exception as e:
        print(f"Error in room_detail: {e}")
        messages.error(request, 'حدث خطأ في تحميل الغرفة')
        return redirect('chat:home')

def chat_home_old(request):
    """للتتوافق مع الروابط القديمة - إعادة توجيه للصفحة الرئيسية"""
    return redirect('chat:home')