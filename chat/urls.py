from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'chat'

urlpatterns = [
    # الصفحات الأساسية
    path('', views.chat_home, name='home'),
    path('room/<str:room_id>/', views.room_detail, name='room_detail'),
    path('create-room/', views.create_room, name='create_room'),
    path('manage-room/<str:room_id>/', views.manage_room, name='manage_room'),
    
    # الرسائل
    path('messages/<str:room_id>/', views.get_messages, name='get_messages'),
    path('send/<str:room_id>/', views.send_message, name='send_message'),
    path('send-image/<str:room_id>/', views.send_image, name='send_image'),
    path('send-file/<str:room_id>/', views.send_file, name='send_file'),
    
    # البحث والملفات الشخصية
    path('search-rooms/', views.search_rooms, name='search_rooms'),
    path('profile/', views.user_profile, name='user_profile'),
    path('create-test-rooms/', views.create_test_rooms, name='create_test_rooms'),
    path('old/', views.chat_home_old, name='room_old'),
    
    # الدعوات
    path('invite/<str:room_id>/', views.invite_user, name='invite_user'),
    path('invitations/accept/<str:token>/', views.accept_invitation, name='accept_invitation'),
    path('invitations/decline/<str:token>/', views.decline_invitation, name='decline_invitation'),
    path('invitations/my/', views.my_invitations, name='my_invitations'),
    path('invitations/check/<str:token>/', views.check_invitation, name='check_invitation'),
    
    # الوقت الحقيقي
    path('online-status/<str:room_id>/', views.update_online_status, name='update_online_status'),
    path('typing/<str:room_id>/', views.typing_indicator, name='typing_indicator'),
    path('typing-status/<str:room_id>/', views.get_typing_status, name='get_typing_status'),
    
    # ردود الفعل والتحرير
    path('react/<str:message_id>/', views.add_reaction, name='add_reaction'),
    path('unreact/<str:message_id>/', views.remove_reaction, name='remove_reaction'),
    path('edit/<str:message_id>/', views.edit_message, name='edit_message'),
    path('delete/<str:message_id>/', views.delete_message, name='delete_message'),

    path('fix-rooms/', views.fix_all_rooms, name='fix_rooms'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)