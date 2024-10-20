import './index.css'

import Alpine from 'alpinejs'

// suggested in the Alpine docs:
// make Alpine on window available for better DX
 
Alpine.data("fileProcessing", () => ({
    formatFileSize(bytesSize: number) {
        if(bytesSize == 0) return '0 Bytes';
        var k = 1000,
            dm = 2,
            sizes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'],
            i = Math.floor(Math.log(bytesSize) / Math.log(k));
        return parseFloat((bytesSize / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
    }
}))

Alpine.data('add', () => {
    return {
    	add_vals() {
            return 2 + 3;
    	}
    }
});
window.Alpine = Alpine
Alpine.start()
