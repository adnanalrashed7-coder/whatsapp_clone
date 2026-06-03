import { currentUser, updateLastMessageId } from '../core/config.js';
import { 
    formatEnhancedContent, 
    getFileIcon, 
    formatFileSize, 
    scrollToBottom, 
    isMessageNew,
    addMessageHoverEvents,
    animateMessageAppearance
} from '../core/utils.js';
import { getReactionEmoji } from '../api/reactions.js';

// ========== دوال عرض الرسائل ==========
export function displayEnhancedMessage(messageData) {
    if (messageData.id && messageData.id.startsWith('temp_')) {
        const tempMsg = document.querySelector(`[data-message-id="${messageData.id}"]`);
        if (tempMsg) {
            tempMsg.remove();
        }
    }
    
    const chatMessages = document.getElementById('chat-messages');
    let messageElement = document.querySelector(`[data-message-id="${messageData.id}"]`);
    
    if (messageElement) {
        updateExistingMessage(messageElement, messageData);
        return;
    }
    
    messageElement = document.createElement('div');
    const isOwnMessage = messageData.sender === currentUser;
    
    messageElement.className = `message ${isOwnMessage ? 'own' : 'other'}`;
    messageElement.dataset.messageId = messageData.id;
    messageElement.dataset.sender = messageData.sender;
    
    // إضافة فئة خاصة للرسائل المؤقتة
    if (messageData.id.startsWith('temp_')) {
        messageElement.classList.add('temp-message');
        messageElement.style.opacity = '0.7';
    }
    
    const messageHTML = buildInteractiveMessageHTML(messageData, isOwnMessage);
    messageElement.innerHTML = messageHTML;
    
    // لا تضيف أحداث التفاعل للرسائل المؤقتة
    if (!messageData.id.startsWith('temp_')) {
        addMessageHoverEvents(messageElement);
    }
    
    chatMessages.appendChild(messageElement);
    
    animateMessageAppearance(messageElement);
    
    if (isMessageNew(messageData)) {
        scrollToBottom();
    }
    
    if (messageData.id && !messageData.id.startsWith('temp_')) {
        updateLastMessageId(messageData.id);
    }
}

export function buildInteractiveMessageHTML(messageData, isOwnMessage) {
    let html = '';
    
    if (!isOwnMessage && messageData.sender !== 'system') {
        html += `<div class="message-sender">${messageData.sender_display || messageData.sender}</div>`;
    }
    
    html += `<div class="message-content">${formatEnhancedContent(messageData.message)}</div>`;
    
    if (messageData.is_edited) {
        html += `<div class="edited-indicator">(تم التحرير)</div>`;
    }
    
    if (messageData.reactions_summary && messageData.reactions_summary.length > 0) {
        html += buildReactionsHTML(messageData.reactions_summary);
    }
    
    if (messageData.image_url) {
        html += `<img src="${messageData.image_url}" class="message-image" alt="صورة مرفوعة" onclick="showImageModal('${messageData.image_url}')">`;
    }
    
    if (messageData.file_url) {
        html += buildFileAttachmentHTML(messageData);
    }
    
    if (messageData.reply_to) {
        html = buildReplyIndicatorHTML(messageData.reply_to) + html;
    }
    
    html += `
        <div class="message-time">
            <i class="far fa-clock"></i>
            ${messageData.timestamp}
            ${messageData.is_edited ? ' <span class="edited-indicator">(تم التحرير)</span>' : ''}
        </div>
        ${buildMessageActionsHTML(messageData, isOwnMessage)}
    `;
    
    return html;
}

export function buildReactionsHTML(reactionsSummary) {
    return `
        <div class="message-reactions">
            ${reactionsSummary.map(reaction => 
                `<span class="reaction-item" title="${reaction.count} تفاعل">
                    ${getReactionEmoji(reaction.reaction_type)} ${reaction.count}
                </span>`
            ).join('')}
        </div>
    `;
}

export function buildFileAttachmentHTML(messageData) {
    const fileIcon = getFileIcon(messageData.file_name);
    const fileSize = formatFileSize(messageData.file_size);
    
    return `
        <div class="file-preview">
            <a href="${messageData.file_url}" target="_blank" download="${messageData.file_name || 'file'}">
                <span class="file-icon">${fileIcon}</span>
                <div class="file-info">
                    <div class="file-name">${messageData.file_name || 'ملف مرفق'}</div>
                    <div class="file-size">${fileSize}</div>
                </div>
            </a>
        </div>
    `;
}

