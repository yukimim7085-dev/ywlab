"""
YW Finance Terminal v1.0
Toss Securities-style Investment Analysis Platform
- Universal Ticker Search (Stocks, Crypto, ETFs, FRED)
- Financial Statement Analysis (All key ratios with explanations)
- Economic Indicator Impact Analysis (Sector/Stock mapping)
- Real-time Market Data Dashboard
- Technical Analysis Charts
"""

import os
# Fix SSL cert path for non-ASCII usernames (한글 사용자명)
_cert_path = "C:/ProgramData/ssl/cacert.pem"
if os.path.exists(_cert_path):
    os.environ["CURL_CA_BUNDLE"] = _cert_path
    os.environ["SSL_CERT_FILE"] = _cert_path
    os.environ["REQUESTS_CA_BUNDLE"] = _cert_path

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import requests
from datetime import datetime, timedelta
import yfinance as yf
import json

# ══════════════════════════════════════════════
#  PAGE CONFIG
# ══════════════════════════════════════════════
st.set_page_config(
    page_title="YW Finance Terminal",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ══════════════════════════════════════════════
#  API KEYS
# ══════════════════════════════════════════════
try:
    ECOS_KEY = st.secrets["ECOS_API_KEY"]
    FRED_KEY = st.secrets["FRED_API_KEY"]
except Exception:
    ECOS_KEY = "QZIGLKAE4NXE2AH490NG"
    FRED_KEY = "4fb5dac909861e78d5e76dadeb5cf9d7"

# ══════════════════════════════════════════════
#  TOSS SECURITIES STYLE UI
# ══════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@300;400;500;600;700;800&display=swap');

/* ─── 토스 컬러 시스템 ─── */
:root {
    --toss-blue: #3182f6;
    --toss-blue-light: #e8f3ff;
    --toss-red: #f04452;
    --toss-red-light: #fff0f0;
    --toss-green: #00b386;
    --toss-green-light: #e8fff3;
    --toss-bg: #f4f5f7;
    --toss-card: #ffffff;
    --toss-text: #191f28;
    --toss-text2: #4e5968;
    --toss-text3: #8b95a1;
    --toss-text4: #b0b8c1;
    --toss-border: #e5e8eb;
    --toss-border-light: #f2f4f6;
}

/* ─── 글로벌 ─── */
*, *::before, *::after {
    font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, sans-serif !important;
}

.block-container {
    padding: 1.2rem 1.5rem 6rem 1.5rem !important;
    max-width: 1200px;
}

/* ─── 하단 겹침 방지 ─── */
div[data-testid="stBottom"],
div[data-testid="stBottomBlockContainer"],
div[data-testid="InputInstructions"],
div[class*="stChatInput"],
div[class*="bottom"],
.stBottom {
    display: none !important;
    height: 0 !important;
    overflow: hidden !important;
    position: static !important;
}
/* 본문 하단에 fixed 요소가 겹치지 않도록 */
section.main > div.block-container {
    padding-bottom: 80px !important;
}

/* ─── 사이드바 ─── */
section[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid var(--toss-border);
}

.sidebar-brand {
    padding: 24px 20px 20px 20px;
    border-bottom: 1px solid var(--toss-border-light);
    margin-bottom: 8px;
}
.sidebar-brand h1 {
    font-size: 1.2rem;
    font-weight: 800;
    color: var(--toss-text);
    margin: 0;
    letter-spacing: -0.5px;
}
.sidebar-brand p {
    font-size: 0.72rem;
    color: var(--toss-blue);
    margin: 4px 0 0 0;
    font-weight: 600;
}

/* ─── 사이드바 라디오 (네비게이션) ─── */
.stRadio > div { gap: 2px !important; }
.stRadio > div > label {
    background: transparent !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 11px 16px !important;
    color: var(--toss-text2) !important;
    font-weight: 500 !important;
    font-size: 0.88rem !important;
    transition: all 0.15s !important;
}
.stRadio > div > label:hover {
    background: var(--toss-bg) !important;
    color: var(--toss-text) !important;
}
.stRadio > div > label[data-checked="true"],
.stRadio > div > label:has(input:checked) {
    background: var(--toss-blue-light) !important;
    color: var(--toss-blue) !important;
    font-weight: 700 !important;
}

/* ─── 메트릭 카드 ─── */
div[data-testid="stMetric"] {
    background: #ffffff;
    border: none;
    border-radius: 16px;
    padding: 18px 20px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    transition: all 0.2s ease;
}
div[data-testid="stMetric"]:hover {
    box-shadow: 0 4px 12px rgba(0,0,0,0.06);
    transform: translateY(-2px);
}
div[data-testid="stMetric"] label {
    color: var(--toss-text3) !important;
    font-size: 0.75rem !important;
    font-weight: 500 !important;
}
div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    color: var(--toss-text) !important;
    font-weight: 700 !important;
    font-size: 1.4rem !important;
    letter-spacing: -0.5px;
}
div[data-testid="stMetric"] [data-testid="stMetricDelta"] {
    font-size: 0.78rem !important;
    font-weight: 600 !important;
}

/* ─── 탭 ─── */
.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    background: transparent;
    border-bottom: 1px solid var(--toss-border);
    padding: 0;
    border-radius: 0;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 0;
    padding: 12px 20px;
    color: var(--toss-text3);
    font-weight: 500;
    font-size: 0.88rem;
    background: transparent;
    border: none;
    border-bottom: 2px solid transparent;
    transition: all 0.15s;
}
.stTabs [data-baseweb="tab"]:hover {
    color: var(--toss-text2);
}
.stTabs [aria-selected="true"] {
    color: var(--toss-text) !important;
    font-weight: 700 !important;
    background: transparent !important;
    border-bottom: 2px solid var(--toss-blue) !important;
}
.stTabs [data-baseweb="tab-panel"] { padding-top: 20px; }

/* ─── 페이지 헤더 ─── */
.page-header {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 4px 0 20px 0;
    margin-bottom: 16px;
}
.page-header-icon {
    width: 44px; height: 44px;
    border-radius: 14px;
    background: var(--toss-blue-light);
    display: flex; align-items: center; justify-content: center;
    font-size: 1.3rem;
}
.page-header h1 {
    font-size: 1.6rem;
    font-weight: 800;
    color: var(--toss-text);
    margin: 0;
    letter-spacing: -0.5px;
}
.page-header p {
    font-size: 0.82rem;
    color: var(--toss-text3);
    margin: 2px 0 0 0;
    font-weight: 400;
}

/* ─── 상태바 ─── */
.status-bar {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 10px 18px;
    background: #ffffff;
    border-radius: 12px;
    margin-bottom: 20px;
    font-size: 0.78rem;
    color: var(--toss-text3);
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.status-dot {
    width: 7px; height: 7px;
    border-radius: 50%;
    background: var(--toss-green);
    display: inline-block;
    animation: pulse 2s infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.3; }
}

/* ─── 분석 카드 ─── */
.analysis-card {
    background: #ffffff;
    border: 1px solid var(--toss-border-light);
    border-radius: 16px;
    padding: 22px 24px;
    margin: 10px 0;
    transition: all 0.2s ease;
}
.analysis-card:hover {
    box-shadow: 0 4px 16px rgba(0,0,0,0.05);
    transform: translateY(-1px);
}
.analysis-card h4 {
    color: var(--toss-text);
    font-size: 0.95rem;
    font-weight: 700;
    margin: 0 0 10px 0;
    letter-spacing: -0.3px;
}
.analysis-card p {
    color: var(--toss-text2);
    line-height: 1.7;
    font-size: 0.84rem;
    margin: 4px 0;
}

/* ─── 영향 배지 ─── */
.impact-positive {
    display: inline-flex; align-items: center; gap: 4px;
    background: var(--toss-green-light); color: var(--toss-green);
    padding: 5px 14px; border-radius: 20px;
    font-size: 0.76rem; font-weight: 700;
    border: none;
}
.impact-negative {
    display: inline-flex; align-items: center; gap: 4px;
    background: var(--toss-red-light); color: var(--toss-red);
    padding: 5px 14px; border-radius: 20px;
    font-size: 0.76rem; font-weight: 700;
    border: none;
}
.impact-mixed {
    display: inline-flex; align-items: center; gap: 4px;
    background: #fff8e8; color: #e09200;
    padding: 5px 14px; border-radius: 20px;
    font-size: 0.76rem; font-weight: 700;
    border: none;
}

/* ─── 섹션 헤더 ─── */
.section-header {
    color: var(--toss-text);
    font-size: 1.1rem;
    font-weight: 700;
    padding: 8px 0;
    margin: 24px 0 14px 0;
    border-bottom: none;
    letter-spacing: -0.3px;
}
.section-header::before {
    content: '';
    width: 4px; height: 18px;
    background: var(--toss-blue);
    border-radius: 2px;
    display: inline-block;
    margin-right: 10px;
    vertical-align: middle;
}

/* ─── 버튼 ─── */
.stButton > button {
    border: 1px solid var(--toss-border) !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    transition: all 0.15s !important;
    background: #ffffff !important;
    color: var(--toss-text2) !important;
    padding: 8px 16px !important;
}
.stButton > button:hover {
    background: var(--toss-bg) !important;
    color: var(--toss-text) !important;
    border-color: var(--toss-text4) !important;
}
.stButton > button:active {
    transform: scale(0.98);
}

/* ─── 검색 인풋 ─── */
.stTextInput input {
    background: #ffffff !important;
    border: 1.5px solid var(--toss-border) !important;
    border-radius: 14px !important;
    color: var(--toss-text) !important;
    font-size: 0.92rem !important;
    padding: 14px 18px !important;
    transition: all 0.15s;
}
.stTextInput input:focus {
    border-color: var(--toss-blue) !important;
    box-shadow: 0 0 0 3px rgba(49,130,246,0.12) !important;
}
.stTextInput input::placeholder { color: var(--toss-text4) !important; }

/* ─── 셀렉트박스 ─── */
.stSelectbox [data-baseweb="select"] > div {
    background: #ffffff !important;
    border-color: var(--toss-border) !important;
    border-radius: 12px !important;
}

/* ─── 데이터프레임 ─── */
.stDataFrame {
    border: 1px solid var(--toss-border-light);
    border-radius: 14px;
    overflow: hidden;
}

/* ─── Expander ─── */
.streamlit-expanderHeader {
    background: #ffffff !important;
    border: 1px solid var(--toss-border-light) !important;
    border-radius: 14px !important;
    color: var(--toss-text2) !important;
    font-weight: 600 !important;
}

/* ─── 구분선 ─── */
hr { border-color: var(--toss-border-light) !important; opacity: 0.6; }

/* ─── 알림 ─── */
.stAlert { border-radius: 14px !important; font-size: 0.85rem; }

