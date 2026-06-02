import { handleTyping, stopTyping } from '../api/typing.js';
import { sendMessage } from '../api/messages.js';
import { replyingTo, clearReplyingTo } from '../core/config.js';
import { showSystemMessage } from '../core/utils.js';

// ========== إدارة منطقة الإدخال ==========
export function handleInputChange(textarea) {
    if (!textarea) return;
    
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
    
    const sendButton = document.getElementById('send-button');
    if (sendButton) {
        if (textarea.value.trim()) {
            sendButton.classList.add('active');
        } else {
            sendButton.classList.remove('active');
        }
    }
    
    // تفعيل مؤشر الكتابة فقط إذا كان هناك نص
    if (textarea.value.trim()) {
        handleTyping();
    } else {
        stopTyping();
    }
}

export function initInputEvents() {
    const messageInput = document.getElementById('message-input');
    const sendButton = document.getElementById('send-button');
    
    if (messageInput) {
        // إزالة الأحداث القديمة أولاً لمنع التكرار
        messageInput.removeEventListener('keydown', handleKeyDown);
        messageInput.removeEventListener('input', handleInput);
        messageInput.removeEventListener('blur', handleBlur);
        
        // إضافة الأحداث الجديدة
        messageInput.addEventListener('keydown', handleKeyDown);
        messageInput.addEventListener('input', handleInput);
        messageInput.addEventListener('blur', handleBlur);
        
        console.log('✅ تم تهيئة أحداث الإدخال');
    }

    if (sendButton) {
        sendButton.removeEventListener('click', handleSendClick);
        sendButton.addEventListener('click', handleSendClick);
    }
    
    // أحداث رفع الملفات
    initFileUploadEvents();
}

// معالجات الأحداث المنفصلة
function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        console.log('⌨️ ضغط على Enter للإرسال');
        handleSendMessage();
    }
}

function handleInput(e) {
    handleInputChange(e.target);
}

function handleBlur() {
    stopTyping();
}

function handleSendClick() {
    console.log('🖱️ ضغط على زر الإرسال');
    handleSendMessage();
}

export function handleSendMessage() {
    const messageInput = document.getElementById('message-input');
    const message = messageInput?.value.trim();
    
    if (!message) return;
    
    // إيقاف الكتابة قبل الإرسال
    stopTyping();
    
    sendMessage(message, replyingTo)
        .then(() => {
            if (replyingTo) {
                clearReplyingTo();
                closeReply();
            }
        })
        .catch(error => {
            console.error('فشل في إرسال الرسالة:', error);
        });
}

export function initFileUploadEvents() {
    const imageInput = document.getElementById('image-input');
    const fileInput = document.getElementById('file-input');
    
    if (imageInput) {
        imageInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                if (file.size > 5 * 1024 * 1024) {
                    showSystemMessage('حجم الصورة كبير جداً (الحد الأقصى 5MB)', 'error');
                    return;
                }
                import('../api/messages.js').then(({ sendImage }) => {
                    sendImage(file);
                });
                e.target.value = '';
            }
        });
    }
    
    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                if (file.size > 10 * 1024 * 1024) {
                    showSystemMessage('حجم الملف كبير جداً (الحد الأقصى 10MB)', 'error');
                    return;
                }
                import('../api/messages.js').then(({ sendFile }) => {
                    sendFile(file);
                });
                e.target.value = '';
            }
        });
    }
}

export function closeReply() {
    const preview = document.getElementById('reply-preview');
    if (preview) {
        preview.style.display = 'none';
    }
}