# from django.apps import AppConfig


# class ChatConfig(AppConfig):
#     default_auto_field = 'django.db.models.BigAutoField'
#     name = 'chat'

#     def ready(self):
#         import chat.signals  # تسجيل الإشارات

from django.apps import AppConfig

class ChatConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'chat'
    verbose_name = 'ADALChat'
    
    def ready(self):
        """تحميل الإشارات عند بدء التطبيق"""
        import chat.models.signals