/* ─── 스크롤바 ─── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--toss-text4); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--toss-text3); }

/* ─── Streamlit 브랜딩 숨기기 ─── */
#MainMenu { visibility: hidden; }
footer { visibility: hidden !important; display: none !important; }
.viewerBadge_container__r5tak { display: none !important; }
div[data-testid="stDecoration"] { display: none !important; }
div[data-testid="stStatusWidget"] { visibility: hidden; }
header[data-testid="stHeader"] {
    background: rgba(244,245,247,0.85);
    backdrop-filter: blur(12px);
    border-bottom: 1px solid var(--toss-border-light);
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
#  STOCK NAME → TICKER MAPPING (이름 검색용)
# ══════════════════════════════════════════════
STOCK_NAME_MAP = {
    # ─── 한국 KOSPI 주요 종목 ───
    "삼성전자": "005930.KS", "삼성": "005930.KS",
    "SK하이닉스": "000660.KS", "하이닉스": "000660.KS",
    "LG에너지솔루션": "373220.KS", "엘지에너지": "373220.KS",
    "삼성바이오로직스": "207940.KS", "삼성바이오": "207940.KS",
    "현대차": "005380.KS", "현대자동차": "005380.KS",
    "기아": "000270.KS", "기아차": "000270.KS",
    "셀트리온": "068270.KS",
    "카카오": "035720.KS",
    "네이버": "035420.KS", "NAVER": "035420.KS",
    "포스코홀딩스": "005490.KS", "포스코": "005490.KS",
    "LG화학": "051910.KS", "엘지화학": "051910.KS",
    "삼성SDI": "006400.KS",
    "현대모비스": "012330.KS",
    "KB금융": "105560.KS",
    "신한지주": "055550.KS",
    "삼성물산": "028260.KS",
    "한국전력": "015760.KS", "한전": "015760.KS",
    "SK텔레콤": "017670.KS", "SKT": "017670.KS",
    "LG전자": "066570.KS", "엘지전자": "066570.KS",
    "카카오뱅크": "323410.KS",
    "두산에너빌리티": "034020.KS",
    "크래프톤": "259960.KS",
    "에코프로비엠": "247540.KS",
    "SK이노베이션": "096770.KS",
    "한화에어로스페이스": "012450.KS", "한화에어로": "012450.KS",
    "한화오션": "042660.KS",
    "HD현대중공업": "329180.KS", "현대중공업": "329180.KS",
    "HD한국조선해양": "009540.KS",
    "하나금융지주": "086790.KS", "하나금융": "086790.KS",
    "우리금융지주": "316140.KS", "우리금융": "316140.KS",
    "삼성생명": "032830.KS",
    "삼성화재": "000810.KS",
    "삼성전기": "009150.KS",
    "삼성엔지니어링": "028050.KS",
    "SK": "034730.KS",
    "SK스퀘어": "402340.KS",
    "LG": "003550.KS",
    "현대건설": "000720.KS",
    "SK바이오팜": "326030.KS",
    "KT": "030200.KS",
    "KT&G": "033780.KS",
    "아모레퍼시픽": "090430.KS",
    "한미약품": "128940.KS",
    "대한항공": "003490.KS",
    "현대글로비스": "086280.KS",
    "CJ제일제당": "097950.KS",
    "고려아연": "010130.KS",
    "한온시스템": "018880.KS",
    "미래에셋증권": "006800.KS",
    "한국타이어": "161390.KS",
    "롯데케미칼": "011170.KS",
    "LG이노텍": "011070.KS",
    "금양": "001570.KS",
    "LG디스플레이": "034220.KS",
    "현대제철": "004020.KS",
    "S-Oil": "010950.KS", "에스오일": "010950.KS",
    "OCI홀딩스": "010060.KS",
    # ─── 한국 KOSDAQ 주요 종목 ───
    "에코프로": "086520.KQ",
    "알테오젠": "196170.KQ",
    "HLB": "028300.KQ",
    "리가켐바이오": "141080.KQ",
    "엔켐": "348370.KQ",
    "레인보우로보틱스": "277810.KQ",
    "클래시스": "214150.KQ",
    "휴젤": "145020.KQ",
    "파마리서치": "214450.KQ",
    "셀트리온제약": "068760.KQ",
    "카카오게임즈": "293490.KQ",
    "펄어비스": "263750.KQ",
    "위메이드": "112040.KQ",
    "JYP엔터테인먼트": "035900.KQ", "JYP": "035900.KQ", "JYP엔터": "035900.KQ",
    "SM엔터테인먼트": "041510.KQ", "SM": "041510.KQ", "SM엔터": "041510.KQ",
    "하이브": "352820.KS", "HYBE": "352820.KS",
    "YG엔터테인먼트": "122870.KQ", "YG": "122870.KQ", "YG엔터": "122870.KQ",
    "CJ ENM": "035760.KQ",
    "씨젠": "096530.KQ",
    "에스티팜": "237690.KQ",
    "포스코DX": "022100.KQ",
    "솔브레인": "357780.KQ",
    "HPSP": "403870.KQ",
    "리노공업": "058470.KQ",
    "티씨케이": "064760.KQ",
    "주성엔지니어링": "036930.KQ",
    "이오테크닉스": "039030.KQ",
    "원익IPS": "240810.KQ",
    "피에스케이": "319660.KQ",
    "파크시스템스": "140860.KQ",
    "메디톡스": "086900.KQ",
    "CJ프레시웨이": "051500.KQ",
    "컴투스": "078340.KQ",
    "네오위즈": "095660.KQ",
    "카페24": "042000.KQ",
    "더블유게임즈": "192080.KQ",
    "덕산네오룩스": "213420.KQ",
    "심텍": "222800.KQ",
    "비에이치": "090460.KQ",
    "나노신소재": "121600.KQ",
    "대주전자재료": "078600.KQ",
    "SKC": "011790.KS",
    "두산로보틱스": "454910.KS",
    # ─── 미국 주요 종목 (한글 이름) ───
    "애플": "AAPL", "마이크로소프트": "MSFT", "엔비디아": "NVDA",
    "구글": "GOOGL", "알파벳": "GOOGL", "아마존": "AMZN",
    "테슬라": "TSLA", "메타": "META", "페이스북": "META",
    "넷플릭스": "NFLX", "디즈니": "DIS",
    "코카콜라": "KO", "존슨앤존슨": "JNJ",
    "비자": "V", "마스터카드": "MA",
    "JP모건": "JPM", "골드만삭스": "GS",
    "워렌버핏": "BRK-B", "버크셔": "BRK-B",
    "보잉": "BA", "인텔": "INTC", "AMD": "AMD",
    "팔란티어": "PLTR", "스노우플레이크": "SNOW",
    "유니티": "U", "로블록스": "RBLX",
    "브로드컴": "AVGO", "ASML": "ASML",
    "마이크론": "MU", "퀄컴": "QCOM",
    "어도비": "ADBE", "세일즈포스": "CRM",
    "오라클": "ORCL", "시스코": "CSCO",
    "IBM": "IBM", "우버": "UBER",
    "에어비앤비": "ABNB", "스포티파이": "SPOT",
    "쇼피파이": "SHOP", "줌": "ZM",
    "코인베이스": "COIN", "로빈후드": "HOOD",
    # ─── 미국 주요 종목 (영문 이름) ───
    "APPLE": "AAPL", "MICROSOFT": "MSFT", "NVIDIA": "NVDA",
    "GOOGLE": "GOOGL", "ALPHABET": "GOOGL", "AMAZON": "AMZN",
    "TESLA": "TSLA", "NETFLIX": "NFLX", "DISNEY": "DIS",
    "COCA-COLA": "KO", "COCA COLA": "KO",
    "JPMORGAN": "JPM", "GOLDMAN SACHS": "GS", "GOLDMAN": "GS",
    "BERKSHIRE": "BRK-B", "BOEING": "BA", "INTEL": "INTC",
    "PALANTIR": "PLTR", "SNOWFLAKE": "SNOW",
    "UNITY": "U", "ROBLOX": "RBLX", "META": "META",
    "BROADCOM": "AVGO", "MICRON": "MU", "QUALCOMM": "QCOM",
    "ADOBE": "ADBE", "SALESFORCE": "CRM", "ORACLE": "ORCL",
    "UBER": "UBER", "AIRBNB": "ABNB", "COINBASE": "COIN",
    # ─── 암호화폐 ───
    "비트코인": "BTC-USD", "BITCOIN": "BTC-USD",
    "이더리움": "ETH-USD", "ETHEREUM": "ETH-USD",
    "리플": "XRP-USD", "솔라나": "SOL-USD",
    "도지코인": "DOGE-USD", "DOGECOIN": "DOGE-USD",
    "폴카닷": "DOT-USD", "에이다": "ADA-USD",
    "아발란체": "AVAX-USD", "체인링크": "LINK-USD",
    # ─── ETF / 원자재 ───
    "S&P500": "SPY", "나스닥100": "QQQ", "다우존스": "DIA",
    "금": "GC=F", "GOLD": "GC=F", "원유": "CL=F", "OIL": "CL=F",
    "은": "SI=F", "SILVER": "SI=F", "천연가스": "NG=F",
    "TIGER나스닥100": "133690.KS", "KODEX200": "069500.KS",
    "KODEX레버리지": "122630.KS", "KODEX인버스": "114800.KS",
}


@st.cache_data(ttl=3600)
def _fetch_krx_stock_list():
    """KRX에서 전체 종목 리스트를 가져와서 이름→코드 매핑 생성"""
    try:
        # KRX 전종목 시세 페이지에서 JSON 받기
        headers = {"User-Agent": "Mozilla/5.0"}
        result = {}
        for mkt_id, suffix in [("STK", ".KS"), ("KSQ", ".KQ")]:
            url = "http://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd"
            payload = {
                "bld": "dbms/MDC/STAT/standard/MDCSTAT01901",
                "locale": "ko_KR",
                "mktId": mkt_id,
                "share": "1",
                "csvxls_is498": "false",
            }
            resp = requests.post(url, data=payload, headers=headers, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                for item in data.get("OutBlock_1", []):
                    name = item.get("ISU_ABBRV", "")
                    code = item.get("ISU_SRT_CD", "")
                    if name and code:
                        result[name] = f"{code}{suffix}"
        return result
    except Exception:
        return {}


def resolve_ticker(user_input):
    """사용자 입력을 티커로 변환. 이름/한글/영문 모두 지원."""
    text = user_input.strip()
    if not text:
        return ""

    upper = text.upper()

    # 1) 이미 티커 형식 (.KS, .KQ, -, =F 포함)이면 그대로
    if any(c in upper for c in [".", "-", "=", "/"]):
        return upper

    # 2) 이름 매핑에서 찾기 (정확 일치)
    if text in STOCK_NAME_MAP:
        return STOCK_NAME_MAP[text]
    if upper in STOCK_NAME_MAP:
        return STOCK_NAME_MAP[upper]

    # 3) 부분 일치 검색 (매핑)
    for name, ticker in STOCK_NAME_MAP.items():
        if text in name or name in text:
            return ticker

    # 4) 한글 입력이면 KRX에서 검색
    import re
    if re.search(r"[가-힣]", text):
        krx_map = _fetch_krx_stock_list()
        # 정확 일치
        if text in krx_map:
            return krx_map[text]
        # 부분 일치
        for name, ticker in krx_map.items():
            if text in name:
                return ticker

    # 5) yfinance Search API 시도
    try:
        s = yf.Search(upper, max_results=1)
        if s.quotes:
            return s.quotes[0].get("symbol", upper)
    except Exception:
        pass

    # 6) 순수 숫자면 한국 종목으로 간주
    if text.isdigit() and len(text) == 6:
        return f"{text}.KS"

    # 7) 못 찾으면 원본을 티커로 간주
    return upper


# ══════════════════════════════════════════════
#  INDICATOR IMPACT KNOWLEDGE BASE
# ══════════════════════════════════════════════
INDICATOR_IMPACT = {
    "FEDFUNDS": {
        "name": "미국 기준금리 (Fed Funds Rate)",
        "description": "미국 연방준비제도(Fed)가 설정하는 기준금리. 모든 금융자산의 할인율 기준.",
        "up_impact": [
            {"sector": "은행/금융", "direction": "positive", "tickers": ["JPM", "BAC", "WFC", "GS"],
             "reason": "순이자마진(NIM) 확대로 은행 수익성 개선. 예대금리차 확대."},
            {"sector": "기술/성장주", "direction": "negative", "tickers": ["AAPL", "MSFT", "GOOGL", "NVDA", "META"],
             "reason": "미래 현금흐름 할인율 상승 → 성장주 밸류에이션 하락. DCF 가치 감소."},
            {"sector": "부동산/리츠", "direction": "negative", "tickers": ["VNQ", "O", "AMT", "SPG"],
             "reason": "모기지 금리 상승 → 부동산 수요 감소, 리츠 배당매력 하락."},
            {"sector": "유틸리티", "direction": "negative", "tickers": ["NEE", "DUK", "SO"],
             "reason": "채권 대비 배당매력 하락, 높은 부채비율로 이자부담 증가."},
            {"sector": "달러/원화", "direction": "negative", "tickers": ["DEXKOUS"],
             "reason": "달러 강세 → 원화 약세. 한미 금리차 확대 시 자본유출 압력."},
            {"sector": "신흥국", "direction": "negative", "tickers": ["EEM", "VWO"],
             "reason": "달러 강세 + 자본유출로 신흥국 통화약세, 외채부담 증가."},
        ],
        "down_impact": [
            {"sector": "기술/성장주", "direction": "positive", "tickers": ["AAPL", "MSFT", "GOOGL", "NVDA"],
             "reason": "할인율 하락으로 성장주 밸류에이션 상승. 유동성 확대 효과."},
            {"sector": "부동산/리츠", "direction": "positive", "tickers": ["VNQ", "O", "AMT"],
             "reason": "모기지 금리 하락 → 부동산 수요 증가, 리츠 배당매력 개선."},
            {"sector": "소비재", "direction": "positive", "tickers": ["AMZN", "TSLA", "NKE"],
             "reason": "가계 이자부담 감소 → 소비여력 증가. 자동차/내구재 수요 회복."},
        ],
        "related_fred": ["DGS10", "DGS2", "MORTGAGE30US", "BAMLH0A0HYM2"],
        "related_kr": ["삼성전자(005930)", "SK하이닉스(000660)", "KB금융(105560)"]
    },
    "DGS10": {
        "name": "미국 10년물 국채금리",
        "description": "장기 시장금리의 벤치마크. 인플레이션 기대와 경제성장 전망을 반영.",
        "up_impact": [
            {"sector": "은행/금융", "direction": "positive", "tickers": ["JPM", "BAC", "GS"],
             "reason": "장기 대출금리 상승 → 순이자마진 확대."},
            {"sector": "기술/성장주", "direction": "negative", "tickers": ["AAPL", "MSFT", "NVDA", "TSLA"],
             "reason": "10년물은 DCF 할인율의 핵심. 상승 시 성장주 타격 크다."},
            {"sector": "채권", "direction": "negative", "tickers": ["TLT", "BND", "AGG"],
             "reason": "금리 상승 = 채권가격 하락. 듀레이션이 긴 채권일수록 타격."},
            {"sector": "금", "direction": "negative", "tickers": ["GLD", "GC=F"],
             "reason": "실질금리 상승 시 이자가 없는 금의 매력도 하락."},
        ],
        "down_impact": [
            {"sector": "기술/성장주", "direction": "positive", "tickers": ["AAPL", "MSFT", "NVDA"],
             "reason": "할인율 하락 → 미래 성장가치 재평가 상승."},
            {"sector": "채권/TLT", "direction": "positive", "tickers": ["TLT", "BND"],
             "reason": "금리 하락 = 채권가격 상승. 안전자산 선호 시 추가 상승."},
        ],
        "related_fred": ["FEDFUNDS", "DGS2", "T10Y2Y", "DFII10"],
        "related_kr": []
    },
    "CPIAUCSL": {
        "name": "미국 소비자물가지수 (CPI)",
        "description": "미국의 인플레이션을 측정하는 핵심 지표. Fed 통화정책의 핵심 변수.",
        "up_impact": [
            {"sector": "원자재/에너지", "direction": "positive", "tickers": ["XOM", "CVX", "COP", "XLE"],
             "reason": "인플레 환경에서 원자재 가격 상승. 에너지 기업 수익 증가."},
            {"sector": "금/귀금속", "direction": "positive", "tickers": ["GLD", "GDX", "NEM", "GOLD"],
             "reason": "인플레 헷지 수단으로 금 수요 증가. 실질가치 보존 효과."},
            {"sector": "기술/성장주", "direction": "negative", "tickers": ["AAPL", "MSFT", "GOOGL"],
             "reason": "CPI 상승 → Fed 긴축 기대 → 금리 상승 → 성장주 압박."},
            {"sector": "소비재", "direction": "negative", "tickers": ["WMT", "TGT", "COST"],
             "reason": "물가 상승 → 실질 구매력 감소 → 소비 위축."},
        ],
        "down_impact": [
            {"sector": "기술/성장주", "direction": "positive", "tickers": ["AAPL", "MSFT", "NVDA"],
             "reason": "인플레 둔화 → Fed 완화 기대 → 금리 하락 → 성장주 수혜."},
            {"sector": "소비재", "direction": "positive", "tickers": ["WMT", "AMZN", "NKE"],
             "reason": "물가 안정 → 실질 구매력 회복 → 소비 증가."},
        ],
        "related_fred": ["FEDFUNDS", "PCEPI", "CPILFESL", "UNRATE"],
        "related_kr": ["삼성전자(005930)", "현대차(005380)"]
    },
    "UNRATE": {
        "name": "미국 실업률",
        "description": "미국 노동시장 건전성 지표. Fed의 이중책무(물가안정+완전고용) 중 하나.",
        "up_impact": [
            {"sector": "경기방어주", "direction": "positive", "tickers": ["PG", "KO", "JNJ", "PEP"],
             "reason": "경기침체 우려 → 필수소비재/헬스케어 등 방어주 선호."},
            {"sector": "채권", "direction": "positive", "tickers": ["TLT", "BND"],
             "reason": "실업률 상승 → Fed 완화 기대 → 금리 하락 → 채권 강세."},
            {"sector": "경기민감주", "direction": "negative", "tickers": ["CAT", "DE", "F", "GM"],
             "reason": "소비/투자 위축 → 경기민감 섹터 실적 악화."},
            {"sector": "소매/여행", "direction": "negative", "tickers": ["AMZN", "MAR", "DAL", "UAL"],
             "reason": "가처분소득 감소 → 재량소비 위축."},
        ],
        "down_impact": [
            {"sector": "경기민감주", "direction": "positive", "tickers": ["CAT", "DE", "F"],
             "reason": "완전고용 → 소비/투자 확대 → 경기민감 섹터 수혜."},
            {"sector": "소매/여행", "direction": "positive", "tickers": ["AMZN", "MAR", "DAL"],
             "reason": "고용 개선 → 소비여력 증가 → 재량소비 확대."},
        ],
        "related_fred": ["FEDFUNDS", "PAYEMS", "ICSA", "CPIAUCSL"],
        "related_kr": []
    },
    "DCOILWTICO": {
        "name": "WTI 원유 가격",
        "description": "국제 원유 기준가격. 인플레이션, 운송비, 산업 전반에 영향.",
        "up_impact": [
            {"sector": "에너지", "direction": "positive", "tickers": ["XOM", "CVX", "COP", "OXY", "XLE"],
             "reason": "유가 상승 → 에너지 기업 매출/이익 직접 증가."},
            {"sector": "항공/운송", "direction": "negative", "tickers": ["DAL", "UAL", "LUV", "FDX", "UPS"],
             "reason": "연료비 급증 → 운송업 마진 압박. 항공유 = 최대 비용항목."},
            {"sector": "화학/플라스틱", "direction": "negative", "tickers": ["DOW", "LYB", "DD"],
             "reason": "원자재(나프타) 가격 상승 → 화학업 원가 부담."},
            {"sector": "소비자", "direction": "negative", "tickers": ["WMT", "TGT"],
             "reason": "휘발유 가격 상승 → 가처분소득 감소 → 소비 위축."},
        ],
        "down_impact": [
            {"sector": "항공/운송", "direction": "positive", "tickers": ["DAL", "UAL", "FDX"],
             "reason": "연료비 절감 → 마진 개선."},
            {"sector": "소비자", "direction": "positive", "tickers": ["WMT", "AMZN"],
             "reason": "에너지 비용 감소 → 소비여력 증가."},
            {"sector": "에너지", "direction": "negative", "tickers": ["XOM", "CVX", "COP"],
             "reason": "유가 하락 → 에너지 기업 매출 감소, 설비투자 축소."},
        ],
        "related_fred": ["CPIAUCSL", "DCOILBRENTEU", "GASREGW"],
        "related_kr": ["SK이노베이션(096770)", "S-Oil(010950)", "대한항공(003490)"]
    },
    "VIXCLS": {
        "name": "VIX 변동성 지수 (공포지수)",
        "description": "S&P500 옵션의 내재변동성. 시장의 공포/불확실성 수준을 측정.",
        "up_impact": [
            {"sector": "안전자산", "direction": "positive", "tickers": ["GLD", "TLT", "BND"],
             "reason": "공포 확대 → 안전자산 선호(Flight to Quality). 금, 국채 강세."},
            {"sector": "변동성 ETF", "direction": "positive", "tickers": ["UVXY", "VXX"],
             "reason": "VIX 직접 추종 상품 가격 상승."},
            {"sector": "주식 전반", "direction": "negative", "tickers": ["SPY", "QQQ", "IWM"],
             "reason": "불확실성 증가 → 위험자산 매도. 시장 전반 하락 압력."},
        ],
        "down_impact": [
            {"sector": "주식 전반", "direction": "positive", "tickers": ["SPY", "QQQ", "IWM"],
             "reason": "불확실성 감소 → 위험선호 확대. 주식시장 상승 우호적."},
            {"sector": "성장주", "direction": "positive", "tickers": ["ARKK", "NVDA", "TSLA"],
             "reason": "변동성 축소 → 고베타 성장주에 유동성 유입."},
        ],
        "related_fred": ["SP500", "BAMLH0A0HYM2", "DTWEXBGS"],
        "related_kr": ["KOSPI", "삼성전자(005930)"]
    },
    "BAMLH0A0HYM2": {
        "name": "하이일드 스프레드 (ICE BofA)",
        "description": "하이일드 채권과 국채의 금리차. 신용위험과 경기침체 확률의 바로미터.",
        "up_impact": [
            {"sector": "안전자산", "direction": "positive", "tickers": ["TLT", "GLD", "BND"],
             "reason": "신용위험 확대 → 안전자산 선호. 국채/금 강세."},
            {"sector": "금융/은행", "direction": "negative", "tickers": ["JPM", "BAC", "C"],
             "reason": "대출 부실 우려 증가 → 은행 자산건전성 악화 우려."},
            {"sector": "경기민감주", "direction": "negative", "tickers": ["CAT", "F", "GM"],
             "reason": "신용경색 → 기업 자금조달 비용 증가 → 투자 위축."},
        ],
        "down_impact": [
            {"sector": "경기민감주", "direction": "positive", "tickers": ["CAT", "F", "XLI"],
             "reason": "신용환경 개선 → 기업 자금조달 용이 → 경기확장 신호."},
            {"sector": "하이일드 채권", "direction": "positive", "tickers": ["HYG", "JNK"],
             "reason": "스프레드 축소 = 하이일드 채권 가격 상승."},
        ],
        "related_fred": ["FEDFUNDS", "VIXCLS", "UNRATE"],
        "related_kr": []
    },
    "DEXKOUS": {
        "name": "원/달러 환율",
        "description": "원화 대비 달러 가치. 한국 수출기업과 외국인 투자에 직접 영향.",
        "up_impact": [
            {"sector": "수출기업", "direction": "positive",
             "tickers": ["005930.KS", "000660.KS", "005380.KS"],
             "reason": "원화 약세 → 수출품 가격경쟁력 상승, 해외매출 환산이익 증가."},
            {"sector": "수입/내수", "direction": "negative",
             "tickers": ["003490.KS", "030200.KS"],
             "reason": "원화 약세 → 수입 원자재 비용 증가, 항공사 연료비 부담."},
            {"sector": "외국인 투자", "direction": "negative",
             "tickers": ["EWY"],
             "reason": "환율 상승 → 외국인 환차손 우려 → 한국증시 매도 압력."},
        ],
        "down_impact": [
            {"sector": "수입/내수", "direction": "positive",
             "tickers": ["003490.KS", "030200.KS"],
             "reason": "원화 강세 → 수입비용 감소, 해외여행 수요 증가."},
            {"sector": "외국인 투자", "direction": "positive",
             "tickers": ["EWY"],
             "reason": "환율 하락 → 외국인 환차익 → 한국증시 매수 유인."},
        ],
        "related_fred": ["FEDFUNDS", "DTWEXBGS", "DGS10"],
        "related_kr": ["삼성전자(005930)", "SK하이닉스(000660)", "현대차(005380)"]
    },
}

# ══════════════════════════════════════════════
#  FINANCIAL RATIO DEFINITIONS
# ══════════════════════════════════════════════
RATIO_DEFINITIONS = {
    "유동비율 (Current Ratio)": {
        "formula": "유동자산 / 유동부채",
        "description": "단기 채무 상환 능력을 측정. 1년 내 만기 도래하는 부채를 갚을 수 있는 능력.",
        "good": "2.0 이상이면 양호. 업종 평균과 비교 필요.",
        "warning": "1.0 미만이면 단기 유동성 위험.",
        "threshold_good": 2.0, "threshold_warn": 1.0
    },
    "당좌비율 (Quick Ratio)": {
        "formula": "(유동자산 - 재고자산) / 유동부채",
        "description": "재고자산을 제외한 순수 유동자산으로 단기 부채를 갚을 수 있는 능력. 유동비율보다 엄격한 지표.",
        "good": "1.0 이상이면 양호.",
        "warning": "0.5 미만이면 위험 신호.",
        "threshold_good": 1.0, "threshold_warn": 0.5
    },
    "부채비율 (Debt-to-Equity)": {
        "formula": "총부채 / 자기자본",
        "description": "기업의 재무 레버리지 수준. 자기자본 대비 얼마나 많은 부채를 사용하는지 측정.",
        "good": "1.0 이하(100% 이하)면 안정적. 업종별 차이 큼.",
        "warning": "2.0 이상이면 과도한 레버리지 주의.",
        "threshold_good": 1.0, "threshold_warn": 2.0, "lower_is_better": True
    },
    "ROE (자기자본이익률)": {
        "formula": "당기순이익 / 자기자본 × 100",
        "description": "주주가 투자한 자본 대비 얼마나 효율적으로 이익을 창출하는지. 워런 버핏이 가장 중시하는 지표.",
        "good": "15% 이상이면 우수. 업종별 차이 있음.",
        "warning": "5% 미만이면 자본 효율성 낮음.",
        "threshold_good": 15.0, "threshold_warn": 5.0
    },
    "ROA (총자산이익률)": {
        "formula": "당기순이익 / 총자산 × 100",
        "description": "기업이 보유한 총자산을 얼마나 효율적으로 활용해 이익을 내는지 측정.",
        "good": "5% 이상이면 양호.",
        "warning": "2% 미만이면 자산 활용 효율 낮음.",
        "threshold_good": 5.0, "threshold_warn": 2.0
    },
    "영업이익률 (Operating Margin)": {
        "formula": "영업이익 / 매출액 × 100",
        "description": "매출에서 영업활동을 통해 얼마나 이익을 남기는지. 기업의 본업 수익성 지표.",
        "good": "15% 이상이면 우수 (업종별 상이).",
        "warning": "5% 미만이면 수익성 약함.",
        "threshold_good": 15.0, "threshold_warn": 5.0
    },
    "순이익률 (Net Margin)": {
        "formula": "당기순이익 / 매출액 × 100",
        "description": "최종적으로 매출의 몇 %가 순이익으로 남는지. 세금/이자 포함 전체 수익성.",
        "good": "10% 이상이면 양호.",
        "warning": "음수이면 적자.",
        "threshold_good": 10.0, "threshold_warn": 0.0
    },
    "PER (주가수익비율)": {
        "formula": "주가 / 주당순이익(EPS)",
        "description": "현재 주가가 1주당 순이익의 몇 배인지. 이익 대비 주가가 저평가/고평가인지 판단.",
        "good": "15배 이하면 저평가 가능성 (성장주는 높을 수 있음).",
        "warning": "50배 이상이면 고평가 주의.",
        "threshold_good": 15.0, "threshold_warn": 50.0, "lower_is_better": True
    },
    "PBR (주가순자산비율)": {
        "formula": "주가 / 주당순자산(BPS)",
        "description": "주가가 1주당 순자산의 몇 배인지. 1 미만이면 청산가치보다 싸게 거래.",
        "good": "1.0 이하면 자산가치 대비 저평가.",
        "warning": "5.0 이상이면 자산 대비 고평가.",
        "threshold_good": 1.0, "threshold_warn": 5.0, "lower_is_better": True
    },
    "EV/EBITDA": {
        "formula": "기업가치(EV) / EBITDA",
        "description": "기업 인수 시 투자금 회수 기간. 기업가치를 영업현금흐름으로 나눈 값.",
        "good": "10배 이하면 합리적.",
        "warning": "20배 이상이면 비싼 편.",
        "threshold_good": 10.0, "threshold_warn": 20.0, "lower_is_better": True
    },
    "배당수익률 (Dividend Yield)": {
        "formula": "주당배당금 / 주가 × 100",
        "description": "투자금액 대비 받을 수 있는 배당금 비율. 인컴 투자자의 핵심 지표.",
        "good": "3% 이상이면 높은 배당.",
        "warning": "배당 없으면 0%. 너무 높으면(8%+) 지속가능성 확인 필요.",
        "threshold_good": 3.0, "threshold_warn": 0.5
    },
}

# ══════════════════════════════════════════════
#  DATA FETCHING FUNCTIONS
# ══════════════════════════════════════════════

@st.cache_data(ttl=3600)
def fetch_fred(series_id, start_date, end_date):
    """FRED API에서 경제 지표 데이터 가져오기"""
    url = "https://api.stlouisfed.org/fred/series/observations"
    params = {
        "series_id": series_id, "api_key": FRED_KEY, "file_type": "json",
        "observation_start": start_date, "observation_end": end_date
    }
    try:
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code == 200:
            obs = resp.json().get("observations", [])
            if obs:
                df = pd.DataFrame(obs)
                df["date"] = pd.to_datetime(df["date"])
                df["value"] = pd.to_numeric(df["value"], errors="coerce")
                df = df.dropna(subset=["value"])
                return df[["date", "value"]]
    except Exception:
        pass
    return pd.DataFrame()


@st.cache_data(ttl=3600)
def fetch_ecos(stat_code, item_code, start_date, end_date):
    """ECOS API에서 한국 경제 지표 데이터 가져오기"""
    start = start_date.replace("-", "")[:6]
    end = end_date.replace("-", "")[:6]
    url = f"https://ecos.bok.or.kr/api/StatisticSearch/{ECOS_KEY}/json/kr/1/1000/{stat_code}/M/{start}/{end}/{item_code}"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if "StatisticSearch" in data:
                rows = data["StatisticSearch"].get("row", [])
                if rows:
                    df = pd.DataFrame(rows)
                    df["date"] = pd.to_datetime(df["TIME"], format="%Y%m")
                    df["value"] = pd.to_numeric(df["DATA_VALUE"], errors="coerce")
                    return df[["date", "value"]].dropna()
    except Exception:
        pass
    return pd.DataFrame()


@st.cache_data(ttl=120)
def fetch_coingecko_price(coin_id):
    """CoinGecko에서 실시간 암호화폐 가격"""
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd&include_24hr_change=true&include_market_cap=true&include_24hr_vol=true"
        resp = requests.get(url, timeout=8)
        if resp.status_code == 200:
            return resp.json().get(coin_id, {})
    except Exception:
        pass
    return {}


@st.cache_data(ttl=300)
def fetch_coingecko_chart(coin_id, days=30):
    """CoinGecko에서 암호화폐 차트 데이터"""
    try:
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=usd&days={days}"
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            prices = resp.json().get("prices", [])
            if prices:
                df = pd.DataFrame(prices, columns=["timestamp", "price"])
                df["date"] = pd.to_datetime(df["timestamp"], unit="ms")
                return df[["date", "price"]]
    except Exception:
        pass
    return pd.DataFrame()


@st.cache_data(ttl=600)
def fetch_stock_info(ticker):
    """yfinance로 종목 기본 정보 가져오기"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return info
    except Exception:
        return {}


@st.cache_data(ttl=600)
def fetch_stock_financials(ticker):
    """yfinance로 재무제표 가져오기"""
    try:
        stock = yf.Ticker(ticker)
        result = {}

        # 재무제표
        bs = stock.balance_sheet
        if bs is not None and not bs.empty:
            result["balance_sheet"] = bs

        inc = stock.income_stmt
        if inc is not None and not inc.empty:
            result["income_stmt"] = inc

        cf = stock.cashflow
        if cf is not None and not cf.empty:
            result["cashflow"] = cf

        # 분기 재무제표
        qbs = stock.quarterly_balance_sheet
        if qbs is not None and not qbs.empty:
            result["q_balance_sheet"] = qbs

        qinc = stock.quarterly_income_stmt
        if qinc is not None and not qinc.empty:
            result["q_income_stmt"] = qinc

        return result
    except Exception:
        return {}


@st.cache_data(ttl=300)
def fetch_stock_history(ticker, period="1y"):
    """yfinance로 주가 히스토리"""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period)
        if isinstance(hist.columns, pd.MultiIndex):
            hist = hist.droplevel(1, axis=1)
        return hist
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=3600)
def search_ticker(query):
    """종목 검색 (yfinance)"""
    try:
        results = []
        # 직접 티커 시도
        stock = yf.Ticker(query)
        info = stock.info
        if info and info.get("shortName"):
            results.append({
                "symbol": info.get("symbol", query),
                "name": info.get("shortName", ""),
                "type": info.get("quoteType", "EQUITY"),
                "exchange": info.get("exchange", ""),
            })
        return results
    except Exception:
        return []


@st.cache_data(ttl=3600)
def load_macro_data(start_date, end_date):
    """거시경제 데이터 일괄 로드"""
    data = {}
    fred_items = {
        "미국금리": "FEDFUNDS", "미국10Y": "DGS10", "미국2Y": "DGS2",
        "원달러": "DEXKOUS", "VIX": "VIXCLS", "S&P500": "SP500",
        "나스닥": "NASDAQCOM", "유가(WTI)": "DCOILWTICO",
        "달러인덱스": "DTWEXBGS", "하이일드스프레드": "BAMLH0A0HYM2",
        "미국CPI": "CPIAUCSL", "미국실업률": "UNRATE",
        "연준자산": "WALCL", "구리": "PCOPPUSDM",
    }
    for name, code in fred_items.items():
        df = fetch_fred(code, start_date, end_date)
        if not df.empty:
            data[name] = df.set_index("date")["value"]

    # ECOS 한국 금리
    df = fetch_ecos("722Y001", "0101000", start_date, end_date)
    if not df.empty:
        data["한국금리"] = df.set_index("date")["value"]

    # KOSPI via ECOS
    start_ym = start_date.replace("-", "")[:6]
    end_ym = end_date.replace("-", "")[:6]
    try:
        url = f"https://ecos.bok.or.kr/api/StatisticSearch/{ECOS_KEY}/json/kr/1/1000/901Y014/M/{start_ym}/{end_ym}/0001000"
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            d = resp.json()
            if "StatisticSearch" in d:
                rows = d["StatisticSearch"].get("row", [])
                if rows:
                    kdf = pd.DataFrame(rows)
                    kdf["date"] = pd.to_datetime(kdf["TIME"], format="%Y%m")
                    kdf["value"] = pd.to_numeric(kdf["DATA_VALUE"], errors="coerce")
                    data["KOSPI"] = kdf.set_index("date")["value"].dropna()
    except Exception:
        pass

    if data:
        result = pd.DataFrame(data).sort_index()
        if "한국금리" in result.columns and "미국금리" in result.columns:
            result["금리차"] = result["한국금리"] - result["미국금리"]
        if "미국10Y" in result.columns and "미국2Y" in result.columns:
            result["장단기스프레드"] = result["미국10Y"] - result["미국2Y"]
        return result
    return pd.DataFrame()


# ══════════════════════════════════════════════
#  FINANCIAL ANALYSIS FUNCTIONS
# ══════════════════════════════════════════════

def safe_get(df, row_names, col_idx=0):
    """재무제표에서 안전하게 값 추출"""
    if df is None or df.empty:
        return None
    for name in row_names if isinstance(row_names, list) else [row_names]:
        if name in df.index:
            try:
                val = df.iloc[df.index.get_loc(name), col_idx]
                if pd.notna(val):
                    return float(val)
            except Exception:
                pass
    return None


def calculate_ratios(financials):
    """재무제표에서 주요 비율 계산"""
    ratios = {}
    bs = financials.get("balance_sheet")
    inc = financials.get("income_stmt")

    if bs is None or inc is None:
        return ratios

    # 대차대조표 항목
    current_assets = safe_get(bs, ["Current Assets", "Total Current Assets"])
    current_liabilities = safe_get(bs, ["Current Liabilities", "Total Current Liabilities"])
    inventory = safe_get(bs, ["Inventory", "Inventories"])
    total_debt = safe_get(bs, ["Total Debt", "Long Term Debt And Capital Lease Obligation"])
    total_equity = safe_get(bs, ["Stockholders Equity", "Total Stockholders Equity", "Common Stock Equity", "Total Equity Gross Minority Interest"])
    total_assets = safe_get(bs, ["Total Assets"])

    # 손익계산서 항목
    revenue = safe_get(inc, ["Total Revenue", "Revenue"])
    operating_income = safe_get(inc, ["Operating Income", "EBIT"])
    net_income = safe_get(inc, ["Net Income", "Net Income Common Stockholders"])
    ebitda = safe_get(inc, ["EBITDA", "Normalized EBITDA"])
    gross_profit = safe_get(inc, ["Gross Profit"])

    # 비율 계산
    if current_assets and current_liabilities and current_liabilities != 0:
        ratios["유동비율 (Current Ratio)"] = current_assets / current_liabilities

    if current_assets and current_liabilities and current_liabilities != 0:
        inv = inventory or 0
        ratios["당좌비율 (Quick Ratio)"] = (current_assets - inv) / current_liabilities

    if total_debt is not None and total_equity and total_equity != 0:
        ratios["부채비율 (Debt-to-Equity)"] = (total_debt or 0) / total_equity

    if net_income is not None and total_equity and total_equity != 0:
        ratios["ROE (자기자본이익률)"] = (net_income / total_equity) * 100

    if net_income is not None and total_assets and total_assets != 0:
        ratios["ROA (총자산이익률)"] = (net_income / total_assets) * 100

    if operating_income is not None and revenue and revenue != 0:
        ratios["영업이익률 (Operating Margin)"] = (operating_income / revenue) * 100

    if net_income is not None and revenue and revenue != 0:
        ratios["순이익률 (Net Margin)"] = (net_income / revenue) * 100

    if gross_profit is not None and revenue and revenue != 0:
        ratios["매출총이익률 (Gross Margin)"] = (gross_profit / revenue) * 100

    return ratios


def calculate_historical_ratios(financials):
    """연도별 비율 추이 계산"""
    bs = financials.get("balance_sheet")
    inc = financials.get("income_stmt")
    if bs is None or inc is None:
        return pd.DataFrame()

    years = []
    for col_idx in range(min(bs.shape[1], inc.shape[1])):
        year_data = {}
        try:
            year_data["연도"] = str(bs.columns[col_idx])[:10]
        except Exception:
            year_data["연도"] = f"Y-{col_idx}"

        ca = safe_get(bs, ["Current Assets", "Total Current Assets"], col_idx)
        cl = safe_get(bs, ["Current Liabilities", "Total Current Liabilities"], col_idx)
        inv = safe_get(bs, ["Inventory", "Inventories"], col_idx)
        eq = safe_get(bs, ["Stockholders Equity", "Total Stockholders Equity", "Common Stock Equity", "Total Equity Gross Minority Interest"], col_idx)
        ta = safe_get(bs, ["Total Assets"], col_idx)
        td = safe_get(bs, ["Total Debt", "Long Term Debt And Capital Lease Obligation"], col_idx)
        rev = safe_get(inc, ["Total Revenue", "Revenue"], col_idx)
        oi = safe_get(inc, ["Operating Income", "EBIT"], col_idx)
        ni = safe_get(inc, ["Net Income", "Net Income Common Stockholders"], col_idx)
        gp = safe_get(inc, ["Gross Profit"], col_idx)

        if ca and cl and cl != 0:
            year_data["유동비율"] = ca / cl
        if ca and cl and cl != 0:
            year_data["당좌비율"] = (ca - (inv or 0)) / cl
        if td is not None and eq and eq != 0:
            year_data["부채비율"] = (td or 0) / eq
        if ni is not None and eq and eq != 0:
            year_data["ROE(%)"] = (ni / eq) * 100
        if ni is not None and ta and ta != 0:
            year_data["ROA(%)"] = (ni / ta) * 100
        if oi is not None and rev and rev != 0:
            year_data["영업이익률(%)"] = (oi / rev) * 100
        if ni is not None and rev and rev != 0:
            year_data["순이익률(%)"] = (ni / rev) * 100
        if gp is not None and rev and rev != 0:
            year_data["매출총이익률(%)"] = (gp / rev) * 100

        years.append(year_data)

    if years:
        df = pd.DataFrame(years)
        if "연도" in df.columns:
            df = df.set_index("연도")
        return df
    return pd.DataFrame()


# ══════════════════════════════════════════════
#  CHART FUNCTIONS
# ══════════════════════════════════════════════

def _chart_layout(title="", height=400):
    """토스 스타일 공통 Plotly 레이아웃"""
    return dict(
        title=dict(text=title, font=dict(size=14, color="#191f28", family="Pretendard, sans-serif"), x=0.01, y=0.97),
        height=height,
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        font=dict(family="Pretendard, sans-serif", color="#8b95a1", size=11),
        xaxis=dict(gridcolor="#f2f4f6", zeroline=False, linecolor="#e5e8eb",
                   tickfont=dict(size=10, color="#b0b8c1")),
        yaxis=dict(gridcolor="#f2f4f6", zeroline=False, linecolor="#e5e8eb",
                   tickfont=dict(size=10, color="#b0b8c1")),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
                    font=dict(size=11, color="#4e5968"), bgcolor="rgba(255,255,255,0)"),
        hovermode="x unified",
        hoverlabel=dict(bgcolor="#ffffff", bordercolor="#e5e8eb",
                        font=dict(family="Pretendard, sans-serif", size=12, color="#191f28")),
        margin=dict(l=50, r=20, t=44, b=40),
    )


def make_candlestick(hist, title=""):
    """캔들스틱 차트"""
    if hist.empty:
        return go.Figure()

    fig = go.Figure(data=[go.Candlestick(
        x=hist.index,
        open=hist["Open"], high=hist["High"],
        low=hist["Low"], close=hist["Close"],
        increasing_line_color="#f04452", increasing_fillcolor="#f04452",
        decreasing_line_color="#3182f6", decreasing_fillcolor="#3182f6",
    )])

    if len(hist) >= 20:
        ma20 = hist["Close"].rolling(20).mean()
        fig.add_trace(go.Scatter(x=hist.index, y=ma20, name="MA20",
                                  line=dict(color="#ff9f43", width=1.2, dash="dot")))
    if len(hist) >= 60:
        ma60 = hist["Close"].rolling(60).mean()
        fig.add_trace(go.Scatter(x=hist.index, y=ma60, name="MA60",
                                  line=dict(color="#6c5ce7", width=1.2, dash="dot")))

    layout = _chart_layout(title, 480)
    layout["xaxis_rangeslider_visible"] = False
    fig.update_layout(**layout)
    return fig


def make_volume_chart(hist):
    """거래량 차트"""
    if hist.empty or "Volume" not in hist.columns:
        return go.Figure()

    colors = ["rgba(240,68,82,0.6)" if hist["Close"].iloc[i] >= hist["Open"].iloc[i]
              else "rgba(49,130,246,0.6)" for i in range(len(hist))]

    fig = go.Figure(data=[go.Bar(x=hist.index, y=hist["Volume"], marker_color=colors)])
    layout = _chart_layout("Volume", 180)
    layout["margin"] = dict(l=50, r=20, t=30, b=20)
    fig.update_layout(**layout)
    return fig


def _hex_to_rgba(hex_color, alpha=0.1):
    h = hex_color.lstrip('#')
    r, g, b = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
    return f"rgba({r},{g},{b},{alpha})"


def make_line(series, title, color="#3182f6", height=350):
    """라인 차트"""
    fig = go.Figure()
    if not series.empty:
        fig.add_trace(go.Scatter(
            x=series.index, y=series.values,
            line=dict(color=color, width=2),
            fill="tozeroy",
            fillcolor=_hex_to_rgba(color, 0.08)
        ))
    fig.update_layout(**_chart_layout(title, height))
    return fig


def make_dual_axis(s1, s2, name1, name2, title, c1="#ef5350", c2="#42a5f5"):
    """듀얼축 차트"""
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    if not s1.empty:
        fig.add_trace(go.Scatter(x=s1.index, y=s1.values, name=name1,
                                  line=dict(color=c1, width=2)), secondary_y=False)
    if not s2.empty:
        fig.add_trace(go.Scatter(x=s2.index, y=s2.values, name=name2,
                                  line=dict(color=c2, width=2)), secondary_y=True)
    fig.update_layout(**_chart_layout(title, 400))
    return fig


def make_ratio_chart(hist_ratios, columns, title):
    """비율 추이 차트"""
    if hist_ratios.empty:
        return go.Figure()

    fig = go.Figure()
    colors = ["#3182f6", "#f04452", "#ff9f43", "#00b386", "#6c5ce7"]

    available = [c for c in columns if c in hist_ratios.columns]
    for i, col in enumerate(available):
        vals = hist_ratios[col].dropna()
        if not vals.empty:
            fig.add_trace(go.Scatter(
                x=vals.index, y=vals.values, name=col,
                line=dict(color=colors[i % len(colors)], width=2.5),
                mode="lines+markers",
                marker=dict(size=7, symbol="circle",
                            line=dict(width=1.5, color="#ffffff"))
            ))

    fig.update_layout(**_chart_layout(title, 400))
    return fig


def make_heatmap(corr_df):
    """상관관계 히트맵"""
    fig = px.imshow(
        corr_df.round(2), text_auto=".2f",
        color_continuous_scale=[[0, "#f04452"], [0.25, "#ff9f43"], [0.5, "#f4f5f7"],
                                [0.75, "#a0d8ef"], [1, "#3182f6"]],
        aspect="auto", zmin=-1, zmax=1
    )
    fig.update_layout(
        height=550,
        plot_bgcolor="#ffffff", paper_bgcolor="#ffffff",
        font=dict(family="Pretendard, sans-serif", color="#4e5968", size=10),
        margin=dict(l=10, r=10, t=10, b=10),
        coloraxis_colorbar=dict(tickfont=dict(color="#8b95a1"))
    )
    return fig


def make_gauge(value, title, ranges, height=250):
    """게이지 차트"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value if pd.notna(value) else 0,
        title={"text": title, "font": {"color": "#191f28", "size": 13, "family": "Pretendard, sans-serif"}},
        number={"font": {"color": "#191f28", "size": 28, "family": "Pretendard, sans-serif"}},
        gauge={
            "axis": {"range": [ranges[0], ranges[-1]], "tickcolor": "#b0b8c1",
                     "tickfont": {"size": 9, "color": "#8b95a1"}},
            "bar": {"color": "rgba(49,130,246,0.5)", "thickness": 0.25},
            "bgcolor": "#f2f4f6",
            "borderwidth": 0,
            "steps": [
                {"range": [ranges[0], ranges[1]], "color": "rgba(0,179,134,0.12)"},
                {"range": [ranges[1], ranges[2]], "color": "rgba(255,159,67,0.08)"},
                {"range": [ranges[2], ranges[3]], "color": "rgba(255,159,67,0.12)"},
                {"range": [ranges[3], ranges[4]], "color": "rgba(240,68,82,0.12)"},
            ]
        }
    ))
    fig.update_layout(
        height=height,
        plot_bgcolor="#ffffff", paper_bgcolor="#ffffff",
        font=dict(color="#8b95a1"),
        margin=dict(l=20, r=20, t=50, b=20)
    )
    return fig