export function buildReplyIndicatorHTML(replyTo) {
    return `
        <div class="reply-indicator">
            <div class="reply-sender">↩️ رد على ${replyTo.sender}</div>
            <div class="reply-content">${replyTo.message}</div>
        </div>
    `;
}

export function buildMessageActionsHTML(messageData, isOwnMessage) {
    const isAdmin = messageData.is_admin || false;
    
    // لا تظهر أزرار الإجراءات للرسائل المؤقتة
    if (messageData.id.startsWith('temp_')) {
        return '';
    }
    
    // تنظيف messageId من أي أحرف خاصة
    const safeMessageId = messageData.id.replace(/'/g, "\\'");
    const safeMessageContent = (messageData.message || '').replace(/'/g, "\\'");
    
    return `
        <div class="message-actions">
            <button class="action-btn reaction-btn" title="إضافة رد فعل" 
                    onclick="showReactionPicker('${safeMessageId}', this)">
                😊
            </button>
            <button class="action-btn reply-btn" title="رد على الرسالة" 
                    onclick="replyToMessage('${safeMessageId}', '${messageData.sender_display || messageData.sender}', '${safeMessageContent}')">
                ↩️
            </button>
            <button class="action-btn copy-btn" title="نسخ النص" 
                    onclick="copyMessageText('${safeMessageId}')">
                📋
            </button>
            ${isOwnMessage ? `
                <button class="action-btn edit-btn" title="تحرير الرسالة" 
                        onclick="enableMessageEdit('${safeMessageId}', \`${safeMessageContent}\`)">
                    ✏️
                </button>
                <button class="action-btn delete-btn" title="حذف الرسالة" 
                        onclick="showDeleteOptions('${safeMessageId}')">
                    🗑️
                </button>
            ` : ''}
            ${isAdmin && !isOwnMessage ? `
                <button class="action-btn admin-delete-btn" title="حذف للجميع" 
                        onclick="deleteMessage('${safeMessageId}', true)">
                    ⚠️
                </button>
            ` : ''}
        </div>
    `;
}

export function updateExistingMessage(messageElement, messageData) {
    const isOwnMessage = messageData.sender === currentUser;
    messageElement.className = `message ${isOwnMessage ? 'own' : 'other'}`;
    messageElement.dataset.messageId = messageData.id;
    messageElement.dataset.sender = messageData.sender_display || messageData.sender;

    if (messageData.id && messageData.id.startsWith('temp_')) {
        messageElement.classList.add('temp-message');
        messageElement.style.opacity = '0.7';
    } else {
        messageElement.classList.remove('temp-message');
        messageElement.style.opacity = '';
    }

    const messageHTML = buildInteractiveMessageHTML(messageData, isOwnMessage);
    messageElement.innerHTML = messageHTML;
    addMessageHoverEvents(messageElement);
}

// ========== دوال تفاعل الرسائل ==========
export function initMessageInteractions() {
    const messagesContainer = document.getElementById('chat-messages');
    if (!messagesContainer) return;
    
    messagesContainer.addEventListener('dblclick', function(e) {
        const message = e.target.closest('.message');
        if (message && !message.classList.contains('system-message')) {
            const messageId = message.dataset.messageId;
            // لا تسمح بالتفاعل مع الرسائل المؤقتة
            if (!messageId.startsWith('temp_')) {
                addQuickReaction(messageId, 'like');
            }
        }
    });
    
    messagesContainer.addEventListener('mouseover', function(e) {
        const message = e.target.closest('.message');
        if (message) {
            const messageId = message.dataset.messageId;
            // إخفاء أزرار الإجراءات للرسائل المؤقتة
            if (messageId.startsWith('temp_')) {
                return;
            }
            
            const actions = message.querySelector('.message-actions');
            if (actions) {
                actions.style.display = 'flex';
            }
        }
    });
    
    messagesContainer.addEventListener('mouseout', function(e) {
        const message = e.target.closest('.message');
        if (message) {
            const actions = message.querySelector('.message-actions');
            if (actions && !message.querySelector('.delete-options-container')) {
                actions.style.display = 'none';
            }
        }
    });
}

export function addQuickReaction(messageId, reactionType) {
    import('./api/reactions.js').then(({ addReaction }) => {
        addReaction(messageId, reactionType);
    });
    
    const messageElement = document.querySelector(`[data-message-id="${messageId}"]`);
    if (messageElement) {
        messageElement.style.transform = 'scale(1.05)';
        setTimeout(() => {
            messageElement.style.transform = 'scale(1)';
        }, 300);
    }
}

export function copyMessageText(messageId) {
    const messageElement = document.querySelector(`[data-message-id="${messageId}"]`);
    if (!messageElement) return;
    
    const messageContent = messageElement.querySelector('.message-content');
    const text = messageContent.textContent || messageContent.innerText;
    
    navigator.clipboard.writeText(text).then(() => {
        import('../core/utils.js').then(({ showTempMessage }) => {
            showTempMessage('تم نسخ النص', 'success');
        });
    }).catch(() => {
        import('../core/utils.js').then(({ showTempMessage }) => {
            showTempMessage('فشل في نسخ النص', 'error');
        });
    });
}

// إزالة التصدير المكرر في الأسفل - الدوال مصدرة بالفعل أعلاه

// دالة لتحديد حجم الرسالة بناءً على المحتوى
// دالة لتحديد حجم الرسالة بناءً على المحتوى والشاشة
function classifyMessageSize(messageElement) {
    const content = messageElement.querySelector('.message-content');
    if (!content) return;
    
    const textLength = content.textContent.length;
    const hasImage = messageElement.querySelector('.message-image');
    const hasFile = messageElement.querySelector('.file-preview');
    const screenWidth = window.innerWidth;
    
    // إزالة الفئات القديمة
    messageElement.classList.remove('short', 'medium', 'long', 'compact', 'spacious');
    
    // تحديد الحد الأقصى بناءً على حجم الشاشة
    let maxLength;
    if (screenWidth < 480) {
        maxLength = 50; // هواتف صغيرة
    } else if (screenWidth < 768) {
        maxLength = 80; // هواتف كبيرة
    } else {
        maxLength = 100; // أجهزة لوحية وكمبيوتر
    }
    
    if (hasImage || hasFile) {
        messageElement.classList.add('spacious');
    } else if (textLength < 15) {
        messageElement.classList.add('short', 'compact');
    } else if (textLength < maxLength) {
        messageElement.classList.add('medium');
    } else {
        messageElement.classList.add('long');
    }
}

// تطبيق التصنيف على جميع الرسائل مع مراعاة حجم الشاشة
document.addEventListener('DOMContentLoaded', function() {
    const messages = document.querySelectorAll('.message');
    messages.forEach(classifyMessageSize);
    
    // إعادة حساب عند تغيير حجم الشاشة
    window.addEventListener('resize', function() {
        messages.forEach(classifyMessageSize);
    });
    
    // مراقبة الرسائل الجديدة
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            mutation.addedNodes.forEach(function(node) {
                if (node.nodeType === 1 && node.classList.contains('message')) {
                    classifyMessageSize(node);
                }
            });
        });
    });
    
    const messagesContainer = document.querySelector('.messages-container');
    if (messagesContainer) {
        observer.observe(messagesContainer, { childList: true, subtree: true });
    }
});

// تحسينات للشاشات التي تدعم اللمس
if ('ontouchstart' in window) {
    document.documentElement.classList.add('touch-device');
    
    // زيادة وقت transition للأجهزة التي باللمس
    const style = document.createElement('style');
    style.textContent = `
        .message, .action-btn, .send-button {
            transition-duration: 0.2s !important;
        }
    `;
    document.head.appendChild(style);
}

// تطبيق التصنيف على جميع الرسائل
document.addEventListener('DOMContentLoaded', function() {
    const messages = document.querySelectorAll('.message');
    messages.forEach(classifyMessageSize);
    
    // مراقبة الرسائل الجديدة
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            mutation.addedNodes.forEach(function(node) {
                if (node.nodeType === 1 && node.classList.contains('message')) {
                    classifyMessageSize(node);
                }
            });
        });
    });
    
    const messagesContainer = document.querySelector('.messages-container');
    if (messagesContainer) {
        observer.observe(messagesContainer, { childList: true, subtree: true });
    }
});