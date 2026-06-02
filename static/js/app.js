// تهيئة التطبيق مع مدير الأيقونة
document.addEventListener('DOMContentLoaded', function() {
    // تهيئة مدير الأيقونة
    window.iconManager.init();
    
    // مثال: تحديث العداد من بيانات Django
    const initialUnread = parseInt(document.body.dataset.unreadCount || '0');
    if (initialUnread > 0) {
        window.iconManager.showUnreadCount(initialUnread);
    }
    
    // استمع للرسائل الجديدة (مثال مع WebSocket أو AJAX)
    setupMessageHandlers();
});

function setupMessageHandlers() {
    // محاكاة استقبال رسائل جديدة
    setInterval(() => {
        // هذا مثال - استبدله بمنطق WebSocket الفعلي
        simulateNewMessage();
    }, 30000);
}

function simulateNewMessage() {
    // زيادة العداد لمحاكاة رسالة جديدة
    window.iconManager.incrementUnread();
    
    // إشعار بصري
    showNotification('رسالة جديدة');
}

function showNotification(message) {
    // يمكنك استخدام مكتبة الإشعارات الخاصة بك
    if ('Notification' in window && Notification.permission === 'granted') {
        new Notification('دردشة الواتساب', {
            body: message,
            icon: '/static/icons/favicon-32x32.png'
        });
    }
}