from django.db import models
from django.utils import timezone
import uuid
from accounts.models import CustomUser
from .base import BaseModel

class ChatRoom(BaseModel):
    ROOM_TYPES = [
        ('public', 'عامة'),
        ('private', 'خاصة'),
        ('group', 'مجموعة'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    room_type = models.CharField(max_length=10, choices=ROOM_TYPES, default='public')
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='created_rooms')
    is_active = models.BooleanField(default=True)
    max_participants = models.IntegerField(default=50)
    
    # للمجموعات الخاصة
    participants = models.ManyToManyField(CustomUser, related_name='chat_rooms', blank=True)
    admins = models.ManyToManyField(CustomUser, related_name='admin_rooms', blank=True)
    
    class Meta:
        unique_together = ['name', 'room_type']
        ordering = ['-created_at']
        verbose_name = 'غرفة دردشة'
        verbose_name_plural = 'غرف الدردشة'
    
    def __str__(self):
        return f"{self.name} ({self.get_room_type_display()})"
    
    def get_online_count(self):
        """الحصول على عدد المستخدمين المتصلين في الغرفة"""
        try:
            from .realtime import OnlineUser
            return OnlineUser.objects.filter(
                room=self,
                is_online=True
            ).distinct().count()
        except Exception as e:
            print(f"Error in get_online_count: {e}")
            return 0
        
    def add_online_user(self, user):
        """إضافة مستخدم إلى قائمة المتصلين"""
        try:
            from .realtime import OnlineUser
            online_user, created = OnlineUser.objects.get_or_create(
                user=user,
                room=self,
                defaults={'is_online': True}
            )
            
            if not created:
                online_user.set_online()
            else:
                print(f"✅ تم إنشاء حالة اتصال جديدة لـ {user.email} في {self.name}")
            
            return True
        except Exception as e:
            print(f"Error adding online user: {e}")
            return False


    def remove_online_user(self, user):
        """إزالة مستخدم من قائمة المتصلين"""
        try:
            from .realtime import OnlineUser
            OnlineUser.objects.filter(
                user=user,
                room=self
            ).update(is_online=False, last_seen=timezone.now())
            return True
        except Exception as e:
            print(f"Error removing online user: {e}")
            return False
    
    def update_online_user(self, user):
        """تحديث حالة المستخدم المتصل"""
        try:
            from .realtime import OnlineUser
            online_user = OnlineUser.objects.get(user=user, room=self)
            online_user.last_seen = timezone.now()
            online_user.save()
            return True
        except OnlineUser.DoesNotExist:
            return False
    
    def get_online_users(self):
        """جلب قائمة المستخدمين المتصلين - طريقة مبسطة"""
        try:
            from .realtime import OnlineUser
            online_statuses = OnlineUser.objects.filter(room=self, is_online=True)
            online_users = [status.user for status in online_statuses]
            return online_users
        except Exception as e:
            print(f"Error in get_online_users: {e}")
            return []
    
    def can_join(self, user):
        """التحقق من إمكانية انضمام المستخدم للغرفة"""
        if self.room_type == 'public':
            return True
        elif self.room_type == 'private':
            return self.participants.filter(id=user.id).exists()
        return False
    
    def get_participants_count(self):
        """الحصول على عدد المشاركين في الغرفة"""
        return self.participants.count()
    
    def get_message_count(self):
        """الحصول على عدد الرسائل في الغرفة"""
        from .messages import Message
        return Message.objects.filter(room=self).count()

    def ensure_creator_is_participant(self):
        """التأكد من أن منشئ الغرفة مضاف كمشارك ومشرف"""
        if not self.participants.filter(id=self.created_by.id).exists():
            self.participants.add(self.created_by)
            print(f"✅ تم إضافة المنشئ كمشارك في {self.name}")
        
        if not self.admins.filter(id=self.created_by.id).exists():
            self.admins.add(self.created_by)
            print(f"✅ تم إضافة المنشئ كمشرف في {self.name}")
        
        return True

    @classmethod
    def get_private_chat_name(cls, user1, user2):
        """إنشاء اسم ثابت للمحادثة الخاصة بين مستخدمين."""
        sorted_ids = sorted([str(user1.id), str(user2.id)])
        return f"dm_{sorted_ids[0]}_{sorted_ids[1]}"

    @classmethod
    def get_or_create_private_chat(cls, inviter, invited_user):
        """إنشاء أو جلب غرفة دردشة خاصة لطلب دعوة بين مستخدمين."""
        if inviter.id == invited_user.id:
            raise ValueError('لا يمكن إرسال دعوة للدردشة الخاصة لنفس المستخدم')

        room_name = cls.get_private_chat_name(inviter, invited_user)
        description = f"دردشة خاصة بين {inviter.email} و {invited_user.email}"

        room, created = cls.objects.get_or_create(
            name=room_name,
            room_type='private',
            defaults={
                'created_by': inviter,
                'description': description,
                'max_participants': 2
            }
        )

        if created:
            room.participants.add(inviter, invited_user)
            room.admins.add(inviter)
            room.save()
            print(f"✅ تم إنشاء غرفة خاصة جديدة: {room.name}")

        return room

    def is_user_online(self, user):
        """التحقق إذا كان المستخدم متصلاً بالغرفة"""
        try:
            from .realtime import OnlineUser
            return OnlineUser.objects.filter(
                user=user,
                room=self,
                is_online=True
            ).exists()
        except Exception as e:
            print(f"Error checking online status: {e}")
            return False


class RoomInvitation(BaseModel):
    """نموذج لدعوات الغرف"""
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='invitations')
    invited_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_invitations')
    invited_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='received_invitations')
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    is_accepted = models.BooleanField(default=False)
    is_declined = models.BooleanField(default=False)
    expires_at = models.DateTimeField()

    class Meta:
        unique_together = ['room', 'invited_user']
        ordering = ['-created_at']
        verbose_name = 'دعوة غرفة'
        verbose_name_plural = 'دعوات الغرف'
    
    def __str__(self):
        return f"دعوة {self.invited_user.email} إلى {self.room.name}"
    
    def is_expired(self):
        """التحقق من انتهاء صلاحية الدعوة"""
        return timezone.now() > self.expires_at
    
    def is_active(self):
        """التحقق من أن الدعوة فعالة"""
        return not self.is_accepted and not self.is_declined and not self.is_expired()
    
    def get_status_display(self):
        """الحصول على حالة الدعوة كنص"""
        if self.is_accepted:
            return "مقبولة"
        elif self.is_declined:
            return "مرفوضة"
        elif self.is_expired():
            return "منتهية"
        else:
            return "قيد الانتظار"
    
    def accept(self):
        """قبول الدعوة"""
        if self.is_active():
            self.is_accepted = True
            self.save()
            # إضافة المستخدم إلى الغرفة
            self.room.participants.add(self.invited_user)
            return True
        return False
    
    def decline(self):
        """رفض الدعوة"""
        if self.is_active():
            self.is_declined = True
            self.save()
            return True
        return False


