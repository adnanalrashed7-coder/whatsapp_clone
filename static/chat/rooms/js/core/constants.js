// ========== الثوابت العامة ==========
export const POLLING_INTERVAL = 3000;
export const TYPING_TIMEOUT = 2000;
export const TYPING_CHECK_INTERVAL = 2000;
export const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
export const MAX_IMAGE_SIZE = 5 * 1024 * 1024; // 5MB

// ========== دوال الكوكيز ==========
export function getCookie(name) {
    if (typeof window.CSRF_TOKEN !== 'undefined' && window.CSRF_TOKEN) {
        return window.CSRF_TOKEN;
    }
    
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// ========== رموز التفاعل ==========
export const REACTION_TYPES = {
    'like': { emoji: '👍', title: 'إعجاب' },
    'love': { emoji: '❤️', title: 'حب' },
    'laugh': { emoji: '😄', title: 'ضحك' },
    'wow': { emoji: '😮', title: 'دهشة' },
    'sad': { emoji: '😢', title: 'حزن' },
    'angry': { emoji: '😠', title: 'غضب' },
    'fire': { emoji: '🔥', title: 'رائع' },
    'clap': { emoji: '👏', title: 'تصفيق' }
};

// ========== فئات الإيموجي ==========
export const EMOJI_CATEGORIES = {
    'وجه': ['😀', '😃', '😄', '😁', '😆', '😅', '😂', '🤣', '😊', '😇', '🙂', '🙃', '😉', '😌', '😍', '🥰', '😘', '😗', '😙', '😚', '😋', '😛', '😝', '😜', '🤪', '🤨', '🧐', '🤓', '😎', '🤩', '🥳', '😏', '😒', '😞', '😔', '😟', '😕', '🙁', '☹️', '😣', '😖', '😫', '😩', '🥺', '😢', '😭', '😤', '😠', '😡', '🤬', '🤯', '😳', '🥵', '🥶', '😱', '😨', '😰', '😥', '😓', '🤗', '🤔', '🤭', '🤫', '🤥', '😶', '😐', '😑', '😬', '🙄', '😯', '😦', '😧', '😮', '😲', '🥱', '😴', '🤤', '😪', '😵', '🤐', '🥴', '🤢', '🤮', '🤧', '😷', '🤒', '🤕', '🤑', '🤠'],
    'قلوب': ['❤️', '🧡', '💛', '💚', '💙', '💜', '🖤', '🤍', '🤎', '💔', '❣️', '💕', '💞', '💓', '💗', '💖', '💘', '💝', '💟'],
    'إيماءات': ['👍', '👎', '👌', '✌️', '🤞', '🤟', '🤘', '👈', '👉', '👆', '👇', '☝️', '✋', '🤚', '🖐️', '🖖', '👋', '🤙', '💪', '🦾', '🦿', '🦵', '🦶', '👂', '🦻', '👃', '🧠', '🦷', '🦴', '👀', '👁️', '👅', '👄'],
    'رموز': ['⚡', '❤️', '🔥', '⭐', '🌟', '🎯', '💯', '✅', '❌', '⚠️', '🚨', '🔔', '🎵', '🎶', '💤', '🚀', '🛸', '🌠', '🌈', '🌪️', '🌊', '🍕', '🍔', '🍟', '🌭', '🍿', '🥓', '🥚', '🍳', '🧇', '🥞', '🧈', '🍞', '🥐', '🥨', '🥯', '🥖', '🧀', '🍖', '🍗', '🥩', '🍠', '🥟', '🥠', '🥡', '🍦', '🍧', '🍨', '🍩', '🍪', '🎂', '🍰', '🧁', '🥧', '🍫', '🍬', '🍭', '🍮', '🍯']
};