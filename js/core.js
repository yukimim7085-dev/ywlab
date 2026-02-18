/* ═══════════════════════════════════════════
   YW Finance Lab — Core Utilities
   fetchWithProxy, DataCache, formatters, i18n
   ═══════════════════════════════════════════ */

// ─── API Keys ───
const FRED_KEY = '4fb5dac909861e78d5e76dadeb5cf9d7';
const ECOS_KEY = 'QZIGLKAE4NXE2AH490NG';

// ─── CORS Proxy Chain ───
const PROXIES = [
    url => `https://api.allorigins.win/raw?url=${encodeURIComponent(url)}`,
    url => `https://corsproxy.io/?${encodeURIComponent(url)}`,
    url => url
];

async function fetchWithProxy(url) {
    for (const proxy of PROXIES) {
        try {
            const resp = await fetch(proxy(url), { signal: AbortSignal.timeout(6000) });
            if (resp.ok) {
                const text = await resp.text();
                return JSON.parse(text);
            }
        } catch (e) { /* next proxy */ }
    }
    return null;
}

async function fetchDirectJSON(url, timeout = 8000) {
    try {
        const resp = await fetch(url, { signal: AbortSignal.timeout(timeout) });
        if (resp.ok) return await resp.json();
    } catch (e) { /* silent */ }
    return null;
}

// ─── DataCache (localStorage) ───
const DataCache = {
    _prefix: 'yw_cache_',

    get(key) {
        try {
            const raw = localStorage.getItem(this._prefix + key);
            if (!raw) return null;
            const entry = JSON.parse(raw);
            if (Date.now() < entry.expires) return entry.data;
            return null; // expired
        } catch { return null; }
    },

    getStale(key) {
        try {
            const raw = localStorage.getItem(this._prefix + key);
            if (!raw) return null;
            return JSON.parse(raw).data;
        } catch { return null; }
    },

    set(key, data, ttlMs) {
        try {
            localStorage.setItem(this._prefix + key, JSON.stringify({
                data,
                expires: Date.now() + ttlMs,
                timestamp: Date.now()
            }));
        } catch (e) {
            // localStorage full — clear old entries
            this._cleanup();
            try {
                localStorage.setItem(this._prefix + key, JSON.stringify({
                    data,
                    expires: Date.now() + ttlMs,
                    timestamp: Date.now()
                }));
            } catch { /* give up */ }
        }
    },

    getTimestamp(key) {
        try {
            const raw = localStorage.getItem(this._prefix + key);
            if (!raw) return null;
            return JSON.parse(raw).timestamp;
        } catch { return null; }
    },

    _cleanup() {
        const keys = [];
        for (let i = 0; i < localStorage.length; i++) {
            const k = localStorage.key(i);
            if (k && k.startsWith(this._prefix)) keys.push(k);
        }
        // remove oldest half
        keys.sort();
        const half = Math.ceil(keys.length / 2);
        for (let i = 0; i < half; i++) {
            localStorage.removeItem(keys[i]);
        }
    }
};

// ─── Cache TTLs ───
const TTL = {
    FRED: 60 * 60 * 1000,       // 1 hour
    ECOS: 60 * 60 * 1000,       // 1 hour
    CRYPTO: 2 * 60 * 1000,      // 2 minutes
    FOREX: 60 * 60 * 1000,      // 1 hour
    FEAR_GREED: 15 * 60 * 1000, // 15 minutes
    NEWS: 15 * 60 * 1000        // 15 minutes
};

