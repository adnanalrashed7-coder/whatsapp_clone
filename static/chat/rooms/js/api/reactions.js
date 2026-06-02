import { getCookie, REACTION_TYPES } from '../core/constants.js';
import { showTempMessage } from '../core/utils.js';
import { replyingTo, setReplyingTo, clearReplyingTo } from '../core/config.js';

// ========== دوال التفاعلات ==========
export async function addReaction(messageId, reactionType) {
    // لا تسمح بالتفاعل مع الرسائل المؤقتة
    if (messageId.startsWith('temp_')) {
        return;
    }
    
    try {
        const response = await fetch(`/chat/react/${messageId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ reaction_type: reactionType })
        });

        if (response.ok) {
            const data = await response.json();
            console.log('✅ تم إضافة التفاعل:', reactionType, 'للرسالة:', messageId);
            updateMessageReactions(messageId, data.reactions_summary);
            
            // إغلاق منتقي التفاعل المحدد
            const picker = document.getElementById('reaction-picker-' + messageId);
            if (picker) {
                picker.remove();
            }
            return data;
        } else {
            throw new Error('فشل في إضافة التفاعل');
        }
    } catch (error) {
        console.error('❌ خطأ في إضافة التفاعل:', error);
        showTempMessage('فشل في إضافة التفاعل', 'error');
        throw error;
    }
}

export function showReactionPicker(messageId, buttonElement) {
    // لا تسمح بالتفاعل مع الرسائل المؤقتة
    if (messageId.startsWith('temp_')) {
        showTempMessage('لا يمكن التفاعل مع الرسالة المؤقتة', 'error');
        return;
    }
    
    closeAllPickers();
    
    const reactions = Object.entries(REACTION_TYPES).map(([type, data]) => ({
        type,
        emoji: data.emoji,
        title: data.title
    }));

    const picker = document.createElement('div');
    picker.id = 'reaction-picker-' + messageId;
    picker.className = 'reaction-picker';
    
    reactions.forEach(reaction => {
        const btn = document.createElement('button');
        btn.className = 'reaction-option';
        btn.innerHTML = reaction.emoji;
        btn.title = reaction.title;
        btn.onclick = (e) => {
            e.stopPropagation();
            addReaction(messageId, reaction.type);
            picker.remove();
        };
        picker.appendChild(btn);
    });

    const rect = buttonElement.getBoundingClientRect();
    picker.style.position = 'fixed';
    picker.style.top = `${rect.top - 60}px`;
    picker.style.left = `${rect.left}px`;
    picker.style.zIndex = '1000';

    document.body.appendChild(picker);

    setTimeout(() => {
        const closePicker = (e) => {
            if (!picker.contains(e.target) && e.target !== buttonElement) {
                picker.remove();
                document.removeEventListener('click', closePicker);
            }
        };
        document.addEventListener('click', closePicker);
    }, 100);
}

export function updateMessageReactions(messageId, reactionsSummary) {
    const messageElement = document.querySelector(`[data-message-id="${messageId}"]`);
    if (!messageElement) {
        console.log('❌ لم يتم العثور على الرسالة:', messageId);
        return;
    }

    let reactionsContainer = messageElement.querySelector('.message-reactions');
    
    if (reactionsSummary && reactionsSummary.length > 0) {
        if (!reactionsContainer) {
            reactionsContainer = document.createElement('div');
            reactionsContainer.className = 'message-reactions';
            const messageTime = messageElement.querySelector('.message-time');
            if (messageTime) {
                messageElement.insertBefore(reactionsContainer, messageTime);
            } else {
                messageElement.appendChild(reactionsContainer);
            }
        }
        
        reactionsContainer.innerHTML = reactionsSummary.map(reaction => 
            `<span class="reaction-item" title="${reaction.count} تفاعل">${getReactionEmoji(reaction.reaction_type)} ${reaction.count}</span>`
        ).join('');
    } else {
        if (reactionsContainer) {
            reactionsContainer.remove();
        }
    }
}

export function getReactionEmoji(type) {
    return REACTION_TYPES[type]?.emoji || '👍';
}

// ========== دوال الرد على الرسائل ==========
export function replyToMessage(messageId, sender, content) {
    setReplyingTo(messageId);
    const preview = document.getElementById('reply-preview');
    const replySender = document.getElementById('reply-sender');
    const replyContent = document.getElementById('reply-content');
    
    if (replySender && replyContent && preview) {
        replySender.textContent = `رد على ${sender}`;
        replyContent.textContent = content.length > 50 ? content.substring(0, 50) + '...' : content;
        preview.style.display = 'block';
        
        const messageInput = document.getElementById('message-input');
        if (messageInput) {
            messageInput.focus();
        }
    }
}

export function closeReply() {
    clearReplyingTo();
    const preview = document.getElementById('reply-preview');
    if (preview) {
        preview.style.display = 'none';
    }
}

// ========== دوال مساعدة ==========
function closeAllPickers() {
    const reactionPickers = document.querySelectorAll('[id^="reaction-picker-"]');
    reactionPickers.forEach(picker => picker.remove());
}