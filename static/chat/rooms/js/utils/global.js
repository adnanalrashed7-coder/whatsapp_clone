// ملف للتوافق مع الاستدعاءات القديمة
export function initCompatibility() {
    // جعل الدوال متاحة globally للتوافق
    if (typeof window !== 'undefined') {
        // دوال التنقل
        window.goBack = window.goBack || function() {
            window.history.back();
        };
        
        window.toggleSidePanel = window.toggleSidePanel || function() {
            const panel = document.getElementById('side-panel');
            if (panel) {
                panel.classList.toggle('open');
            }
        };
        
        window.searchInChat = window.searchInChat || function() {
            const searchTerm = prompt('ابحث في المحادثة:');
            if (searchTerm) {
                // تنفيذ البحث
                console.log('بحث عن:', searchTerm);
            }
        };
        
        // دوال الرسائل
        window.sendMessage = window.sendMessage || function() {
            console.log('إرسال رسالة...');
        };
        
        // دوال الإيموجي
        window.toggleEmojiPicker = window.toggleEmojiPicker || function() {
            console.log('تبديل منتقي الإيموجي...');
        };
        
        // دوال التفاعلات
        window.closeReply = window.closeReply || function() {
            const preview = document.getElementById('reply-preview');
            if (preview) {
                preview.style.display = 'none';
            }
        };
        
        console.log('✅ تم تهيئة التوافقية');
    }
}

// التهيئة التلقائية
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initCompatibility);
} else {
    initCompatibility();
}