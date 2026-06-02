from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.utils import timezone

@receiver(post_save)
def send_invitation_notification(sender, instance, created, **kwargs):
    """إرسال إشعار عند إنشاء دعوة جديدة"""
    if created:
        try:
            from .chat_rooms import RoomInvitation
            if isinstance(instance, RoomInvitation):
                # يمكنك إضافة إشعارات ويب أو إشعارات داخل التطبيق هنا
                print(f"تم إنشاء دعوة جديدة: {instance}")
        except ImportError:
            pass

@receiver(post_save)
def handle_new_message(sender, instance, created, **kwargs):
    """معالجة الرسائل الجديدة"""
    if created:
        try:
            from .messages import Message
            if isinstance(instance, Message) and instance.message_type == 'text':
                # تحديث آخر نشاط في الغرفة
                instance.room.updated_at = timezone.now()
                instance.room.save()
                
                # يمكنك إضافة إشعارات هنا
                print(f"رسالة جديدة في {instance.room.name}: {instance.content[:50]}")
        except ImportError:
            pass

@receiver(pre_delete)
def handle_user_leave(sender, instance, **kwargs):
    """معالجة خروج المستخدم من الغرفة"""
    try:
        from .realtime import OnlineUser
        if isinstance(instance, OnlineUser):
            # يمكنك إضافة رسالة نظام عند خروج المستخدم
            try:
                from .messages import Message
                system_message = Message.objects.create(
                    room=instance.room,
                    sender=instance.user,
                    content=f'غادر {instance.user.email} الغرفة',
                    message_type='system'
                )
            except Exception as e:
                print(f"Error creating system message: {e}")
    except ImportError:
        pass

@receiver(post_save)
def handle_room_creation(sender, instance, created, **kwargs):
    """معالجة إنشاء غرفة جديدة"""
    try:
        from .chat_rooms import ChatRoom
        if isinstance(instance, ChatRoom) and created:
            # إضافة المنشئ كمشرف ومشارك تلقائياً
            instance.admins.add(instance.created_by)
            instance.participants.add(instance.created_by)
            
            # رسالة ترحيب في الغرفة
            try:
                from .messages import Message
                welcome_message = Message.objects.create(
                    room=instance,
                    sender=instance.created_by,
                    content=f'مرحباً بكم في غرفة "{instance.name}"!',
                    message_type='system'
                )
            except Exception as e:
                print(f"Error creating welcome message: {e}")
    except ImportError:
        pass