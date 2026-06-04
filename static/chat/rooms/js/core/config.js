// ========== متغيرات عامة ==========
export let roomId = '';
export let currentUser = '';
export let currentUserId = '';
export let lastMessageId = '0';
export let isPolling = true;
export let isSending = false;
export let replyingTo = null;
export let isInitialized = false;
export let offlineMode = false;
export let messageCache = []; // in-memory cache (also persisted to localStorage)

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

// ========== Offline / Cache Helpers ==========
export function setOfflineMode(value) {
    offlineMode = !!value;
}

export function getOfflineMode() {
    return offlineMode;
}

export function loadCacheFromStorage() {
    try {
        const key = `chat_cache_room_${roomId}`;
        const raw = localStorage.getItem(key);
        if (raw) {
            messageCache = JSON.parse(raw);
        } else {
            messageCache = [];
        }
    } catch (e) {
        console.warn('خطأ في تحميل الكاش المحلي:', e);
        messageCache = [];
    }
}

export function saveCacheToStorage() {
    try {
        const key = `chat_cache_room_${roomId}`;
        localStorage.setItem(key, JSON.stringify(messageCache || []));
    } catch (e) {
        console.warn('خطأ في حفظ الكاش المحلي:', e);
    }
}

export function addMessagesToCache(newMessages) {
    if (!Array.isArray(newMessages)) return;
    // merge while avoiding duplicates by id
    const existingIds = new Set((messageCache || []).map(m => m.id));
    newMessages.forEach(m => {
        if (!existingIds.has(m.id)) messageCache.push(m);
    });
    // keep cache size bounded
    if (messageCache.length > 1000) {
        messageCache = messageCache.slice(-1000);
    }
    saveCacheToStorage();
}

export function clearCacheStorage() {
    try {
        const key = `chat_cache_room_${roomId}`;
        localStorage.removeItem(key);
        messageCache = [];
    } catch (e) {
        console.warn('خطأ في مسح الكاش المحلي:', e);
    }
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