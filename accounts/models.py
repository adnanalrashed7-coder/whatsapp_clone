from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('يجب تقديم البريد الإلكتروني')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    username = None  # تعطيل اسم المستخدم
    email = models.EmailField(unique=True, verbose_name='البريد الإلكتروني')
    is_email_verified = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    objects = CustomUserManager()
    
    def __str__(self):
        return self.email


@receiver(pre_delete, sender=CustomUser)
def delete_custom_user_related(sender, instance, **kwargs):
    """حذف البيانات المرتبطة بالمستخدم قبل حذف الحساب لحماية قيود المفتاح الأجنبي."""
    try:
        from chat.models.chat_rooms import ChatRoom, RoomInvitation
        from chat.models.messages import Message, Reaction
        from chat.models.realtime import OnlineUser, TypingStatus
        from chat.models.users import UserProfile
        from calls.models import Call
    except ImportError:
        return

    # تنظيف علاقات M2M
    try:
        instance.groups.clear()
        instance.user_permissions.clear()
    except Exception:
        pass

    try:
        ChatRoom.participants.through.objects.filter(customuser=instance).delete()
        ChatRoom.admins.through.objects.filter(customuser=instance).delete()
    except Exception:
        pass

    try:
        Message.deleted_for.through.objects.filter(customuser=instance).delete()
    except Exception:
        pass

    # حذف السجلات المرتبطة مباشرة
    UserProfile.objects.filter(user=instance).delete()
    OnlineUser.objects.filter(user=instance).delete()
    TypingStatus.objects.filter(user=instance).delete()
    Reaction.objects.filter(user=instance).delete()
    Message.objects.filter(sender=instance).delete()
    RoomInvitation.objects.filter(invited_by=instance).delete()
    RoomInvitation.objects.filter(invited_user=instance).delete()
    Call.objects.filter(caller=instance).delete()
    Call.objects.filter(receiver=instance).delete()
    ChatRoom.objects.filter(created_by=instance).delete()
