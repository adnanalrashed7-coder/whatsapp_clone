from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import json
from ..models import ChatRoom, OnlineUser, TypingStatus

@login_required
@csrf_exempt
def update_online_status(request, room_id):
    """تحديث حالة الاتصال للمستخدم"""
    if request.method == 'POST':
        try:
            room = get_object_or_404(ChatRoom, id=room_id)
            action = request.POST.get('action', 'ping')
            
            if action == 'join':
                room.add_online_user(request.user)
            elif action == 'leave':
                room.remove_online_user(request.user)
            elif action == 'ping':
                # تحديث last_seen فقط
                OnlineUser.objects.filter(
                    user=request.user,
                    room=room
                ).update(last_seen=timezone.now())
            
            return JsonResponse({
                'status': 'success',
                'online_count': room.get_online_count()
            })
            
        except Exception as e:
            print(f"Error in update_online_status: {e}")
            return JsonResponse({'status': 'error', 'error': str(e)})
    
    return JsonResponse({'status': 'error', 'error': 'Method not allowed'})

@csrf_exempt
@login_required
def typing_indicator(request, room_id):
    """إدارة مؤشر الكتابة"""
    if request.method == 'POST':
        try:
            room = get_object_or_404(ChatRoom, id=room_id)
            data = json.loads(request.body)
            is_typing = data.get('typing', False)
            
            # حفظ أو تحديث حالة الكتابة
            typing_status, created = TypingStatus.objects.get_or_create(
                room=room,
                user=request.user,
                defaults={'is_typing': is_typing}
            )
            
            if not created:
                typing_status.is_typing = is_typing
                typing_status.save()
            
            # جلب جميع المستخدمين الذين يكتبون حالياً (باستثناء المستخدم الحالي)
            typing_users = TypingStatus.objects.filter(
                room=room,
                is_typing=True
            ).exclude(
                user=request.user
            ).select_related('user')
            
            typing_data = []
            for status in typing_users:
                # التحقق من أن المستخدم لا يزال يكتب (آخر 5 ثواني)
                if timezone.now() - status.last_typed < timezone.timedelta(seconds=5):
                    display_name = status.user.email
                    try:
                        if hasattr(status.user, 'chat_profile') and status.user.chat_profile.display_name:
                            display_name = status.user.chat_profile.display_name
                    except Exception:
                        pass
                    
                    typing_data.append({
                        'user': status.user.email,
                        'display_name': display_name
                    })
            
            return JsonResponse({
                'status': 'success',
                'typing_users': typing_data
            })
            
        except Exception as e:
            print(f"Error in typing_indicator: {e}")
            return JsonResponse({'status': 'error', 'error': str(e)})
    
    return JsonResponse({'status': 'error', 'error': 'Method not allowed'})

@login_required
def get_typing_status(request, room_id):
    """جلب حالة الكتابة للمستخدمين الآخرين"""
    try:
        room = get_object_or_404(ChatRoom, id=room_id)
        
        print(f"🔍 جلب حالة الكتابة للغرفة: {room.name}")
        
        # تنظيف الحالات القديمة أولاً
        old_typing = TypingStatus.objects.filter(
            room=room,
            last_typed__lt=timezone.now() - timezone.timedelta(seconds=10)
        )
        old_typing.update(is_typing=False)
        
        # جلب المستخدمين الذين يكتبون حالياً (باستثناء المستخدم الحالي)
        typing_users = TypingStatus.objects.filter(
            room=room,
            is_typing=True
        ).exclude(
            user=request.user
        ).select_related('user')
        
        typing_data = []
        for status in typing_users:
            # التحقق من أن المستخدم لا يزال يكتب (آخر 5 ثواني)
            if timezone.now() - status.last_typed < timezone.timedelta(seconds=5):
                display_name = status.user.email
                try:
                    if hasattr(status.user, 'chat_profile') and status.user.chat_profile.display_name:
                        display_name = status.user.chat_profile.display_name
                except Exception:
                    pass
                
                typing_data.append({
                    'user': status.user.email,
                    'display_name': display_name
                })
            else:
                # إذا انتهى الوقت، تحديث الحالة
                status.is_typing = False
                status.save()
                print(f"🛑 توقف {status.user.email} عن الكتابة (انتهى الوقت)")
        
        print(f"📊 عدد المستخدمين الذين يكتبون: {len(typing_data)}")
        
        return JsonResponse({
            'status': 'success',
            'typing_users': typing_data
        })
        
    except Exception as e:
        print(f"❌ خطأ في get_typing_status: {e}")
        import traceback
        print(f"❌ تفاصيل الخطأ: {traceback.format_exc()}")
        return JsonResponse({
            'status': 'error',
            'typing_users': [],
            'error': str(e)
        })