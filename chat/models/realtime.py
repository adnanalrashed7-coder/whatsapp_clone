from django.db import models
from django.utils import timezone
from accounts.models import CustomUser
from .base import BaseModel
from .chat_rooms import ChatRoom

class OnlineUser(BaseModel):
    """تتبع المستخدمين المتصلين بالغرف"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='onlinestatuses')
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='online_users')
    is_online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(default=timezone.now)
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'room']
        ordering = ['-last_seen']
        verbose_name = 'مستخدم متصل'
        verbose_name_plural = 'المستخدمون المتصلون'
    
    def __str__(self):
        return f"{self.user.email} - {self.room.name} ({'online' if self.is_online else 'offline'})"
    
    def update_last_seen(self):
        """تحديث وقت آخر ظهور"""
        self.last_seen = timezone.now()
        self.save()
    
    def set_online(self):
        """تعيين المستخدم كمتصلة"""
        self.is_online = True
        self.update_last_seen()
        print(f"✅ {self.user.email} أصبح متصلاً في {self.room.name}")
    
    def set_offline(self):
        """تعيين المستخدم كغير متصل"""
        self.is_online = False
        self.update_last_seen()
        print(f"🔴 {self.user.email} أصبح غير متصل في {self.room.name}")
    
    def is_recently_online(self, minutes=5):
        """التحقق إذا كان المستخدم متصل مؤخراً"""
        return (timezone.now() - self.last_seen).total_seconds() < minutes * 60
    
    def is_currently_online(self):
        """التحقق إذا كان المستخدم متصلاً حالياً (في آخر دقيقتين)"""
        return self.is_online and (timezone.now() - self.last_seen).total_seconds() < 120


class TypingStatus(BaseModel):
    """تتبع حالة الكتابة للمستخدمين"""
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='typing_statuses')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='typing_statuses')
    is_typing = models.BooleanField(default=False)
    last_typed = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['room', 'user']
        verbose_name = 'حالة الكتابة'
        verbose_name_plural = 'حالات الكتابة'
    
    def __str__(self):
        return f"{self.user.email} - {'يكتب' if self.is_typing else 'توقف'}"
    
    def start_typing(self):
        """بدء حالة الكتابة"""
        self.is_typing = True
        self.save()
    
    def stop_typing(self):
        """إيقاف حالة الكتابة"""
        self.is_typing = False
        self.save()
    
    def is_currently_typing(self, seconds=5):
        """التحقق إذا كان المستخدم يكتب حالياً"""
        return self.is_typing and (timezone.now() - self.last_typed).total_seconds() < seconds