class Friendship(BaseModel):
    """نموذج للصداقة الثنائية بين مستخدمين."""
    user1 = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='friendships_initiated')
    user2 = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='friendships_received')

    class Meta:
        unique_together = [('user1', 'user2')]
        ordering = ['-created_at']
        verbose_name = 'صداقة'
        verbose_name_plural = 'الصّداقات'

    def save(self, *args, **kwargs):
        if self.user1.id > self.user2.id:
            self.user1, self.user2 = self.user2, self.user1
        super().save(*args, **kwargs)

    @classmethod
    def be_friends(cls, user_a, user_b):
        if user_a.id == user_b.id:
            return False
        user1, user2 = (user_a, user_b) if user_a.id < user_b.id else (user_b, user_a)
        return cls.objects.filter(user1=user1, user2=user2).exists()

    @classmethod
    def create_friendship(cls, user_a, user_b):
        if user_a.id == user_b.id:
            return None
        user1, user2 = (user_a, user_b) if user_a.id < user_b.id else (user_b, user_a)
        friendship, created = cls.objects.get_or_create(user1=user1, user2=user2)
        return friendship

    @classmethod
    def get_friends(cls, user):
        friendships = cls.objects.filter(models.Q(user1=user) | models.Q(user2=user))
        friends = []
        for friendship in friendships:
            friends.append(friendship.user2 if friendship.user1 == user else friendship.user1)
        return friends


class FriendRequest(BaseModel):
    """نموذج لطلبات الصداقة بين المستخدمين."""
    STATUS_CHOICES = [
        ('pending', 'قيد الانتظار'),
        ('accepted', 'مقبول'),
        ('declined', 'مرفوض')
    ]

    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_friend_requests')
    receiver = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='received_friend_requests')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    expires_at = models.DateTimeField()

    class Meta:
        unique_together = [('sender', 'receiver')]
        ordering = ['-created_at']
        verbose_name = 'طلب صداقة'
        verbose_name_plural = 'طلبات الصداقة'

    def __str__(self):
        return f"طلب صداقة من {self.sender.email} إلى {self.receiver.email}"

    def is_expired(self):
        return timezone.now() > self.expires_at

    def is_active(self):
        return self.status == 'pending' and not self.is_expired()

    def accept(self):
        if not self.is_active():
            return False
        self.status = 'accepted'
        self.save()
        Friendship.create_friendship(self.sender, self.receiver)
        room = ChatRoom.get_or_create_private_chat(self.sender, self.receiver)
        return room

    def decline(self):
        if not self.is_active():
            return False
        self.status = 'declined'
        self.save()
        return True

    def get_status_display(self):
        if self.status == 'accepted':
            return 'مقبول'
        elif self.status == 'declined':
            return 'مرفوض'
        return 'قيد الانتظار'
