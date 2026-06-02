// ========== الملف الرئيسي للتنسيق ==========
import { 
    roomId, currentUser, currentUserId, isPolling, isInitialized,
    initializeChatConfig, resetChatConfig 
} from './core/config.js';
import { addTempMessageStyles, scrollToBottom } from './core/utils.js';
import { fetchMessages } from './api/messages.js';
import { startTypingPolling, stopTypingPolling } from './api/typing.js';
import { initMessageInteractions } from './ui/messages.js';
import { initInputEvents } from './ui/input.js';
import { initEmojiButton } from './ui/emoji.js';
import { initSidePanelEvents } from './ui/sidepanel.js';

// ========== دوال التنقل والأساسية ==========
export function goBack() {
    window.history.back();
}

export function toggleSidePanel() {
    const panel = document.getElementById('side-panel');
    if (panel) {
        panel.classList.toggle('open');
    }
}

export function searchInChat() {
    const searchTerm = prompt('ابحث في المحادثة:');
    if (searchTerm) {
        // سيتم تنفيذ البحث لاحقاً
        console.log('بحث عن:', searchTerm);
    }
}

// ========== نظام الـ Polling المحسن ==========
async function pollMessages() {
    if (!isPolling) return;
    
    console.log('🔄 بدء نظام الـ Polling');
    
    while (isPolling) {
        try {
            const messages = await fetchMessages();
            
            if (messages.length > 0) {
                const loadingIndicator = document.getElementById('loading-indicator');
                if (loadingIndicator && loadingIndicator.style.display !== 'none') {
                    loadingIndicator.style.display = 'none';
                }
                
                messages.forEach(message => {
                    const existingMessage = document.querySelector(`[data-message-id="${message.id}"]`);
                    if (!existingMessage) {
                        import('./ui/messages.js').then(({ displayEnhancedMessage }) => {
                            displayEnhancedMessage(message);
                        });
                        console.log('📩 عرض رسالة جديدة:', message.id);
                    }
                });
                
                scrollToBottom();
            }

            // التحقق من حالة الكتابة
            await import('./api/typing.js').then(({ checkTypingStatus }) => {
                checkTypingStatus();
            });
            
            await new Promise(resolve => setTimeout(resolve, 3000));
            
        } catch (error) {
            console.error('❌ خطأ في Polling:', error);
            await new Promise(resolve => setTimeout(resolve, 5000));
        }
    }
    
    console.log('🛑 توقف نظام الـ Polling');
}

// ========== تحميل الرسائل الأولى ==========
async function loadInitialMessages() {
    try {
        const messages = await fetchMessages();
        const loadingIndicator = document.getElementById('loading-indicator');
        const chatMessages = document.getElementById('chat-messages');
        
        if (messages.length > 0) {
            if (loadingIndicator) loadingIndicator.style.display = 'none';
            
            messages.forEach(message => {
                import('./ui/messages.js').then(({ displayEnhancedMessage }) => {
                    displayEnhancedMessage(message);
                });
            });
            
            setTimeout(() => {
                if (chatMessages) chatMessages.scrollTop = chatMessages.scrollHeight;
            }, 100);
            
        } else {
            if (loadingIndicator) {
                loadingIndicator.innerHTML = 'لا توجد رسائل بعد. كن أول من يرسل رسالة!';
                loadingIndicator.style.color = '#888';
            }
        }
    } catch (error) {
        const loadingIndicator = document.getElementById('loading-indicator');
        if (loadingIndicator) {
            loadingIndicator.innerHTML = 'فشل في تحميل الرسائل';
            loadingIndicator.style.color = '#dc3545';
        }
        console.error('Error in loadInitialMessages:', error);
    }
}

// ========== تحديث التهيئة الرئيسية ==========
let typingIntervalId;