# ══════════════════════════════════════════════
#  HELPER / RENDER FUNCTIONS
# ══════════════════════════════════════════════

def format_large_number(val):
    """큰 숫자를 읽기 쉽게 포맷"""
    if val is None or pd.isna(val):
        return "--"
    abs_val = abs(val)
    sign = "-" if val < 0 else ""
    if abs_val >= 1e12:
        return f"{sign}{abs_val/1e12:.1f}조"
    if abs_val >= 1e8:
        return f"{sign}{abs_val/1e8:.1f}억"
    if abs_val >= 1e4:
        return f"{sign}{abs_val/1e4:.1f}만"
    return f"{sign}{abs_val:,.0f}"


def ratio_color_class(ratio_name, value):
    """비율 값에 따른 색상 클래스 반환"""
    if value is None:
        return ""
    defn = RATIO_DEFINITIONS.get(ratio_name, {})
    tg = defn.get("threshold_good")
    tw = defn.get("threshold_warn")
    lower = defn.get("lower_is_better", False)

    if tg is None or tw is None:
        return ""

    if lower:
        if value <= tg:
            return "ratio-good"
        elif value >= tw:
            return "ratio-bad"
        return "ratio-warn"
    else:
        if value >= tg:
            return "ratio-good"
        elif value <= tw:
            return "ratio-bad"
        return "ratio-warn"


