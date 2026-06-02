import { getCookie } from './constants.js';

// ========== دوال مساعدة عامة ==========
export function formatEnhancedContent(content) {
    if (!content) return '';
    
    // الروابط
    content = content.replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank" class="message-link">$1</a>');
    
    // البريد الإلكتروني
    content = content.replace(/([a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9._-]+)/g, '<a href="mailto:$1" class="message-email">$1</a>');
    
    // الهاشتاغ
    content = content.replace(/#(\w+)/g, '<span class="message-hashtag">#$1</span>');
    
    // الأسطر الجديدة
    content = content.replace(/\n/g, '<br>');
    
    return content;
}

export function formatFileSize(bytes) {
    if (!bytes) return '0 B';
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
}

export function getFileIcon(fileName) {
    if (!fileName) return '📄';
    
    const extension = fileName.split('.').pop().toLowerCase();
    const icons = {
        'pdf': '📕', 'doc': '📘', 'docx': '📘', 'xls': '📗', 'xlsx': '📗',
        'ppt': '📙', 'pptx': '📙', 'zip': '📦', 'rar': '📦', 'mp3': '🎵',
        'wav': '🎵', 'mp4': '🎬', 'avi': '🎬', 'mov': '🎬', 'jpg': '🖼️',
        'jpeg': '🖼️', 'png': '🖼️', 'gif': '🖼️', 'txt': '📄', 'default': '📄'
    };
    
    return icons[extension] || icons['default'];
}

export function showTempMessage(message, type = 'info') {
    const tempMsg = document.createElement('div');
    tempMsg.className = `temp-message ${type}`;
    tempMsg.textContent = message;
    tempMsg.style.cssText = `
        position: fixed;
        top: 20px;
        left: 50%;
        transform: translateX(-50%);
        background: ${type === 'success' ? '#28a745' : type === 'error' ? '#dc3545' : '#17a2b8'};
        color: white;
        padding: 12px 20px;
        border-radius: 8px;
        z-index: 10000;
        animation: slideDown 0.3s ease;
    `;
    
    document.body.appendChild(tempMsg);
    
    setTimeout(() => {
        tempMsg.remove();
    }, 3000);
}

export function scrollToBottom() {
    const chatMessages = document.getElementById('chat-messages');
    const isNearBottom = chatMessages.scrollHeight - chatMessages.clientHeight <= chatMessages.scrollTop + 100;
    
    if (isNearBottom) {
        setTimeout(() => {
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }, 100);
    }
}

export function isMessageNew(messageData) {
    if (messageData.timestamp) {
        const messageTime = new Date(messageData.timestamp);
        const currentTime = new Date();
        return (currentTime - messageTime) < 10000;
    }
    return true;
}

export function closeAllPickers() {
    // إغلاق جميع منتقيات التفاعل
    const reactionPickers = document.querySelectorAll('[id^="reaction-picker-"]');
    reactionPickers.forEach(picker => picker.remove());
    
    // إغلاق خيارات الحذف
    closeDeleteOptions();
    
    // إغلاق منتقي الإيموجي
    const emojiPicker = document.getElementById('emoji-picker');
    if (emojiPicker) {
        emojiPicker.style.display = 'none';
    }
}

export function addTempMessageStyles() {
    if (document.getElementById('temp-message-styles')) return;
    
    const style = document.createElement('style');
    style.id = 'temp-message-styles';
    style.textContent = `
        .message.temp-message {
            opacity: 0.7;
            pointer-events: none;
        }
        
        .message.temp-message .message-actions {
            display: none !important;
        }
        
        .message.temp-message:hover {
            transform: none;
            background: inherit;
        }
        
        .temp-message-indicator {
            font-size: 10px;
            color: #888;
            font-style: italic;
            margin-top: 5px;
        }
    `;
    document.head.appendChild(style);
}

// ========== دوال خاصة بالرسائل ==========
export function addMessageHoverEvents(messageElement) {
    messageElement.addEventListener('mouseenter', function() {
        const actions = this.querySelector('.message-actions');
        if (actions) {
            actions.style.display = 'flex';
        }
    });
    
    messageElement.addEventListener('mouseleave', function() {
        const actions = this.querySelector('.message-actions');
        if (actions && !this.querySelector('.delete-options-container')) {
            actions.style.display = 'none';
        }
    });
}

export function animateMessageAppearance(messageElement) {
    messageElement.style.opacity = '0';
    messageElement.style.transform = 'translateY(20px)';
    
    setTimeout(() => {
        messageElement.style.transition = 'all 0.3s ease';
        messageElement.style.opacity = '1';
        messageElement.style.transform = 'translateY(0)';
    }, 10);
}

// ========== دوال مساعدة إضافية ==========
export function closeDeleteOptions() {
    const deleteOptions = document.querySelector('.delete-options-container');
    if (deleteOptions) {
        deleteOptions.remove();
    }
    
    const messageActions = document.querySelectorAll('.message-actions');
    messageActions.forEach(actions => {
        actions.style.display = 'flex';
    });
}

export function showSystemMessage(message, type = 'info') {
    const chatMessages = document.getElementById('chat-messages');
    if (!chatMessages) return;
    
    const systemMessage = document.createElement('div');
    systemMessage.className = 'system-message';
    systemMessage.style.cssText = `
        background: ${type === 'error' ? '#f8d7da' : '#d4edda'};
        color: ${type === 'error' ? '#721c24' : '#155724'};
    `;
    systemMessage.textContent = message;
    chatMessages.appendChild(systemMessage);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}