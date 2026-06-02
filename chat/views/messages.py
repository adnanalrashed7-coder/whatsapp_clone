from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.contrib import messages
import json
import uuid
from ..models import ChatRoom, Message, Reaction, MessageEditHistory

@login_required
def get_messages(request, room_id):
    """جلب الرسائل - مع دعم التحميل التلقائي"""
    try:
        try:
            room_uuid = uuid.UUID(room_id)
            room = get_object_or_404(ChatRoom, id=room_uuid)
        except ValueError:
            room = get_object_or_404(ChatRoom, name=room_id)
        
        if not room.can_join(request.user):
            return JsonResponse([], safe=False)
        
        last_id = request.GET.get('last_id')
        first_id = request.GET.get('first_id')
        direction = request.GET.get('direction', 'newer')
        
        query = Message.objects.filter(room=room).exclude(deleted_for=request.user)
        
        if direction == 'older' and first_id:
            # جلب الرسائل الأقدم
            try:
                first_uuid = uuid.UUID(first_id)
                first_message = Message.objects.get(id=first_uuid)
                query = query.filter(timestamp__lt=first_message.timestamp)
            except (ValueError, Message.DoesNotExist):
                pass
                
            messages_list = query.order_by('-timestamp')[:20]
            
        else:
            # جلب الرسائل الأحدث (السلوك الافتراضي)
            if last_id:
                try:
                    last_uuid = uuid.UUID(last_id)
                    last_message = Message.objects.get(id=last_uuid)
                    query = query.filter(timestamp__gt=last_message.timestamp)
                except (ValueError, Message.DoesNotExist):
                    pass
            
            messages_list = query.order_by('timestamp')[:50]
        
        messages_data = []
        for msg in messages_list:
            sender_display = msg.sender.email
            try:
                if hasattr(msg.sender, 'chat_profile') and msg.sender.chat_profile.display_name:
                    sender_display = msg.sender.chat_profile.display_name
            except Exception:
                pass
            
            message_data = {
                'id': str(msg.id),
                'sender': msg.sender.email,
                'sender_display': sender_display,
                'message': msg.content,
                'message_type': msg.message_type,
                'timestamp': msg.timestamp.strftime("%H:%M"),
                'is_edited': msg.is_edited,
            }
            
            if msg.image:
                message_data['image_url'] = msg.image.url
            if msg.file:
                message_data['file_url'] = msg.file.url
                message_data['file_name'] = msg.file_name
            if msg.reply_to:
                message_data['reply_to'] = {
                    'id': str(msg.reply_to.id),
                    'sender': msg.reply_to.sender.email,
                    'message': msg.reply_to.content[:50]
                }
            
            messages_data.append(message_data)
        
        return JsonResponse(messages_data, safe=False)
        
    except Exception as e:
        print(f"Error in get_messages: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@login_required
def send_message(request, room_id):
    """إرسال رسالة جديدة - متوافق مع UUID والأسماء"""
    if request.method == 'POST':
        try:
            # محاولة البحث بـ UUID أولاً
            try:
                room_uuid = uuid.UUID(room_id)
                room = get_object_or_404(ChatRoom, id=room_uuid)
            except ValueError:
                # إذا لم يكن UUID، البحث بالاسم
                room = get_object_or_404(ChatRoom, name=room_id)
            
            if not room.can_join(request.user):
                return JsonResponse({'status': 'error', 'error': 'غير مصرح بالدخول'})
            
            data = json.loads(request.body)
            message_content = data.get('message', '').strip()
            reply_to_id = data.get('reply_to')
            
            if message_content:
                reply_to = None
                if reply_to_id:
                    try:
                        reply_to = Message.objects.get(id=reply_to_id, room=room)
                    except Message.DoesNotExist:
                        pass
                
                message = Message.objects.create(
                    room=room,
                    sender=request.user,
                    content=message_content,
                    reply_to=reply_to
                )
                
                # الحصول على الاسم المعروض بشكل آمن
                sender_display = request.user.email
                try:
                    if hasattr(request.user, 'chat_profile') and request.user.chat_profile.display_name:
                        sender_display = request.user.chat_profile.display_name
                except Exception:
                    pass
                
                return JsonResponse({
                    'status': 'success', 
                    'message_id': str(message.id),
                    'sender': request.user.email,
                    'sender_display': sender_display,
                    'timestamp': message.timestamp.strftime("%H:%M"),
                    'reply_to': {
                        'id': str(reply_to.id),
                        'sender': reply_to.sender.email,
                        'message': reply_to.content[:50]
                    } if reply_to else None
                })
            else:
                return JsonResponse({'status': 'error', 'error': 'الرسالة فارغة'})
                
        except Exception as e:
            print(f"Error in send_message: {e}")
            return JsonResponse({'status': 'error', 'error': str(e)})
    
    return JsonResponse({'status': 'error', 'error': 'Method not allowed'})

@csrf_exempt
@login_required
def send_image(request, room_id):
    """إرسال صورة - متوافق مع UUID والأسماء"""
    if request.method == 'POST' and request.FILES.get('image'):
        try:
            # محاولة البحث بـ UUID أولاً
            try:
                room_uuid = uuid.UUID(room_id)
                room = get_object_or_404(ChatRoom, id=room_uuid)
            except ValueError:
                # إذا لم يكن UUID، البحث بالاسم
                room = get_object_or_404(ChatRoom, name=room_id)
            
            image_file = request.FILES['image']
            
            # حفظ الرسالة مع الصورة
            message = Message.objects.create(
                room=room,
                sender=request.user,
                content='📷 صورة مرفوعة',
                image=image_file,
                message_type='image'
            )
            
            return JsonResponse({
                'status': 'success', 
                'message_id': str(message.id),
                'sender': request.user.email,
                'image_url': message.image.url,
                'timestamp': message.timestamp.strftime("%H:%M")
            })
                
        except Exception as e:
            print(f"Error in send_image: {e}")
            return JsonResponse({'status': 'error', 'error': str(e)})
    
    return JsonResponse({'status': 'error', 'error': 'لم يتم اختيار صورة'})

@csrf_exempt
@login_required
def send_file(request, room_id):
    """إرسال ملف"""
    if request.method == 'POST' and request.FILES.get('file'):
        try:
            room = get_object_or_404(ChatRoom, id=room_id)
            
            if not room.can_join(request.user):
                return JsonResponse({'status': 'error', 'error': 'غير مصرح بالدخول'})
            
            file = request.FILES['file']
            file_name = file.name
            file_size = file.size
            file_type = file.content_type
            
            # التحقق من حجم الملف (10MB كحد أقصى)
            if file_size > 10 * 1024 * 1024:
                return JsonResponse({'status': 'error', 'error': 'حجم الملف كبير جداً (الحد الأقصى 10MB)'})
            
            # حفظ الرسالة مع الملف
            message = Message.objects.create(
                room=room,
                sender=request.user,
                content=f'📎 {file_name}',
                file=file,
                file_name=file_name,
                file_size=file_size,
                file_type=file_type,
                message_type='file'
            )
            
            return JsonResponse({
                'status': 'success', 
                'message_id': str(message.id),
                'sender': request.user.email,
                'file_url': message.file.url,
                'file_name': file_name,
                'file_size': file_size,
                'file_type': file_type,
                'file_icon': message.get_file_icon(),
                'timestamp': message.timestamp.strftime("%H:%M")
            })
                
        except Exception as e:
            print(f"Error in send_file: {e}")
            return JsonResponse({'status': 'error', 'error': str(e)})
    
    return JsonResponse({'status': 'error', 'error': 'لم يتم اختيار ملف'})

@csrf_exempt
@login_required
def add_reaction(request, message_id):
    """إضافة رد فعل على رسالة"""
    if request.method == 'POST':
        try:
            message = get_object_or_404(Message, id=message_id)
            data = json.loads(request.body)
            reaction_type = data.get('reaction_type')
            
            if reaction_type not in dict(Reaction.REACTION_TYPES):
                return JsonResponse({'status': 'error', 'error': 'رد الفعل غير صحيح'})
            
            # إنشاء أو تحديث رد الفعل
            reaction, created = Reaction.objects.get_or_create(
                message=message,
                user=request.user,
                defaults={'reaction_type': reaction_type}
            )
            
            if not created:
                reaction.reaction_type = reaction_type
                reaction.save()
            
            # الحصول على ملخص ردود الفعل
            reactions_summary = message.get_reactions_summary()
            
            return JsonResponse({
                'status': 'success',
                'reaction_id': reaction.id,
                'reaction_type': reaction_type,
                'reactions_summary': list(reactions_summary)
            })
            
        except Exception as e:
            print(f"Error in add_reaction: {e}")
            return JsonResponse({'status': 'error', 'error': str(e)})
    
    return JsonResponse({'status': 'error', 'error': 'Method not allowed'})

@login_required
def remove_reaction(request, message_id):
    """إزالة رد فعل من رسالة"""
    if request.method == 'POST':
        try:
            message = get_object_or_404(Message, id=message_id)
            
            # حذف رد الفعل إذا موجود
            Reaction.objects.filter(message=message, user=request.user).delete()
            
            # الحصول على ملخص ردود الفعل المحدث
            reactions_summary = message.get_reactions_summary()
            
            return JsonResponse({
                'status': 'success',
                'reactions_summary': list(reactions_summary)
            })
            
        except Exception as e:
            print(f"Error in remove_reaction: {e}")
            return JsonResponse({'status': 'error', 'error': str(e)})
    
    return JsonResponse({'status': 'error', 'error': 'Method not allowed'})

@csrf_exempt
@login_required
def edit_message(request, message_id):
    """تحرير رسالة"""
    if request.method == 'POST':
        try:
            message = get_object_or_404(Message, id=message_id)
            
            # التحقق من أن المستخدم هو مرسل الرسالة
            if message.sender != request.user:
                return JsonResponse({'status': 'error', 'error': 'لا يمكنك تحرير هذه الرسالة'})
            
            data = json.loads(request.body)
            new_content = data.get('content', '').strip()
            
            if not new_content:
                return JsonResponse({'status': 'error', 'error': 'المحتوى لا يمكن أن يكون فارغاً'})
            
            # التحقق من أن المحتوى تغير فعلاً
            if message.content == new_content:
                return JsonResponse({'status': 'error', 'error': 'لم يتم تغيير المحتوى'})
            
            # حفظ المحتوى القديم في التاريخ
            MessageEditHistory.objects.create(
                message=message,
                old_content=message.content
            )
            
            # تحديث الرسالة
            message.content = new_content
            message.is_edited = True
            message.edited_at = timezone.now()
            message.save()
            
            return JsonResponse({
                'status': 'success',
                'message_id': str(message.id),
                'new_content': new_content,
                'edited_at': message.edited_at.strftime("%H:%M")
            })
            
        except Exception as e:
            print(f"Error in edit_message: {e}")
            return JsonResponse({'status': 'error', 'error': str(e)})
    
    return JsonResponse({'status': 'error', 'error': 'Method not allowed'})

@csrf_exempt
@login_required
def delete_message(request, message_id):
    """حذف رسالة"""
    if request.method == 'POST':
        try:
            message = get_object_or_404(Message, id=message_id)
            data = json.loads(request.body)
            delete_for_all = data.get('for_all', False)
            
            # الحذف للجميع (المشرف أو المرسل فقط)
            if delete_for_all:
                if message.room.admins.filter(id=request.user.id).exists() or message.sender == request.user:
                    message.is_deleted = True
                    message.content = "تم حذف هذه الرسالة"
                    message.image = None
                    message.file = None
                    message.save()
                else:
                    return JsonResponse({'status': 'error', 'error': 'ليس لديك صلاحية لحذف هذه الرسالة للجميع'})
            else:
                # الحذف للمستخدم فقط
                message.deleted_for.add(request.user)
            
            return JsonResponse({
                'status': 'success',
                'message_id': str(message.id),
                'deleted_for_all': delete_for_all
            })
            
        except Exception as e:
            print(f"Error in delete_message: {e}")
            return JsonResponse({'status': 'error', 'error': str(e)})
    
    return JsonResponse({'status': 'error', 'error': 'Method not allowed'})