def render_ratio_analysis(ratio_name, value, hist_values=None):
    """개별 비율에 대한 상세 분석 렌더링"""
    defn = RATIO_DEFINITIONS.get(ratio_name, {})
    if not defn:
        return

    cls = ratio_color_class(ratio_name, value)
    val_str = f"{value:.2f}" if value is not None else "--"

    color_map = {"ratio-good": "#00b386", "ratio-warn": "#ff9f43", "ratio-bad": "#f04452"}
    val_color = color_map.get(cls, "#191f28")

    st.markdown(f"""
    <div class="analysis-card">
        <h4>{ratio_name}</h4>
        <p style="font-size: 2rem; color: {val_color}; margin: 4px 0;">{val_str}</p>
        <p><strong>공식:</strong> {defn.get('formula', '')}</p>
        <p>{defn.get('description', '')}</p>
        <p style="color: #00b386;">✅ {defn.get('good', '')}</p>
        <p style="color: #f04452;">⚠️ {defn.get('warning', '')}</p>
    </div>
    """, unsafe_allow_html=True)

    # 과거 추이가 있으면 표시
    if hist_values is not None and len(hist_values) > 1:
        prev = hist_values.iloc[-1] if len(hist_values) > 1 else None
        curr = hist_values.iloc[0]
        if prev is not None and pd.notna(prev) and pd.notna(curr):
            change = curr - prev
            direction = "개선" if (change > 0 and not defn.get("lower_is_better", False)) or \
                                  (change < 0 and defn.get("lower_is_better", False)) else "악화"
            st.caption(f"전기 대비: {change:+.2f} ({direction})")


def render_impact_analysis(indicator_id, direction="up"):
    """경제지표 변동에 따른 섹터/종목 영향 분석 렌더링"""
    impact_data = INDICATOR_IMPACT.get(indicator_id)
    if not impact_data:
        st.info("이 지표에 대한 영향 분석 데이터가 없습니다.")
        return

    st.markdown(f"### {impact_data['name']}")
    st.markdown(f"*{impact_data['description']}*")

    impact_key = "up_impact" if direction == "up" else "down_impact"
    impacts = impact_data.get(impact_key, [])

    if not impacts:
        st.info(f"{'상승' if direction == 'up' else '하락'} 시 영향 데이터가 없습니다.")
        return

    st.markdown(f"#### {'📈 상승' if direction == 'up' else '📉 하락'} 시 영향")

    for imp in impacts:
        badge_cls = f"impact-{imp['direction']}"
        direction_text = {"positive": "긍정적 ↑", "negative": "부정적 ↓", "mixed": "혼합 ↔"}
        dir_text = direction_text.get(imp["direction"], "")

        tickers_str = ", ".join(imp["tickers"][:6])

        st.markdown(f"""
        <div class="analysis-card" style="margin: 6px 0;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h4 style="margin: 0;">{imp['sector']}</h4>
                <span class="{badge_cls}">{dir_text}</span>
            </div>
            <p style="margin: 4px 0; color: #8b95a1; font-size: 0.85rem;">📌 {tickers_str}</p>
            <p style="margin: 4px 0;">{imp['reason']}</p>
        </div>
        """, unsafe_allow_html=True)

    # 관련 지표
    related = impact_data.get("related_fred", [])
    if related:
        st.markdown("**관련 지표:** " + " · ".join(related))

    related_kr = impact_data.get("related_kr", [])
    if related_kr:
        st.markdown("**관련 한국종목:** " + " · ".join(related_kr))


# ══════════════════════════════════════════════
#  MAIN APPLICATION
# ══════════════════════════════════════════════

def main():
    # ─── Sidebar ───
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-brand">
            <h1>YW TERMINAL</h1>
            <p>Investment Research</p>
        </div>
        """, unsafe_allow_html=True)

        # Navigation
        page = st.radio(
            "nav",
            ["📊  대시보드", "🔍  종목 분석", "📋  재무 분석", "🧠  펀더멘탈 분석", "🌐  경제지표 영향", "📈  매크로 분석"],
            label_visibility="collapsed"
        )

        st.markdown("---")

        # 기간 선택
        st.markdown('<p style="color:#475569;font-size:0.7rem;font-weight:600;letter-spacing:1px;text-transform:uppercase;margin-bottom:6px;">기간 설정</p>', unsafe_allow_html=True)
        period_opt = st.selectbox("기간", ["1년", "2년", "3년", "5년", "직접입력"], label_visibility="collapsed")
        today = datetime.now()

        if period_opt == "직접입력":
            start_date = st.date_input("시작", value=today - timedelta(days=730))
            end_date = st.date_input("종료", value=today)
            start_str = start_date.strftime("%Y-%m-%d")
            end_str = end_date.strftime("%Y-%m-%d")
        else:
            days_map = {"1년": 365, "2년": 730, "3년": 1095, "5년": 1825}
            start_str = (today - timedelta(days=days_map[period_opt])).strftime("%Y-%m-%d")
            end_str = today.strftime("%Y-%m-%d")

        st.markdown("---")

        if st.button("🔄  새로고침", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

        st.page_link("pages/1_경제_기초_교육.py", label="📚  경제 기초 교육")

        # Footer
        st.markdown("---")
        st.markdown(f"""
        <div style="padding:8px 0;font-size:0.68rem;color:#334155;line-height:1.8;">
            <div><span class="status-dot" style="width:5px;height:5px;border-radius:50%;background:#22c55e;display:inline-block;margin-right:4px;"></span> LIVE — {datetime.now().strftime('%H:%M')}</div>
            <div style="margin-top:4px;">FRED · ECOS · Yahoo · CoinGecko</div>
            <div style="margin-top:2px;color:#1e293b;">YW Finance Terminal v1.0</div>
        </div>
        """, unsafe_allow_html=True)

    # ─── Page Router ───
    if "대시보드" in page:
        render_dashboard(start_str, end_str)
    elif "종목 분석" in page:
        render_stock_analysis()
    elif "재무 분석" in page:
        render_financial_analysis()
    elif "펀더멘탈" in page:
        render_fundamental_analysis()
    elif "경제지표" in page:
        render_impact_page()
    elif "매크로" in page:
        render_macro_analysis(start_str, end_str)


# ══════════════════════════════════════════════
#  PAGE: DASHBOARD
# ══════════════════════════════════════════════

def render_dashboard(start_str, end_str):
    st.markdown("""
    <div class="page-header">
        <div class="page-header-icon">📊</div>
        <div>
            <h1>Market Dashboard</h1>
            <p>실시간 글로벌 시장 현황</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 데이터 로드
    with st.spinner("📡 시장 데이터 수집중..."):
        df = load_macro_data(start_str, end_str)

    if df.empty:
        st.error("데이터 로드 실패. 새로고침을 시도하세요.")
        st.stop()

    cols_ok = [c for c in df.columns if df[c].notna().any()]
    st.markdown(f"""
    <div class="status-bar">
        <span><span class="status-dot"></span>&nbsp; LIVE</span>
        <span>지표 <b style="color:#191f28">{len(cols_ok)}개</b></span>
        <span>데이터 <b style="color:#191f28">{len(df)}</b> 포인트</span>
        <span style="margin-left:auto;color:#334155">{datetime.now().strftime('%Y-%m-%d %H:%M')}</span>
    </div>
    """, unsafe_allow_html=True)

    # ─── 핵심 메트릭 ───
    last = df.ffill().iloc[-1] if len(df) > 0 else pd.Series()
    prev = df.ffill().iloc[-2] if len(df) > 1 else pd.Series()

    def get_delta(col):
        v = last.get(col)
        p = prev.get(col)
        if pd.notna(v) and pd.notna(p) and p != 0:
            return f"{((v - p) / abs(p)) * 100:+.2f}%"
        return None

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        v = last.get("금리차")
        st.metric("금리차 (KR-US)", f"{v:.2f}%p" if pd.notna(v) else "--", delta=get_delta("금리차"))
    with c2:
        v = last.get("원달러")
        st.metric("USD/KRW", f"{v:,.0f}원" if pd.notna(v) else "--", delta=get_delta("원달러"), delta_color="inverse")
    with c3:
        v = last.get("VIX")
        st.metric("VIX", f"{v:.1f}" if pd.notna(v) else "--", delta=get_delta("VIX"), delta_color="inverse")
    with c4:
        v = last.get("KOSPI")
        st.metric("KOSPI", f"{v:,.0f}" if pd.notna(v) else "--", delta=get_delta("KOSPI"))
    with c5:
        v = last.get("S&P500")
        st.metric("S&P 500", f"{v:,.0f}" if pd.notna(v) else "--", delta=get_delta("S&P500"))
    with c6:
        v = last.get("미국금리")
        st.metric("Fed Rate", f"{v:.2f}%" if pd.notna(v) else "--", delta=get_delta("미국금리"), delta_color="inverse")

    st.divider()

    # ─── 차트 그리드 ───
    tabs = st.tabs(["💰 금리", "💱 환율", "📈 주가", "🛢 원자재", "😱 공포지표"])

    with tabs[0]:
        # 한미 금리 비교
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        if "한국금리" in df.columns:
            s = df["한국금리"].dropna()
            fig.add_trace(go.Scatter(x=s.index, y=s.values, name="한국", line=dict(color="#ef5350", width=3)), secondary_y=False)
        if "미국금리" in df.columns:
            s = df["미국금리"].dropna()
            fig.add_trace(go.Scatter(x=s.index, y=s.values, name="미국", line=dict(color="#42a5f5", width=3)), secondary_y=False)
        if "금리차" in df.columns:
            s = df["금리차"].dropna()
            colors = ["#26a69a" if v >= 0 else "#ef5350" for v in s.values]
            fig.add_trace(go.Bar(x=s.index, y=s.values, name="금리차", marker_color=colors, opacity=0.4), secondary_y=True)
        fig.update_layout(**_chart_layout("한미 기준금리 비교", 450))
        st.plotly_chart(fig, use_container_width=True)

        c1, c2 = st.columns(2)
        with c1:
            if "미국10Y" in df.columns:
                st.plotly_chart(make_line(df["미국10Y"].dropna(), "미국 10Y 국채금리", "#42a5f5"), use_container_width=True)
        with c2:
            if "장단기스프레드" in df.columns:
                st.plotly_chart(make_line(df["장단기스프레드"].dropna(), "장단기 스프레드 (10Y-2Y)", "#bb86fc"), use_container_width=True)

    with tabs[1]:
        c1, c2 = st.columns(2)
        with c1:
            if "원달러" in df.columns:
                st.plotly_chart(make_line(df["원달러"].dropna(), "USD/KRW", "#42a5f5"), use_container_width=True)
        with c2:
            if "달러인덱스" in df.columns:
                st.plotly_chart(make_line(df["달러인덱스"].dropna(), "달러 인덱스 (DXY)", "#bb86fc"), use_container_width=True)

        if "원달러" in df.columns and "금리차" in df.columns:
            st.plotly_chart(
                make_dual_axis(df["원달러"].dropna(), df["금리차"].dropna(), "원달러", "금리차", "환율 vs 금리차"),
                use_container_width=True
            )

    with tabs[2]:
        c1, c2 = st.columns(2)
        with c1:
            if "KOSPI" in df.columns:
                st.plotly_chart(make_line(df["KOSPI"].dropna(), "KOSPI", "#ef5350"), use_container_width=True)
        with c2:
            if "S&P500" in df.columns:
                st.plotly_chart(make_line(df["S&P500"].dropna(), "S&P 500", "#42a5f5"), use_container_width=True)
        c1, c2 = st.columns(2)
        with c1:
            if "나스닥" in df.columns:
                st.plotly_chart(make_line(df["나스닥"].dropna(), "NASDAQ Composite", "#bb86fc"), use_container_width=True)
        with c2:
            btc = fetch_coingecko_chart("bitcoin", 90)
            if not btc.empty:
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=btc["date"], y=btc["price"], line=dict(color="#f7931a", width=2), fill="tozeroy", fillcolor="rgba(247,147,26,0.1)"))
                fig.update_layout(**_chart_layout("Bitcoin (90D)", 350))
                st.plotly_chart(fig, use_container_width=True)

    with tabs[3]:
        c1, c2 = st.columns(2)
        with c1:
            if "유가(WTI)" in df.columns:
                st.plotly_chart(make_line(df["유가(WTI)"].dropna(), "WTI 원유", "#26a69a"), use_container_width=True)
        with c2:
            if "구리" in df.columns:
                st.plotly_chart(make_line(df["구리"].dropna(), "구리 (경기선행)", "#ff9800"), use_container_width=True)

    with tabs[4]:
        c1, c2 = st.columns(2)
        with c1:
            vix = last.get("VIX", 20)
            st.plotly_chart(make_gauge(vix, "VIX 공포지수", [0, 15, 25, 35, 50]), use_container_width=True)
            if pd.notna(vix):
                if vix > 30:
                    st.error("극심한 공포 구간. 시장 변동성 매우 높음.")
                elif vix > 20:
                    st.warning("불안 구간. 시장 불확실성 존재.")
                else:
                    st.success("안정 구간. 시장 변동성 낮음.")
        with c2:
            hy = last.get("하이일드스프레드", 4)
            st.plotly_chart(make_gauge(hy, "하이일드 스프레드", [0, 3, 5, 7, 10]), use_container_width=True)

        if "VIX" in df.columns and "S&P500" in df.columns:
            st.plotly_chart(
                make_dual_axis(df["VIX"].dropna(), df["S&P500"].dropna(), "VIX", "S&P500", "VIX vs S&P 500", "#ef5350", "#42a5f5"),
                use_container_width=True
            )

    # 전체 데이터
    with st.expander("📋 전체 데이터 테이블"):
        st.dataframe(df.round(2), use_container_width=True)
        csv = df.to_csv().encode("utf-8-sig")
        st.download_button("📥 CSV 다운로드", csv, "finance_data.csv", "text/csv")


