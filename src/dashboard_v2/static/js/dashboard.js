/**
 * KimpTrade Dashboard V2 - Client-side JavaScript
 *
 * Handles:
 * - Data fetching from API endpoints
 * - Auto-refresh every 10 seconds
 * - Error handling with retry
 * - Loading states
 */

// Global state
let refreshIntervalId = null;
let kimpChart = null;

/**
 * Initialize the dashboard
 * @param {number} refreshInterval - Refresh interval in milliseconds
 */
function initDashboard(refreshInterval = 10000) {
    console.log('Initializing dashboard with refresh interval:', refreshInterval);

    // Initial data fetch
    refreshAllData();

    // Set up auto-refresh
    if (refreshIntervalId) {
        clearInterval(refreshIntervalId);
    }
    refreshIntervalId = setInterval(refreshAllData, refreshInterval);

    // Initialize chart
    initKimpChart();
}

/**
 * Refresh all dashboard data
 */
async function refreshAllData() {
    console.log('Refreshing all data...');

    try {
        // Fetch all data in parallel
        const results = await Promise.allSettled([
            fetchKimpData(),
            fetchPositionData(),
            fetchPnlData(),
            fetchHealthData(),
        ]);

        // Check for any failures
        const failures = results.filter(r => r.status === 'rejected');
        if (failures.length > 0) {
            console.error('Some data fetches failed:', failures);
        }

        // Update last updated time
        updateLastUpdated();

    } catch (error) {
        console.error('Error refreshing data:', error);
        showError('데이터 갱신 중 오류가 발생했습니다.');
    }
}

/**
 * Fetch kimp data from API
 */
async function fetchKimpData() {
    try {
        const response = await fetch('/api/kimp/current');
        if (!response.ok) throw new Error(`HTTP ${response.status}`);

        const data = await response.json();
        updateKimpDisplay(data);

        // Also fetch history for chart
        const historyResponse = await fetch('/api/kimp');
        if (historyResponse.ok) {
            const historyData = await historyResponse.json();
            updateKimpChart(historyData);
        }

    } catch (error) {
        console.error('Kimp fetch error:', error);
        showSectionError('kimp');
        throw error;
    }
}

/**
 * Fetch position data from API
 */
async function fetchPositionData() {
    try {
        const response = await fetch('/api/position');
        if (!response.ok) throw new Error(`HTTP ${response.status}`);

        const data = await response.json();
        updatePositionDisplay(data);

    } catch (error) {
        console.error('Position fetch error:', error);
        showSectionError('position');
        throw error;
    }
}

/**
 * Fetch PnL data from API
 */
async function fetchPnlData() {
    try {
        const response = await fetch('/api/pnl');
        if (!response.ok) throw new Error(`HTTP ${response.status}`);

        const data = await response.json();
        updatePnlDisplay(data);

    } catch (error) {
        console.error('PnL fetch error:', error);
        showSectionError('pnl');
        throw error;
    }
}

/**
 * Fetch health/status data from API
 */
async function fetchHealthData() {
    try {
        const response = await fetch('/api/health');
        if (!response.ok) throw new Error(`HTTP ${response.status}`);

        const data = await response.json();
        updateHealthDisplay(data);

    } catch (error) {
        console.error('Health fetch error:', error);
        showSectionError('health');
        throw error;
    }
}

/**
 * Update kimp display
 * @param {Object} data - Kimp data from API
 */
function updateKimpDisplay(data) {
    const currentKimpEl = document.getElementById('currentKimp');
    const usdKrwEl = document.getElementById('usdKrw');

    if (currentKimpEl && data.kimp !== undefined) {
        currentKimpEl.textContent = `${data.kimp.toFixed(2)}%`;
        currentKimpEl.classList.remove('skeleton');
    }

    if (usdKrwEl && data.usd_krw !== undefined) {
        usdKrwEl.textContent = `₩${data.usd_krw.toLocaleString()}`;
        usdKrwEl.classList.remove('skeleton');
    }
}

