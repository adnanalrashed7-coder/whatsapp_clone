"""
ملف models.py الرئيسي - يعمل كملف توجيه فقط
يتم استيراد جميع النماذج من المجلد models
"""

# استيراد جميع النماذج
from .models import *

# استيراد الإشارات
from .models.signals import *

# يمكنك إضافة أي نماذج إضافية هنا إذا لزم الأمر
# أو إعادة تعريف بعض النماذج إذا كانت تحتاج تعديلات خاصة

# التأكد من تحميل الإشارات
default_app_config = 'chat.apps.ChatConfig'
# from django.db import models
# from accounts.models import CustomUser
# from django.utils import timezone
# import uuid

# class ChatRoom(models.Model):
#     ROOM_TYPES = [
#         ('public', 'عامة'),
#         ('private', 'خاصة'),
#         ('group', 'مجموعة'),
#     ]
    
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     name = models.CharField(max_length=100)
#     description = models.TextField(blank=True, null=True)
#     room_type = models.CharField(max_length=10, choices=ROOM_TYPES, default='public')
#     created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='created_rooms')
#     created_at = models.DateTimeField(auto_now_add=True)
#     is_active = models.BooleanField(default=True)
#     max_participants = models.IntegerField(default=50)
    
#     # للمجموعات الخاصة
#     participants = models.ManyToManyField(CustomUser, related_name='chat_rooms', blank=True)
#     admins = models.ManyToManyField(CustomUser, related_name='admin_rooms', blank=True)
#     online_users = models.ManyToManyField(
#         CustomUser, 
#         through='OnlineUser',
#         related_name='online_rooms',
#         blank=True
#     )
    
#     class Meta:
#         unique_together = ['name', 'room_type']
#         ordering = ['-created_at']
    
#     def __str__(self):
#         return f"{self.name} ({self.get_room_type_display()})"
    
#     def get_online_count(self):
#         """الحصول على عدد المستخدمين المتصلين في الغرفة"""
#         try:
#             # استخدام OnlineUser model للعد
#             return self.online_users.filter(
#                 onlineuser__is_online=True
#             ).distinct().count()
#         except Exception as e:
#             print(f"Error in get_online_count: {e}")
#             return 0
        
#     def add_online_user(self, user):
#         """إضافة مستخدم إلى قائمة المتصلين"""
#         try:
#             online_user, created = OnlineUser.objects.get_or_create(
#                 user=user,
#                 room=self,
#                 defaults={'is_online': True}
#             )
#             if not created:
#                 online_user.is_online = True
#                 online_user.last_seen = timezone.now()
#                 online_user.save()
#             return True
#         except Exception as e:
#             print(f"Error adding online user: {e}")
#             return False
    
#     def remove_online_user(self, user):
#         """إزالة مستخدم من قائمة المتصلين"""
#         try:
#             OnlineUser.objects.filter(
#                 user=user,
#                 room=self
#             ).update(is_online=False, last_seen=timezone.now())
#             return True
#         except Exception as e:
#             print(f"Error removing online user: {e}")
#             return False
    
#     def update_online_user(self, user):
#         """تحديث حالة المستخدم المتصل"""
#         try:
#             online_user = OnlineUser.objects.get(user=user, room=self)
#             online_user.last_seen = timezone.now()
#             online_user.save()
#             return True
#         except OnlineUser.DoesNotExist:
#             return False
    
#     def get_online_users(self):
#         """جلب قائمة المستخدمين المتصلين"""
#         return self.online_users.filter(
#             onlineuser__is_online=True
#         ).distinct()

#     def can_join(self, user):
#         if self.room_type == 'public':
#             return True
#         elif self.room_type == 'private':
#             return self.participants.filter(id=user.id).exists()
#         return False

# class RoomInvitation(models.Model):
#     room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='invitations')
#     invited_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_invitations')
#     invited_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='received_invitations')
#     token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
#     is_accepted = models.BooleanField(default=False)
#     is_declined = models.BooleanField(default=False)
#     created_at = models.DateTimeField(auto_now_add=True)
#     expires_at = models.DateTimeField()

#     class Meta:
#         unique_together = ['room', 'invited_user']
#         ordering = ['-created_at']
    
#     def __str__(self):
#         return f"دعوة {self.invited_user.email} إلى {self.room.name}"
    
#     def is_expired(self):
#         return timezone.now() > self.expires_at
    
#     def is_active(self):
#         return not self.is_accepted and not self.is_declined and not self.is_expired()

    
#     def get_status_display(self):
#         """الحصول على حالة الدعوة كنص"""
#         if self.is_accepted:
#             return "مقبولة"
#         elif self.is_declined:
#             return "مرفوضة"
#         elif self.is_expired():
#             return "منتهية"
#         else:
#             return "قيد الانتظار"


# class Message(models.Model):
#     MESSAGE_TYPES = [
#         ('text', 'نص'),
#         ('image', 'صورة'),
#         ('file', 'ملف'),
#         ('system', 'نظام'),
#     ]
    
#     # الحقول الحالية...
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
#     sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
#     content = models.TextField(blank=True)
#     message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES, default='text')
#     image = models.ImageField(upload_to='chat_images/', blank=True, null=True)
#     file = models.FileField(upload_to='chat_files/', blank=True, null=True)
#     file_name = models.CharField(max_length=255, blank=True, null=True)
#     file_size = models.IntegerField(default=0)  # حجم الملف بالبايت
#     file_type = models.CharField(max_length=50, blank=True, null=True)  # نوع الملف
#     timestamp = models.DateTimeField(default=timezone.now)
#     is_edited = models.BooleanField(default=False)
#     edited_at = models.DateTimeField(blank=True, null=True)
#     reply_to = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True)
#     deleted_for = models.ManyToManyField(CustomUser, related_name='deleted_messages', blank=True)
#     is_deleted = models.BooleanField(default=False)  # للحذف الكامل
    
