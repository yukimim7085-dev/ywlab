/* ═══════════════════════════════════════════
   YW Finance Lab — Data Service Layer
   API integration: FRED, ECOS, CoinGecko,
   Frankfurter, Fear&Greed, RSS
   ═══════════════════════════════════════════ */

// ─── FRED API ───
async function fetchFRED(seriesId, limit = 2) {
    const cacheKey = `fred_${seriesId}`;
    const cached = DataCache.get(cacheKey);
    if (cached) return cached;

    const end = new Date().toISOString().slice(0, 10);
    const start = new Date(Date.now() - 400 * 86400000).toISOString().slice(0, 10);
    const url = `https://api.stlouisfed.org/fred/series/observations?series_id=${seriesId}&api_key=${FRED_KEY}&file_type=json&sort_order=desc&limit=${limit}&observation_start=${start}`;

    try {
        const data = await fetchWithProxy(url);
        if (!data) return DataCache.getStale(cacheKey);
        const obs = data.observations?.filter(o => o.value !== '.');
        if (obs && obs.length >= 2) {
            const current = parseFloat(obs[0].value);
            const prev = parseFloat(obs[1].value);
            const change = current - prev;
            const pct = prev !== 0 ? (change / prev) * 100 : 0;
            const result = { value: current, change, pct, date: obs[0].date };
            DataCache.set(cacheKey, result, TTL.FRED);
            return result;
        } else if (obs && obs.length === 1) {
            const result = { value: parseFloat(obs[0].value), change: 0, pct: 0, date: obs[0].date };
            DataCache.set(cacheKey, result, TTL.FRED);
            return result;
        }
    } catch (e) { console.warn('FRED error:', seriesId, e); }
    return DataCache.getStale(cacheKey);
}

async function fetchFREDSeries(seriesId, days = 365) {
    const cacheKey = `fred_series_${seriesId}_${days}`;
    const cached = DataCache.get(cacheKey);
    if (cached) return cached;

    const end = new Date().toISOString().slice(0, 10);
    const start = new Date(Date.now() - days * 86400000).toISOString().slice(0, 10);
    const url = `https://api.stlouisfed.org/fred/series/observations?series_id=${seriesId}&api_key=${FRED_KEY}&file_type=json&sort_order=asc&observation_start=${start}&observation_end=${end}`;

    try {
        const data = await fetchWithProxy(url);
        if (!data) return DataCache.getStale(cacheKey);
        const obs = data.observations?.filter(o => o.value !== '.').map(o => ({
            date: o.date,
            value: parseFloat(o.value)
        }));
        if (obs && obs.length > 0) {
            DataCache.set(cacheKey, obs, TTL.FRED);
            return obs;
        }
    } catch (e) { console.warn('FRED series error:', seriesId, e); }
    return DataCache.getStale(cacheKey);
}

// ─── ECOS API (Bank of Korea) ───
async function fetchECOS(statCode, itemCode) {
    const cacheKey = `ecos_${statCode}_${itemCode}`;
    const cached = DataCache.get(cacheKey);
    if (cached) return cached;

    const now = new Date();
    const end = now.getFullYear() + String(now.getMonth() + 1).padStart(2, '0');
    const startD = new Date(now);
    startD.setMonth(startD.getMonth() - 13);
    const start = startD.getFullYear() + String(startD.getMonth() + 1).padStart(2, '0');
    const url = `https://ecos.bok.or.kr/api/StatisticSearch/${ECOS_KEY}/json/kr/1/5/${statCode}/M/${start}/${end}/${itemCode}`;

    try {
        const data = await fetchWithProxy(url);
        if (!data) return DataCache.getStale(cacheKey);
        const rows = data?.StatisticSearch?.row;
        if (rows && rows.length >= 2) {
            const current = parseFloat(rows[rows.length - 1].DATA_VALUE);
            const prev = parseFloat(rows[rows.length - 2].DATA_VALUE);
            const change = current - prev;
            const pct = prev !== 0 ? (change / prev) * 100 : 0;
            const result = { value: current, change, pct, date: rows[rows.length - 1].TIME };
            DataCache.set(cacheKey, result, TTL.ECOS);
            return result;
        } else if (rows && rows.length === 1) {
            const result = { value: parseFloat(rows[0].DATA_VALUE), change: 0, pct: 0, date: rows[0].TIME };
            DataCache.set(cacheKey, result, TTL.ECOS);
            return result;
        }
    } catch (e) { console.warn('ECOS error:', statCode, e); }
    return DataCache.getStale(cacheKey);
}

