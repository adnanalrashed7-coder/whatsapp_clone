import { roomId, currentUser, isTyping, typingTimeout, setTypingStatus, setTypingTimeout } from '../core/config.js';

// ========== دوال مؤشر الكتابة ==========
export function handleTyping() {
    if (!isTyping) {
        setTypingStatus(true);
        sendTypingStatus(true);
    }
    
    clearTimeout(typingTimeout);
    const newTimeout = setTimeout(() => {
        setTypingStatus(false);
        sendTypingStatus(false);
    }, 2000);
    
    setTypingTimeout(newTimeout);
}

export function stopTyping() {
    if (isTyping) {
        setTypingStatus(false);
        sendTypingStatus(false);
        clearTimeout(typingTimeout);
    }
}

export async function sendTypingStatus(typing) {
    try {
        // استيراد getCookie بشكل ديناميكي لتجنب التكرار
        const { getCookie } = await import('../core/constants.js');
        
        const response = await fetch(`/chat/typing/${roomId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                typing: typing,
                user: currentUser
            })
        });

        if (response.ok) {
            console.log('📝 حالة الكتابة:', typing ? 'يكتب' : 'توقف');
        } else {
            console.error('❌ فشل في إرسال حالة الكتابة:', response.status);
        }
    } catch (error) {
        console.error('❌ خطأ في إرسال حالة الكتابة:', error);
    }
}

export async function checkTypingStatus() {
    try {
        const response = await fetch(`/chat/typing-status/${roomId}/`);
        if (response.ok) {
            const data = await response.json();
            updateTypingIndicator(data.typing_users || []);
        } else {
            console.error('❌ فشل في جلب حالة الكتابة:', response.status);
        }
    } catch (error) {
        console.error('❌ خطأ في جلب حالة الكتابة:', error);
    }
}

export function updateTypingIndicator(typingUsers) {
    const existingIndicator = document.getElementById('typing-indicator');
    
    // تصفية المستخدم الحالي من القائمة
    const otherTypingUsers = typingUsers.filter(user => user.email !== currentUser);
    
    if (otherTypingUsers.length > 0) {
        let indicatorText = '';
        if (otherTypingUsers.length === 1) {
            indicatorText = `${otherTypingUsers[0].display_name || otherTypingUsers[0].email} يكتب...`;
        } else if (otherTypingUsers.length === 2) {
            indicatorText = `${otherTypingUsers[0].display_name || otherTypingUsers[0].email} و ${otherTypingUsers[1].display_name || otherTypingUsers[1].email} يكتبان...`;
        } else {
            indicatorText = `${otherTypingUsers.length} أشخاص يكتبون...`;
        }
        
        if (!existingIndicator) {
            createTypingIndicator(indicatorText);
        } else {
            updateExistingIndicator(existingIndicator, indicatorText);
        }
    } else {
        removeTypingIndicator(existingIndicator);
    }
}

function createTypingIndicator(text) {
    const indicator = document.createElement('div');
    indicator.id = 'typing-indicator';
    indicator.className = 'typing-indicator';
    indicator.innerHTML = `
        <div class="typing-content">
            <div class="typing-dots">
                <span></span>
                <span></span>
                <span></span>
            </div>
            <span class="typing-text">${text}</span>
        </div>
    `;
    
    const chatMessages = document.getElementById('chat-messages');
    if (chatMessages) {
        chatMessages.appendChild(indicator);
        
        setTimeout(() => {
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }, 100);
    }
}

function updateExistingIndicator(indicator, text) {
    const typingText = indicator.querySelector('.typing-text');
    if (typingText) {
        typingText.textContent = text;
    }
}

function removeTypingIndicator(indicator) {
    if (indicator) {
        indicator.remove();
    }
}

export function startTypingPolling() {
    return setInterval(checkTypingStatus, 2000);
}

export function stopTypingPolling(intervalId) {
    if (intervalId) {
        clearInterval(intervalId);
    }
}