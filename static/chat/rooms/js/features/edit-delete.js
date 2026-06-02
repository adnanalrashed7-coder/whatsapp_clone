import { getCookie } from '../core/constants.js';
import { showTempMessage } from '../core/utils.js';
import { formatEnhancedContent } from '../core/utils.js';

// ========== دوال حذف الرسائل ==========
export function showDeleteOptions(messageId) {
    // لا تسمح بحذف الرسائل المؤقتة
    if (messageId.startsWith('temp_')) {
        showTempMessage('لا يمكن حذف الرسالة المؤقتة', 'error');
        return;
    }
    
    closeAllPickers();
    
    const messageElement = document.querySelector(`[data-message-id="${messageId}"]`);
    const isOwnMessage = messageElement.classList.contains('own');
    
    let optionsHTML = `
        <div class="delete-options">
            <button class="delete-option personal" onclick="deleteMessage('${messageId}', false)">
                🗑️ حذف لي فقط
            </button>
    `;
    
    if (isOwnMessage) {
        optionsHTML += `
            <button class="delete-option everyone" onclick="deleteMessage('${messageId}', true)">
                ⚠️ حذف للجميع
            </button>
        `;
    }
    
    optionsHTML += `
            <button class="delete-option cancel" onclick="closeDeleteOptions()">
                ❌ إلغاء
            </button>
        </div>
    `;
    
    const messageActions = messageElement.querySelector('.message-actions');
    if (messageActions) {
        messageActions.style.display = 'none';
    }
    
    const deleteOptions = document.createElement('div');
    deleteOptions.className = 'delete-options-container';
    deleteOptions.innerHTML = optionsHTML;
    messageElement.appendChild(deleteOptions);
}

export async function deleteMessage(messageId, forAll = false) {
    // لا تسمح بحذف الرسائل المؤقتة
    if (messageId.startsWith('temp_')) {
        showTempMessage('لا يمكن حذف الرسالة المؤقتة', 'error');
        return;
    }
    
    closeDeleteOptions();
    
    const confirmMessage = forAll ? 
        'هل أنت متأكد من حذف هذه الرسالة للجميع؟ لا يمكن التراجع عن هذا الإجراء.' :
        'هل تريد حذف هذه الرسالة؟';
    
    if (!confirm(confirmMessage)) {
        return;
    }
    
    try {
        const response = await fetch(`/chat/delete/${messageId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ for_all: forAll })
        });

        const data = await response.json();
        
        if (data.status === 'success') {
            if (forAll) {
                const messageElement = document.querySelector(`[data-message-id="${messageId}"]`);
                if (messageElement) {
                    messageElement.querySelector('.message-content').textContent = 'تم حذف هذه الرسالة';
                    messageElement.querySelector('.message-image')?.remove();
                    messageElement.querySelector('.file-preview')?.remove();
                    messageElement.style.opacity = '0.6';
                    messageElement.style.fontStyle = 'italic';
                    
                    // إخفاء أزرار الإجراءات بعد الحذف
                    const messageActions = messageElement.querySelector('.message-actions');
                    if (messageActions) {
                        messageActions.style.display = 'none';
                    }
                }
            } else {
                document.querySelector(`[data-message-id="${messageId}"]`)?.remove();
            }
            console.log('✅ تم حذف الرسالة بنجاح');
        } else {
            throw new Error(data.error);
        }
    } catch (error) {
        console.error('❌ خطأ في حذف الرسالة:', error);
        alert('فشل في حذف الرسالة: ' + error.message);
    }
}

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

// ========== دوال تحرير الرسائل ==========
export function enableMessageEdit(messageId, currentContent) {
    // لا تسمح بتحرير الرسائل المؤقتة
    if (messageId.startsWith('temp_')) {
        showTempMessage('لا يمكن تحرير الرسالة المؤقتة', 'error');
        return;
    }
    
    closeAllPickers();
    
    const messageElement = document.querySelector(`[data-message-id="${messageId}"]`);
    const messageContent = messageElement.querySelector('.message-content');
    const messageActions = messageElement.querySelector('.message-actions');
    
    if (messageActions) {
        messageActions.style.display = 'none';
    }
    
    const originalContent = messageContent.innerHTML;
    messageElement.dataset.originalContent = originalContent;
    
    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = currentContent;
    const plainText = tempDiv.textContent || tempDiv.innerText || '';
    
    messageContent.innerHTML = `
        <div class="edit-container">
            <textarea class="message-edit-input" rows="3">${plainText}</textarea>
            <div class="edit-controls">
                <button class="edit-btn save" onclick="saveMessageEdit('${messageId}')">
                    💾 حفظ
                </button>
                <button class="edit-btn cancel" onclick="cancelMessageEdit('${messageId}')">
                    ❌ إلغاء
                </button>
            </div>
        </div>
    `;
    
    const editInput = messageContent.querySelector('.message-edit-input');
    editInput.focus();
    editInput.setSelectionRange(editInput.value.length, editInput.value.length);
}

export async function saveMessageEdit(messageId) {
    // لا تسمح بتحرير الرسائل المؤقتة
    if (messageId.startsWith('temp_')) {
        showTempMessage('لا يمكن تحرير الرسالة المؤقتة', 'error');
        return;
    }
    
    const messageElement = document.querySelector(`[data-message-id="${messageId}"]`);
    const editInput = messageElement.querySelector('.message-edit-input');
    const newContent = editInput.value.trim();
    
    if (!newContent) {
        alert('لا يمكن أن تكون الرسالة فارغة');
        return;
    }
    
    try {
        const response = await fetch(`/chat/edit/${messageId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ content: newContent })
        });

        const data = await response.json();
        
        if (data.status === 'success') {
            const messageContent = messageElement.querySelector('.message-content');
            messageContent.innerHTML = formatEnhancedContent(newContent);
            
            const messageTime = messageElement.querySelector('.message-time');
            messageTime.innerHTML = `${data.edited_at} <span class="edited-indicator">(تم التحرير)</span>`;
            
            const messageActions = messageElement.querySelector('.message-actions');
            if (messageActions) {
                messageActions.style.display = 'flex';
            }
            
            console.log('✅ تم تحرير الرسالة بنجاح');
        } else {
            throw new Error(data.error);
        }
    } catch (error) {
        console.error('❌ خطأ في تحرير الرسالة:', error);
        alert('فشل في تحرير الرسالة: ' + error.message);
        cancelMessageEdit(messageId);
    }
}

export function cancelMessageEdit(messageId) {
    const messageElement = document.querySelector(`[data-message-id="${messageId}"]`);
    const messageContent = messageElement.querySelector('.message-content');
    const messageActions = messageElement.querySelector('.message-actions');
    
    const originalContent = messageElement.dataset.originalContent;
    messageContent.innerHTML = originalContent;
    
    if (messageActions) {
        messageActions.style.display = 'flex';
    }
}

function closeAllPickers() {
    const reactionPickers = document.querySelectorAll('[id^="reaction-picker-"]');
    reactionPickers.forEach(picker => picker.remove());
}