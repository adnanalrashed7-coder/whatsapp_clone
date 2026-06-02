// ========== البحث في المحادثة ==========
export function searchInChat() {
    const searchTerm = prompt('ابحث في المحادثة:');
    if (searchTerm) {
        highlightSearchTerm(searchTerm);
        scrollToFirstMatch(searchTerm);
    }
}

export function highlightSearchTerm(term) {
    const messages = document.querySelectorAll('.message-content');
    messages.forEach(msg => {
        const content = msg.innerHTML;
        const highlighted = content.replace(
            new RegExp(term, 'gi'),
            match => `<mark style="background: yellow; color: black;">${match}</mark>`
        );
        msg.innerHTML = highlighted;
    });
}

export function scrollToFirstMatch(term) {
    const firstMatch = document.querySelector('mark');
    if (firstMatch) {
        firstMatch.scrollIntoView({ behavior: 'smooth', block: 'center' });
        firstMatch.style.animation = 'highlightPulse 2s ease-in-out';
    }
}

export function clearSearchHighlights() {
    const marks = document.querySelectorAll('mark');
    marks.forEach(mark => {
        const parent = mark.parentNode;
        parent.replaceChild(document.createTextNode(mark.textContent), mark);
        parent.normalize();
    });
}