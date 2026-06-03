import { roomId, lastMessageId, updateLastMessageId, isSending, setSendingStatus, currentUser } from '../core/config.js';
import { getCookie } from '../core/constants.js';
import { scrollToBottom, showSystemMessage } from '../core/utils.js';
import { stopTyping } from './typing.js';

// ========== دوال جلب الرسائل ==========
export async function fetchMessages() {
    try {
        if (!roomId) {
            console.error('❌ roomId غير صالح:', roomId);
            return [];
        }

        const url = `/chat/messages/${roomId}/?last_id=${lastMessageId}`;
        console.log('📡 جلب الرسائل من:', url);
        
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`فشل في جلب الرسائل: ${response.status}`);
        }
        
        const messages = await response.json();
        
        if (messages.error) {
            throw new Error(messages.error);
        }
        
        console.log(`✅ تم جلب ${messages.length} رسالة`);
        return messages;
        
    } catch (error) {
        console.error('❌ خطأ في جلب الرسائل:', error);
        showSystemMessage('فشل في تحميل الرسائل', 'error');
        return [];
    }
}

// ========== دوال إرسال الرسائل ==========
export async function sendMessage(message, replyTo = null) {
    if (isSending) {
        console.log('⏳ جاري إرسال رسالة سابقة...');
        return;
    }
    
    const messageInput = document.getElementById('message-input');
    const messageText = message || messageInput?.value.trim();
    
    if (!messageText) {
        console.log('❌ لا يوجد نص للإرسال');
        return;
    }

    let tempMessageId;

    try {
        setSendingStatus(true);
        console.log('🚀 بدء إرسال الرسالة:', messageText);
        
        // إيقاف مؤشر الكتابة قبل الإرسال
        stopTyping();
        
        tempMessageId = 'temp_' + Date.now();
        const tempTimestamp = new Date().toLocaleTimeString('ar-EG', {hour: '2-digit', minute:'2-digit'});
        const messageData = {
            id: tempMessageId,
            sender: currentUser || window.CURRENT_USER || 'غير معروف',
            sender_display: currentUser || window.CURRENT_USER || 'غير معروف',
            message: messageText,
            timestamp: tempTimestamp,
            message_type: 'text'
        };
        
        if (replyTo) {
            const replyContent = document.getElementById('reply-content')?.textContent;
            messageData.reply_to = {
                id: replyTo,
                sender: document.getElementById('reply-sender')?.textContent.replace('رد على ', ''),
                message: replyContent
            };
        }
        
        // استيراد دالة العرض بشكل ديناميكي
        const { displayEnhancedMessage } = await import('../ui/messages.js');
        displayEnhancedMessage(messageData);
        
        if (messageInput) {
            messageInput.value = '';
            handleInputChange(messageInput);
        }
        
        const requestData = { 
            message: messageText 
        };
        
        if (replyTo && !replyTo.startsWith('temp_')) {
            requestData.reply_to = replyTo;
        }
        
        console.log('📤 إرسال البيانات:', requestData);
        
        if (!roomId) {
            throw new Error('معرف الغرفة غير صالح');
        }
        
        const response = await fetch(`/chat/send/${roomId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(requestData)
        });

        console.log('📨 حالة الاستجابة:', response.status, response.statusText);
        
        if (response.ok) {
            const data = await response.json();
            console.log('✅ تم إرسال الرسالة بنجاح:', data);

            if (tempMessageId) {
                const tempMsg = document.querySelector(`[data-message-id="${tempMessageId}"]`);
                if (tempMsg) {
                    const updatedMessageData = {
                        id: data.message_id,
                        sender: data.sender || currentUser || window.CURRENT_USER,
                        sender_display: data.sender_display || data.sender || currentUser || window.CURRENT_USER,
                        message: messageText,
                        timestamp: data.timestamp,
                        message_type: 'text',
                        reply_to: data.reply_to || null,
                    };

                    tempMsg.dataset.messageId = data.message_id;
                    tempMsg.dataset.sender = updatedMessageData.sender_display;
                    const { updateExistingMessage } = await import('../ui/messages.js');
                    updateExistingMessage(tempMsg, updatedMessageData);
                    updateLastMessageId(data.message_id);
                }
            }

            return data;
        } else {
            let errorData;
            try {
                errorData = await response.json();
            } catch (e) {
                errorData = { error: 'فشل في تحليل استجابة الخادم' };
            }
            
            console.error('❌ خطأ في الاستجابة:', errorData);
            throw new Error(errorData.error || `فشل في إرسال الرسالة: ${response.status}`);
        }
        
    } catch (error) {
        console.error('❌ خطأ في الإرسال:', error);
        showSystemMessage('فشل في إرسال الرسالة: ' + error.message, 'error');
        
        if (tempMessageId) {
            const tempMsg = document.querySelector(`[data-message-id="${tempMessageId}"]`);
            if (tempMsg) {
                tempMsg.remove();
            }
        }
        throw error;
    } finally {
        setSendingStatus(false);
        console.log('🔄 حالة الإرسال:', isSending);
    }
}

export async function sendImage(file) {
    if (!file) return;
    
    try {
        const formData = new FormData();
        formData.append('image', file);
        
        const response = await fetch(`/chat/send-image/${roomId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: formData
        });

        if (response.ok) {
            const data = await response.json();
            console.log('✅ تم إرسال الصورة:', data.message_id);
            return data;
        } else {
            throw new Error('فشل في إرسال الصورة');
        }
    } catch (error) {
        console.error('خطأ في إرسال الصورة:', error);
        showSystemMessage('فشل في إرسال الصورة', 'error');
        throw error;
    }
}

export async function sendFile(file) {
    if (!file) return;
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch(`/chat/send-file/${roomId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: formData
        });

        if (response.ok) {
            const data = await response.json();
            console.log('✅ تم إرسال الملف:', data.file_name);
            return data;
        } else {
            const errorData = await response.json();
            throw new Error(errorData.error);
        }
    } catch (error) {
        console.error('❌ خطأ في إرسال الملف:', error);
        alert('فشل في إرسال الملف: ' + error.message);
        throw error;
    }
}

// ========== دوال مساعدة ==========
function handleInputChange(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
    
    const sendButton = document.getElementById('send-button');
    if (textarea.value.trim()) {
        sendButton?.classList.add('active');
    } else {
        sendButton?.classList.remove('active');
    }
}

// إزالة التصدير المكرر في الأسفل - الدوال مصدرة بالفعل أعلاه