from django.db import models
from django.utils import timezone
import uuid
from accounts.models import CustomUser
from .base import BaseModel
from .chat_rooms import ChatRoom

class Message(BaseModel):
    MESSAGE_TYPES = [
        ('text', 'نص'),
        ('image', 'صورة'),
        ('file', 'ملف'),
        ('system', 'نظام'),
    ]
    
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField(blank=True)
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES, default='text')
    image = models.ImageField(upload_to='chat_images/', blank=True, null=True)
    file = models.FileField(upload_to='chat_files/', blank=True, null=True)
    file_name = models.CharField(max_length=255, blank=True, null=True)
    file_size = models.IntegerField(default=0)  # حجم الملف بالبايت
    file_type = models.CharField(max_length=50, blank=True, null=True)  # نوع الملف
    timestamp = models.DateTimeField(default=timezone.now)
    is_edited = models.BooleanField(default=False)
    edited_at = models.DateTimeField(blank=True, null=True)
    reply_to = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True)
    deleted_for = models.ManyToManyField(CustomUser, related_name='deleted_messages', blank=True)
    is_deleted = models.BooleanField(default=False)  # للحذف الكامل
    
    class Meta:
        ordering = ['timestamp']
        indexes = [
            models.Index(fields=['room', 'timestamp']),
            models.Index(fields=['sender', 'timestamp']),
        ]
        verbose_name = 'رسالة'
        verbose_name_plural = 'الرسائل'
    
    def __str__(self):
        return f"{self.sender.email}: {self.content[:20]}"
    
    def is_deleted_for_user(self, user):
        """التحقق من حذف الرسالة للمستخدم"""
        return self.deleted_for.filter(id=user.id).exists()
    
    def get_reactions_summary(self):
        """الحصول على ملخص ردود الفعل"""
        return self.reactions.values('reaction_type').annotate(
            count=models.Count('id')
        ).order_by('-count')
    
    def get_file_icon(self):
        """الحصول على أيقونة للملف حسب النوع"""
        if not self.file_type:
            return '📄'
        
        file_type = self.file_type.lower()
        if any(ext in file_type for ext in ['pdf']):
            return '📕'
        elif any(ext in file_type for ext in ['word', 'doc']):
            return '📘'
        elif any(ext in file_type for ext in ['excel', 'xls']):
            return '📗'
        elif any(ext in file_type for ext in ['powerpoint', 'ppt']):
            return '📙'
        elif any(ext in file_type for ext in ['zip', 'rar', 'tar']):
            return '📦'
        elif any(ext in file_type for ext in ['image']):
            return '🖼️'
        elif any(ext in file_type for ext in ['video']):
            return '🎬'
        elif any(ext in file_type for ext in ['audio']):
            return '🎵'
        else:
            return '📄'
    
    def edit(self, new_content):
        """تحرير محتوى الرسالة"""
        if self.content != new_content:
            # حفظ المحتوى القديم في التاريخ
            MessageEditHistory.objects.create(
                message=self,
                old_content=self.content
            )
            self.content = new_content
            self.is_edited = True
            self.edited_at = timezone.now()
            self.save()
            return True
        return False
    
    def delete_for_user(self, user):
        """حذف الرسالة لمستخدم معين"""
        self.deleted_for.add(user)
    
    def delete_for_all(self):
        """حذف الرسالة للجميع"""
        self.is_deleted = True
        self.content = "تم حذف هذه الرسالة"
        self.image = None
        self.file = None
        self.save()
    
    def get_reply_chain(self):
        """الحصول على سلسلة الردود"""
        chain = []
        current = self.reply_to
        while current:
            chain.append(current)
            current = current.reply_to
        return chain

class Reaction(BaseModel):
    REACTION_TYPES = [
        ('like', '👍'),
        ('love', '❤️'),
        ('laugh', '😄'),
        ('wow', '😮'),
        ('sad', '😢'),
        ('angry', '😠'),
        ('fire', '🔥'),
        ('clap', '👏'),
    ]
    
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='reactions')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    reaction_type = models.CharField(max_length=10, choices=REACTION_TYPES)
    
    class Meta:
        unique_together = ['message', 'user']
        ordering = ['created_at']
        verbose_name = 'رد فعل'
        verbose_name_plural = 'ردود الفعل'
    
    def __str__(self):
        return f"{self.user.email} - {self.get_reaction_type_display()} على رسالة {self.message.id}"

class MessageEditHistory(BaseModel):
    """سجل تعديلات الرسائل"""
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='edit_history')
    old_content = models.TextField()
    edited_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-edited_at']
        verbose_name = 'سجل تعديل الرسالة'
        verbose_name_plural = 'سجلات تعديل الرسائل'
    
    def __str__(self):
        return f"تعديل رسالة {self.message.id}"