#     class Meta:
#         ordering = ['timestamp']
#         indexes = [
#             models.Index(fields=['room', 'timestamp']),
#             models.Index(fields=['sender', 'timestamp']),
#         ]
    
#     def __str__(self):
#         return f"{self.sender.email}: {self.content[:20]}"
    
#     def is_deleted_for_user(self, user):
#         return self.deleted_for.filter(id=user.id).exists()
    
#     def get_reactions_summary(self):
#         """الحصول على ملخص ردود الفعل"""
#         from django.db.models import Count
#         return self.reactions.values('reaction_type').annotate(count=Count('id')).order_by('-count')
    
#     def get_file_icon(self):
#         """الحصول على أيقونة للملف حسب النوع"""
#         if not self.file_type:
#             return '📄'
        
#         file_type = self.file_type.lower()
#         if any(ext in file_type for ext in ['pdf']):
#             return '📕'
#         elif any(ext in file_type for ext in ['word', 'doc']):
#             return '📘'
#         elif any(ext in file_type for ext in ['excel', 'xls']):
#             return '📗'
#         elif any(ext in file_type for ext in ['powerpoint', 'ppt']):
#             return '📙'
#         elif any(ext in file_type for ext in ['zip', 'rar', 'tar']):
#             return '📦'
#         elif any(ext in file_type for ext in ['image']):
#             return '🖼️'
#         elif any(ext in file_type for ext in ['video']):
#             return '🎬'
#         elif any(ext in file_type for ext in ['audio']):
#             return '🎵'
#         else:
#             return '📄'



# # في models.py بعد نموذج Message
# class Reaction(models.Model):
#     REACTION_TYPES = [
#         ('like', '👍'),
#         ('love', '❤️'),
#         ('laugh', '😄'),
#         ('wow', '😮'),
#         ('sad', '😢'),
#         ('angry', '😠'),
#         ('fire', '🔥'),
#         ('clap', '👏'),
#     ]
    
#     message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='reactions')
#     user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
#     reaction_type = models.CharField(max_length=10, choices=REACTION_TYPES)
#     created_at = models.DateTimeField(auto_now_add=True)
    
#     class Meta:
#         unique_together = ['message', 'user']
#         ordering = ['created_at']
    
#     def __str__(self):
#         return f"{self.user.email} - {self.get_reaction_type_display()} على رسالة {self.message.id}"

# class MessageEditHistory(models.Model):
#     message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='edit_history')
#     old_content = models.TextField()
#     edited_at = models.DateTimeField(auto_now_add=True)
    
#     class Meta:
#         ordering = ['-edited_at']
    
#     def __str__(self):
#         return f"تعديل رسالة {self.message.id}"

# # تحديث نموذج Message لإضافة الحقول الجديدة

# class UserProfile(models.Model):
#     user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='chat_profile')
#     display_name = models.CharField(max_length=50, blank=True, null=True)
#     avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
#     status = models.CharField(max_length=20, default='online', choices=[
#         ('online', 'متصل'),
#         ('away', 'بعيد'),
#         ('busy', 'مشغول'),
#         ('offline', 'غير متصل'),
#     ])
#     last_seen = models.DateTimeField(auto_now=True)
#     theme = models.CharField(max_length=20, default='light', choices=[
#         ('light', 'فاتح'),
#         ('dark', 'داكن'),
#         ('auto', 'تلقائي'),
#     ])
    
#     def __str__(self):
#         return f"{self.user.email} Profile"

# # في chat/models.py - تأكد من نموذج OnlineUser
# class OnlineUser(models.Model):
#     user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
#     room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
#     is_online = models.BooleanField(default=False)
#     last_seen = models.DateTimeField(default=timezone.now)
#     joined_at = models.DateTimeField(auto_now_add=True)
    
#     class Meta:
#         unique_together = ['user', 'room']
#         verbose_name = 'مستخدم متصل'
#         verbose_name_plural = 'المستخدمون المتصلون'
    
#     def __str__(self):
#         return f"{self.user.email} - {self.room.name} ({'online' if self.is_online else 'offline'})"


# class TypingStatus(models.Model):
#     room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
#     user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
#     is_typing = models.BooleanField(default=False)
#     last_typed = models.DateTimeField(auto_now=True)
    
#     class Meta:
#         unique_together = ['room', 'user']
#         verbose_name = 'حالة الكتابة'
#         verbose_name_plural = 'حالات الكتابة'
    
#     def __str__(self):
#         return f"{self.user.email} - {'يكتب' if self.is_typing else 'توقف'}"



# # في نهاية chat/models.py أضف هذه الإشارة
# from django.db.models.signals import post_save
# from django.dispatch import receiver

# @receiver(post_save, sender=CustomUser)
# def create_user_profile(sender, instance, created, **kwargs):
#     """إنشاء UserProfile تلقائياً عند إنشاء مستخدم جديد"""
#     if created:
#         UserProfile.objects.create(user=instance)

# @receiver(post_save, sender=CustomUser)
# def save_user_profile(sender, instance, **kwargs):
#     """حفظ UserProfile عند حفظ المستخدم"""
#     if hasattr(instance, 'chat_profile'):
#         instance.chat_profile.save()

# @receiver(post_save, sender=RoomInvitation)
# def send_invitation_notification(sender, instance, created, **kwargs):
#     """إرسال إشعار عند إنشاء دعوة جديدة"""
#     if created:
#         # يمكنك إضافة إشعارات ويب أو إشعارات داخل التطبيق هنا
#         pass