# ══════════════════════════════════════════════
#  PAGE: STOCK ANALYSIS (종목 분석)
# ══════════════════════════════════════════════

def render_stock_analysis():
    st.markdown("""
    <div class="page-header">
        <div class="page-header-icon">🔍</div>
        <div>
            <h1>Stock Analysis</h1>
            <p>종목 검색 · 차트 · 기술 지표 · 밸류에이션</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 검색 바
    col_search, col_period = st.columns([3, 1])
    with col_search:
        ticker_input = st.text_input(
            "종목 검색",
            placeholder="종목명 또는 티커 (예: 삼성전자, 애플, AAPL, 비트코인...)",
            label_visibility="collapsed"
        )
    with col_period:
        chart_period = st.selectbox("차트 기간", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=3, label_visibility="collapsed")

    # 인기 종목 퀵 버튼
    st.markdown("**인기 종목:**")
    quick_cols = st.columns(8)
    quick_tickers = ["AAPL", "MSFT", "NVDA", "TSLA", "005930.KS", "GOOGL", "AMZN", "BTC-USD"]
    quick_names = ["Apple", "Microsoft", "NVIDIA", "Tesla", "삼성전자", "Google", "Amazon", "Bitcoin"]
    for i, (tick, name) in enumerate(zip(quick_tickers, quick_names)):
        with quick_cols[i]:
            if st.button(f"{name}", key=f"quick_{tick}", use_container_width=True):
                st.session_state["current_ticker"] = tick

    # 이름 → 티커 변환 후 세션 저장
    if ticker_input:
        resolved = resolve_ticker(ticker_input)
        st.session_state["current_ticker"] = resolved

    current_ticker = st.session_state.get("current_ticker", "")

    if not current_ticker:
        st.info("위 검색창에 종목명 또는 티커를 입력하거나 인기 종목을 클릭하세요.")
        st.markdown("""
        **검색 예시:**
        - 한글 이름: `삼성전자`, `네이버`, `카카오`, `애플`, `테슬라`, `비트코인`
        - 미국주식: `AAPL`, `MSFT`, `GOOGL`, `NVDA`, `TSLA`
        - 한국주식: `005930.KS` (삼성전자), `000660.KS` (SK하이닉스)
        - ETF: `SPY`, `QQQ`, `VTI`, `ARKK`
        - 암호화폐: `BTC-USD`, `ETH-USD`
        - 원자재: `금`, `원유`, `GC=F`, `CL=F`
        """)
        return

    # ─── 종목 데이터 로드 ───
    with st.spinner(f"📡 {current_ticker} 데이터 로딩..."):
        info = fetch_stock_info(current_ticker)
        hist = fetch_stock_history(current_ticker, period=chart_period)

    if not info and hist.empty:
        st.error(f"'{current_ticker}' 데이터를 찾을 수 없습니다. 티커를 확인하세요.")
        return

    # ─── 종목 헤더 ───
    name = info.get("shortName", info.get("longName", current_ticker))
    sector = info.get("sector", "")
    industry = info.get("industry", "")
    exchange = info.get("exchange", "")
    currency = info.get("currency", "USD")

    price = info.get("currentPrice") or info.get("regularMarketPrice") or info.get("previousClose")
    prev_close = info.get("previousClose") or info.get("regularMarketPreviousClose")
    change = None
    change_pct = None
    if price and prev_close and prev_close != 0:
        change = price - prev_close
        change_pct = (change / prev_close) * 100

    st.markdown(f"## {name} ({current_ticker})")
    if sector:
        st.caption(f"{sector} · {industry} · {exchange}")

    # 가격 메트릭
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        price_str = f"{currency} {price:,.2f}" if price else "--"
        delta_str = f"{change:+.2f} ({change_pct:+.2f}%)" if change is not None else None
        st.metric("현재가", price_str, delta=delta_str)
    with c2:
        mc = info.get("marketCap")
        st.metric("시가총액", format_large_number(mc) if mc else "--")
    with c3:
        pe = info.get("trailingPE")
        st.metric("PER", f"{pe:.1f}x" if pe else "--")
    with c4:
        pb = info.get("priceToBook")
        st.metric("PBR", f"{pb:.2f}x" if pb else "--")
    with c5:
        dy = info.get("dividendYield")
        st.metric("배당수익률", f"{dy*100:.2f}%" if dy else "--")

    st.divider()

    # ─── 차트 ───
    if not hist.empty:
        st.plotly_chart(make_candlestick(hist, f"{name} 주가 차트"), use_container_width=True)
        st.plotly_chart(make_volume_chart(hist), use_container_width=True)

    # ─── 추가 정보 탭 ───
    info_tabs = st.tabs(["📊 기본 정보", "📈 기술 지표", "💰 밸류에이션"])

    with info_tabs[0]:
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("**가격 정보**")
            st.write(f"- 52주 최고: {info.get('fiftyTwoWeekHigh', '--')}")
            st.write(f"- 52주 최저: {info.get('fiftyTwoWeekLow', '--')}")
            st.write(f"- 50일 평균: {info.get('fiftyDayAverage', '--')}")
            st.write(f"- 200일 평균: {info.get('twoHundredDayAverage', '--')}")
        with c2:
            st.markdown("**거래 정보**")
            vol = info.get("volume")
            avg_vol = info.get("averageVolume")
            st.write(f"- 거래량: {vol:,.0f}" if vol else "- 거래량: --")
            st.write(f"- 평균 거래량: {avg_vol:,.0f}" if avg_vol else "- 평균 거래량: --")
            beta = info.get("beta")
            st.write(f"- 베타: {beta:.2f}" if beta else "- 베타: --")
        with c3:
            st.markdown("**재무 요약**")
            rev = info.get("totalRevenue")
            st.write(f"- 매출: {format_large_number(rev)}" if rev else "- 매출: --")
            ni = info.get("netIncomeToCommon")
            st.write(f"- 순이익: {format_large_number(ni)}" if ni else "- 순이익: --")
            eps = info.get("trailingEps")
            st.write(f"- EPS: {eps:.2f}" if eps else "- EPS: --")
            roe = info.get("returnOnEquity")
            st.write(f"- ROE: {roe*100:.1f}%" if roe else "- ROE: --")

    with info_tabs[1]:
        if not hist.empty and len(hist) > 20:
            # RSI
            delta_p = hist["Close"].diff()
            gain = (delta_p.where(delta_p > 0, 0)).rolling(window=14).mean()
            loss = (-delta_p.where(delta_p < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))

            c1, c2 = st.columns(2)
            with c1:
                rsi_val = rsi.iloc[-1] if not rsi.empty and pd.notna(rsi.iloc[-1]) else None
                st.metric("RSI (14)", f"{rsi_val:.1f}" if rsi_val else "--")
                if rsi_val:
                    if rsi_val > 70:
                        st.warning("과매수 구간 (70+)")
                    elif rsi_val < 30:
                        st.success("과매도 구간 (30-)")
                    else:
                        st.info("중립 구간")

            with c2:
                # MACD
                ema12 = hist["Close"].ewm(span=12).mean()
                ema26 = hist["Close"].ewm(span=26).mean()
                macd_line = ema12 - ema26
                signal_line = macd_line.ewm(span=9).mean()
                macd_val = macd_line.iloc[-1]
                signal_val = signal_line.iloc[-1]
                st.metric("MACD", f"{macd_val:.2f}" if pd.notna(macd_val) else "--")
                if pd.notna(macd_val) and pd.notna(signal_val):
                    if macd_val > signal_val:
                        st.success("골든크로스 (매수 시그널)")
                    else:
                        st.warning("데드크로스 (매도 시그널)")

            # RSI 차트
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=rsi.index, y=rsi.values, line=dict(color="#bb86fc", width=2), name="RSI"))
            fig.add_hline(y=70, line_dash="dash", line_color="#ef5350", annotation_text="과매수")
            fig.add_hline(y=30, line_dash="dash", line_color="#26a69a", annotation_text="과매도")
            layout = _chart_layout("RSI (14)", 300)
            layout["yaxis"]["range"] = [0, 100]
            fig.update_layout(**layout)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("기술 지표를 계산하기에 데이터가 부족합니다.")

    with info_tabs[2]:
        val_data = {
            "PER (TTM)": info.get("trailingPE"),
            "Forward PER": info.get("forwardPE"),
            "PBR": info.get("priceToBook"),
            "PSR": info.get("priceToSalesTrailing12Months"),
            "EV/EBITDA": info.get("enterpriseToEbitda"),
            "EV/Revenue": info.get("enterpriseToRevenue"),
            "PEG Ratio": info.get("pegRatio"),
        }
        val_df = pd.DataFrame(
            [(k, f"{v:.2f}" if v else "--") for k, v in val_data.items()],
            columns=["지표", "값"]
        )
        st.dataframe(val_df, use_container_width=True, hide_index=True)

        # 배당 정보
        st.markdown("**배당 정보**")
        div_data = {
            "배당수익률": f"{info.get('dividendYield', 0)*100:.2f}%" if info.get('dividendYield') else "--",
            "주당배당금": f"${info.get('dividendRate', 0):.2f}" if info.get('dividendRate') else "--",
            "배당성향": f"{info.get('payoutRatio', 0)*100:.1f}%" if info.get('payoutRatio') else "--",
            "배당일": info.get("exDividendDate", "--"),
        }
        for k, v in div_data.items():
            st.write(f"- {k}: {v}")


# ══════════════════════════════════════════════
#  PAGE: FINANCIAL ANALYSIS (재무 분석)
# ══════════════════════════════════════════════

def render_financial_analysis():
    st.markdown("""
    <div class="page-header">
        <div class="page-header-icon">📋</div>
        <div>
            <h1>Financial Analysis</h1>
            <p>회계 · 재무비율 · 수익성 · 안정성 · 밸류에이션</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 검색
    ticker_input = st.text_input(
        "종목 검색",
        placeholder="종목명 또는 티커 (예: 삼성전자, 애플, AAPL...)",
        key="fin_ticker",
        label_visibility="collapsed"
    )

    quick_cols = st.columns(6)
    quick_fin = ["AAPL", "MSFT", "GOOGL", "005930.KS", "TSLA", "JPM"]
    quick_fin_names = ["Apple", "Microsoft", "Google", "삼성전자", "Tesla", "JP Morgan"]
    for i, (tick, name) in enumerate(zip(quick_fin, quick_fin_names)):
        with quick_cols[i]:
            if st.button(name, key=f"fin_quick_{tick}", use_container_width=True):
                st.session_state["fin_current_ticker"] = tick

    if ticker_input:
        st.session_state["fin_current_ticker"] = resolve_ticker(ticker_input)

    current_ticker = st.session_state.get("fin_current_ticker", "")

    if not current_ticker:
        st.info("재무 분석할 종목을 검색하세요.")
        st.markdown("""
        **분석 항목:**
        - 유동비율, 당좌비율 (단기 안정성)
        - 부채비율 (재무 레버리지)
        - ROE, ROA (수익성)
        - 영업이익률, 순이익률 (마진)
        - PER, PBR, EV/EBITDA (밸류에이션)
        - 연도별 추이 비교 & 상세 해설
        """)
        return

    # 데이터 로드
    with st.spinner(f"📡 {current_ticker} 재무제표 로딩..."):
        info = fetch_stock_info(current_ticker)
        financials = fetch_stock_financials(current_ticker)

    if not financials:
        st.error(f"'{current_ticker}'의 재무제표를 가져올 수 없습니다.")
        return

    name = info.get("shortName", current_ticker)
    st.markdown(f"## {name} ({current_ticker}) — 재무 분석")
    st.divider()

    # ─── 핵심 비율 계산 ───
    ratios = calculate_ratios(financials)
    hist_ratios = calculate_historical_ratios(financials)

    if not ratios:
        st.warning("재무 비율을 계산할 수 없습니다. 재무제표 데이터가 부족합니다.")
        return

    # ─── 비율 요약 카드 ───
    st.markdown('<div class="section-header">핵심 재무비율 요약</div>', unsafe_allow_html=True)

    ratio_items = list(ratios.items())
    cols_per_row = 4
    for row_start in range(0, len(ratio_items), cols_per_row):
        cols = st.columns(cols_per_row)
        for i, (rname, rval) in enumerate(ratio_items[row_start:row_start+cols_per_row]):
            with cols[i]:
                cls = ratio_color_class(rname, rval)
                color_map = {"ratio-good": "#00b386", "ratio-warn": "#ff9f43", "ratio-bad": "#f04452"}
                vc = color_map.get(cls, "#191f28")
                unit = "%" if "%" in rname or "ROE" in rname or "ROA" in rname or "이익률" in rname else "x" if "PER" in rname or "PBR" in rname or "EV" in rname else ""
                st.markdown(f"""
                <div class="analysis-card" style="text-align: center;">
                    <p style="color: #8b95a1; font-size: 0.8rem; margin: 0;">{rname.split('(')[0].strip()}</p>
                    <p style="color: {vc}; font-size: 1.8rem; font-weight: bold; margin: 4px 0;">{rval:.2f}{unit}</p>
                </div>
                """, unsafe_allow_html=True)

    st.divider()

    # ─── 상세 분석 탭 ───
    analysis_tabs = st.tabs(["📊 안정성", "💰 수익성", "📈 밸류에이션", "📉 추이", "📋 재무제표"])

    with analysis_tabs[0]:
        st.markdown('<div class="section-header">안정성 분석 (Stability)</div>', unsafe_allow_html=True)
        for rname in ["유동비율 (Current Ratio)", "당좌비율 (Quick Ratio)", "부채비율 (Debt-to-Equity)"]:
            if rname in ratios:
                hist_col_map = {
                    "유동비율 (Current Ratio)": "유동비율",
                    "당좌비율 (Quick Ratio)": "당좌비율",
                    "부채비율 (Debt-to-Equity)": "부채비율"
                }
                hc = hist_col_map.get(rname, "")
                hv = hist_ratios[hc] if hc in hist_ratios.columns else None
                render_ratio_analysis(rname, ratios[rname], hv)

    with analysis_tabs[1]:
        st.markdown('<div class="section-header">수익성 분석 (Profitability)</div>', unsafe_allow_html=True)
        for rname in ["ROE (자기자본이익률)", "ROA (총자산이익률)", "영업이익률 (Operating Margin)", "순이익률 (Net Margin)"]:
            if rname in ratios:
                hist_col_map = {
                    "ROE (자기자본이익률)": "ROE(%)",
                    "ROA (총자산이익률)": "ROA(%)",
                    "영업이익률 (Operating Margin)": "영업이익률(%)",
                    "순이익률 (Net Margin)": "순이익률(%)"
                }
                hc = hist_col_map.get(rname, "")
                hv = hist_ratios[hc] if hc in hist_ratios.columns else None
                render_ratio_analysis(rname, ratios[rname], hv)

    with analysis_tabs[2]:
        st.markdown('<div class="section-header">밸류에이션 분석 (Valuation)</div>', unsafe_allow_html=True)

        # yfinance info 기반 밸류에이션
        val_ratios = {}
        pe = info.get("trailingPE")
        if pe:
            val_ratios["PER (주가수익비율)"] = pe
        pb = info.get("priceToBook")
        if pb:
            val_ratios["PBR (주가순자산비율)"] = pb
        ev_ebitda = info.get("enterpriseToEbitda")
        if ev_ebitda:
            val_ratios["EV/EBITDA"] = ev_ebitda
        dy = info.get("dividendYield")
        if dy:
            val_ratios["배당수익률 (Dividend Yield)"] = dy * 100

        for rname, rval in val_ratios.items():
            render_ratio_analysis(rname, rval)

    with analysis_tabs[3]:
        st.markdown('<div class="section-header">연도별 재무비율 추이</div>', unsafe_allow_html=True)

        if not hist_ratios.empty:
            st.dataframe(hist_ratios.round(2), use_container_width=True)

            # 수익성 추이 차트
            profit_cols = ["ROE(%)", "ROA(%)", "영업이익률(%)", "순이익률(%)"]
            available_profit = [c for c in profit_cols if c in hist_ratios.columns]
            if available_profit:
                st.plotly_chart(
                    make_ratio_chart(hist_ratios, available_profit, "수익성 추이"),
                    use_container_width=True
                )

            # 안정성 추이 차트
            stable_cols = ["유동비율", "당좌비율", "부채비율"]
            available_stable = [c for c in stable_cols if c in hist_ratios.columns]
            if available_stable:
                st.plotly_chart(
                    make_ratio_chart(hist_ratios, available_stable, "안정성 추이"),
                    use_container_width=True
                )
        else:
            st.info("연도별 추이 데이터를 계산할 수 없습니다.")

    with analysis_tabs[4]:
        st.markdown('<div class="section-header">재무제표 원본</div>', unsafe_allow_html=True)

        fs_tabs = st.tabs(["대차대조표", "손익계산서", "현금흐름표"])

        with fs_tabs[0]:
            bs = financials.get("balance_sheet")
            if bs is not None and not bs.empty:
                st.dataframe(bs, use_container_width=True)
            else:
                st.info("대차대조표 데이터가 없습니다.")

        with fs_tabs[1]:
            inc = financials.get("income_stmt")
            if inc is not None and not inc.empty:
                st.dataframe(inc, use_container_width=True)
            else:
                st.info("손익계산서 데이터가 없습니다.")

        with fs_tabs[2]:
            cf = financials.get("cashflow")
            if cf is not None and not cf.empty:
                st.dataframe(cf, use_container_width=True)
            else:
                st.info("현금흐름표 데이터가 없습니다.")


# ══════════════════════════════════════════════
#  PAGE: IMPACT ANALYSIS (경제지표 영향)
# ══════════════════════════════════════════════

def render_impact_page():
    st.markdown("""
    <div class="page-header">
        <div class="page-header-icon">🌐</div>
        <div>
            <h1>Impact Analysis</h1>
            <p>경제지표 변동 → 섹터 · 종목 자동 리서치</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="analysis-card" style="margin-bottom:20px;">
        <p style="color:#94a3b8;margin:0;">경제지표가 변동하면 어떤 섹터와 종목이 영향을 받는지 자동으로 분석합니다.
        지표를 선택하고 방향을 지정하면 영향받는 섹터, 관련 종목, 이유를 확인할 수 있습니다.</p>
    </div>
    """, unsafe_allow_html=True)

    # 지표 선택
    indicator_names = {k: v["name"] for k, v in INDICATOR_IMPACT.items()}
    col1, col2 = st.columns([3, 1])

    with col1:
        selected_id = st.selectbox(
            "경제지표 선택",
            list(indicator_names.keys()),
            format_func=lambda x: f"{x} — {indicator_names[x]}"
        )
    with col2:
        direction = st.radio("방향", ["📈 상승", "📉 하락"], horizontal=True)

    st.divider()

    dir_key = "up" if "상승" in direction else "down"
    render_impact_analysis(selected_id, dir_key)

    st.divider()

    # 현재 지표값 표시
    st.markdown("### 📊 현재 지표값")
    with st.spinner("현재 데이터 조회중..."):
        today = datetime.now()
        start = (today - timedelta(days=365)).strftime("%Y-%m-%d")
        end = today.strftime("%Y-%m-%d")
        df = fetch_fred(selected_id, start, end)

    if not df.empty:
        latest = df.iloc[-1]
        prev_month = df.iloc[-2] if len(df) > 1 else None

        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("최신값", f"{latest['value']:.2f}", delta=f"{latest['value'] - prev_month['value']:.2f}" if prev_month is not None else None)
        with c2:
            st.metric("날짜", latest["date"].strftime("%Y-%m-%d"))
        with c3:
            if len(df) > 12:
                yoy = ((latest["value"] - df.iloc[-13]["value"]) / abs(df.iloc[-13]["value"])) * 100 if df.iloc[-13]["value"] != 0 else 0
                st.metric("YoY 변화", f"{yoy:+.2f}%")

        # 차트
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df["date"], y=df["value"],
            line=dict(color="#3182f6", width=2),
            fill="tozeroy", fillcolor="rgba(49,130,246,0.08)"
        ))
        fig.update_layout(**_chart_layout(f"{INDICATOR_IMPACT[selected_id]['name']} 추이", 350))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("현재 지표값을 조회할 수 없습니다.")


