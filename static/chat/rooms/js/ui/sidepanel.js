// ========== إدارة اللوحة الجانبية ==========
export function toggleSidePanel() {
    const panel = document.getElementById('side-panel');
    panel.classList.toggle('open');
}

export function closeSidePanel() {
    const panel = document.getElementById('side-panel');
    panel.classList.remove('open');
}

export function initSidePanelEvents() {
    // إغلاق اللوحة الجانبية عند النقر خارجها
    document.addEventListener('click', function(event) {
        const panel = document.getElementById('side-panel');
        const toggleBtn = document.querySelector('[onclick*="toggleSidePanel"]');
        
        if (panel && panel.classList.contains('open') && 
            !panel.contains(event.target) && 
            !toggleBtn.contains(event.target)) {
            closeSidePanel();
        }
    });
    
    // منع إغلاق اللوحة عند النقر داخلها
    const panel = document.getElementById('side-panel');
    if (panel) {
        panel.addEventListener('click', function(event) {
            event.stopPropagation();
        });
    }
}

export function loadParticipants(participants) {
    const participantList = document.getElementById('participant-list');
    if (!participantList) return;
    
    participantList.innerHTML = '';
    
    participants.forEach(participant => {
        const participantItem = document.createElement('li');
        participantItem.className = 'participant-item';
        
        participantItem.innerHTML = `
            <div class="participant-avatar">
                ${getInitials(participant.name || participant.email)}
            </div>
            <div class="participant-info">
                <div class="participant-name">${participant.name || participant.email}</div>
                <div class="participant-status">
                    <span class="status-dot ${participant.online ? 'online' : 'offline'}"></span>
                    ${participant.online ? 'متصل الآن' : 'غير متصل'}
                </div>
            </div>
        `;
        
        participantList.appendChild(participantItem);
    });
}

function getInitials(name) {
    return name.split(' ').map(word => word[0]).join('').toUpperCase().substring(0, 2);
}

export function showRoomSettings() {
    alert('سيتم إضافة إعدادات متقدمة للغرفة قريباً!');
}