/**
 * Update position display
 * @param {Object} data - Position data from API
 */
function updatePositionDisplay(data) {
    const totalInvestedEl = document.getElementById('totalInvested');
    const positionsTableEl = document.getElementById('positionsTable');

    if (totalInvestedEl && data.total_invested_krw !== undefined) {
        totalInvestedEl.textContent = `₩${data.total_invested_krw.toLocaleString()}`;
        totalInvestedEl.classList.remove('skeleton');
    }

    if (positionsTableEl && data.positions) {
        updatePositionsTable(data.positions);
    }
}

/**
 * Update PnL display
 * @param {Object} data - PnL data from API
 */
function updatePnlDisplay(data) {
    const entryKimpEl = document.getElementById('entryKimp');
    const breakevenKimpEl = document.getElementById('breakevenKimp');
    const kimpProfitEl = document.getElementById('kimpProfit');
    const netProfitEl = document.getElementById('netProfit');
    const profitStatusEl = document.getElementById('profitStatus');

    if (entryKimpEl && data.entry_kimp !== undefined) {
        entryKimpEl.textContent = `${data.entry_kimp.toFixed(2)}%`;
    }

    if (breakevenKimpEl && data.breakeven_kimp !== undefined) {
        breakevenKimpEl.textContent = `${data.breakeven_kimp.toFixed(2)}%`;
        breakevenKimpEl.classList.remove('skeleton');
    }

    if (kimpProfitEl && data.kimp_profit !== undefined) {
        kimpProfitEl.textContent = `${data.kimp_profit >= 0 ? '+' : ''}${data.kimp_profit.toFixed(2)}%`;
        kimpProfitEl.classList.toggle('profit', data.kimp_profit >= 0);
        kimpProfitEl.classList.toggle('loss', data.kimp_profit < 0);
    }

    if (netProfitEl && data.net_profit !== undefined) {
        netProfitEl.textContent = `${data.net_profit >= 0 ? '+' : ''}${data.net_profit.toFixed(2)}%`;
        netProfitEl.classList.toggle('profit', data.net_profit >= 0);
        netProfitEl.classList.toggle('loss', data.net_profit < 0);
    }

    if (profitStatusEl && data.is_profitable !== undefined) {
        if (data.is_profitable) {
            profitStatusEl.textContent = '수익 구간';
            profitStatusEl.className = 'kpi-value data-value profit';
        } else {
            profitStatusEl.textContent = '손실 구간';
            profitStatusEl.className = 'kpi-value data-value loss';
        }
    }
}

/**
 * Update health/status display
 * @param {Object} data - Health data from API
 */
function updateHealthDisplay(data) {
    const systemStatusEl = document.getElementById('systemStatus');
    if (!systemStatusEl) return;

    // Clear existing content
    systemStatusEl.innerHTML = '';

    // Create status cards for each service
    const services = [
        { name: 'Dashboard', status: data.status === 'healthy' },
        { name: 'Supabase', status: data.supabase || false },
        { name: 'Upbit', status: data.upbit || false },
        { name: 'Binance', status: data.binance || false },
    ];

    services.forEach(service => {
        const card = document.createElement('div');
        card.className = 'flex items-center space-x-2 p-2 bg-gray-50 rounded';

        const dot = document.createElement('span');
        dot.className = `status-dot ${service.status ? 'status-dot-green' : 'status-dot-red'}`;

        const name = document.createElement('span');
        name.className = 'text-sm font-medium';
        name.textContent = service.name;

        card.appendChild(dot);
        card.appendChild(name);
        systemStatusEl.appendChild(card);
    });
}

/**
 * Update positions table
 * @param {Array} positions - Array of position objects
 */
