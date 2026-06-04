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
    // Avoid showing duplicate system messages with same key
    const key = 'sys-' + encodeURIComponent(message);
    if (chatMessages.querySelector(`.system-message[data-key="${key}"]`)) return;

    const systemMessage = document.createElement('div');
    systemMessage.className = 'system-message';
    systemMessage.setAttribute('data-key', key);
    systemMessage.style.cssText = `
        background: ${type === 'error' ? '#f8d7da' : '#d4edda'};
        color: ${type === 'error' ? '#721c24' : '#155724'};
        padding: 10px 12px;
        border-radius: 8px;
        margin: 8px 0;
    `;
    systemMessage.textContent = message;
    chatMessages.appendChild(systemMessage);

    // Only auto-scroll if the user is near the bottom
    const isNearBottom = chatMessages.scrollHeight - chatMessages.clientHeight <= chatMessages.scrollTop + 100;
    if (isNearBottom) {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
}

export function clearSystemMessages(keyContains = null) {
    const chatMessages = document.getElementById('chat-messages');
    if (!chatMessages) return;
    const systemMessages = Array.from(chatMessages.querySelectorAll('.system-message'));
    systemMessages.forEach(el => {
        if (!keyContains) {
            el.remove();
        } else {
            const key = el.getAttribute('data-key') || '';
            if (key.includes(encodeURIComponent(keyContains))) el.remove();
        }
    });
}

// Sticky banner shown at top of chat for persistent notices (e.g., offline)
export function showStickyBanner(message, type = 'info') {
    const container = document.getElementById('chat-container') || document.body;
    let banner = document.getElementById('system-banner');
    if (!banner) {
        banner = document.createElement('div');
        banner.id = 'system-banner';
        banner.style.cssText = `
            position: sticky;
            top: 0;
            z-index: 9999;
            width: 100%;
            display: flex;
            justify-content: center;
            padding: 8px 12px;
            box-sizing: border-box;
        `;
        container.insertBefore(banner, container.firstChild);
    }

    banner.textContent = message;
    if (type === 'error') {
        banner.style.background = '#fdecea';
        banner.style.color = '#721c24';
        banner.style.borderBottom = '1px solid rgba(114,28,36,0.08)';
    } else {
        banner.style.background = '#e9f7ef';
        banner.style.color = '#155724';
        banner.style.borderBottom = '1px solid rgba(21,87,36,0.06)';
    }
}

export function clearStickyBanner() {
    const banner = document.getElementById('system-banner');
    if (banner) banner.remove();
}

export function createCacheClearButton() {
    const actions = document.querySelector('.header-actions');
    const header = document.querySelector('.chat-header');
    const container = actions || header || document.getElementById('chat-container') || document.body;
    if (!container) return;

    // Avoid duplicate button
    if (document.getElementById('clear-cache-button')) return;

    const btn = document.createElement('button');
    btn.id = 'clear-cache-button';
    btn.className = 'header-btn cache-btn';
    btn.textContent = 'مسح الكاش';
    btn.title = 'مسح الرسائل المخزنة محلياً';
    btn.addEventListener('click', async () => {
        try {
            const cfg = await import('../core/config.js');
            cfg.clearCacheStorage();
            clearStickyBanner();
            showSystemMessage('تم مسح الكاش المحلي', 'info');
            setTimeout(() => clearSystemMessages('تم مسح الكاش المحلي'), 3000);
        } catch (e) {
            console.error('خطأ في مسح الكاش:', e);
            showSystemMessage('فشل في مسح الكاش', 'error');
        }
    });

    if (actions) {
        actions.appendChild(btn);
    } else if (header) {
        header.appendChild(btn);
    } else {
        container.appendChild(btn);
    }
}