// ========== متغيرات عامة ==========
export let roomId = '';
export let currentUser = '';
export let currentUserId = '';
export let lastMessageId = '0';
export let isPolling = true;
export let isSending = false;
export let replyingTo = null;
export let isInitialized = false;

// متغيرات مؤشر الكتابة
export let typingTimeout;
export let isTyping = false;
export let typingCheckInterval;

// ========== دوال إدارة الحالة ==========
export function initializeChatConfig(room, user, userId) {
    roomId = room;
    currentUser = user;
    currentUserId = userId;
    isInitialized = true;
    console.log('🔧 تهيئة إعدادات الدردشة:', { roomId, currentUser, currentUserId });
}

export function resetChatConfig() {
    roomId = '';
    currentUser = '';
    currentUserId = '';
    lastMessageId = '0';
    isPolling = false;
    isSending = false;
    replyingTo = null;
    isInitialized = false;
    isTyping = false;
    
    clearTimeout(typingTimeout);
    clearInterval(typingCheckInterval);
    
    console.log('🔄 إعادة تعيين إعدادات الدردشة');
}

export function updateLastMessageId(messageId) {
    if (messageId && !messageId.startsWith('temp_')) {
        lastMessageId = messageId;
    }
}

export function setReplyingTo(messageId) {
    replyingTo = messageId;
}

export function clearReplyingTo() {
    replyingTo = null;
}

// ========== دوال الحالة ==========
export function setSendingStatus(status) {
    isSending = status;
}

export function getSendingStatus() {
    return isSending;
}

export function setPollingStatus(status) {
    isPolling = status;
}

export function getPollingStatus() {
    return isPolling;
}

export function setTypingStatus(status) {
    isTyping = status;
}

export function getTypingStatus() {
    return isTyping;
}

export function setTypingTimeout(timeout) {
    typingTimeout = timeout;
}

export function getTypingTimeout() {
    return typingTimeout;
}