/* ═══════════════════════════════════════════
   YW Finance Lab — Panel System
   Layout management + localStorage persistence
   ═══════════════════════════════════════════ */

const PANELS = [
    { id: 'market-overview', labelKey: 'marketOverview', icon: '📊', wide: true, default: true },
    { id: 'us-indicators', labelKey: 'usIndicators', icon: '🇺🇸', wide: false, default: true },
    { id: 'kr-indicators', labelKey: 'krIndicators', icon: '🇰🇷', wide: false, default: true },
    { id: 'crypto', labelKey: 'crypto', icon: '₿', wide: false, default: true },
    { id: 'forex', labelKey: 'forex', icon: '💱', wide: false, default: true },
    { id: 'fear-greed', labelKey: 'fearGreed', icon: '😱', wide: false, default: true },
    { id: 'chart-workspace', labelKey: 'chartWorkspace', icon: '📈', wide: true, default: true },
    { id: 'news-feed', labelKey: 'newsFeed', icon: '📰', wide: false, default: true },
    { id: 'watchlist', labelKey: 'watchlist', icon: '⭐', wide: false, default: true },
    { id: 'calendar', labelKey: 'calendar', icon: '📅', wide: false, default: true },
];

const LAYOUT_KEY = 'yw_panel_layout';

function getLayout() {
    try {
        const saved = localStorage.getItem(LAYOUT_KEY);
        if (saved) {
            const layout = JSON.parse(saved);
            // Merge with defaults (new panels get default visibility)
            const result = {};
            PANELS.forEach(p => {
                result[p.id] = layout[p.id] !== undefined ? layout[p.id] : p.default;
            });
            return result;
        }
    } catch { /* fallback */ }
    const defaults = {};
    PANELS.forEach(p => { defaults[p.id] = p.default; });
    return defaults;
}

function saveLayout(layout) {
    try {
        localStorage.setItem(LAYOUT_KEY, JSON.stringify(layout));
    } catch { /* silent */ }
}

function togglePanel(id) {
    const layout = getLayout();
    layout[id] = !layout[id];
    saveLayout(layout);
    applyLayout();
}

function applyLayout() {
    const layout = getLayout();
    PANELS.forEach(p => {
        const el = document.getElementById(`panel-${p.id}`);
        if (el) {
            el.classList.toggle('hidden', !layout[p.id]);
        }
    });
}

function isPanelVisible(id) {
    return getLayout()[id] !== false;
}

// Mobile panel collapse/expand
function togglePanelCollapse(id) {
    const body = document.querySelector(`#panel-${id} .panel-body`);
    if (body) {
        body.classList.toggle('collapsed');
    }
}

function renderPanelGrid() {
    const grid = document.getElementById('panelGrid');
    if (!grid) return;
    const layout = getLayout();

    grid.innerHTML = PANELS.map(p => {
        const hidden = !layout[p.id] ? ' hidden' : '';
        const wide = p.wide ? ' panel-wide' : '';
        return `
        <div class="panel${wide}${hidden}" id="panel-${p.id}">
            <div class="panel-header" onclick="if(window.innerWidth<=768)togglePanelCollapse('${p.id}')">
                <div class="panel-title">
                    <span class="panel-title-icon">${p.icon}</span>
                    ${t(p.labelKey)}
                </div>
                <div class="panel-actions">
                    <span class="panel-badge live" id="badge-${p.id}">LIVE</span>
                </div>
            </div>
            <div class="panel-body" id="body-${p.id}">
                <div class="panel-loading">
                    <div class="spinner"></div>
                    ${t('loading')}
                </div>
            </div>
        </div>`;
    }).join('');
}

function renderSettingsToggles() {
    const container = document.getElementById('settingsToggles');
    if (!container) return;
    const layout = getLayout();

    container.innerHTML = PANELS.map(p => `
        <div class="settings-toggle-item">
            <span class="settings-toggle-label">${p.icon} ${t(p.labelKey)}</span>
            <label class="settings-toggle">
                <input type="checkbox" ${layout[p.id] ? 'checked' : ''} onchange="togglePanel('${p.id}')">
                <span class="settings-toggle-track"></span>
            </label>
        </div>
    `).join('');
}
