from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from accounts.models import CustomUser
from .base import BaseModel

class UserProfile(BaseModel):
    """الملف الشخصي للمستخدم في الدردشة"""
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='chat_profile')
    display_name = models.CharField(max_length=50, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    status = models.CharField(max_length=20, default='online', choices=[
        ('online', 'متصل'),
        ('away', 'بعيد'),
        ('busy', 'مشغول'),
        ('offline', 'غير متصل'),
    ])
    last_seen = models.DateTimeField(auto_now=True)
    theme = models.CharField(max_length=20, default='light', choices=[
        ('light', 'فاتح'),
        ('dark', 'داكن'),
        ('auto', 'تلقائي'),
    ])
    bio = models.TextField(blank=True, null=True, max_length=500)
    is_online = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'ملف المستخدم'
        verbose_name_plural = 'ملفات المستخدمين'
    
    def __str__(self):
        return f"{self.user.email} Profile"
    
    def get_display_name(self):
        """الحصول على الاسم المعروض"""
        return self.display_name or self.user.email
    
    def update_online_status(self, is_online=True):
        """تحديث حالة الاتصال"""
        self.is_online = is_online
        self.last_seen = timezone.now()
        self.save()
    
    def get_status_display(self):
        """الحصول على حالة المستخدم"""
        if self.is_online:
            return "متصل الآن"
        else:
            return f"آخر ظهور {self.last_seen.strftime('%H:%M')}"

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    """إنشاء UserProfile تلقائياً عند إنشاء مستخدم جديد"""
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    """حفظ UserProfile عند حفظ المستخدم"""
    if hasattr(instance, 'chat_profile'):
        instance.chat_profile.save()