// ─── CoinGecko API (no CORS proxy needed) ───
async function fetchCrypto() {
    const cacheKey = 'crypto_top';
    const cached = DataCache.get(cacheKey);
    if (cached) return cached;

    const url = 'https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=10&page=1&sparkline=true&price_change_percentage=24h';
    try {
        const data = await fetchDirectJSON(url, 10000);
        if (data && Array.isArray(data)) {
            const result = data.map(c => ({
                id: c.id,
                symbol: c.symbol.toUpperCase(),
                name: c.name,
                price: c.current_price,
                change24h: c.price_change_percentage_24h,
                marketCap: c.market_cap,
                image: c.image,
                sparkline: c.sparkline_in_7d?.price || []
            }));
            DataCache.set(cacheKey, result, TTL.CRYPTO);
            return result;
        }
    } catch (e) { console.warn('CoinGecko error:', e); }
    return DataCache.getStale(cacheKey);
}

// ─── Frankfurter Exchange Rates (no CORS proxy needed) ───
async function fetchForex() {
    const cacheKey = 'forex_rates';
    const cached = DataCache.get(cacheKey);
    if (cached) return cached;

    const url = 'https://api.frankfurter.dev/latest?base=USD&symbols=EUR,GBP,JPY,KRW,CNY,CHF';
    try {
        const data = await fetchDirectJSON(url, 8000);
        if (data && data.rates) {
            const result = {
                base: data.base,
                date: data.date,
                rates: data.rates
            };
            DataCache.set(cacheKey, result, TTL.FOREX);
            return result;
        }
    } catch (e) { console.warn('Frankfurter error:', e); }
    return DataCache.getStale(cacheKey);
}

// ─── Fear & Greed Index (no CORS proxy needed) ───
async function fetchFearGreed() {
    const cacheKey = 'fear_greed';
    const cached = DataCache.get(cacheKey);
    if (cached) return cached;

    const url = 'https://api.alternative.me/fng/?limit=30&format=json';
    try {
        const data = await fetchDirectJSON(url, 8000);
        if (data && data.data) {
            const result = data.data.map(d => ({
                value: parseInt(d.value),
                label: d.value_classification,
                timestamp: parseInt(d.timestamp) * 1000
            }));
            DataCache.set(cacheKey, result, TTL.FEAR_GREED);
            return result;
        }
    } catch (e) { console.warn('Fear & Greed error:', e); }
    return DataCache.getStale(cacheKey);
}

// ─── RSS News Feed via rss2json ───
async function fetchNews(feedUrl, tag) {
    const cacheKey = `news_${tag}`;
    const cached = DataCache.get(cacheKey);
    if (cached) return cached;

    const url = `https://api.rss2json.com/v1/api.json?rss_url=${encodeURIComponent(feedUrl)}`;
    try {
        const data = await fetchDirectJSON(url, 10000);
        if (data && data.items) {
            const result = data.items.slice(0, 10).map(item => ({
                title: item.title,
                link: item.link,
                pubDate: item.pubDate,
                source: data.feed?.title || tag,
                tag
            }));
            DataCache.set(cacheKey, result, TTL.NEWS);
            return result;
        }
    } catch (e) { console.warn('RSS error:', tag, e); }
    return DataCache.getStale(cacheKey);
}

// ─── Batch Loader ───
async function loadBatch(tasks, batchSize = 3) {
    const results = [];
    for (let i = 0; i < tasks.length; i += batchSize) {
        const batch = tasks.slice(i, i + batchSize);
        const batchResults = await Promise.all(batch.map(fn => fn()));
        results.push(...batchResults);
    }
    return results;
}