export function initEnhancedChat() {
    if (isInitialized) {
        console.log('⚠️ تم تهيئة الدردشة مسبقاً');
        return;
    }
    
    console.log('🚀 بدء تحميل الدردشة المحسنة...');
    
    // استخدام المتغيرات العالمية من window
    const roomId = window.ROOM_ID || '';
    const currentUser = window.CURRENT_USER || '';
    const currentUserId = window.CURRENT_USER_ID || '';
    
    console.log('🔍 متغيرات الدردشة:', { roomId, currentUser, currentUserId });
    
    if (!roomId) {
        console.error('❌ roomId غير محدد');
        return;
    }
    
    // تهيئة الإعدادات
    initializeChatConfig(roomId, currentUser, currentUserId);
    
    // إضافة أنماط الرسائل المؤقتة
    addTempMessageStyles();
    
    // تحديث تاريخ اليوم
    updateDateLabel();
    
    // تهيئة التفاعلات
    initMessageInteractions();
    initInputEvents();
    initEmojiButton();
    initSidePanelEvents();
    
    // جعل الدوال متاحة globally
    makeFunctionsGlobal();
    
    // بدء تتبع حالة الكتابة
    startTypingSystem();
    
    // تحميل الرسائل القديمة أولاً
    loadInitialMessages();
    
    // بدء الـ Polling بعد تحميل الرسائل الأولى
    setTimeout(() => {
        pollMessages();
    }, 1000);
    
    console.log('✅ تم تهيئة الدردشة المحسنة بنجاح');
}

// ========== نظام مؤشر الكتابة ==========
function startTypingSystem() {
    try {
        typingIntervalId = startTypingPolling();
        console.log('📝 تم بدء نظام مؤشر الكتابة');
    } catch (error) {
        console.error('❌ فشل في بدء نظام مؤشر الكتابة:', error);
    }
}

// ========== جعل الدوال متاحة globally ==========
function makeFunctionsGlobal() {
    // دوال التنقل
    window.goBack = goBack;
    window.toggleSidePanel = toggleSidePanel;
    window.searchInChat = searchInChat;
    
    // دوال الرسائل والتفاعلات
    import('./api/messages.js').then(({ sendMessage }) => {
        window.sendMessage = sendMessage;
    });
    
    import('./ui/input.js').then(({ handleInputChange, handleSendMessage }) => {
        window.handleInputChange = handleInputChange;
        window.handleSendMessage = handleSendMessage;
    });
    
    import('./ui/emoji.js').then(({ toggleEmojiPicker }) => {
        window.toggleEmojiPicker = toggleEmojiPicker;
    });
    
    import('./api/reactions.js').then(({ closeReply }) => {
        window.closeReply = closeReply;
    });
    
    import('./api/typing.js').then(({ handleTyping, stopTyping }) => {
        window.handleTyping = handleTyping;
        window.stopTyping = stopTyping;
    });
    
    import('./ui/sidepanel.js').then(({ showRoomSettings }) => {
        window.showRoomSettings = showRoomSettings;
    });
    
    import('./features/edit-delete.js').then(({ 
        showDeleteOptions, enableMessageEdit, deleteMessage, 
        saveMessageEdit, cancelMessageEdit 
    }) => {
        window.showDeleteOptions = showDeleteOptions;
        window.enableMessageEdit = enableMessageEdit;
        window.deleteMessage = deleteMessage;
        window.saveMessageEdit = saveMessageEdit;
        window.cancelMessageEdit = cancelMessageEdit;
    });
    
    import('./api/reactions.js').then(({ 
        showReactionPicker, addReaction, replyToMessage 
    }) => {
        window.showReactionPicker = showReactionPicker;
        window.addReaction = addReaction;
        window.replyToMessage = replyToMessage;
    });
    
    import('./ui/messages.js').then(({ copyMessageText }) => {
        window.copyMessageText = copyMessageText;
    });
}

// ========== دوال مساعدة ==========
function updateDateLabel() {
    const today = new Date().toLocaleDateString('ar-EG', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
    const todayLabel = document.getElementById('today-label');
    if (todayLabel) {
        todayLabel.textContent = today;
    }
}

// ========== أحداث الصفحة ==========
window.addEventListener('beforeunload', function() {
    isPolling = false;
    if (typingIntervalId) stopTypingPolling(typingIntervalId);
    resetChatConfig();
    console.log('🛑 إيقاف الـ Polling ومؤشر الكتابة');
});

// دوال للتوافق مع الكود القديم
window.initChat = initEnhancedChat;