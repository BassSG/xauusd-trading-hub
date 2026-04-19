/**
 * XAUUSD Trading Hub - Enhanced JavaScript
 * Interactive elements, animations, and data handling
 */

(function() {
    'use strict';

    // ================================================
    // INITIALIZATION
    // ================================================
    
    document.addEventListener('DOMContentLoaded', function() {
        initAnimations();
        initInteractiveElements();
        initNavigation();
        initTooltips();
    });

    // ================================================
    // ANIMATIONS
    // ================================================
    
    function initAnimations() {
        // Intersection Observer for scroll animations
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                    observer.unobserve(entry.target);
                }
            });
        }, observerOptions);

        // Observe elements that should animate on scroll
        document.querySelectorAll('.section, .price-card, .card, .scenario-item, .level-item, .event-item').forEach(el => {
            el.classList.add('scroll-animate');
            observer.observe(el);
        });

        // Staggered animation for grid items
        document.querySelectorAll('.card-grid, .grid-4, .grid-2').forEach(grid => {
            const items = grid.querySelectorAll(':scope > *');
            items.forEach((item, index) => {
                item.style.animationDelay = `${index * 0.1}s`;
                item.classList.add('stagger-item');
            });
        });
    }

    // ================================================
    // INTERACTIVE ELEMENTS
    // ================================================
    
    function initInteractiveElements() {
        // Enhanced card hover effects
        document.querySelectorAll('.card, .price-card, .scenario-item').forEach(card => {
            card.addEventListener('mouseenter', handleCardHover);
            card.addEventListener('mouseleave', handleCardLeave);
        });

        // Level items hover effect
        document.querySelectorAll('.level-item').forEach(item => {
            item.addEventListener('click', handleLevelClick);
        });

        // Event items hover effect
        document.querySelectorAll('.event-item').forEach(item => {
            item.addEventListener('click', handleEventClick);
        });
    }

    function handleCardHover(e) {
        const card = e.currentTarget;
        card.classList.add('hover-active');
        
        // Add ripple effect
        const ripple = document.createElement('div');
        ripple.className = 'card-ripple';
        card.appendChild(ripple);
        
        setTimeout(() => ripple.remove(), 600);
    }

    function handleCardLeave(e) {
        e.currentTarget.classList.remove('hover-active');
    }

    function handleLevelClick(e) {
        const item = e.currentTarget;
        const price = item.querySelector('.level-price')?.textContent;
        
        if (price) {
            // Copy to clipboard functionality
            navigator.clipboard.writeText(price).then(() => {
                showToast(`Copied ${price} to clipboard`, 'success');
            }).catch(() => {
                showToast('Click to copy price', 'info');
            });
        }
    }

    function handleEventClick(e) {
        const item = e.currentTarget;
        item.classList.toggle('expanded');
    }

    // ================================================
    // NAVIGATION
    // ================================================
    
    function initNavigation() {
        // Smooth scroll for anchor links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function(e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            });
        });

        // Active nav highlighting based on scroll position
        const sections = document.querySelectorAll('section[id]');
        const navLinks = document.querySelectorAll('.nav a');

        window.addEventListener('scroll', () => {
            let current = '';
            sections.forEach(section => {
                const sectionTop = section.offsetTop;
                const sectionHeight = section.clientHeight;
                if (scrollY >= sectionTop - 200) {
                    current = section.getAttribute('id');
                }
            });

            navLinks.forEach(link => {
                link.classList.remove('active');
                if (link.getAttribute('href') === `#${current}`) {
                    link.classList.add('active');
                }
            });
        });
    }

    // ================================================
    // TOOLTIPS
    // ================================================
    
    function initTooltips() {
        const tooltipElements = document.querySelectorAll('[data-tooltip]');
        
        tooltipElements.forEach(el => {
            const tooltipText = el.getAttribute('data-tooltip');
            const tooltip = document.createElement('div');
            tooltip.className = 'tooltip-text';
            tooltip.textContent = tooltipText;
            el.appendChild(tooltip);
        });
    }

    // ================================================
    // TOAST NOTIFICATIONS
    // ================================================
    
    function showToast(message, type = 'info') {
        // Remove existing toast container if present
        let container = document.querySelector('.toast-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'toast-container';
            document.body.appendChild(container);
        }

        const icons = {
            success: '✅',
            error: '❌',
            warning: '⚠️',
            info: 'ℹ️'
        };

        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.innerHTML = `
            <span class="toast-icon">${icons[type]}</span>
            <span class="toast-message">${message}</span>
            <button class="toast-close" onclick="this.parentElement.remove()">×</button>
        `;

        container.appendChild(toast);

        // Auto remove after 4 seconds
        setTimeout(() => {
            toast.style.animation = 'slide-out 0.3s ease-out forwards';
            setTimeout(() => toast.remove(), 300);
        }, 4000);
    }

    // Make showToast globally available
    window.showToast = showToast;

    // ================================================
    // LOADING STATES
    // ================================================
    
    function showLoading(element, text = 'Loading...') {
        element.innerHTML = `
            <div class="loading-spinner">
                <div class="spinner"></div>
                <span class="loading-text">${text}</span>
            </div>
        `;
        element.classList.add('loading');
    }

    function hideLoading(element) {
        element.classList.remove('loading');
    }

    // Skeleton loading helpers
    function createSkeleton(type = 'text') {
        const skeleton = document.createElement('div');
        skeleton.className = `skeleton skeleton-${type}`;
        return skeleton;
    }

    function showSkeleton(element, count = 3, type = 'text') {
        element.innerHTML = '';
        for (let i = 0; i < count; i++) {
            element.appendChild(createSkeleton(type));
        }
    }

    // ================================================
    // DATA REFRESH
    // ================================================
    
    async function refreshData(url, callback) {
        const targetElement = document.querySelector('[data-refresh]');
        if (targetElement) {
            showLoading(targetElement, 'Refreshing data...');
            
            try {
                const response = await fetch(url);
                const data = await response.json();
                hideLoading(targetElement);
                if (callback) callback(data);
            } catch (error) {
                hideLoading(targetElement);
                showToast('Failed to refresh data', 'error');
                console.error('Data refresh error:', error);
            }
        }
    }

    // ================================================
    // UTILITY FUNCTIONS
    // ================================================
    
    // Format number with commas and currency symbol
    function formatPrice(num, currency = '$') {
        return currency + num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    }

    // Calculate percentage change
    function calculateChange(current, previous) {
        const change = current - previous;
        const percent = (change / previous) * 100;
        return {
            change: change.toFixed(2),
            percent: percent.toFixed(2),
            direction: change >= 0 ? 'up' : 'down'
        };
    }

    // Debounce function for performance
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    // Throttle function for scroll events
    function throttle(func, limit) {
        let inThrottle;
        return function(...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }

    // ================================================
    // ACCESSIBILITY
    // ================================================
    
    // Keyboard navigation support
    document.addEventListener('keydown', (e) => {
        // Escape key closes any open modals/toasts
        if (e.key === 'Escape') {
            document.querySelectorAll('.toast').forEach(toast => toast.remove());
        }
    });

    // Reduced motion check
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
    
    if (prefersReducedMotion.matches) {
        document.documentElement.style.setProperty('--transition-fast', '0.01ms');
        document.documentElement.style.setProperty('--transition-normal', '0.01ms');
        document.documentElement.style.setProperty('--transition-slow', '0.01ms');
    }

    // ================================================
    // EXPORTED API
    // ================================================
    
    window.TradingHub = {
        showToast,
        showLoading,
        hideLoading,
        showSkeleton,
        formatPrice,
        calculateChange,
        refreshData,
        debounce,
        throttle
    };

})();
