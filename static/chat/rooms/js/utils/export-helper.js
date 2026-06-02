// ملف مساعد للتحقق من التصديرات
export function validateExports(moduleName, exports) {
    const uniqueExports = [...new Set(exports)];
    if (uniqueExports.length !== exports.length) {
        console.warn(`⚠️ تحذير: هناك تصديرات مكررة في ${moduleName}`);
    }
    return uniqueExports;
}

// دالة لتصدير جميع الدوال من كائن
export function exportAllFromObject(obj) {
    return Object.keys(obj).reduce((exports, key) => {
        if (typeof obj[key] === 'function') {
            exports[key] = obj[key];
        }
        return exports;
    }, {});
}