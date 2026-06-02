from django.db import models
from django.utils import timezone
import uuid

class BaseModel(models.Model):
    """نموذج أساسي مجرد يحتوي على الحقول المشتركة"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True
        ordering = ['-created_at']

class TimestampMixin(models.Model):
    """مزيج لإضافة الطوابع الزمنية"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True

class UUIDMixin(models.Model):
    """مزيج لإضافة UUID كمعرف رئيسي"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    class Meta:
        abstract = True