// ─── Dashboard Indicator Definitions ───
const INDICATORS_US = [
    { id: 'FEDFUNDS', label: '미국 기준금리', labelEn: 'Fed Funds Rate', flag: '🇺🇸', unit: '%', source: 'FRED' },
    { id: 'DGS10', label: '미국 10년물', labelEn: 'US 10Y Treasury', flag: '🇺🇸', unit: '%', source: 'FRED' },
    { id: 'DGS2', label: '미국 2년물', labelEn: 'US 2Y Treasury', flag: '🇺🇸', unit: '%', source: 'FRED' },
    { id: 'UNRATE', label: '미국 실업률', labelEn: 'US Unemployment', flag: '🇺🇸', unit: '%', source: 'FRED' },
    { id: 'CPIAUCSL', label: '미국 CPI', labelEn: 'US CPI', flag: '🇺🇸', unit: '', source: 'FRED' },
    { id: 'DCOILWTICO', label: 'WTI 유가', labelEn: 'WTI Oil', flag: '🛢️', unit: '$', source: 'FRED' },
    { id: 'VIXCLS', label: 'VIX 지수', labelEn: 'VIX', flag: '📊', unit: '', source: 'FRED' },
    { id: 'BAMLH0A0HYM2', label: '하이일드 스프레드', labelEn: 'HY Spread', flag: '📈', unit: '%', source: 'FRED' },
];

const INDICATORS_KR = [
    { id: 'bok_rate', label: '한국 기준금리', labelEn: 'BOK Rate', flag: '🇰🇷', unit: '%', source: 'ECOS', stat: '722Y001', item: '0101000' },
    { id: 'bok_cpi', label: '한국 CPI', labelEn: 'Korea CPI', flag: '🇰🇷', unit: '', source: 'ECOS', stat: '901Y009', item: '0' },
    { id: 'DEXKOUS', label: '원/달러 환율', labelEn: 'USD/KRW', flag: '🇰🇷', unit: '원', source: 'FRED' },
];

const MARKET_OVERVIEW_ITEMS = [
    { id: 'DGS10', label: '미 10년물', labelEn: 'US 10Y', flag: '🇺🇸', unit: '%', type: 'fred' },
    { id: 'DEXKOUS', label: '원/달러', labelEn: 'USD/KRW', flag: '🇰🇷', unit: '원', type: 'fred' },
    { id: 'VIXCLS', label: 'VIX', labelEn: 'VIX', flag: '📊', unit: '', type: 'fred' },
    { id: 'DCOILWTICO', label: 'WTI', labelEn: 'WTI', flag: '🛢️', unit: '$', type: 'fred' },
];

// ─── Chart Series Options ───
const CHART_SERIES_OPTIONS = [
    { id: 'DGS10', label: '미국 10년 국채 금리' },
    { id: 'DGS2', label: '미국 2년 국채 금리' },
    { id: 'FEDFUNDS', label: '미국 기준금리 (Fed Funds)' },
    { id: 'UNRATE', label: '미국 실업률' },
    { id: 'CPIAUCSL', label: '미국 CPI 지수' },
    { id: 'DCOILWTICO', label: 'WTI 유가' },
    { id: 'VIXCLS', label: 'VIX 변동성 지수' },
    { id: 'DEXKOUS', label: 'USD/KRW 환율' },
    { id: 'BAMLH0A0HYM2', label: '하이일드 스프레드' },
    { id: 'WALCL', label: '연준 총자산' },
    { id: 'T10Y2Y', label: '10Y-2Y 스프레드' },
    { id: 'GDP', label: '미국 GDP' },
];

// ─── News Feed Sources ───
const NEWS_FEEDS = [
    { url: 'https://feeds.bbci.co.uk/news/business/rss.xml', tag: 'global', label: 'BBC Business' },
    { url: 'https://rss.nytimes.com/services/xml/rss/nyt/Business.xml', tag: 'global', label: 'NYT Business' },
    { url: 'https://www.mk.co.kr/rss/30100041/', tag: 'korea', label: '매일경제' },
];

