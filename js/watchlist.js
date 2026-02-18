/* ═══════════════════════════════════════════
   YW Finance Lab — Watchlist
   Personal watchlist CRUD + preset templates
   ═══════════════════════════════════════════ */

const WATCHLIST_KEY = 'yw_watchlist';

const WATCHLIST_PRESETS = {
    korean: {
        label: '한국 투자자',
        labelEn: 'Korean Investor',
        items: [
            { type: 'fred', id: 'DEXKOUS', label: '원/달러 환율' },
            { type: 'fred', id: 'DGS10', label: '미 10년물 금리' },
            { type: 'fred', id: 'DCOILWTICO', label: 'WTI 유가' },
            { type: 'crypto', id: 'bitcoin', label: 'Bitcoin' },
            { type: 'crypto', id: 'ethereum', label: 'Ethereum' },
        ]
    },
    usmarket: {
        label: 'US Market',
        labelEn: 'US Market',
        items: [
            { type: 'fred', id: 'FEDFUNDS', label: 'Fed Funds Rate' },
            { type: 'fred', id: 'DGS10', label: 'US 10Y Treasury' },
            { type: 'fred', id: 'DGS2', label: 'US 2Y Treasury' },
            { type: 'fred', id: 'VIXCLS', label: 'VIX' },
            { type: 'fred', id: 'UNRATE', label: 'Unemployment Rate' },
        ]
    },
    crypto: {
        label: 'Crypto Tracker',
        labelEn: 'Crypto Tracker',
        items: [
            { type: 'crypto', id: 'bitcoin', label: 'Bitcoin' },
            { type: 'crypto', id: 'ethereum', label: 'Ethereum' },
            { type: 'crypto', id: 'solana', label: 'Solana' },
            { type: 'crypto', id: 'ripple', label: 'XRP' },
            { type: 'crypto', id: 'cardano', label: 'Cardano' },
        ]
    }
};

function getWatchlistItems() {
    try {
        const saved = localStorage.getItem(WATCHLIST_KEY);
        if (saved) return JSON.parse(saved);
    } catch { /* fallback */ }
    return WATCHLIST_PRESETS.korean.items;
}

function saveWatchlistItems(items) {
    try {
        localStorage.setItem(WATCHLIST_KEY, JSON.stringify(items));
    } catch { /* silent */ }
}

function addWatchlistItem(item) {
    const items = getWatchlistItems();
    const exists = items.some(i => i.type === item.type && i.id === item.id);
    if (!exists) {
        items.push(item);
        saveWatchlistItems(items);
    }
    return items;
}

function removeWatchlistItem(type, id) {
    let items = getWatchlistItems();
    items = items.filter(i => !(i.type === type && i.id === id));
    saveWatchlistItems(items);
    return items;
}

function applyWatchlistPreset(presetKey) {
    const preset = WATCHLIST_PRESETS[presetKey];
    if (preset) {
        saveWatchlistItems([...preset.items]);
    }
}

function renderWatchlistPanel() {
    const body = document.getElementById('body-watchlist');
    if (!body) return;
    const items = getWatchlistItems();

    let html = '<div class="watchlist-items">';
    if (items.length === 0) {
        html += `<div style="text-align:center;padding:1rem;color:var(--text-dim);font-size:0.85rem">${t('noData')}</div>`;
    } else {
        items.forEach(item => {
            html += `
            <div class="watchlist-item" id="wl-${item.type}-${item.id}">
                <div class="watchlist-item-left">
                    <span class="watchlist-item-type ${item.type}">${item.type.toUpperCase()}</span>
                    <span class="watchlist-item-label">${item.label}</span>
                </div>
                <div class="watchlist-item-right">
                    <span class="watchlist-item-value" id="wl-val-${item.type}-${item.id}">--</span>
                    <button class="watchlist-remove" onclick="onRemoveWatchlistItem('${item.type}','${item.id}')" title="삭제">✕</button>
                </div>
            </div>`;
        });
    }
    html += '</div>';

    // Add input
    html += `
    <div class="watchlist-add-wrap">
        <input type="text" class="watchlist-add-input" id="watchlistAddInput" placeholder="FRED ID (예: DGS10)">
        <button class="watchlist-add-btn" onclick="onAddWatchlistItem()">${t('addToWatchlist')}</button>
    </div>`;

    // Presets
    html += '<div class="watchlist-presets">';
    Object.keys(WATCHLIST_PRESETS).forEach(key => {
        const preset = WATCHLIST_PRESETS[key];
        html += `<button class="watchlist-preset-btn" onclick="onApplyPreset('${key}')">${preset.label}</button>`;
    });
    html += '</div>';

    body.innerHTML = html;
}

function onRemoveWatchlistItem(type, id) {
    removeWatchlistItem(type, id);
    renderWatchlistPanel();
    loadWatchlistData();
}

function onAddWatchlistItem() {
    const input = document.getElementById('watchlistAddInput');
    if (!input) return;
    const val = input.value.trim().toUpperCase();
    if (!val) return;
    addWatchlistItem({ type: 'fred', id: val, label: val });
    input.value = '';
    renderWatchlistPanel();
    loadWatchlistData();
}

function onApplyPreset(key) {
    applyWatchlistPreset(key);
    renderWatchlistPanel();
    loadWatchlistData();
}

async function loadWatchlistData() {
    const items = getWatchlistItems();
    for (const item of items) {
        const valEl = document.getElementById(`wl-val-${item.type}-${item.id}`);
        if (!valEl) continue;

        if (item.type === 'fred') {
            const result = await fetchFRED(item.id);
            if (result) {
                valEl.textContent = formatValue(result.value, guessUnit(item.id), item.id);
            }
        } else if (item.type === 'crypto') {
            const cryptoData = DataCache.getStale('crypto_top');
            if (cryptoData) {
                const coin = cryptoData.find(c => c.id === item.id);
                if (coin) {
                    valEl.textContent = '$' + coin.price.toLocaleString('en-US', { maximumFractionDigits: 2 });
                }
            }
        }
    }
}

function guessUnit(fredId) {
    const percentIds = ['FEDFUNDS', 'DGS10', 'DGS2', 'DGS30', 'UNRATE', 'BAMLH0A0HYM2', 'T10Y2Y'];
    const dollarIds = ['DCOILWTICO'];
    const wonIds = ['DEXKOUS'];
    if (percentIds.includes(fredId)) return '%';
    if (dollarIds.includes(fredId)) return '$';
    if (wonIds.includes(fredId)) return '원';
    return '';
}