// ─── Formatters ───
function formatCurrency(val, currency = 'USD') {
    if (val == null || isNaN(val)) return '--';
    if (currency === 'KRW') return formatKoreanWon(val);
    return '$' + val.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function formatKoreanWon(val) {
    if (val == null || isNaN(val)) return '--';
    return val.toLocaleString('ko-KR', { maximumFractionDigits: 0 }) + '원';
}

function formatPercent(val, decimals = 2) {
    if (val == null || isNaN(val)) return '--';
    const sign = val > 0 ? '+' : '';
    return sign + val.toFixed(decimals) + '%';
}

function formatCompact(val) {
    if (val == null || isNaN(val)) return '--';
    const abs = Math.abs(val);
    if (abs >= 1e12) return (val / 1e12).toFixed(1) + 'T';
    if (abs >= 1e9) return (val / 1e9).toFixed(1) + 'B';
    if (abs >= 1e6) return (val / 1e6).toFixed(1) + 'M';
    if (abs >= 1e3) return (val / 1e3).toFixed(1) + 'K';
    return val.toFixed(2);
}

function formatValue(val, unit, id) {
    if (val == null) return '--';
    if (unit === 'B$') return '$' + (val / 1000000).toFixed(1) + 'T';
    if (unit === '$') return '$' + val.toFixed(2);
    if (unit === '원') return val.toFixed(0).replace(/\B(?=(\d{3})+(?!\d))/g, ',') + '원';
    if (unit === '%') return val.toFixed(2) + '%';
    if (id === 'CPIAUCSL' || id === 'bok_cpi') return val.toFixed(1);
    return val.toFixed(2);
}

function formatTimeAgo(timestamp) {
    if (!timestamp) return '';
    const diff = Date.now() - timestamp;
    const mins = Math.floor(diff / 60000);
    if (mins < 1) return '방금 전';
    if (mins < 60) return `${mins}분 전`;
    const hours = Math.floor(mins / 60);
    if (hours < 24) return `${hours}시간 전`;
    return `${Math.floor(hours / 24)}일 전`;
}

// ─── i18n ───
const i18nStrings = {
    ko: {
        dashboard: '대시보드',
        refresh: '새로고침',
        settings: '설정',
        lastUpdate: '마지막 업데이트',
        loading: '로딩 중...',
        loadFailed: '연결 실패',
        retry: '재시도',
        marketOverview: '시장 개요',
        usIndicators: '미국 경제지표',
        krIndicators: '한국 경제지표',
        crypto: '암호화폐',
        forex: '환율',
        fearGreed: 'Fear & Greed',
        chartWorkspace: '차트 분석',
        newsFeed: '뉴스 피드',
        watchlist: '관심목록',
        calendar: '경제 캘린더',
        panelSettings: '패널 설정',
        language: '언어',
        watchlistPresets: '워치리스트 템플릿',
        all: '전체',
        korea: '한국',
        global: '글로벌',
        addToWatchlist: '추가',
        extremeFear: '극도의 공포',
        fear: '공포',
        neutral: '중립',
        greed: '탐욕',
        extremeGreed: '극도의 탐욕',
        noData: '데이터 없음',
        loaded: '로드됨'
    },
    en: {
        dashboard: 'Dashboard',
        refresh: 'Refresh',
        settings: 'Settings',
        lastUpdate: 'Last Update',
        loading: 'Loading...',
        loadFailed: 'Connection Failed',
        retry: 'Retry',
        marketOverview: 'Market Overview',
        usIndicators: 'US Indicators',
        krIndicators: 'KR Indicators',
        crypto: 'Cryptocurrency',
        forex: 'Forex',
        fearGreed: 'Fear & Greed',
        chartWorkspace: 'Chart Workspace',
        newsFeed: 'News Feed',
        watchlist: 'Watchlist',
        calendar: 'Economic Calendar',
        panelSettings: 'Panel Settings',
        language: 'Language',
        watchlistPresets: 'Watchlist Presets',
        all: 'All',
        korea: 'Korea',
        global: 'Global',
        addToWatchlist: 'Add',
        extremeFear: 'Extreme Fear',
        fear: 'Fear',
        neutral: 'Neutral',
        greed: 'Greed',
        extremeGreed: 'Extreme Greed',
        noData: 'No Data',
        loaded: 'Loaded'
    }
};

function getLang() {
    return localStorage.getItem('yw_lang') || 'ko';
}

function setLang(lang) {
    localStorage.setItem('yw_lang', lang);
}

function t(key) {
    const lang = getLang();
    return (i18nStrings[lang] && i18nStrings[lang][key]) || i18nStrings.ko[key] || key;
}