# ══════════════════════════════════════════════
#  PAGE: MACRO ANALYSIS (매크로 분석)
# ══════════════════════════════════════════════

def render_macro_analysis(start_str, end_str):
    st.markdown("""
    <div class="page-header">
        <div class="page-header-icon">📈</div>
        <div>
            <h1>Macro Analysis</h1>
            <p>상관관계 · 수익률 · 회귀분석 · 통계</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.spinner("📡 데이터 로딩..."):
        df = load_macro_data(start_str, end_str)

    if df.empty:
        st.error("데이터를 로드할 수 없습니다.")
        return

    tabs = st.tabs(["🔥 상관관계", "📊 수익률", "📐 회귀분석", "📋 통계", "📥 데이터"])

    with tabs[0]:
        st.markdown("### 지표 간 상관관계 히트맵")
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        corr = df[numeric_cols].corr()
        st.plotly_chart(make_heatmap(corr), use_container_width=True)

    with tabs[1]:
        st.markdown("### 기간별 수익률 비교")
        returns = {}
        for col in df.columns:
            if df[col].notna().sum() > 12:
                returns[col] = {}
                for p in [1, 3, 6, 12]:
                    s = df[col].dropna()
                    if len(s) > p:
                        curr = s.iloc[-1]
                        past = s.iloc[-p-1] if len(s) > p else s.iloc[0]
                        returns[col][f"{p}M"] = ((curr - past) / abs(past)) * 100 if past != 0 else 0
        returns_df = pd.DataFrame(returns).T
        if not returns_df.empty:
            fig = go.Figure()
            colors = ["#3182f6", "#00b386", "#6c5ce7", "#ff9f43"]
            for i, period in enumerate(returns_df.columns):
                fig.add_trace(go.Bar(name=period, x=returns_df.index, y=returns_df[period], marker_color=colors[i % len(colors)]))
            fig.update_layout(**_chart_layout("기간별 수익률", 500), barmode="group")
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(returns_df.round(2), use_container_width=True)

    with tabs[2]:
        st.markdown("### 금리차 → 환율 회귀분석")
        if "금리차" in df.columns and "원달러" in df.columns:
            clean = df[["금리차", "원달러"]].dropna()
            if len(clean) > 10:
                corr_val = clean["금리차"].corr(clean["원달러"])
                x = clean["금리차"]
                y = clean["원달러"]
                slope = np.cov(x, y)[0, 1] / np.var(x) if np.var(x) != 0 else 0
                intercept = y.mean() - slope * x.mean()

                c1, c2, c3 = st.columns(3)
                with c1:
                    st.metric("상관계수", f"{corr_val:.3f}")
                with c2:
                    st.metric("기울기", f"{slope:.2f}")
                with c3:
                    st.metric("R²", f"{corr_val**2:.3f}")

                st.markdown(f"**회귀식:** 원달러 = {intercept:.2f} + ({slope:.2f}) × 금리차")
                st.markdown(f"**해석:** 금리차가 1%p 하락하면 원달러 약 {abs(slope):.0f}원 상승")

                fig = go.Figure()
                fig.add_trace(go.Scatter(x=x, y=y, mode="markers", marker=dict(color="#3182f6", size=6, opacity=0.6), name="데이터"))
                x_line = np.linspace(x.min(), x.max(), 100)
                y_line = intercept + slope * x_line
                fig.add_trace(go.Scatter(x=x_line, y=y_line, mode="lines", line=dict(color="#f04452", width=2, dash="dash"), name="회귀선"))
                fig.update_layout(**_chart_layout("금리차 vs 원달러 산점도", 400), xaxis_title="금리차(%p)", yaxis_title="원달러(원)")
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("금리차/원달러 데이터가 필요합니다.")

        # 추가 회귀분석
        st.markdown("### 커스텀 회귀분석")
        numeric_cols = [c for c in df.columns if df[c].notna().sum() > 10]
        c1, c2 = st.columns(2)
        with c1:
            x_col = st.selectbox("X축 (독립변수)", numeric_cols, index=0)
        with c2:
            y_col = st.selectbox("Y축 (종속변수)", numeric_cols, index=min(1, len(numeric_cols)-1))

        if x_col and y_col and x_col != y_col:
            clean = df[[x_col, y_col]].dropna()
            if len(clean) > 5:
                corr_v = clean[x_col].corr(clean[y_col])
                st.metric("상관계수", f"{corr_v:.3f}")

                fig = go.Figure()
                fig.add_trace(go.Scatter(x=clean[x_col], y=clean[y_col], mode="markers",
                                          marker=dict(color="#3182f6", size=6, opacity=0.6)))
                fig.update_layout(**_chart_layout(f"{x_col} vs {y_col}", 400), xaxis_title=x_col, yaxis_title=y_col)
                st.plotly_chart(fig, use_container_width=True)

    with tabs[3]:
        st.markdown("### 기술통계량")
        desc = df.describe().T
        st.dataframe(desc.round(2), use_container_width=True)

    with tabs[4]:
        st.markdown("### 데이터 다운로드")
        csv = df.to_csv().encode("utf-8-sig")
        st.download_button("📥 전체 데이터 CSV", csv, "yw_finance_data.csv", "text/csv", use_container_width=True)
        st.dataframe(df.round(2), use_container_width=True)


# ══════════════════════════════════════════════
#  PAGE: FUNDAMENTAL ANALYSIS (펀더멘탈 분석)
# ══════════════════════════════════════════════

@st.cache_data(ttl=300)
def fetch_news_data(ticker):
    """yfinance에서 뉴스 데이터 가져오기"""
    try:
        stock = yf.Ticker(ticker)
        news = stock.news
        if news:
            return news
        return []
    except Exception:
        return []


def analyze_news_sentiment(news_item):
    """키워드 기반 뉴스 감성 분석"""
    positive_keywords = [
        "surge", "beat", "growth", "record", "upgrade", "rally", "gain",
        "profit", "revenue up", "outperform", "bullish", "breakthrough",
        "innovation", "strong", "expand", "raise", "exceed", "optimism",
        "상승", "호실적", "성장", "신고가", "매수", "흑자", "개선", "호조",
        "돌파", "최고", "확대", "상향", "수혜", "기대", "반등"
    ]
    negative_keywords = [
        "decline", "miss", "cut", "downgrade", "layoff", "loss", "drop",
        "fall", "crash", "bear", "recession", "weak", "risk", "warning",
        "lawsuit", "fraud", "investigation", "bankruptcy", "debt",
        "하락", "적자", "감소", "매도", "리스크", "손실", "하향", "위기",
        "부진", "축소", "경고", "소송", "파산", "부채"
    ]

    title = news_item.get("title", "").lower()
    # Some news structures use 'relatedTickers' or 'summary'
    summary = ""
    if isinstance(news_item.get("summary"), str):
        summary = news_item["summary"].lower()
    elif isinstance(news_item.get("description"), str):
        summary = news_item["description"].lower()

    text = title + " " + summary

    pos_count = sum(1 for kw in positive_keywords if kw.lower() in text)
    neg_count = sum(1 for kw in negative_keywords if kw.lower() in text)

    if pos_count > neg_count:
        return "positive", pos_count - neg_count
    elif neg_count > pos_count:
        return "negative", neg_count - pos_count
    else:
        return "neutral", 0


def calculate_financial_health_score(info):
    """재무 건전성 점수 계산 (0-100)"""
    score = 0
    details = {"profitability": 0, "stability": 0, "valuation": 0, "growth": 0}

    # ─── 수익성 (25점) ───
    prof_score = 0
    roe = info.get("returnOnEquity")
    if roe is not None:
        if roe > 0.20:
            prof_score += 8
        elif roe > 0.15:
            prof_score += 7
        elif roe > 0.10:
            prof_score += 5
        elif roe > 0.05:
            prof_score += 3
        elif roe > 0:
            prof_score += 1

    roa = info.get("returnOnAssets")
    if roa is not None:
        if roa > 0.10:
            prof_score += 7
        elif roa > 0.07:
            prof_score += 6
        elif roa > 0.05:
            prof_score += 4
        elif roa > 0.02:
            prof_score += 2
        elif roa > 0:
            prof_score += 1

    margin = info.get("profitMargins")
    if margin is not None:
        if margin > 0.25:
            prof_score += 10
        elif margin > 0.15:
            prof_score += 8
        elif margin > 0.10:
            prof_score += 6
        elif margin > 0.05:
            prof_score += 4
        elif margin > 0:
            prof_score += 2

    details["profitability"] = min(prof_score, 25)

    # ─── 안정성 (25점) ───
    stab_score = 0
    current_ratio = info.get("currentRatio")
    if current_ratio is not None:
        if current_ratio >= 2.0:
            stab_score += 13
        elif current_ratio >= 1.5:
            stab_score += 10
        elif current_ratio >= 1.0:
            stab_score += 7
        elif current_ratio >= 0.5:
            stab_score += 3

    dte = info.get("debtToEquity")
    if dte is not None:
        if dte < 30:
            stab_score += 12
        elif dte < 50:
            stab_score += 10
        elif dte < 100:
            stab_score += 7
        elif dte < 150:
            stab_score += 4
        elif dte < 200:
            stab_score += 2

    details["stability"] = min(stab_score, 25)

    # ─── 밸류에이션 (25점) ───
    val_score = 0
    pe = info.get("trailingPE")
    if pe is not None and pe > 0:
        if pe < 10:
            val_score += 10
        elif pe < 15:
            val_score += 8
        elif pe < 22:
            val_score += 6
        elif pe < 30:
            val_score += 4
        elif pe < 50:
            val_score += 2

    pb = info.get("priceToBook")
    if pb is not None and pb > 0:
        if pb < 1.0:
            val_score += 8
        elif pb < 2.0:
            val_score += 6
        elif pb < 4.0:
            val_score += 4
        elif pb < 7.0:
            val_score += 2

    peg = info.get("pegRatio")
    if peg is not None and peg > 0:
        if peg < 1.0:
            val_score += 7
        elif peg < 1.5:
            val_score += 5
        elif peg < 2.0:
            val_score += 3
        elif peg < 3.0:
            val_score += 1

    details["valuation"] = min(val_score, 25)

    # ─── 성장성 (25점) ───
    grow_score = 0
    rev_growth = info.get("revenueGrowth")
    if rev_growth is not None:
        if rev_growth > 0.30:
            grow_score += 13
        elif rev_growth > 0.20:
            grow_score += 10
        elif rev_growth > 0.10:
            grow_score += 7
        elif rev_growth > 0.05:
            grow_score += 5
        elif rev_growth > 0:
            grow_score += 3

    earn_growth = info.get("earningsGrowth")
    if earn_growth is not None:
        if earn_growth > 0.30:
            grow_score += 12
        elif earn_growth > 0.20:
            grow_score += 10
        elif earn_growth > 0.10:
            grow_score += 7
        elif earn_growth > 0.05:
            grow_score += 5
        elif earn_growth > 0:
            grow_score += 3

    details["growth"] = min(grow_score, 25)

    score = details["profitability"] + details["stability"] + details["valuation"] + details["growth"]
    return min(score, 100), details


def get_letter_grade(score):
    """점수를 등급으로 변환"""
    if score >= 90:
        return "A+", "#00b386"
    elif score >= 80:
        return "A", "#00b386"
    elif score >= 70:
        return "B+", "#3182f6"
    elif score >= 60:
        return "B", "#3182f6"
    elif score >= 50:
        return "C", "#ff9f43"
    elif score >= 40:
        return "D", "#f04452"
    else:
        return "F", "#f04452"


def generate_fundamental_report(info, score_details, news_sentiments, hist):
    """규칙 기반 AI 펀더멘탈 리포트 생성"""
    total_score = score_details["profitability"] + score_details["stability"] + score_details["valuation"] + score_details["growth"]
    name = info.get("shortName", info.get("longName", "해당 종목"))
    ticker = info.get("symbol", "")

    # ─── 1. 종합 의견 ───
    if total_score >= 70:
        overall_opinion = "강세 (Bullish)"
        opinion_color = "#00b386"
        opinion_summary = (
            f"{name}은(는) 재무 건전성 점수 {total_score}점으로 양호한 투자 매력도를 보이고 있습니다. "
            f"수익성, 안정성, 밸류에이션, 성장성 측면에서 전반적으로 긍정적인 요소가 우세하며, "
            f"중장기적으로 포트폴리오 편입을 고려할 만합니다."
        )
    elif total_score >= 45:
        overall_opinion = "중립 (Neutral)"
        opinion_color = "#ff9f43"
        opinion_summary = (
            f"{name}은(는) 재무 건전성 점수 {total_score}점으로 보통 수준입니다. "
            f"일부 재무 지표에서 강점을 보이나, 개선이 필요한 영역도 존재합니다. "
            f"추가적인 모니터링과 선별적 접근이 권장됩니다."
        )
    else:
        overall_opinion = "약세 (Bearish)"
        opinion_color = "#f04452"
        opinion_summary = (
            f"{name}은(는) 재무 건전성 점수 {total_score}점으로 주의가 필요합니다. "
            f"주요 재무 지표에서 취약점이 확인되며, 투자 시 충분한 리스크 분석이 선행되어야 합니다."
        )

    # ─── 2. 재무 건전성 분석 ───
    profitability_analysis = _analyze_profitability(info, score_details["profitability"])
    stability_analysis = _analyze_stability(info, score_details["stability"])

    # ─── 3. 밸류에이션 분석 ───
    valuation_analysis = _analyze_valuation(info, score_details["valuation"])

    # ─── 4. 성장성 분석 ───
    growth_analysis = _analyze_growth(info, score_details["growth"], hist)

    # ─── 5. 최근 이슈 영향 분석 ───
    news_impact_analysis = _analyze_news_impact(news_sentiments)

    # ─── 6. 리스크 요인 ───
    risk_analysis = _analyze_risks(info, score_details)

    # ─── 7. 투자 전략 제안 ───
    strategy_analysis = _generate_strategy(info, total_score, score_details, news_sentiments)

    report_html = f"""
    <div style="font-family: 'Pretendard', sans-serif;">

        <!-- 종합 의견 -->
        <div style="background:#ffffff;border-radius:16px;padding:24px 28px;margin:16px 0;border-left:5px solid {opinion_color};box-shadow:0 1px 4px rgba(0,0,0,0.04);">
            <h3 style="margin:0 0 8px 0;font-size:1.05rem;font-weight:700;color:#191f28;">1. 종합 의견</h3>
            <div style="display:inline-block;background:{opinion_color}18;color:{opinion_color};padding:5px 16px;border-radius:20px;font-weight:700;font-size:0.88rem;margin-bottom:12px;">
                {overall_opinion}
            </div>
            <p style="color:#4e5968;line-height:1.8;font-size:0.88rem;margin-top:12px;">{opinion_summary}</p>
        </div>

        <!-- 재무 건전성 분석 -->
        <div style="background:#ffffff;border-radius:16px;padding:24px 28px;margin:16px 0;border-left:5px solid #3182f6;box-shadow:0 1px 4px rgba(0,0,0,0.04);">
            <h3 style="margin:0 0 14px 0;font-size:1.05rem;font-weight:700;color:#191f28;">2. 재무 건전성 분석</h3>
            <div style="color:#4e5968;line-height:1.9;font-size:0.86rem;">
                <h4 style="color:#191f28;font-size:0.92rem;font-weight:600;margin:10px 0 6px 0;">수익성 ({score_details["profitability"]}/25점)</h4>
                {profitability_analysis}
                <h4 style="color:#191f28;font-size:0.92rem;font-weight:600;margin:16px 0 6px 0;">안정성 ({score_details["stability"]}/25점)</h4>
                {stability_analysis}
            </div>
        </div>

        <!-- 밸류에이션 분석 -->
        <div style="background:#ffffff;border-radius:16px;padding:24px 28px;margin:16px 0;border-left:5px solid #ff9f43;box-shadow:0 1px 4px rgba(0,0,0,0.04);">
            <h3 style="margin:0 0 14px 0;font-size:1.05rem;font-weight:700;color:#191f28;">3. 밸류에이션 분석 ({score_details["valuation"]}/25점)</h3>
            <div style="color:#4e5968;line-height:1.9;font-size:0.86rem;">
                {valuation_analysis}
            </div>
        </div>

        <!-- 성장성 분석 -->
        <div style="background:#ffffff;border-radius:16px;padding:24px 28px;margin:16px 0;border-left:5px solid #00b386;box-shadow:0 1px 4px rgba(0,0,0,0.04);">
            <h3 style="margin:0 0 14px 0;font-size:1.05rem;font-weight:700;color:#191f28;">4. 성장성 분석 ({score_details["growth"]}/25점)</h3>
            <div style="color:#4e5968;line-height:1.9;font-size:0.86rem;">
                {growth_analysis}
            </div>
        </div>

        <!-- 최근 이슈 영향 분석 -->
        <div style="background:#ffffff;border-radius:16px;padding:24px 28px;margin:16px 0;border-left:5px solid #6c5ce7;box-shadow:0 1px 4px rgba(0,0,0,0.04);">
            <h3 style="margin:0 0 14px 0;font-size:1.05rem;font-weight:700;color:#191f28;">5. 최근 이슈 영향 분석</h3>
            <div style="color:#4e5968;line-height:1.9;font-size:0.86rem;">
                {news_impact_analysis}
            </div>
        </div>

        <!-- 리스크 요인 -->
        <div style="background:#ffffff;border-radius:16px;padding:24px 28px;margin:16px 0;border-left:5px solid #f04452;box-shadow:0 1px 4px rgba(0,0,0,0.04);">
            <h3 style="margin:0 0 14px 0;font-size:1.05rem;font-weight:700;color:#191f28;">6. 리스크 요인</h3>
            <div style="color:#4e5968;line-height:1.9;font-size:0.86rem;">
                {risk_analysis}
            </div>
        </div>

        <!-- 투자 전략 제안 -->
        <div style="background:#ffffff;border-radius:16px;padding:24px 28px;margin:16px 0;border-left:5px solid #191f28;box-shadow:0 1px 4px rgba(0,0,0,0.04);">
            <h3 style="margin:0 0 14px 0;font-size:1.05rem;font-weight:700;color:#191f28;">7. 투자 전략 제안</h3>
            <div style="color:#4e5968;line-height:1.9;font-size:0.86rem;">
                {strategy_analysis}
            </div>
        </div>

        <div style="text-align:center;padding:12px;color:#b0b8c1;font-size:0.72rem;margin-top:8px;">
            본 리포트는 공개된 재무 데이터에 기반한 정량 분석이며, 투자 권유가 아닙니다. 투자 결정 시 전문가 상담을 권장합니다.
        </div>
    </div>
    """
    return report_html


def _analyze_profitability(info, score):
    """수익성 분석 세부 내용 생성"""
    parts = []
    roe = info.get("returnOnEquity")
    roa = info.get("returnOnAssets")
    margin = info.get("profitMargins")
    op_margin = info.get("operatingMargins")

    if roe is not None:
        roe_pct = roe * 100
        if roe_pct > 20:
            parts.append(
                f"<p>ROE <b>{roe_pct:.1f}%</b>로 자기자본 대비 수익 창출 능력이 매우 우수합니다. "
                f"업계 평균(~10-12%) 대비 크게 높은 수준으로, 경영 효율성이 뛰어나며 "
                f"주주 가치 창출에 적극적인 것으로 평가됩니다.</p>"
            )
        elif roe_pct > 15:
            parts.append(
                f"<p>ROE <b>{roe_pct:.1f}%</b>로 자기자본 대비 수익 창출 능력이 우수합니다. "
                f"업계 평균(~10-12%) 대비 높은 수준으로, 경영 효율성이 뛰어납니다.</p>"
            )
        elif roe_pct > 10:
            parts.append(
                f"<p>ROE <b>{roe_pct:.1f}%</b>로 업계 평균 수준의 자본 효율성을 보이고 있습니다. "
                f"안정적인 수익 구조를 유지하고 있으나, 추가적인 수익성 개선 여력이 있습니다.</p>"
            )
        elif roe_pct > 0:
            parts.append(
                f"<p>ROE <b>{roe_pct:.1f}%</b>로 업계 평균 대비 다소 낮은 자본 효율성을 보입니다. "
                f"수익성 개선을 위한 전략적 노력이 필요한 상황입니다.</p>"
            )
        else:
            parts.append(
                f"<p>ROE <b>{roe_pct:.1f}%</b>로 자기자본 대비 손실이 발생하고 있습니다. "
                f"수익 구조의 근본적 개선이 필요합니다.</p>"
            )

    if roa is not None:
        roa_pct = roa * 100
        if roa_pct > 10:
            parts.append(f"<p>ROA <b>{roa_pct:.1f}%</b>로 자산 활용 효율이 탁월합니다.</p>")
        elif roa_pct > 5:
            parts.append(f"<p>ROA <b>{roa_pct:.1f}%</b>로 양호한 자산 수익성을 보입니다.</p>")
        elif roa_pct > 0:
            parts.append(f"<p>ROA <b>{roa_pct:.1f}%</b>로 자산 수익성이 낮은 편입니다. 자산 활용 개선이 필요합니다.</p>")
        else:
            parts.append(f"<p>ROA <b>{roa_pct:.1f}%</b>로 자산 대비 손실 상태입니다.</p>")

    if margin is not None:
        margin_pct = margin * 100
        if margin_pct > 25:
            parts.append(
                f"<p>순이익률 <b>{margin_pct:.1f}%</b>로 뛰어난 수익 마진을 기록하고 있습니다. "
                f"높은 부가가치 사업 구조 또는 강력한 가격 결정력을 보유한 것으로 판단됩니다.</p>"
            )
        elif margin_pct > 10:
            parts.append(f"<p>순이익률 <b>{margin_pct:.1f}%</b>로 안정적인 수익 마진을 유지하고 있습니다.</p>")
        elif margin_pct > 0:
            parts.append(f"<p>순이익률 <b>{margin_pct:.1f}%</b>로 마진이 다소 얇은 편입니다. 원가 관리가 중요한 시점입니다.</p>")
        else:
            parts.append(f"<p>순이익률 <b>{margin_pct:.1f}%</b>로 적자 상태입니다. 비용 구조 개선이 시급합니다.</p>")

    if op_margin is not None:
        op_pct = op_margin * 100
        parts.append(f"<p>영업이익률은 <b>{op_pct:.1f}%</b>입니다.</p>")

    if not parts:
        parts.append("<p>수익성 관련 데이터를 확인할 수 없습니다.</p>")

    return "\n".join(parts)


def _analyze_stability(info, score):
    """안정성 분석 세부 내용 생성"""
    parts = []
    cr = info.get("currentRatio")
    dte = info.get("debtToEquity")
    quick = info.get("quickRatio")

    if cr is not None:
        if cr >= 2.0:
            parts.append(
                f"<p>유동비율 <b>{cr:.2f}x</b>로 단기 채무 상환 능력이 매우 우수합니다. "
                f"유동자산이 유동부채의 2배 이상으로, 단기 유동성 리스크가 매우 낮습니다.</p>"
            )
        elif cr >= 1.5:
            parts.append(
                f"<p>유동비율 <b>{cr:.2f}x</b>로 양호한 단기 지급 능력을 보유하고 있습니다.</p>"
            )
        elif cr >= 1.0:
            parts.append(
                f"<p>유동비율 <b>{cr:.2f}x</b>로 단기 채무 상환은 가능하나, 여유가 크지 않습니다. "
                f"유동성 관리에 주의가 필요합니다.</p>"
            )
        else:
            parts.append(
                f"<p>유동비율 <b>{cr:.2f}x</b>로 유동부채가 유동자산을 초과합니다. "
                f"단기 유동성 리스크에 각별한 주의가 필요합니다.</p>"
            )

    if quick is not None:
        parts.append(f"<p>당좌비율은 <b>{quick:.2f}x</b>입니다.</p>")

    if dte is not None:
        if dte < 30:
            parts.append(
                f"<p>부채비율 <b>{dte:.1f}%</b>로 매우 건전한 재무구조를 유지하고 있습니다. "
                f"레버리지 리스크가 극히 낮아 경기 침체 시에도 재무적 안정성이 높습니다.</p>"
            )
        elif dte < 50:
            parts.append(
                f"<p>부채비율 <b>{dte:.1f}%</b>로 안정적인 수준입니다.</p>"
            )
        elif dte < 100:
            parts.append(
                f"<p>부채비율 <b>{dte:.1f}%</b>로 업계 평균 수준입니다. "
                f"적정 레버리지를 활용 중이나, 금리 상승기에는 이자 부담 증가에 유의해야 합니다.</p>"
            )
        elif dte < 200:
            parts.append(
                f"<p>부채비율 <b>{dte:.1f}%</b>로 다소 높은 편입니다. "
                f"차입금 의존도가 높아 금리 변동에 민감하며, 재무 건전성 모니터링이 필요합니다.</p>"
            )
        else:
            parts.append(
                f"<p>부채비율 <b>{dte:.1f}%</b>로 과도한 수준입니다. "
                f"재무 레버리지가 매우 높아 신용 리스크가 상당하며, 부채 축소가 시급합니다.</p>"
            )

    if not parts:
        parts.append("<p>안정성 관련 데이터를 확인할 수 없습니다.</p>")

    return "\n".join(parts)


def _analyze_valuation(info, score):
    """밸류에이션 분석 세부 내용 생성"""
    parts = []
    pe = info.get("trailingPE")
    fwd_pe = info.get("forwardPE")
    pb = info.get("priceToBook")
    ps = info.get("priceToSalesTrailing12Months")
    peg = info.get("pegRatio")
    ev_ebitda = info.get("enterpriseToEbitda")

    if pe is not None:
        if pe < 0:
            parts.append(
                f"<p>PER <b>{pe:.1f}x</b>로 현재 적자 상태이며, PER 기준 밸류에이션 분석이 제한적입니다.</p>"
            )
        elif pe < 10:
            parts.append(
                f"<p>PER <b>{pe:.1f}x</b>로 시장 평균(~22x) 대비 매우 저평가 상태입니다. "
                f"가치주 투자 관점에서 매력적인 진입점이 될 수 있으나, "
                f"저평가의 원인(성장 둔화, 산업 구조 변화 등)을 면밀히 분석할 필요가 있습니다.</p>"
            )
        elif pe < 22:
            parts.append(
                f"<p>PER <b>{pe:.1f}x</b>로 시장 평균(~22x) 대비 합리적인 수준에서 거래되고 있습니다. "
                f"밸류에이션 부담이 크지 않아 안정적인 진입이 가능합니다.</p>"
            )
        elif pe < 30:
            parts.append(
                f"<p>PER <b>{pe:.1f}x</b>로 시장 평균(~22x) 대비 약간의 프리미엄이 반영되어 있습니다. "
                f"성장 기대가 일부 선반영된 상태로, 실적 달성 여부가 주가 방향성의 핵심 변수입니다.</p>"
            )
        else:
            parts.append(
                f"<p>PER <b>{pe:.1f}x</b>로 시장 평균(~22x) 대비 프리미엄 거래 중입니다. "
                f"높은 성장 기대가 반영되어 있으나, 실적 부진 시 밸류에이션 압축 리스크가 있습니다.</p>"
            )

    if fwd_pe is not None and pe is not None and fwd_pe > 0:
        if fwd_pe < pe:
            parts.append(
                f"<p>Forward PER <b>{fwd_pe:.1f}x</b>로 현재 PER 대비 낮아 실적 개선이 기대됩니다.</p>"
            )
        else:
            parts.append(
                f"<p>Forward PER <b>{fwd_pe:.1f}x</b>로 현재 PER 대비 높아 향후 실적 둔화가 예상됩니다.</p>"
            )

    if pb is not None:
        if pb < 1.0:
            parts.append(
                f"<p>PBR <b>{pb:.2f}x</b>로 장부가치 이하에서 거래 중입니다. "
                f"자산가치 대비 저평가되어 있으나, 수익성 개선 여부가 관건입니다.</p>"
            )
        elif pb < 4.0:
            parts.append(
                f"<p>PBR <b>{pb:.2f}x</b>로 시장 평균(S&P500 ~4x) 대비 적정 수준입니다.</p>"
            )
        else:
            parts.append(
                f"<p>PBR <b>{pb:.2f}x</b>로 시장 평균(S&P500 ~4x) 대비 프리미엄 거래 중입니다. "
                f"높은 ROE 또는 무형자산 가치가 반영된 결과로 보입니다.</p>"
            )

    if peg is not None and peg > 0:
        if peg < 1.0:
            parts.append(f"<p>PEG <b>{peg:.2f}</b>로 성장 대비 저평가 구간입니다 (PEG &lt; 1 = 매력적).</p>")
        elif peg < 2.0:
            parts.append(f"<p>PEG <b>{peg:.2f}</b>로 성장 대비 적정 밸류에이션입니다.</p>")
        else:
            parts.append(f"<p>PEG <b>{peg:.2f}</b>로 성장 대비 고평가 구간에 진입해 있습니다.</p>")

    if ev_ebitda is not None and ev_ebitda > 0:
        parts.append(f"<p>EV/EBITDA <b>{ev_ebitda:.1f}x</b>입니다.</p>")

    if not parts:
        parts.append("<p>밸류에이션 관련 데이터를 확인할 수 없습니다.</p>")

    return "\n".join(parts)


def _analyze_growth(info, score, hist):
    """성장성 분석 세부 내용 생성"""
    parts = []
    rev_growth = info.get("revenueGrowth")
    earn_growth = info.get("earningsGrowth")
    rev_qoq = info.get("quarterlyRevenueGrowth")
    earn_qoq = info.get("quarterlyEarningsGrowth")

    if rev_growth is not None:
        rg_pct = rev_growth * 100
        if rg_pct > 30:
            parts.append(
                f"<p>매출 성장률 <b>{rg_pct:.1f}%</b>로 고성장 궤도에 있습니다. "
                f"시장 점유율 확대 또는 신규 시장 진출이 매출 성장을 견인하고 있는 것으로 판단됩니다. "
                f"이러한 성장세가 지속 가능한지 여부가 중요합니다.</p>"
            )
        elif rg_pct > 10:
            parts.append(
                f"<p>매출 성장률 <b>{rg_pct:.1f}%</b>로 안정적인 성장세를 유지하고 있습니다. "
                f"GDP 성장률(~3%) 대비 크게 높은 수준으로, 시장 기대에 부합하는 성장입니다.</p>"
            )
        elif rg_pct > 0:
            parts.append(
                f"<p>매출 성장률 <b>{rg_pct:.1f}%</b>로 저성장 국면입니다. "
                f"성숙 시장에서의 점유율 유지에 초점을 맞추는 전략으로 보입니다.</p>"
            )
        else:
            parts.append(
                f"<p>매출 성장률 <b>{rg_pct:.1f}%</b>로 역성장 상태입니다. "
                f"매출 감소의 원인(시장 위축, 경쟁 심화, 제품 주기 등)을 면밀히 파악해야 합니다.</p>"
            )

    if earn_growth is not None:
        eg_pct = earn_growth * 100
        if eg_pct > 30:
            parts.append(
                f"<p>이익 성장률 <b>{eg_pct:.1f}%</b>로 강력한 이익 모멘텀을 보여주고 있습니다. "
                f"매출 성장과 함께 마진 확대가 동반되는 이상적인 성장 패턴입니다.</p>"
            )
        elif eg_pct > 10:
            parts.append(f"<p>이익 성장률 <b>{eg_pct:.1f}%</b>로 양호한 이익 증가세를 기록하고 있습니다.</p>")
        elif eg_pct > 0:
            parts.append(f"<p>이익 성장률 <b>{eg_pct:.1f}%</b>로 완만한 이익 증가입니다.</p>")
        else:
            parts.append(
                f"<p>이익 성장률 <b>{eg_pct:.1f}%</b>로 이익이 감소하고 있습니다. "
                f"비용 증가 또는 경쟁 압력으로 인한 마진 축소가 우려됩니다.</p>"
            )

    if rev_qoq is not None:
        parts.append(f"<p>분기 매출 성장률(QoQ): <b>{rev_qoq*100:.1f}%</b></p>")
    if earn_qoq is not None:
        parts.append(f"<p>분기 이익 성장률(QoQ): <b>{earn_qoq*100:.1f}%</b></p>")

    # 주가 추세 기반 성장 인사이트
    if hist is not None and not hist.empty and len(hist) > 20:
        try:
            start_price = hist["Close"].iloc[0]
            end_price = hist["Close"].iloc[-1]
            price_return = ((end_price - start_price) / start_price) * 100
            if price_return > 0:
                parts.append(
                    f"<p>분석 기간 주가 수익률은 <b style='color:#00b386;'>{price_return:+.1f}%</b>로 "
                    f"시장에서 성장 기대감이 반영되고 있습니다.</p>"
                )
            else:
                parts.append(
                    f"<p>분석 기간 주가 수익률은 <b style='color:#f04452;'>{price_return:+.1f}%</b>로 "
                    f"시장의 성장 우려가 반영된 상태입니다.</p>"
                )
        except Exception:
            pass

    if not parts:
        parts.append("<p>성장성 관련 데이터를 확인할 수 없습니다.</p>")

    return "\n".join(parts)


def _analyze_news_impact(news_sentiments):
    """뉴스 영향 분석"""
    if not news_sentiments:
        return "<p>최근 뉴스 데이터가 없어 이슈 영향 분석이 제한적입니다.</p>"

    parts = []
    pos_count = sum(1 for s, _ in news_sentiments if s == "positive")
    neg_count = sum(1 for s, _ in news_sentiments if s == "negative")
    neutral_count = sum(1 for s, _ in news_sentiments if s == "neutral")
    total = len(news_sentiments)

    parts.append(
        f"<p>최근 뉴스 {total}건 분석 결과: "
        f"<span style='color:#00b386;font-weight:600;'>긍정 {pos_count}건</span>, "
        f"<span style='color:#f04452;font-weight:600;'>부정 {neg_count}건</span>, "
        f"<span style='color:#8b95a1;font-weight:600;'>중립 {neutral_count}건</span></p>"
    )

    if pos_count > neg_count:
        parts.append(
            "<p>전반적으로 긍정적인 뉴스 흐름이 우세합니다. "
            "실적 호조, 시장 확대, 또는 긍정적 이슈가 주가 상승 모멘텀으로 작용할 가능성이 높습니다. "
            "긍정적 뉴스가 연속될 경우 단기적으로 2~4주간 가격 상승 압력이 유지될 수 있습니다.</p>"
        )
    elif neg_count > pos_count:
        parts.append(
            "<p>부정적 뉴스 흐름이 우세하여 단기 주가 하방 압력이 예상됩니다. "
            "실적 부진, 구조조정, 또는 업종 불확실성이 투자 심리에 부정적 영향을 줄 수 있습니다. "
            "다만, 과도한 하락 시 역발상 투자 기회가 될 수도 있으므로 펀더멘탈과 함께 판단이 필요합니다.</p>"
        )
    else:
        parts.append(
            "<p>긍정과 부정 뉴스가 혼재되어 있어 방향성이 불분명합니다. "
            "시장 참여자 간 의견이 갈리는 상황으로, 향후 실적 발표 또는 주요 이벤트가 "
            "주가 방향성의 촉매가 될 것으로 예상됩니다.</p>"
        )

    return "\n".join(parts)


def _analyze_risks(info, score_details):
    """리스크 요인 분석"""
    risks = []

    dte = info.get("debtToEquity")
    if dte is not None and dte > 100:
        risks.append(
            f"<li><b>높은 부채 수준:</b> 부채비율 {dte:.1f}%로 과도한 레버리지가 우려됩니다. "
            f"금리 상승 환경에서 이자 비용 증가로 수익성이 악화될 수 있습니다.</li>"
        )

    margin = info.get("profitMargins")
    if margin is not None and margin < 0.05:
        margin_pct = margin * 100
        risks.append(
            f"<li><b>낮은 수익 마진:</b> 순이익률 {margin_pct:.1f}%로 마진이 얇습니다. "
            f"원가 상승이나 가격 경쟁 심화 시 적자 전환 리스크가 있습니다.</li>"
        )

    pe = info.get("trailingPE")
    if pe is not None and pe > 40:
        risks.append(
            f"<li><b>높은 밸류에이션:</b> PER {pe:.1f}x로 고평가 상태입니다. "
            f"시장 기대에 못 미치는 실적 발표 시 급격한 주가 조정이 발생할 수 있습니다.</li>"
        )

    beta = info.get("beta")
    if beta is not None and beta > 1.5:
        risks.append(
            f"<li><b>높은 변동성:</b> 베타 {beta:.2f}로 시장 대비 변동성이 큽니다. "
            f"시장 하락 시 더 큰 폭의 손실이 발생할 수 있습니다.</li>"
        )

    cr = info.get("currentRatio")
    if cr is not None and cr < 1.0:
        risks.append(
            f"<li><b>유동성 리스크:</b> 유동비율 {cr:.2f}x로 단기 채무 상환 능력이 부족합니다.</li>"
        )

    rev_growth = info.get("revenueGrowth")
    if rev_growth is not None and rev_growth < 0:
        risks.append(
            f"<li><b>매출 감소:</b> 매출 성장률 {rev_growth*100:.1f}%로 역성장 중입니다. "
            f"시장 경쟁력 약화 또는 산업 구조 변화에 대한 대응이 필요합니다.</li>"
        )

    if score_details["profitability"] < 8:
        risks.append(
            "<li><b>수익성 저하:</b> 수익성 지표가 전반적으로 취약합니다. "
            "지속적인 수익 창출 능력에 대한 재검토가 필요합니다.</li>"
        )

    if not risks:
        return "<p>현재 데이터 기반으로 특별한 고위험 요인은 식별되지 않았습니다. 다만, 시장 전반의 거시경제 리스크(금리, 인플레이션, 지정학적 불확실성)에 대한 모니터링은 지속해야 합니다.</p>"

    return "<ul style='padding-left:20px;'>" + "\n".join(risks) + "</ul>"


def _generate_strategy(info, total_score, score_details, news_sentiments):
    """투자 전략 제안"""
    pos_news = sum(1 for s, _ in news_sentiments if s == "positive") if news_sentiments else 0
    neg_news = sum(1 for s, _ in news_sentiments if s == "negative") if news_sentiments else 0
    name = info.get("shortName", info.get("longName", "해당 종목"))

    pe = info.get("trailingPE")
    pb = info.get("priceToBook")
    high52 = info.get("fiftyTwoWeekHigh")
    low52 = info.get("fiftyTwoWeekLow")
    price = info.get("currentPrice") or info.get("regularMarketPrice")

    parts = []

    # 전략 결정
    if total_score >= 75 and pos_news >= neg_news:
        strategy = "적극 매수 (Strong Buy)"
        strategy_color = "#00b386"
        parts.append(
            f"<p><span style='background:#e8fff3;color:#00b386;padding:4px 12px;border-radius:12px;font-weight:700;'>"
            f"{strategy}</span></p>"
            f"<p>{name}은(는) 우수한 재무 건전성(점수 {total_score}/100)과 긍정적 뉴스 흐름을 보이고 있어 "
            f"적극적인 포지션 구축을 권장합니다.</p>"
        )
    elif total_score >= 60:
        strategy = "분할 매수 (Accumulate)"
        strategy_color = "#3182f6"
        parts.append(
            f"<p><span style='background:#e8f3ff;color:#3182f6;padding:4px 12px;border-radius:12px;font-weight:700;'>"
            f"{strategy}</span></p>"
            f"<p>재무 건전성이 양호한 수준(점수 {total_score}/100)으로, "
            f"분할 매수를 통한 점진적 포지션 확대가 적합합니다.</p>"
        )
    elif total_score >= 45:
        strategy = "관망 / 보유 (Hold)"
        strategy_color = "#ff9f43"
        parts.append(
            f"<p><span style='background:#fff8e8;color:#e09200;padding:4px 12px;border-radius:12px;font-weight:700;'>"
            f"{strategy}</span></p>"
            f"<p>재무 건전성 점수 {total_score}/100으로 보통 수준입니다. "
            f"기존 보유자는 유지하되, 신규 진입은 추가 확인 후 결정하는 것이 바람직합니다.</p>"
        )
    elif total_score >= 30:
        strategy = "비중 축소 (Reduce)"
        strategy_color = "#f04452"
        parts.append(
            f"<p><span style='background:#fff0f0;color:#f04452;padding:4px 12px;border-radius:12px;font-weight:700;'>"
            f"{strategy}</span></p>"
            f"<p>재무 건전성이 취약한 수준(점수 {total_score}/100)입니다. "
            f"기존 보유자는 비중 축소를 검토하고, 신규 진입은 신중하게 접근해야 합니다.</p>"
        )
    else:
        strategy = "투자 회피 (Avoid)"
        strategy_color = "#f04452"
        parts.append(
            f"<p><span style='background:#fff0f0;color:#f04452;padding:4px 12px;border-radius:12px;font-weight:700;'>"
            f"{strategy}</span></p>"
            f"<p>재무 건전성 점수 {total_score}/100으로 심각한 수준입니다. "
            f"펀더멘탈 개선 신호가 확인될 때까지 투자를 자제하는 것이 권장됩니다.</p>"
        )

    # 가격 레벨 기반 제안
    if price and high52 and low52 and high52 > low52:
        position_pct = ((price - low52) / (high52 - low52)) * 100
        parts.append(
            f"<p>현재 주가는 52주 범위({format_large_number(low52)} ~ {format_large_number(high52)}) 내 "
            f"<b>{position_pct:.0f}%</b> 위치에 있습니다.</p>"
        )
        if position_pct < 30:
            parts.append("<p>52주 저점 부근으로 기술적 반등 가능성이 있으나, 하락 추세가 지속될 수 있으므로 분할 접근이 유리합니다.</p>")
        elif position_pct > 80:
            parts.append("<p>52주 고점 부근으로 추격 매수보다는 조정 시 진입을 권장합니다.</p>")

    parts.append(
        "<p style='margin-top:12px;padding:12px 16px;background:#f4f5f7;border-radius:10px;font-size:0.82rem;color:#4e5968;'>"
        "<b>참고:</b> 본 전략은 정량적 재무 분석에 기반한 것이며, 실제 투자 시에는 거시경제 환경, "
        "산업 동향, 기업 고유 이벤트 등을 종합적으로 고려해야 합니다. "
        "투자의 최종 결정과 책임은 투자자 본인에게 있습니다.</p>"
    )

    return "\n".join(parts)


def render_fundamental_analysis():
    """펀더멘탈 분석 페이지 렌더링"""
    st.markdown("""
    <div class="page-header">
        <div class="page-header-icon">🧠</div>
        <div>
            <h1>Fundamental Analysis</h1>
            <p>기업 펀더멘탈 심층 분석 · 재무 건전성 · 뉴스 감성 · AI 리포트</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ─── 검색 바 ───
    col_search, col_period = st.columns([3, 1])
    with col_search:
        ticker_input = st.text_input(
            "종목 검색",
            placeholder="종목명 또는 티커 (예: 삼성전자, 애플, AAPL, 비트코인...)",
            label_visibility="collapsed",
            key="fundamental_ticker_input"
        )
    with col_period:
        fa_period = st.selectbox("분석 기간", ["3mo", "6mo", "1y", "2y"], index=2, label_visibility="collapsed", key="fa_period")

    # 인기 종목 퀵 버튼
    st.markdown("**인기 종목:**")
    quick_cols = st.columns(8)
    quick_tickers = ["AAPL", "MSFT", "NVDA", "TSLA", "005930.KS", "GOOGL", "AMZN", "BTC-USD"]
    quick_names = ["Apple", "Microsoft", "NVIDIA", "Tesla", "삼성전자", "Google", "Amazon", "Bitcoin"]
    for i, (tick, name) in enumerate(zip(quick_tickers, quick_names)):
        with quick_cols[i]:
            if st.button(f"{name}", key=f"fa_quick_{tick}", use_container_width=True):
                st.session_state["fa_current_ticker"] = tick

    # 이름 → 티커 변환 후 세션 저장
    if ticker_input:
        resolved = resolve_ticker(ticker_input)
        st.session_state["fa_current_ticker"] = resolved

    current_ticker = st.session_state.get("fa_current_ticker", "")

    if not current_ticker:
        st.info("위 검색창에 종목명 또는 티커를 입력하거나 인기 종목을 클릭하세요.")
        st.markdown("""
        **검색 예시:**
        - 한글 이름: `삼성전자`, `네이버`, `카카오`, `애플`, `테슬라`, `비트코인`
        - 미국주식: `AAPL`, `MSFT`, `GOOGL`, `NVDA`, `TSLA`
        - 한국주식: `005930.KS` (삼성전자), `000660.KS` (SK하이닉스)
        - ETF: `SPY`, `QQQ`, `VTI`, `ARKK`
        - 암호화폐: `BTC-USD`, `ETH-USD`
        """)
        return

    # ─── 데이터 로드 ───
    with st.spinner(f"📡 {current_ticker} 펀더멘탈 데이터 수집중..."):
        info = fetch_stock_info(current_ticker)
        hist = fetch_stock_history(current_ticker, period=fa_period)
        news_data = fetch_news_data(current_ticker)

    if not info and hist.empty:
        st.error(f"'{current_ticker}' 데이터를 찾을 수 없습니다. 티커를 확인하세요.")
        return

    # ══════════════════════════════════════════════
    #  (a) Company Overview
    # ══════════════════════════════════════════════
    company_name = info.get("shortName", info.get("longName", current_ticker))
    sector = info.get("sector", "N/A")
    industry = info.get("industry", "N/A")
    market_cap = info.get("marketCap")
    employees = info.get("fullTimeEmployees")
    high52 = info.get("fiftyTwoWeekHigh")
    low52 = info.get("fiftyTwoWeekLow")
    beta = info.get("beta")
    div_yield = info.get("dividendYield")

    st.markdown(f'<div class="section-header">기업 개요 — {company_name} ({current_ticker})</div>', unsafe_allow_html=True)

    ov_c1, ov_c2, ov_c3, ov_c4 = st.columns(4)
    with ov_c1:
        st.metric("섹터", sector if sector != "N/A" else "--")
    with ov_c2:
        st.metric("산업", industry if industry != "N/A" else "--")
    with ov_c3:
        st.metric("시가총액", format_large_number(market_cap) if market_cap else "--")
    with ov_c4:
        st.metric("직원 수", f"{employees:,}명" if employees else "--")

    ov2_c1, ov2_c2, ov2_c3, ov2_c4 = st.columns(4)
    with ov2_c1:
        st.metric("52주 최고가", f"{high52:,.2f}" if high52 else "--")
    with ov2_c2:
        st.metric("52주 최저가", f"{low52:,.2f}" if low52 else "--")
    with ov2_c3:
        st.metric("베타", f"{beta:.2f}" if beta else "--")
    with ov2_c4:
        st.metric("배당수익률", f"{div_yield*100:.2f}%" if div_yield else "--")

    st.divider()

    # ══════════════════════════════════════════════
    #  (b) Financial Health Score
    # ══════════════════════════════════════════════
    st.markdown('<div class="section-header">재무 건전성 점수</div>', unsafe_allow_html=True)

    total_score, score_details = calculate_financial_health_score(info)
    grade, grade_color = get_letter_grade(total_score)

    sc_c1, sc_c2 = st.columns([1, 1])
    with sc_c1:
        # 게이지 차트 (make_gauge와 유사하지만 0-100 range로)
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=total_score,
            title={"text": "Financial Health Score", "font": {"color": "#191f28", "size": 14, "family": "Pretendard, sans-serif"}},
            number={"font": {"color": "#191f28", "size": 36, "family": "Pretendard, sans-serif"}, "suffix": "/100"},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": "#b0b8c1", "tickfont": {"size": 10, "color": "#8b95a1"}},
                "bar": {"color": grade_color, "thickness": 0.25},
                "bgcolor": "#f2f4f6",
                "borderwidth": 0,
                "steps": [
                    {"range": [0, 30], "color": "rgba(240,68,82,0.12)"},
                    {"range": [30, 50], "color": "rgba(255,159,67,0.12)"},
                    {"range": [50, 70], "color": "rgba(255,159,67,0.08)"},
                    {"range": [70, 90], "color": "rgba(49,130,246,0.10)"},
                    {"range": [90, 100], "color": "rgba(0,179,134,0.12)"},
                ],
                "threshold": {
                    "line": {"color": grade_color, "width": 3},
                    "thickness": 0.8,
                    "value": total_score
                }
            }
        ))
        fig_gauge.update_layout(
            height=280,
            plot_bgcolor="#ffffff", paper_bgcolor="#ffffff",
            font=dict(color="#8b95a1"),
            margin=dict(l=30, r=30, t=60, b=20)
        )
        st.plotly_chart(fig_gauge, use_container_width=True)

    with sc_c2:
        st.markdown(f"""
        <div style="text-align:center;padding:20px;">
            <div style="font-size:4rem;font-weight:800;color:{grade_color};line-height:1;">{grade}</div>
            <div style="font-size:0.9rem;color:#4e5968;margin-top:8px;">종합 등급</div>
        </div>
        """, unsafe_allow_html=True)

        # 세부 점수 막대 차트
        categories = ["수익성", "안정성", "밸류에이션", "성장성"]
        scores = [score_details["profitability"], score_details["stability"], score_details["valuation"], score_details["growth"]]
        colors = ["#3182f6", "#00b386", "#ff9f43", "#6c5ce7"]

        fig_bar = go.Figure()
        for cat, sc, col in zip(categories, scores, colors):
            fig_bar.add_trace(go.Bar(
                x=[sc], y=[cat], orientation="h",
                marker_color=col, text=[f"{sc}/25"], textposition="outside",
                textfont=dict(size=12, color="#191f28", family="Pretendard, sans-serif"),
                name=cat, showlegend=False
            ))
        fig_bar.update_layout(
            height=220,
            plot_bgcolor="#ffffff", paper_bgcolor="#ffffff",
            xaxis=dict(range=[0, 28], showgrid=False, showticklabels=False, zeroline=False),
            yaxis=dict(autorange="reversed", tickfont=dict(size=12, color="#4e5968", family="Pretendard, sans-serif")),
            margin=dict(l=90, r=50, t=10, b=10),
            bargap=0.35
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    st.divider()

    # ══════════════════════════════════════════════
    #  (c) Recent News / Issues
    # ══════════════════════════════════════════════
    st.markdown('<div class="section-header">최근 뉴스 / 이슈</div>', unsafe_allow_html=True)

    news_sentiments = []

    if news_data:
        for item in news_data[:10]:
            # yfinance news structure varies by version
            title = item.get("title", "")
            publisher = item.get("publisher", "")
            link = item.get("link", "")

            # Handle different date formats
            pub_date = ""
            if "providerPublishTime" in item:
                try:
                    pub_date = datetime.fromtimestamp(item["providerPublishTime"]).strftime("%Y-%m-%d %H:%M")
                except Exception:
                    pub_date = ""
            elif "publishedDate" in item:
                pub_date = str(item["publishedDate"])[:16]

            # Newer yfinance versions may nest data differently
            if not title and "content" in item:
                content = item["content"]
                if isinstance(content, dict):
                    title = content.get("title", "")
                    publisher = content.get("provider", {}).get("displayName", "") if isinstance(content.get("provider"), dict) else ""
                    pub_date = str(content.get("pubDate", ""))[:16]
                    link = content.get("canonicalUrl", {}).get("url", "") if isinstance(content.get("canonicalUrl"), dict) else ""

            if not title:
                continue

            sentiment, strength = analyze_news_sentiment({"title": title, "summary": item.get("summary", "")})
            news_sentiments.append((sentiment, strength))

            if sentiment == "positive":
                badge_html = '<span style="background:#e8fff3;color:#00b386;padding:3px 10px;border-radius:12px;font-size:0.72rem;font-weight:700;">긍정</span>'
                border_color = "#00b386"
            elif sentiment == "negative":
                badge_html = '<span style="background:#fff0f0;color:#f04452;padding:3px 10px;border-radius:12px;font-size:0.72rem;font-weight:700;">부정</span>'
                border_color = "#f04452"
            else:
                badge_html = '<span style="background:#f4f5f7;color:#8b95a1;padding:3px 10px;border-radius:12px;font-size:0.72rem;font-weight:700;">중립</span>'
                border_color = "#e5e8eb"

            link_html = f'<a href="{link}" target="_blank" style="color:#3182f6;text-decoration:none;font-size:0.78rem;">기사 보기 &rarr;</a>' if link else ""

            st.markdown(f"""
            <div style="background:#ffffff;border-radius:12px;padding:16px 20px;margin:8px 0;
                         border-left:4px solid {border_color};box-shadow:0 1px 3px rgba(0,0,0,0.03);">
                <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:12px;">
                    <div style="flex:1;">
                        <div style="font-size:0.88rem;font-weight:600;color:#191f28;line-height:1.5;margin-bottom:6px;">
                            {title}
                        </div>
                        <div style="font-size:0.75rem;color:#8b95a1;">
                            {publisher} {('· ' + pub_date) if pub_date else ''} &nbsp; {link_html}
                        </div>
                    </div>
                    <div>{badge_html}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("뉴스를 불러올 수 없습니다.")

    st.divider()

    # ══════════════════════════════════════════════
    #  (d) AI Fundamental Report
    # ══════════════════════════════════════════════
    st.markdown('<div class="section-header">AI 펀더멘탈 리포트</div>', unsafe_allow_html=True)

    report_html = generate_fundamental_report(info, score_details, news_sentiments, hist)
    st.markdown(report_html, unsafe_allow_html=True)


# ══════════════════════════════════════════════
#  RUN
# ══════════════════════════════════════════════

if __name__ == "__main__":
    main()
