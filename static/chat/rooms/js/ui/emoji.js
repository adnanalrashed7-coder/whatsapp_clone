import { EMOJI_CATEGORIES } from '../core/constants.js';
import { handleTyping } from '../api/typing.js';

// ========== منتقي الإيموجي ==========
let currentEmojiCategory = 'وجه';

export function initEmojiPicker() {
    const categoriesContainer = document.getElementById('emoji-categories');
    const emojiGrid = document.getElementById('emoji-grid');
    
    if (!categoriesContainer || !emojiGrid) return;
    
    Object.keys(EMOJI_CATEGORIES).forEach(category => {
        const btn = document.createElement('button');
        btn.className = 'emoji-category-btn';
        btn.textContent = EMOJI_CATEGORIES[category][0];
        btn.title = category;
        btn.onclick = () => switchEmojiCategory(category);
        categoriesContainer.appendChild(btn);
    });
    
    switchEmojiCategory('وجه');
    initEmojiPickerEvents();
}

export function switchEmojiCategory(category) {
    currentEmojiCategory = category;
    const emojiGrid = document.getElementById('emoji-grid');
    const categoryButtons = document.querySelectorAll('.emoji-category-btn');
    
    if (!emojiGrid) return;
    
    categoryButtons.forEach(btn => {
        btn.classList.remove('active');
        if (btn.title === category) {
            btn.classList.add('active');
        }
    });
    
    emojiGrid.innerHTML = '';
    EMOJI_CATEGORIES[category].forEach(emoji => {
        const emojiBtn = document.createElement('button');
        emojiBtn.className = 'emoji-item';
        emojiBtn.textContent = emoji;
        emojiBtn.onclick = () => insertEmoji(emoji);
        emojiGrid.appendChild(emojiBtn);
    });
}

export function toggleEmojiPicker() {
    const picker = document.getElementById('emoji-picker');
    if (!picker) return;
    
    if (picker.style.display === 'none' || !picker.style.display) {
        picker.style.display = 'block';
        initEmojiPicker();
    } else {
        picker.style.display = 'none';
    }
}

export function insertEmoji(emoji) {
    const messageInput = document.getElementById('message-input');
    if (!messageInput) return;
    
    const startPos = messageInput.selectionStart;
    const endPos = messageInput.selectionEnd;
    
    messageInput.value = messageInput.value.substring(0, startPos) + 
                        emoji + 
                        messageInput.value.substring(endPos);
    
    messageInput.focus();
    messageInput.selectionStart = messageInput.selectionEnd = startPos + emoji.length;
    
    // تحديث واجهة الإدخال
    import('./input.js').then(({ handleInputChange }) => {
        handleInputChange(messageInput);
    });
    
    // تفعيل مؤشر الكتابة
    handleTyping();
    
    // إغلاق منتقي الإيموجي بعد الإدراج
    const picker = document.getElementById('emoji-picker');
    if (picker) {
        picker.style.display = 'none';
    }
}

function initEmojiPickerEvents() {
    // إغلاق منتقي الإيموجي عند النقر خارجها
    document.addEventListener('click', function(event) {
        const picker = document.getElementById('emoji-picker');
        const emojiBtn = document.querySelector('.emoji-btn');
        
        if (picker && picker.style.display === 'block' && 
            !picker.contains(event.target) && 
            !emojiBtn.contains(event.target)) {
            picker.style.display = 'none';
        }
    });
}

export function initEmojiButton() {
    const emojiButton = document.querySelector('.emoji-btn');
    if (emojiButton) {
        emojiButton.addEventListener('click', function(e) {
            e.stopPropagation();
            toggleEmojiPicker();
        });
    }
}