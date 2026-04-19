// ================================================
// XAUUSD Trading Hub - PWA Manager
// ================================================

// Install prompt handling
let deferredPrompt;
const installBanner = document.getElementById('install-banner');
const installBtn = document.getElementById('install-btn');
const installClose = document.getElementById('install-close');

// Show install banner when PWA install is available
window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
    
    // Show banner with animation
    if (installBanner) {
        installBanner.classList.add('show');
    }
});

// Install button click
if (installBtn) {
    installBtn.addEventListener('click', async () => {
        if (!deferredPrompt) return;
        
        deferredPrompt.prompt();
        const { outcome } = await deferredPrompt.userChoice;
        
        if (outcome === 'accepted') {
            installBanner.classList.remove('show');
        }
        deferredPrompt = null;
    });
}

// Close install banner
if (installClose) {
    installClose.addEventListener('click', () => {
        installBanner.classList.remove('show');
    });
}

// Register service worker
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js')
            .then((registration) => {
                console.log('[PWA] Service Worker registered:', registration.scope);
                
                // Check for updates
                registration.addEventListener('updatefound', () => {
                    const newWorker = registration.installing;
                    newWorker.addEventListener('statechange', () => {
                        if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                            // New content available
                            console.log('[PWA] New content available, refresh to update');
                        }
                    });
                });
            })
            .catch((error) => {
                console.log('[PWA] Service Worker registration failed:', error);
            });
    });
}

// Hide splash screen after load
window.addEventListener('load', () => {
    setTimeout(() => {
        const splash = document.getElementById('splash-screen');
        if (splash) {
            splash.classList.add('hide');
        }
    }, 1500);
});

// Handle online/offline status
function updateOnlineStatus() {
    const statusDot = document.querySelector('.status-dot.offline');
    if (statusDot) {
        if (navigator.onLine) {
            statusDot.classList.remove('show');
        } else {
            statusDot.classList.add('show');
        }
    }
}

window.addEventListener('online', updateOnlineStatus);
window.addEventListener('offline', updateOnlineStatus);

// Bottom navigation active state
function setActiveNav() {
    const currentPage = window.location.pathname.split('/').pop() || 'index.html';
    const navLinks = document.querySelectorAll('.bottom-nav a');
    
    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === currentPage) {
            link.classList.add('active');
        }
    });
}

// Set active nav on load
document.addEventListener('DOMContentLoaded', setActiveNav);

// Pull to refresh (simple version)
let touchStartY = 0;
let touchEndY = 0;

document.addEventListener('touchstart', (e) => {
    touchStartY = e.changedTouches[0].screenY;
}, { passive: true });

document.addEventListener('touchend', (e) => {
    touchEndY = e.changedTouches[0].screenY;
    handlePullToRefresh();
}, { passive: true });

function handlePullToRefresh() {
    // Only trigger when at top of page
    if (window.scrollY === 0 && touchEndY < touchStartY - 100) {
        const refreshBtn = document.querySelector('.refresh-btn');
        if (refreshBtn) {
            refreshBtn.click();
        }
    }
}

// Share API (if available)
async function shareApp() {
    if (navigator.share) {
        try {
            await navigator.share({
                title: 'XAUUSD Trading Hub',
                text: 'รายงานและข่าวทองคำล่าสุด',
                url: window.location.href
            });
        } catch (err) {
            console.log('Share cancelled');
        }
    }
}