// ─── Indicator Impact Knowledge Base (Hybrid: static mapping) ───
const INDICATOR_IMPACT = {
    'FEDFUNDS': {
        name: '미국 기준금리 (Fed Funds Rate)',
        description: '미 연준이 설정하는 단기 정책금리. 모든 금융자산의 할인율에 영향.',
        upImpact: [
            { sector: '은행/금융', direction: 'positive', tickers: ['XLF','KRE','JPM','BAC'], reason: '순이자마진(NIM) 확대, 예대마진 증가' },
            { sector: '부동산/REITs', direction: 'negative', tickers: ['VNQ','IYR','O'], reason: '모기지 금리 상승 → 수요 위축, 차입비용 증가' },
            { sector: '기술/성장주', direction: 'negative', tickers: ['QQQ','ARKK','XLK'], reason: '미래 현금흐름 할인율 상승 → 밸류에이션 하락' },
            { sector: '유틸리티', direction: 'negative', tickers: ['XLU','NEE','DUK'], reason: '채권 대비 배당 매력 감소, 높은 부채 부담' },
            { sector: '채권', direction: 'negative', tickers: ['TLT','AGG','BND'], reason: '금리 상승 시 채권가격 하락' },
            { sector: '달러/원화', direction: 'mixed', tickers: ['UUP','FXE'], reason: '달러 강세 → 원화 약세, 수출기업 수혜' },
        ],
        relatedFRED: ['DGS10','DGS2','MORTGAGE30US','T10Y2Y']
    },
    'DGS10': {
        name: '미국 10년 국채 금리',
        description: '글로벌 자산 가격의 기준이 되는 장기 무위험 금리.',
        upImpact: [
            { sector: '기술/성장주', direction: 'negative', tickers: ['QQQ','MSFT','AAPL','NVDA'], reason: 'DCF 할인율 상승 → 고PER 종목 밸류에이션 압박' },
            { sector: '은행/금융', direction: 'positive', tickers: ['XLF','GS','MS'], reason: '장기 대출금리 상승으로 수익성 개선' },
            { sector: '부동산/건설', direction: 'negative', tickers: ['XHB','ITB','VNQ'], reason: '주택담보대출 금리 상승 → 주택 수요 감소' },
            { sector: '고배당주', direction: 'negative', tickers: ['VYM','SCHD','DVY'], reason: '채권 금리 상승 시 배당주 상대 매력 하락' },
            { sector: '신흥국', direction: 'negative', tickers: ['EEM','VWO','IEMG'], reason: '달러 강세 + 자본유출 압력' },
        ],
        relatedFRED: ['FEDFUNDS','DGS2','T10Y2Y','BAMLH0A0HYM2']
    },
    'DGS2': {
        name: '미국 2년 국채 금리',
        description: '연준 금리정책 기대를 가장 민감하게 반영하는 단기 금리.',
        upImpact: [
            { sector: '금리 민감주', direction: 'negative', tickers: ['QQQ','XLU','VNQ'], reason: '기준금리 인상 기대 강화 → 성장주·부동산 부담' },
            { sector: '달러', direction: 'positive', tickers: ['UUP','DXY'], reason: '단기 금리 상승 → 달러 강세' },
            { sector: '금/원자재', direction: 'negative', tickers: ['GLD','SLV','GDX'], reason: '실질금리 상승 → 비이자 자산 매력 감소' },
        ],
        relatedFRED: ['FEDFUNDS','DGS10','T10Y2Y']
    },
    'UNRATE': {
        name: '미국 실업률',
        description: '노동시장 건전성 지표. 경기 상태와 연준 정책에 직접 영향.',
        upImpact: [
            { sector: '소비재/리테일', direction: 'negative', tickers: ['XLY','AMZN','WMT','TGT'], reason: '소비자 지출 감소 우려' },
            { sector: '경기 방어주', direction: 'positive', tickers: ['XLP','PG','KO','JNJ'], reason: '경기 둔화 시 방어적 성격의 주식 선호' },
            { sector: '채권/안전자산', direction: 'positive', tickers: ['TLT','GLD','AGG'], reason: '경기 침체 우려 → 안전자산 수요 증가' },
            { sector: '연준 정책', direction: 'mixed', tickers: [], reason: '실업률 상승 → 금리 인하 기대 → 성장주에 긍정적 가능성' },
        ],
        relatedFRED: ['FEDFUNDS','CPIAUCSL','PAYEMS']
    },
    'CPIAUCSL': {
        name: '미국 CPI (소비자물가지수)',
        description: '인플레이션의 핵심 지표. 연준 금리정책의 직접적 결정 요인.',
        upImpact: [
            { sector: '원자재/에너지', direction: 'positive', tickers: ['XLE','USO','PDBC'], reason: '인플레 헤지 수단으로 원자재 수요 증가' },
            { sector: '금/귀금속', direction: 'positive', tickers: ['GLD','SLV','GDX'], reason: '인플레 헤지 자산으로 금 수요 증가' },
            { sector: '채권', direction: 'negative', tickers: ['TLT','AGG','TIPS'], reason: '금리 인상 기대 → 채권가격 하락 (TIPS는 수혜 가능)' },
            { sector: '기술/성장주', direction: 'negative', tickers: ['QQQ','XLK','ARKK'], reason: '금리 인상 경로 강화 → 밸류에이션 부담' },
            { sector: '부동산', direction: 'mixed', tickers: ['VNQ','O','AMT'], reason: '임대료 상승 수혜 vs 금리 상승 부담' },
        ],
        relatedFRED: ['FEDFUNDS','CPIAUCSL','CPILFESL','PCEPI']
    },
    'DCOILWTICO': {
        name: 'WTI 유가',
        description: '글로벌 에너지 가격의 벤치마크. 인플레이션과 기업 비용에 직접 영향.',
        upImpact: [
            { sector: '에너지/정유', direction: 'positive', tickers: ['XLE','XOM','CVX','COP'], reason: '유가 상승 → 에너지 기업 수익 증가' },
            { sector: '항공/운송', direction: 'negative', tickers: ['JETS','DAL','UAL','FDX'], reason: '연료비 부담 증가 → 마진 압박' },
            { sector: '화학/소재', direction: 'mixed', tickers: ['XLB','LYB','DOW'], reason: '원가 상승 부담 vs 제품가 전가 가능성' },
            { sector: '소비자', direction: 'negative', tickers: ['XLY','XLP'], reason: '유류비·물류비 상승 → 가처분소득 감소' },
            { sector: '한국 수출', direction: 'negative', tickers: [], reason: '원유 수입 비용 증가 → 무역수지 악화, 원화 약세' },
        ],
        relatedFRED: ['DCOILBRENTEU','GASREGW','CPIAUCSL']
    },
    'VIXCLS': {
        name: 'VIX 변동성 지수',
        description: 'S&P 500 옵션 내재변동성. 시장 공포 심리의 대표 지표.',
        upImpact: [
            { sector: '주식 전반', direction: 'negative', tickers: ['SPY','QQQ','IWM'], reason: 'VIX 급등 = 시장 공포 확산 → 주가 하락 동반' },
            { sector: '안전자산', direction: 'positive', tickers: ['TLT','GLD','UUP'], reason: '위험회피 심리 → 채권·금·달러 수요 증가' },
            { sector: '변동성 상품', direction: 'positive', tickers: ['UVXY','VXX'], reason: 'VIX 추종 ETF 직접 수혜' },
            { sector: '풋옵션/헤지', direction: 'positive', tickers: [], reason: '옵션 프리미엄 상승 → 헤지 비용 증가' },
        ],
        relatedFRED: ['BAMLH0A0HYM2','DGS10','T10Y2Y']
    },
    'BAMLH0A0HYM2': {
        name: '하이일드 스프레드',
        description: '투기등급 회사채와 국채의 금리 차이. 신용시장 리스크의 핵심 지표.',
        upImpact: [
            { sector: '하이일드 채권', direction: 'negative', tickers: ['HYG','JNK','USHY'], reason: '스프레드 확대 → 하이일드 채권 가격 하락' },
            { sector: '레버리지 기업', direction: 'negative', tickers: [], reason: '차입비용 증가 → 고부채 기업 재무 부담' },
            { sector: '은행/금융', direction: 'negative', tickers: ['XLF','KRE'], reason: '대출 부실 우려 증가' },
            { sector: '안전자산', direction: 'positive', tickers: ['TLT','GLD'], reason: '신용 리스크 확대 → 안전자산 선호' },
        ],
        relatedFRED: ['DGS10','FEDFUNDS','VIXCLS']
    },
    'DEXKOUS': {
        name: 'USD/KRW 환율',
        description: '원/달러 환율. 한국 수출기업과 외국인 투자에 직접 영향.',
        upImpact: [
            { sector: '수출 대기업', direction: 'positive', tickers: [], reason: '원화 약세 → 수출 가격경쟁력 개선 (삼성전자, 현대차 등)' },
            { sector: '수입 기업', direction: 'negative', tickers: [], reason: '수입 원가 상승 → 마진 압박 (항공, 정유)' },
            { sector: '외국인 투자', direction: 'negative', tickers: [], reason: '원화 약세 → 외국인 투자자 환차손 → 매도 압력' },
            { sector: '해외투자자', direction: 'mixed', tickers: [], reason: '해외주식 보유 시 환차익 발생' },
        ],
        relatedFRED: ['DGS10','FEDFUNDS','DCOILWTICO']
    },
    'bok_rate': {
        name: '한국 기준금리',
        description: '한국은행 금통위에서 결정하는 정책금리. 한국 금융시장의 핵심 변수.',
        upImpact: [
            { sector: '한국 은행주', direction: 'positive', tickers: [], reason: '예대마진 확대 → 은행 수익성 개선 (KB, 신한, 하나)' },
            { sector: '한국 부동산', direction: 'negative', tickers: [], reason: '주담대 금리 상승 → 부동산 수요 위축' },
            { sector: '한국 성장주', direction: 'negative', tickers: [], reason: '할인율 상승 → 고밸류 종목 부담 (2차전지, 바이오)' },
            { sector: '가계부채', direction: 'mixed', tickers: [], reason: '이자 부담 증가 → 소비 위축 가능성' },
        ],
        relatedFRED: ['FEDFUNDS','DEXKOUS']
    },
    'bok_cpi': {
        name: '한국 CPI',
        description: '한국 소비자물가지수. 한국은행 금리정책의 핵심 참고 지표.',
        upImpact: [
            { sector: '식품/유통', direction: 'negative', tickers: [], reason: '원가 상승 → 마진 압박' },
            { sector: '임대/부동산', direction: 'positive', tickers: [], reason: '임대료 상승 수혜' },
            { sector: '한국은행 정책', direction: 'mixed', tickers: [], reason: 'CPI 상승 → 금리 인상 가능성 → 시장 전반 부담' },
        ],
        relatedFRED: ['CPIAUCSL','FEDFUNDS']
    },
};

