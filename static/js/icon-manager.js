#pylint:disable=E0001


class IconManager {
    constructor() {
        this.currentIcon = 'default';
        this.unreadCount = 0;
        this.icons = {
            default: '/static/icons/favicon.ico',
            unread: '/static/icons/favicon-unread.ico',
            typing: '/static/icons/favicon-typing.ico'
        };
        
        this.init();
    }
    
    init() {
        this.setupVisibilityListener();
        this.setupMessageListeners();
    }
    
    // تغيير الأيقونة
    changeIcon(iconType) {
        const iconPath = this.icons[iconType] || this.icons.default;
        this.updateFavicon(iconPath);
        this.currentIcon = iconType;
    }
    
    // تحديث الأيقونة في DOM
    updateFavicon(iconPath) {
        let favicon = document.querySelector('link[rel="icon"]');
        
        if (!favicon) {
            favicon = document.createElement('link');
            favicon.rel = 'icon';
            document.head.appendChild(favicon);
        }
        
        favicon.href = iconPath;
    }
    
    // إظهار عدد الرسائل غير المقروءة
    showUnreadCount(count) {
        this.unreadCount = count;
        
        if (count > 0) {
            this.changeIcon('unread');
            this.updateTitleWithCount(count);
            
            // إنشاء أيقونة ديناميكية إذا لم تكن الأيقونة الجاهزة موجودة
            if (count <= 9) {
                this.createDynamicBadge(count);
            }
        } else {
            this.changeIcon('default');
            this.resetTitle();
        }
    }
    
    // إنشاء شارة ديناميكية للأرقام
    createDynamicBadge(count) {
        const canvas = document.createElement('canvas');
        canvas.width = 32;
        canvas.height = 32;
        const ctx = canvas.getContext('2d');
        
        // الخلفية
        ctx.beginPath();
        ctx.arc(16, 16, 16, 0, 2 * Math.PI);
        ctx.fillStyle = '#25D366';
        ctx.fill();
        
        // النص
        ctx.fillStyle = '#FFFFFF';
        ctx.font = 'bold 16px Arial';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(count.toString(), 16, 16);
        
        // تحديث الأيقونة
        this.updateFavicon(canvas.toDataURL());
    }
    
    // تحديث العنوان بعدد الرسائل
    updateTitleWithCount(count) {
        const baseTitle = 'دردشة الواتساب';
        document.title = `(${count}) ${baseTitle}`;
    }
    
    // استعادة العنوان الأصلي
    resetTitle() {
        document.title = 'دردشة الواتساب';
    }
    
    // إعداد مستمعي visibility
    setupVisibilityListener() {
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.onPageHidden();
            } else {
                this.onPageVisible();
            }
        });
    }
    
    // إعداد مستمعي الرسائل
    setupMessageListeners() {
        // استمع لرسائل Django (يمكن تكييفه مع قنواتك)
        document.addEventListener('djangoMessage', (event) => {
            this.handleNewMessage(event.detail);
        });
        
        // استمع للكتابة
        document.addEventListener('typingStart', () => {
            this.changeIcon('typing');
        });
        
        document.addEventListener('typingStop', () => {
            if (this.unreadCount > 0) {
                this.changeIcon('unread');
            } else {
                this.changeIcon('default');
            }
        });
    }
    
    onPageHidden() {
        // يمكن إضافة منطق عند إخفاء الصفحة
        console.log('الصفحة غير مرئية');
    }
    
    onPageVisible() {
        // استعادة الحالة عند ظهور الصفحة
        if (this.unreadCount > 0) {
            this.showUnreadCount(this.unreadCount);
        } else {
            this.changeIcon('default');
        }
    }
    
    // زيادة العداد
    incrementUnread() {
        this.unreadCount++;
        this.showUnreadCount(this.unreadCount);
    }
    
    // تقليل العداد
    decrementUnread() {
        this.unreadCount = Math.max(0, this.unreadCount - 1);
        this.showUnreadCount(this.unreadCount);
    }
    
    // إعادة تعيين العداد
    resetUnread() {
        this.unreadCount = 0;
        this.showUnreadCount(0);
    }
}

// إنشاء نسخة عامة
const iconManager = new IconManager();

// جعلها متاحة globally
window.iconManager = iconManager;