function updatePositionsTable(positions) {
    const container = document.getElementById('positionsTable');
    if (!container) return;

    if (!positions || positions.length === 0) {
        container.innerHTML = '<p class="text-gray-500 text-center py-4">오픈 포지션 없음</p>';
        return;
    }

    let html = `
        <table class="neo-table">
            <thead>
                <tr>
                    <th>심볼</th>
                    <th>수량</th>
                    <th>진입가</th>
                    <th>현재가</th>
                    <th>손익</th>
                </tr>
            </thead>
            <tbody>
    `;

    positions.forEach(pos => {
        const pnlClass = pos.pnl >= 0 ? 'profit' : 'loss';
        html += `
            <tr>
                <td>${pos.symbol || 'BTC'}</td>
                <td>${pos.quantity?.toFixed(6) || '-'}</td>
                <td>₩${pos.entry_price?.toLocaleString() || '-'}</td>
                <td>₩${pos.current_price?.toLocaleString() || '-'}</td>
                <td class="${pnlClass}">${pos.pnl >= 0 ? '+' : ''}${pos.pnl?.toFixed(2) || 0}%</td>
            </tr>
        `;
    });

    html += '</tbody></table>';
    container.innerHTML = html;
}

/**
 * Initialize kimp chart
 */
function initKimpChart() {
    const ctx = document.getElementById('kimpChart');
    if (!ctx) return;

    kimpChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: '김프율 (%)',
                data: [],
                borderColor: '#84CC16',
                backgroundColor: 'rgba(132, 204, 22, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    display: true,
                    title: {
                        display: false,
                    },
                    ticks: {
                        maxTicksLimit: 12,
                    }
                },
                y: {
                    display: true,
                    title: {
                        display: true,
                        text: 'KIMP (%)'
                    }
                }
            },
            plugins: {
                legend: {
                    display: false,
                }
            }
        }
    });
}

/**
 * Update kimp chart with new data
 * @param {Array} data - Array of kimp history data
 */
function updateKimpChart(data) {
    if (!kimpChart || !data || !Array.isArray(data)) return;

    const labels = data.map(d => {
        const date = new Date(d.timestamp);
        return `${date.getHours()}:${date.getMinutes().toString().padStart(2, '0')}`;
    });

    const values = data.map(d => d.kimp);

    kimpChart.data.labels = labels;
    kimpChart.data.datasets[0].data = values;
    kimpChart.update('none');
}

/**
 * Update last updated timestamp
 */
function updateLastUpdated() {
    const el = document.getElementById('lastUpdated');
    if (el) {
        const now = new Date();
        el.textContent = `마지막 업데이트: ${now.toLocaleTimeString()}`;
    }
}

/**
 * Show section-specific error
 * @param {string} sectionName - Name of the section
 */
function showSectionError(sectionName) {
    const elements = document.querySelectorAll(`[data-section="${sectionName}"]`);
    elements.forEach(el => {
        const valueEl = el.querySelector('.kpi-value');
        if (valueEl) {
            valueEl.textContent = '오류';
            valueEl.classList.add('loss');
        }
    });
}

/**
 * Show global error message
 * @param {string} message - Error message to display
 */
function showError(message) {
    const errorOverlay = document.getElementById('errorOverlay');
    const errorMessage = document.getElementById('errorMessage');

    if (errorOverlay && errorMessage) {
        errorMessage.textContent = message;
        errorOverlay.classList.remove('hidden');
    }
}

/**
 * Hide global error message
 */
function hideError() {
    const errorOverlay = document.getElementById('errorOverlay');
    if (errorOverlay) {
        errorOverlay.classList.add('hidden');
    }
}

/**
 * Retry failed data load
 */
function retryLoad() {
    hideError();
    refreshAllData();
}

/**
 * Load all data - alias for refreshAllData for compatibility
 */
function loadAllData() {
    refreshAllData();
}

// Export functions for use in templates
window.initDashboard = initDashboard;
window.refreshAllData = refreshAllData;
window.loadAllData = loadAllData;
window.showError = showError;
window.hideError = hideError;
window.retryLoad = retryLoad;