// ─── Crypto Detail Fetch ───
async function fetchCryptoDetail(coinId) {
    const cacheKey = `crypto_detail_${coinId}`;
    const cached = DataCache.get(cacheKey);
    if (cached) return cached;

    const url = `https://api.coingecko.com/api/v3/coins/${coinId}?localization=false&tickers=false&community_data=false&developer_data=false&sparkline=true`;
    try {
        const data = await fetchDirectJSON(url, 10000);
        if (data) {
            const result = {
                id: data.id,
                name: data.name,
                symbol: data.symbol?.toUpperCase(),
                price: data.market_data?.current_price?.usd,
                change24h: data.market_data?.price_change_percentage_24h,
                change7d: data.market_data?.price_change_percentage_7d,
                change30d: data.market_data?.price_change_percentage_30d,
                marketCap: data.market_data?.market_cap?.usd,
                volume24h: data.market_data?.total_volume?.usd,
                high24h: data.market_data?.high_24h?.usd,
                low24h: data.market_data?.low_24h?.usd,
                ath: data.market_data?.ath?.usd,
                athDate: data.market_data?.ath_date?.usd,
                sparkline: data.market_data?.sparkline_7d?.price || [],
                description: data.description?.en?.slice(0, 300) || '',
            };
            DataCache.set(cacheKey, result, TTL.CRYPTO);
            return result;
        }
    } catch (e) { console.warn('CoinGecko detail error:', coinId, e); }
    return DataCache.getStale(cacheKey);
}

// ─── Calendar Events (static, updated periodically) ───
const CALENDAR_EVENTS = [
    { date: '2026-03-18', title: 'FOMC 회의', detail: '미 연방공개시장위원회 정책 결정', importance: 'high' },
    { date: '2026-03-07', title: '미국 고용보고서', detail: '2월 비농업 고용 변화', importance: 'high' },
    { date: '2026-02-27', title: '한국 BOK 기준금리', detail: '한국은행 금통위 금리 결정', importance: 'high' },
    { date: '2026-03-12', title: '미국 CPI', detail: '2월 소비자물가지수 발표', importance: 'high' },
    { date: '2026-03-14', title: '미시간 소비자심리', detail: '3월 예비치 발표', importance: 'medium' },
    { date: '2026-02-28', title: '미국 GDP (수정치)', detail: 'Q4 2025 GDP 2차 추정치', importance: 'medium' },
    { date: '2026-03-03', title: 'ISM 제조업 PMI', detail: '2월 제조업 구매관리자지수', importance: 'medium' },
    { date: '2026-03-20', title: 'BOJ 금리 결정', detail: '일본은행 통화정책 결정', importance: 'medium' },
];
