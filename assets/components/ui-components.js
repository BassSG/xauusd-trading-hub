/**
 * XAUUSD Trading Hub - Reusable UI Components
 * Interactive charts, graphs, and UI elements
 */

(function() {
    'use strict';

    // ================================================
    // MINI CHART COMPONENT
    // ================================================
    
    class MiniChart {
        constructor(container, data, options = {}) {
            this.container = typeof container === 'string' ? document.querySelector(container) : container;
            this.data = data || [];
            this.options = {
                width: options.width || 200,
                height: options.height || 80,
                lineColor: options.lineColor || '#FFD700',
                fillColor: options.fillColor || 'rgba(255, 215, 0, 0.1)',
                showGrid: options.showGrid !== false,
                animated: options.animated !== false,
                ...options
            };
            this.init();
        }

        init() {
            if (!this.container || this.data.length === 0) return;
            this.render();
        }

        render() {
            const canvas = document.createElement('canvas');
            canvas.width = this.options.width;
            canvas.height = this.options.height;
            canvas.className = 'mini-chart';
            this.container.appendChild(canvas);
            
            this.ctx = canvas.getContext('2d');
            this.draw();
        }

        draw() {
            const ctx = this.ctx;
            const { width, height, lineColor, fillColor, showGrid } = this.options;
            const padding = 10;
            
            // Clear canvas
            ctx.clearRect(0, 0, width, height);
            
            // Draw grid
            if (showGrid) {
                ctx.strokeStyle = 'rgba(255, 255, 255, 0.05)';
                ctx.lineWidth = 1;
                
                // Horizontal lines
                for (let i = 0; i <= 4; i++) {
                    const y = (height / 4) * i;
                    ctx.beginPath();
                    ctx.moveTo(0, y);
                    ctx.lineTo(width, y);
                    ctx.stroke();
                }
                
                // Vertical lines
                for (let i = 0; i <= 4; i++) {
                    const x = (width / 4) * i;
                    ctx.beginPath();
                    ctx.moveTo(x, 0);
                    ctx.lineTo(x, height);
                    ctx.stroke();
                }
            }
            
            // Calculate bounds
            const min = Math.min(...this.data);
            const max = Math.max(...this.data);
            const range = max - min || 1;
            
            // Scale data
            const points = this.data.map((value, index) => ({
                x: padding + (index / (this.data.length - 1)) * (width - padding * 2),
                y: padding + (1 - (value - min) / range) * (height - padding * 2)
            }));
            
            // Draw fill
            ctx.fillStyle = fillColor;
            ctx.beginPath();
            ctx.moveTo(points[0].x, height - padding);
            points.forEach(point => ctx.lineTo(point.x, point.y));
            ctx.lineTo(points[points.length - 1].x, height - padding);
            ctx.closePath();
            ctx.fill();
            
            // Draw line
            ctx.strokeStyle = lineColor;
            ctx.lineWidth = 2;
            ctx.lineCap = 'round';
            ctx.lineJoin = 'round';
            ctx.beginPath();
            points.forEach((point, index) => {
                if (index === 0) ctx.moveTo(point.x, point.y);
                else ctx.lineTo(point.x, point.y);
            });
            ctx.stroke();
            
            // Draw end point
            const lastPoint = points[points.length - 1];
            ctx.fillStyle = lineColor;
            ctx.beginPath();
            ctx.arc(lastPoint.x, lastPoint.y, 4, 0, Math.PI * 2);
            ctx.fill();
        }

        update(newData) {
            this.data = newData;
            this.draw();
        }
    }

    // ================================================
    // PRICE DISPLAY COMPONENT
    // ================================================
    
    class PriceDisplay {
        constructor(element, options = {}) {
            this.element = typeof element === 'string' ? document.querySelector(element) : element;
            this.price = options.price || 0;
            this.previousPrice = options.previousPrice || 0;
            this.options = {
                currency: options.currency || '$',
                decimals: options.decimals || 2,
                showChange: options.showChange !== false,
                animated: options.animated !== false,
                ...options
            };
            this.init();
        }

        init() {
            if (!this.element) return;
            this.render();
        }

        render() {
            const change = this.price - this.previousPrice;
            const percentChange = this.previousPrice ? (change / this.previousPrice * 100) : 0;
            const direction = change >= 0 ? 'up' : 'down';
            
            this.element.innerHTML = `
                <div class="price-display">
                    <div class="price-main">
                        <span class="price-currency">${this.options.currency}</span>
                        <span class="price-value">${this.formatNumber(this.price)}</span>
                    </div>
                    ${this.options.showChange ? `
                        <div class="price-change ${direction}">
                            <span class="change-icon">${direction === 'up' ? '📈' : '📉'}</span>
                            <span class="change-value">${this.formatNumber(Math.abs(change))}</span>
                            <span class="change-percent">(${percentChange >= 0 ? '+' : ''}${percentChange.toFixed(2)}%)</span>
                        </div>
                    ` : ''}
                </div>
            `;
        }

        formatNumber(num) {
            return num.toFixed(this.options.decimals).replace(/\B(?=(\d{3})+(?!\d))/g, ',');
        }

        update(newPrice, newPreviousPrice) {
            if (newPreviousPrice !== undefined) this.previousPrice = newPreviousPrice;
            this.price = newPrice;
            this.render();
        }
    }

    // ================================================
    // PROGRESS INDICATOR COMPONENT
    // ================================================
    
    class ProgressIndicator {
        constructor(container, options = {}) {
            this.container = typeof container === 'string' ? document.querySelector(container) : container;
            this.value = options.value || 0;
            this.max = options.max || 100;
            this.options = {
                label: options.label || '',
                showPercent: options.showPercent !== false,
                color: options.color || 'gold',
                height: options.height || 8,
                animated: options.animated !== false,
                ...options
            };
            this.init();
        }

        init() {
            if (!this.container) return;
            this.render();
        }

        render() {
            const percent = (this.value / this.max) * 100;
            
            this.container.innerHTML = `
                <div class="progress-indicator">
                    ${this.options.label ? `<span class="progress-label">${this.options.label}</span>` : ''}
                    <div class="progress-bar" style="height: ${this.options.height}px;">
                        <div class="progress-fill ${this.options.color}" style="width: ${percent}%;"></div>
                    </div>
                    ${this.options.showPercent ? `<span class="progress-percent">${percent.toFixed(0)}%</span>` : ''}
                </div>
            `;
        }

        update(value) {
            this.value = value;
            const percent = (this.value / this.max) * 100;
            const fill = this.container.querySelector('.progress-fill');
            if (fill) {
                fill.style.width = `${percent}%`;
            }
        }
    }

    // ================================================
    // TICKER COMPONENT
    // ================================================
    
    class PriceTicker {
        constructor(container, items = []) {
            this.container = typeof container === 'string' ? document.querySelector(container) : container;
            this.items = items;
            this.currentIndex = 0;
            this.init();
        }

        init() {
            if (!this.container) return;
            this.render();
            this.startAnimation();
        }

        render() {
            this.container.innerHTML = `
                <div class="price-ticker">
                    ${this.items.map((item, index) => `
                        <div class="ticker-item" data-index="${index}">
                            <span class="ticker-label">${item.label}:</span>
                            <span class="ticker-value">${item.value}</span>
                            <span class="ticker-change ${item.direction}">${item.change}</span>
                        </div>
                    `).join('')}
                </div>
            `;
        }

        startAnimation() {
            setInterval(() => {
                this.currentIndex = (this.currentIndex + 1) % this.items.length;
                this.container.querySelectorAll('.ticker-item').forEach((el, index) => {
                    el.style.opacity = index === this.currentIndex ? '1' : '0.3';
                });
            }, 3000);
        }

        updateItems(newItems) {
            this.items = newItems;
            this.render();
        }
    }

    // ================================================
    // RSI GAUGE COMPONENT
    // ================================================
    
    class RSIGauge {
        constructor(container, options = {}) {
            this.container = typeof container === 'string' ? document.querySelector(container) : container;
            this.value = options.value || 50;
            this.options = {
                min: options.min || 0,
                max: options.max || 100,
                size: options.size || 120,
                ...options
            };
            this.init();
        }

        init() {
            if (!this.container) return;
            this.render();
        }

        render() {
            const { min, max, size } = this.options;
            const percent = (this.value - min) / (max - min) * 100;
            
            let status = 'Neutral';
            let statusColor = 'var(--neutral)';
            
            if (this.value >= 70) {
                status = 'Overbought';
                statusColor = 'var(--bearish)';
            } else if (this.value <= 30) {
                status = 'Oversold';
                statusColor = 'var(--bullish)';
            }

            this.container.innerHTML = `
                <div class="rsi-gauge">
                    <svg viewBox="0 0 100 60" width="${size}" height="${size * 0.6}">
                        <!-- Background arc -->
                        <path d="M 10 50 A 40 40 0 0 1 90 50" 
                              fill="none" 
                              stroke="var(--bg-card-hover)" 
                              stroke-width="8"
                              stroke-linecap="round"/>
                        
                        <!-- Colored zones -->
                        <path d="M 10 50 A 40 40 0 0 1 30 15" 
                              fill="none" 
                              stroke="var(--bullish)" 
                              stroke-width="8"
                              stroke-linecap="round"
                              opacity="0.3"/>
                        <path d="M 30 15 A 40 40 0 0 1 70 15" 
                              fill="none" 
                              stroke="var(--neutral)" 
                              stroke-width="8"
                              stroke-linecap="round"
                              opacity="0.3"/>
                        <path d="M 70 15 A 40 40 0 0 1 90 50" 
                              fill="none" 
                              stroke="var(--bearish)" 
                              stroke-width="8"
                              stroke-linecap="round"
                              opacity="0.3"/>
                        
                        <!-- Value arc -->
                        <path d="M 10 50 A 40 40 0 0 1 ${10 + (90-10) * (percent/100)} 50" 
                              fill="none" 
                              stroke="${statusColor}" 
                              stroke-width="8"
                              stroke-linecap="round"
                              class="value-arc"/>
                        
                        <!-- Needle -->
                        <line x1="50" y1="50" 
                              x2="${50 + 30 * Math.cos((Math.PI * (100 - percent)) / 100 - Math.PI / 2)}" 
                              y2="${50 + 30 * Math.sin((Math.PI * (100 - percent)) / 100 - Math.PI / 2)}" 
                              stroke="${statusColor}" 
                              stroke-width="2"
                              stroke-linecap="round"/>
                        
                        <!-- Center dot -->
                        <circle cx="50" cy="50" r="4" fill="${statusColor}"/>
                    </svg>
                    <div class="rsi-value" style="color: ${statusColor}">${this.value.toFixed(1)}</div>
                    <div class="rsi-label">${status}</div>
                </div>
            `;
        }

        update(value) {
            this.value = value;
            this.render();
        }
    }

    // ================================================
    // LEVELS VISUALIZATION
    // ================================================
    
    class LevelsChart {
        constructor(container, levels = {}, currentPrice = 0) {
            this.container = typeof container === 'string' ? document.querySelector(container) : container;
            this.levels = levels;
            this.currentPrice = currentPrice;
            this.init();
        }

        init() {
            if (!this.container) return;
            this.render();
        }

        render() {
            const allLevels = [
                ...this.levels.support.map(l => ({ price: l.price, type: 'support', strength: l.strength })),
                ...this.levels.resistance.map(l => ({ price: l.price, type: 'resistance', strength: l.strength }))
            ].sort((a, b) => a.price - b.price);

            const minPrice = allLevels[0]?.price * 0.98 || this.currentPrice * 0.95;
            const maxPrice = allLevels[allLevels.length - 1]?.price * 1.02 || this.currentPrice * 1.05;
            const range = maxPrice - minPrice;

            const toPercent = (price) => ((price - minPrice) / range) * 100;
            const currentPercent = toPercent(this.currentPrice);

            this.container.innerHTML = `
                <div class="levels-chart">
                    <div class="levels-bar">
                        <div class="current-price-marker" style="bottom: ${currentPercent}%;">
                            <span class="marker-label">Current: $${this.currentPrice.toFixed(2)}</span>
                        </div>
                        ${allLevels.map(level => `
                            <div class="level-marker ${level.type}" 
                                 style="bottom: ${toPercent(level.price)}%;"
                                 data-strength="${level.strength}">
                                <span class="marker-price">$${level.price.toFixed(2)}</span>
                                <span class="marker-type">${level.type === 'support' ? 'S' : 'R'}</span>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        }
    }

    // ================================================
    // EXPORTED API
    // ================================================
    
    window.TradingHubComponents = {
        MiniChart,
        PriceDisplay,
        ProgressIndicator,
        PriceTicker,
        RSIGauge,
        LevelsChart
    };

})();
