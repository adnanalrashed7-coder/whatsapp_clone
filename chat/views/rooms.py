from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from django.contrib import messages
from ..models import ChatRoom, Message
from accounts.models import CustomUser
import uuid

@login_required
def create_room(request):
    """إنشاء غرفة دردشة جديدة"""
    if request.method == 'POST':
        room_name = request.POST.get('room_name')
        room_type = request.POST.get('room_type', 'public')
        description = request.POST.get('description', '')
        
        if room_name:
            room = ChatRoom.objects.create(
                name=room_name,
                room_type=room_type,
                description=description,
                created_by=request.user
            )
            
            # إضافة المنشئ كمشرف ومشارك
            room.admins.add(request.user)
            room.participants.add(request.user)
            
            messages.success(request, f'تم إنشاء الغرفة "{room_name}" بنجاح')
            return redirect('chat:room_detail', room_id=room.id)
    
    return render(request, 'chat/create_room.html')

@login_required
def manage_room(request, room_id):
    """إدارة غرفة الدردشة"""
    try:
        room_uuid = uuid.UUID(room_id)
        room = get_object_or_404(ChatRoom, id=room_uuid)
    except ValueError:
        room = get_object_or_404(ChatRoom, name=room_id)
    
    # التحقق من الصلاحيات
    if not room.admins.filter(id=request.user.id).exists() and room.created_by != request.user:
        messages.error(request, 'ليس لديك صلاحية لإدارة هذه الغرفة')
        return redirect('chat:room_detail', room_id=room_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update_room':
            room.name = request.POST.get('room_name', room.name)
            room.description = request.POST.get('description', room.description)
            room.max_participants = request.POST.get('max_participants', room.max_participants)
            room.save()
            messages.success(request, 'تم تحديث إعدادات الغرفة')
            
        elif action == 'add_participant':
            email = request.POST.get('email')
            try:
                user = CustomUser.objects.get(email=email)
                room.participants.add(user)
                messages.success(request, f'تم إضافة {email} إلى الغرفة')
                
                # إنشاء رسالة نظام
                Message.objects.create(
                    room=room,
                    sender=request.user,
                    content=f'انضم {user.email} إلى الغرفة',
                    message_type='system'
                )
                
            except CustomUser.DoesNotExist:
                messages.error(request, 'المستخدم غير موجود')
                
        elif action == 'remove_participant':
            user_id = request.POST.get('user_id')
            try:
                user = CustomUser.objects.get(id=user_id)
                room.participants.remove(user)
                room.admins.remove(user)
                messages.success(request, f'تم إزالة {user.email} من الغرفة')
            except CustomUser.DoesNotExist:
                messages.error(request, 'المستخدم غير موجود')
    
    participants = room.participants.all()
    return render(request, 'chat/manage_room.html', {
        'room': room,
        'participants': participants
    })

@login_required
def search_rooms(request):
    """بحث الغرف"""
    query = request.GET.get('q', '')
    
    if query:
        rooms = ChatRoom.objects.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query),
            is_active=True
        ).filter(
            Q(room_type='public') | 
            Q(participants=request.user) |
            Q(created_by=request.user)
        ).distinct()
    else:
        rooms = ChatRoom.objects.none()
    
    rooms_data = []
    for room in rooms:
        rooms_data.append({
            'id': str(room.id),
            'name': room.name,
            'description': room.description,
            'room_type': room.get_room_type_display(),
            'online_count': room.get_online_count(),
            'created_by': room.created_by.email
        })
    
    return JsonResponse(rooms_data, safe=False)

@login_required
def create_test_rooms(request):
    """إنشاء غرف اختبارية (للتطوير فقط)"""
    try:
        # غرفة عامة
        public_room, created = ChatRoom.objects.get_or_create(
            name='الغرفة العامة',
            room_type='public',
            defaults={
                'created_by': request.user,
                'description': 'هذه هي الغرفة العامة للجميع'
            }
        )
        
        # غرفة خاصة للمستخدم
        private_room, created = ChatRoom.objects.get_or_create(
            name='غرفتي الخاصة',
            room_type='private',
            created_by=request.user,
            defaults={
                'description': 'هذه غرفتي الخاصة'
            }
        )
        private_room.participants.add(request.user)
        private_room.admins.add(request.user)
        
        messages.success(request, 'تم إنشاء غرف الاختبار بنجاح')
        return redirect('chat:home')
        
    except Exception as e:
        messages.error(request, f'خطأ في إنشاء غرف الاختبار: {e}')
        return redirect('chat:home')
    
@login_required
def fix_all_rooms(request):
    """إصلاح جميع الغرف - للمشرفين فقط"""
    if not request.user.is_superuser:
        messages.error(request, 'ليس لديك صلاحية للوصول إلى هذه الصفحة')
        return redirect('chat:home')
    
    fixed_rooms = []
    
    for room in ChatRoom.objects.all():
        fixes = []
        
        # إضافة المنشئ كمشارك إذا لم يكن مضافاً
        if not room.participants.filter(id=room.created_by.id).exists():
            room.participants.add(room.created_by)
            fixes.append("تم إضافة المنشئ كمشارك")
        
        # إضافة المنشئ كمشرف إذا لم يكن مضافاً
        if not room.admins.filter(id=room.created_by.id).exists():
            room.admins.add(room.created_by)
            fixes.append("تم إضافة المنشئ كمشرف")
        
        if fixes:
            fixed_rooms.append({
                'room': room.name,
                'fixes': fixes,
                'participants_count': room.participants.count(),
                'admins_count': room.admins.count()
            })
    
    context = {
        'fixed_rooms': fixed_rooms,
        'total_rooms': ChatRoom.objects.count()
    }
    
    return render(request, 'chat/fix_rooms.html', context)