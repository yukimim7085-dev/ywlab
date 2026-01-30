"""
금융 지표 대시보드 Pro v7.0
모든 기능 탑재: 데이터, 분석, 시각화, 논문용 통계
- SSL 문제 우회용 대체 API 추가
- Deprecation 경고 수정
"""

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import requests
from datetime import datetime, timedelta
import yfinance as yf
import os

# ========== 페이지 설정 ==========
st.set_page_config(
    page_title="금융 대시보드 Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== API 키 ==========
try:
    ECOS_KEY = st.secrets["ECOS_API_KEY"]
    FRED_KEY = st.secrets["FRED_API_KEY"]
except:
    ECOS_KEY = "QZIGLKAE4NXE2AH490NG"
    FRED_KEY = "4fb5dac909861e78d5e76dadeb5cf9d7"


# ========== 다크모드 CSS ==========
def apply_theme(dark_mode):
    if dark_mode:
        st.markdown("""
        <style>
        .stApp { background-color: #0e1117; color: #fafafa; }
        .stMetric { background-color: #1e2130; border-radius: 10px; padding: 10px; }
        .stTabs [data-baseweb="tab"] { background-color: #1e2130; }
        </style>
        """, unsafe_allow_html=True)


# ========== 데이터 수집 함수 ==========
def fetch_fred(series_id, start_date, end_date):
    """FRED 데이터"""
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
                df["ym"] = df["date"].dt.to_period("M")
                df = df.groupby("ym")["value"].mean().reset_index()
                df["date"] = df["ym"].dt.to_timestamp()
                return df[["date", "value"]]
    except:
        pass
    return pd.DataFrame()


def fetch_ecos(stat_code, item_code, start_date, end_date):
    """ECOS 데이터"""
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
    except:
        pass
    return pd.DataFrame()


def fetch_yahoo(ticker, start_date, end_date):
    """Yahoo Finance 데이터"""
    try:
        data = yf.download(ticker, start=start_date, end=end_date, progress=False)
        if not data.empty and len(data) > 0:
            # 멀티인덱스 처리
            if isinstance(data.columns, pd.MultiIndex):
                data = data.droplevel(1, axis=1)
            df = data[["Close"]].reset_index()
            df.columns = ["date", "value"]
            df["date"] = pd.to_datetime(df["date"])
            df["ym"] = df["date"].dt.to_period("M")
            df = df.groupby("ym")["value"].mean().reset_index()
            df["date"] = df["ym"].dt.to_timestamp()
            return df[["date", "value"]]
    except Exception as e:
        pass
    return pd.DataFrame()


def fetch_coingecko(coin_id, start_date, end_date):
    """CoinGecko에서 가격 가져오기 (비트코인, 금, 은 등)"""
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        days = min((end - start).days, 365)  # CoinGecko 무료 API 제한

        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=usd&days={days}"
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            prices = resp.json().get("prices", [])
            if prices:
                df = pd.DataFrame(prices, columns=["timestamp", "value"])
                df["date"] = pd.to_datetime(df["timestamp"], unit="ms")
                df["ym"] = df["date"].dt.to_period("M")
                df = df.groupby("ym")["value"].mean().reset_index()
                df["date"] = df["ym"].dt.to_timestamp()
                return df[["date", "value"]]
    except:
        pass
    return pd.DataFrame()


def fetch_kospi_ecos(start_date, end_date):
    """ECOS에서 KOSPI 지수 가져오기"""
    start = start_date.replace("-", "")[:6]
    end = end_date.replace("-", "")[:6]
    # KOSPI 지수: 901Y014, 0001000
    url = f"https://ecos.bok.or.kr/api/StatisticSearch/{ECOS_KEY}/json/kr/1/1000/901Y014/M/{start}/{end}/0001000"
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
    except:
        pass
    return pd.DataFrame()


@st.cache_data(ttl=3600)
def load_all_data(start_date, end_date):
    """모든 데이터 로드"""
    data = {}

    # FRED 데이터
    fred_items = {
        "미국금리": "FEDFUNDS",
        "미국10Y": "DGS10",
        "미국2Y": "DGS2",
        "원달러": "DEXKOUS",
        "VIX": "VIXCLS",
        "SP500": "SP500",
        "나스닥": "NASDAQCOM",
        "유가": "DCOILWTICO",
        "달러인덱스": "DTWEXBGS",
        "하이일드스프레드": "BAMLH0A0HYM2",
        "미국CPI": "CPIAUCSL",
        "미국실업률": "UNRATE",
        "연준자산": "WALCL",
        "구리": "PCOPPUSDM",
    }

    for name, code in fred_items.items():
        df = fetch_fred(code, start_date, end_date)
        if not df.empty:
            data[name] = df.set_index("date")["value"]

    # ECOS 데이터
    df = fetch_ecos("722Y001", "0101000", start_date, end_date)
    if not df.empty:
        data["한국금리"] = df.set_index("date")["value"]

    # Yahoo Finance (SSL 문제시 대체 API 사용)
    # KOSPI - Yahoo 시도 후 ECOS 폴백
    df = fetch_yahoo("^KS11", start_date, end_date)
    if df.empty:
        df = fetch_kospi_ecos(start_date, end_date)
    if not df.empty:
        data["KOSPI"] = df.set_index("date")["value"]

    # 금 - Yahoo 시도 후 FRED 폴백
    df = fetch_yahoo("GC=F", start_date, end_date)
    if df.empty:
        df = fetch_fred("GOLDAMGBD228NLBM", start_date, end_date)
    if not df.empty:
        data["금"] = df.set_index("date")["value"]

    # 은 - Yahoo 시도 후 FRED 폴백
    df = fetch_yahoo("SI=F", start_date, end_date)
    if df.empty:
        df = fetch_fred("SLVPRUSD", start_date, end_date)
    if not df.empty:
        data["은"] = df.set_index("date")["value"]

    # 비트코인 - CoinGecko API (SSL 문제 우회)
    btc_df = fetch_coingecko("bitcoin", start_date, end_date)
    if not btc_df.empty:
        data["비트코인"] = btc_df.set_index("date")["value"]

    # DataFrame 합치기
    if data:
        result = pd.DataFrame(data)
        result = result.sort_index()

        # 파생 지표
        if "한국금리" in result.columns and "미국금리" in result.columns:
            result["금리차"] = result["한국금리"] - result["미국금리"]

        if "미국10Y" in result.columns and "미국2Y" in result.columns:
            result["미국장단기스프레드"] = result["미국10Y"] - result["미국2Y"]

        if "미국CPI" in result.columns:
            result["미국CPI_YoY"] = result["미국CPI"].pct_change(periods=12, fill_method=None) * 100

        return result

    return pd.DataFrame()


# ========== 분석 함수 ==========
def calc_correlation(df):
    """상관관계 계산"""
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    return df[numeric_cols].corr()


def calc_returns(df, periods=[1, 3, 6, 12]):
    """기간별 수익률"""
    returns = {}
    for col in df.columns:
        if df[col].notna().sum() > 12:
            returns[col] = {}
            for p in periods:
                if len(df) > p:
                    current = df[col].dropna().iloc[-1]
                    past = df[col].dropna().iloc[-p-1] if len(df[col].dropna()) > p else df[col].dropna().iloc[0]
                    returns[col][f"{p}M"] = ((current - past) / past) * 100 if past != 0 else 0
    return pd.DataFrame(returns).T


def add_moving_averages(series, windows=[20, 60, 120]):
    """이동평균선 추가"""
    result = {"원본": series}
    for w in windows:
        if len(series) >= w:
            result[f"MA{w}"] = series.rolling(window=w).mean()
    return pd.DataFrame(result)


def calc_volatility(series, window=20):
    """변동성 (표준편차)"""
    return series.pct_change().rolling(window=window).std() * np.sqrt(252) * 100


# ========== 차트 함수 ==========
def make_line_chart(df, col, title, color="#3498db", ma=False):
    """라인 차트"""
    fig = go.Figure()

    if col in df.columns:
        y = df[col].dropna()
        if not y.empty:
            fig.add_trace(go.Scatter(
                x=y.index, y=y.values, name=col,
                line=dict(color=color, width=2),
                fill="tozeroy", fillcolor=f"rgba{tuple(list(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) + [0.1])}"
            ))

            # 이동평균선
            if ma and len(y) > 20:
                ma20 = y.rolling(20).mean()
                fig.add_trace(go.Scatter(x=ma20.index, y=ma20.values, name="MA20",
                                        line=dict(color="#e74c3c", width=1, dash="dash")))
            if ma and len(y) > 60:
                ma60 = y.rolling(60).mean()
                fig.add_trace(go.Scatter(x=ma60.index, y=ma60.values, name="MA60",
                                        line=dict(color="#f39c12", width=1, dash="dash")))

    fig.update_layout(
        title=title, height=350, hovermode="x unified",
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=40, r=40, t=50, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02)
    )
    return fig


def make_dual_chart(df, col1, col2, title, c1="#e74c3c", c2="#3498db"):
    """듀얼 축 차트"""
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    if col1 in df.columns:
        y1 = df[col1].dropna()
        if not y1.empty:
            fig.add_trace(go.Scatter(x=y1.index, y=y1.values, name=col1,
                                    line=dict(color=c1, width=2)), secondary_y=False)

    if col2 in df.columns:
        y2 = df[col2].dropna()
        if not y2.empty:
            fig.add_trace(go.Scatter(x=y2.index, y=y2.values, name=col2,
                                    line=dict(color=c2, width=2)), secondary_y=True)

    fig.update_layout(
        title=title, height=400, hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)"
    )
    return fig


def make_rate_chart(df, events=None):
    """금리차 차트 (이벤트 표시 포함)"""
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # 한국 금리
    if "한국금리" in df.columns:
        y = df["한국금리"].dropna()
        if not y.empty:
            fig.add_trace(go.Scatter(x=y.index, y=y.values, name="🇰🇷 한국",
                                    line=dict(color="#e74c3c", width=3)), secondary_y=False)

    # 미국 금리
    if "미국금리" in df.columns:
        y = df["미국금리"].dropna()
        if not y.empty:
            fig.add_trace(go.Scatter(x=y.index, y=y.values, name="🇺🇸 미국",
                                    line=dict(color="#3498db", width=3)), secondary_y=False)

    # 금리차 바
    if "금리차" in df.columns:
        y = df["금리차"].dropna()
        if not y.empty:
            colors = ["#27ae60" if v >= 0 else "#c0392b" for v in y.values]
            fig.add_trace(go.Bar(x=y.index, y=y.values, name="금리차",
                                marker_color=colors, opacity=0.4), secondary_y=True)

    # 이벤트 표시
    if events and len(df) > 0:
        min_date = df.index.min()
        max_date = df.index.max()
        for date_str, label in events.items():
            try:
                event_date = pd.to_datetime(date_str)
                if min_date <= event_date <= max_date:
                    fig.add_vline(x=event_date, line_dash="dash", line_color="gray", opacity=0.5)
                    fig.add_annotation(x=event_date, y=1.05, yref="paper", text=label,
                                     showarrow=False, textangle=-45, font=dict(size=9))
            except:
                pass

    fig.update_layout(
        title="📊 한미 기준금리 비교", height=500, hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(title="기준금리 (%)"), yaxis2=dict(title="금리차 (%p)")
    )
    return fig


def make_heatmap(corr_df):
    """상관관계 히트맵"""
    fig = px.imshow(
        corr_df.round(2),
        text_auto=True,
        color_continuous_scale="RdBu_r",
        aspect="auto",
        zmin=-1, zmax=1
    )
    fig.update_layout(
        title="📈 지표 간 상관관계", height=600,
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)"
    )
    return fig


def make_returns_chart(returns_df):
    """수익률 비교 차트"""
    fig = go.Figure()

    colors = px.colors.qualitative.Set2
    for i, period in enumerate(returns_df.columns):
        fig.add_trace(go.Bar(
            name=period,
            x=returns_df.index,
            y=returns_df[period],
            marker_color=colors[i % len(colors)]
        ))

    fig.update_layout(
        title="📊 기간별 수익률 비교", height=400,
        barmode="group", hovermode="x unified",
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)"
    )
    return fig


def make_gauge(value, title, ranges):
    """게이지 차트"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value if pd.notna(value) else 0,
        title={"text": title},
        gauge={
            "axis": {"range": [ranges[0], ranges[-1]]},
            "bar": {"color": "#2c3e50"},
            "steps": [
                {"range": [ranges[0], ranges[1]], "color": "#27ae60"},
                {"range": [ranges[1], ranges[2]], "color": "#f1c40f"},
                {"range": [ranges[2], ranges[3]], "color": "#e67e22"},
                {"range": [ranges[3], ranges[4]], "color": "#e74c3c"},
            ]
        }
    ))
    fig.update_layout(height=250, margin=dict(l=20, r=20, t=50, b=20))
    return fig


# ========== 주요 이벤트 데이터 ==========
RATE_EVENTS = {
    "2022-03-17": "Fed 인상시작",
    "2022-05-26": "한은 빅스텝",
    "2022-09-21": "금리역전",
    "2023-01-13": "한은 동결시작",
    "2024-09-18": "Fed 인하시작",
}


# ========== 메인 앱 ==========
def main():
    # 사이드바
    with st.sidebar:
        st.markdown("## ⚙️ 설정")

        # 다크모드
        dark_mode = st.toggle("🌙 다크모드", value=False)
        apply_theme(dark_mode)

        st.divider()

        # 기간 선택
        period_opt = st.selectbox("📅 기간", ["1년", "2년", "3년", "5년", "직접 입력"])
        today = datetime.now()

        if period_opt == "직접 입력":
            start_date = st.date_input("시작일", value=today - timedelta(days=730))
            end_date = st.date_input("종료일", value=today)
            start_str = start_date.strftime("%Y-%m-%d")
            end_str = end_date.strftime("%Y-%m-%d")
        else:
            days = {"1년": 365, "2년": 730, "3년": 1095, "5년": 1825}[period_opt]
            start_str = (today - timedelta(days=days)).strftime("%Y-%m-%d")
            end_str = today.strftime("%Y-%m-%d")

        st.divider()

        # 새로고침
        if st.button("🔄 데이터 새로고침", width="stretch"):
            st.cache_data.clear()
            st.rerun()

        st.divider()

        # 경제 기초 교육 페이지 링크
        st.markdown("### 📚 교육 자료")
        if st.button("경제 기초 교육 보기", type="primary", use_container_width=True):
            st.switch_page("pages/1_경제_기초_교육.py")

        st.divider()
        st.caption("📡 데이터: FRED, ECOS, Yahoo")
        st.caption(f"🕐 마지막 갱신: {datetime.now().strftime('%m/%d %H:%M')}")

        with st.expander("ℹ️ 업데이트 주기"):
            st.markdown("""
            **앱 캐시**: 1시간

            **FRED** (미국)
            - 금리, VIX: 매일
            - CPI, 실업률: 매월

            **ECOS** (한국)
            - 기준금리: 금통위 후

            **Yahoo**
            - 주가, 원자재: 실시간
            """)

    # 제목
    st.markdown("# 📊 금융 지표 대시보드 Pro")
    st.caption("한미 금리차 | 환율 | 주가 | 원자재 | 공포지표 | 분석")
    st.divider()

    # 데이터 로드
    with st.spinner("📡 데이터 수집중..."):
        df = load_all_data(start_str, end_str)

    if df.empty:
        st.error("❌ 데이터 로드 실패")
        st.stop()

    # 수집 현황
    cols_ok = [c for c in df.columns if df[c].notna().any()]
    st.success(f"✅ **{len(cols_ok)}개** 지표 수집  |  📅 **{len(df)}개월** 데이터")

    # ===== 핵심 지표 =====
    st.markdown("### 📈 핵심 지표")
    last = df.ffill().iloc[-1] if len(df) > 0 else pd.Series()

    c1, c2, c3, c4, c5, c6 = st.columns(6)

    with c1:
        v = last.get("금리차")
        color = "🔴" if pd.notna(v) and v < 0 else "🟢"
        st.metric(f"{color} 금리차", f"{v:.2f}%p" if pd.notna(v) else "N/A")

    with c2:
        v = last.get("원달러")
        st.metric("💵 원/달러", f"{v:,.0f}원" if pd.notna(v) else "N/A")

    with c3:
        v = last.get("VIX")
        color = "🔴" if pd.notna(v) and v > 25 else "🟢"
        st.metric(f"{color} VIX", f"{v:.1f}" if pd.notna(v) else "N/A")

    with c4:
        v = last.get("KOSPI")
        st.metric("🇰🇷 KOSPI", f"{v:,.0f}" if pd.notna(v) else "N/A")

    with c5:
        v = last.get("SP500")
        st.metric("🇺🇸 S&P500", f"{v:,.0f}" if pd.notna(v) else "N/A")

    with c6:
        v = last.get("비트코인")
        st.metric("₿ BTC", f"${v:,.0f}" if pd.notna(v) else "N/A")

    st.divider()

    # ===== 탭 =====
    tabs = st.tabs(["💰 금리", "💱 환율", "📈 주가", "🛢️ 원자재", "😱 공포지표", "📊 분석", "📑 논문용"])

    # 금리 탭
    with tabs[0]:
        show_events = st.checkbox("📌 주요 이벤트 표시", value=True)
        events = RATE_EVENTS if show_events else None
        st.plotly_chart(make_rate_chart(df, events), width="stretch")

        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(make_dual_chart(df, "미국2Y", "미국10Y", "🇺🇸 미국 국채금리"), width="stretch")
        with c2:
            st.plotly_chart(make_line_chart(df, "미국장단기스프레드", "📉 미국 장단기 스프레드", "#9b59b6"), width="stretch")

        # 해석
        v = last.get("금리차")
        if pd.notna(v):
            if v < -1.5:
                st.error("🚨 **금리차 역전 심화** → 자본유출 압력, 원화약세")
            elif v < 0:
                st.warning("⚠️ **금리차 역전** → 외국인 자금 유출 가능성")
            else:
                st.success("✅ **금리차 정상** → 자본유입 우호적")

    # 환율 탭
    with tabs[1]:
        show_ma = st.checkbox("📈 이동평균선 표시", value=True, key="fx_ma")
        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(make_line_chart(df, "원달러", "💵 원/달러", "#3498db", ma=show_ma), width="stretch")
        with c2:
            st.plotly_chart(make_line_chart(df, "달러인덱스", "💪 달러인덱스", "#9b59b6", ma=show_ma), width="stretch")

        st.plotly_chart(make_dual_chart(df, "원달러", "금리차", "📉 환율 vs 금리차", "#3498db", "#e74c3c"), width="stretch")

    # 주가 탭
    with tabs[2]:
        show_ma = st.checkbox("📈 이동평균선 표시", value=True, key="stock_ma")
        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(make_line_chart(df, "KOSPI", "🇰🇷 KOSPI", "#e74c3c", ma=show_ma), width="stretch")
        with c2:
            st.plotly_chart(make_line_chart(df, "SP500", "🇺🇸 S&P500", "#3498db", ma=show_ma), width="stretch")

        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(make_line_chart(df, "나스닥", "📱 나스닥", "#9b59b6", ma=show_ma), width="stretch")
        with c2:
            st.plotly_chart(make_line_chart(df, "비트코인", "₿ 비트코인", "#f39c12", ma=show_ma), width="stretch")

    # 원자재 탭
    with tabs[3]:
        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(make_line_chart(df, "금", "🥇 금", "#f1c40f", ma=True), width="stretch")
        with c2:
            st.plotly_chart(make_line_chart(df, "유가", "🛢️ WTI 유가", "#27ae60", ma=True), width="stretch")

        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(make_line_chart(df, "구리", "🔶 구리 (경기선행)", "#e67e22", ma=True), width="stretch")
        with c2:
            st.plotly_chart(make_line_chart(df, "은", "🥈 은", "#95a5a6", ma=True), width="stretch")

    # 공포지표 탭
    with tabs[4]:
        c1, c2, c3 = st.columns(3)

        with c1:
            vix = last.get("VIX", 20)
            st.plotly_chart(make_gauge(vix, "VIX 공포지수", [0, 15, 25, 35, 50]), width="stretch")
            if pd.notna(vix):
                if vix > 30: st.error("🔴 극심한 공포")
                elif vix > 20: st.warning("🟠 불안")
                else: st.success("🟢 안정")

        with c2:
            hy = last.get("하이일드스프레드", 4)
            st.plotly_chart(make_gauge(hy, "하이일드 스프레드", [0, 3, 5, 7, 10]), width="stretch")

        with c3:
            spread = last.get("미국장단기스프레드", 0)
            st.metric("📉 장단기스프레드", f"{spread:.2f}%p" if pd.notna(spread) else "N/A")
            if pd.notna(spread) and spread < 0:
                st.warning("⚠️ 수익률곡선 역전 (경기침체 신호)")

        st.plotly_chart(make_dual_chart(df, "VIX", "SP500", "😱 VIX vs S&P500", "#e74c3c", "#3498db"), width="stretch")

    # 분석 탭
    with tabs[5]:
        st.markdown("### 📊 상관관계 분석")
        corr = calc_correlation(df)
        st.plotly_chart(make_heatmap(corr), width="stretch")

        st.divider()

        st.markdown("### 📈 기간별 수익률")
        returns = calc_returns(df)
        if not returns.empty:
            st.plotly_chart(make_returns_chart(returns), width="stretch")
            st.dataframe(returns.round(2).style.format("{:.2f}%"), width="stretch")

    # 논문용 탭
    with tabs[6]:
        st.markdown("### 📑 논문용 통계 분석")

        st.markdown("#### 1️⃣ 기술통계량")
        desc = df.describe().T
        st.dataframe(desc.round(2), width="stretch")

        st.divider()

        st.markdown("#### 2️⃣ 주요 변수 상관계수")
        key_cols = ["금리차", "원달러", "VIX", "KOSPI", "SP500"]
        available_cols = [c for c in key_cols if c in df.columns]
        if available_cols:
            st.dataframe(df[available_cols].corr().round(3), width="stretch")

        st.divider()

        st.markdown("#### 3️⃣ 금리차-환율 회귀분석")
        if "금리차" in df.columns and "원달러" in df.columns:
            clean = df[["금리차", "원달러"]].dropna()
            if len(clean) > 10:
                corr_val = clean["금리차"].corr(clean["원달러"])
                st.metric("상관계수", f"{corr_val:.3f}")

                # 간단한 회귀계수
                x = clean["금리차"]
                y = clean["원달러"]
                slope = np.cov(x, y)[0, 1] / np.var(x)
                intercept = y.mean() - slope * x.mean()

                st.write(f"**회귀식**: 원달러 = {intercept:.2f} + ({slope:.2f}) × 금리차")
                st.write(f"**해석**: 금리차가 1%p 하락하면 원달러 환율 약 {abs(slope):.0f}원 상승")

        st.divider()

        st.markdown("#### 4️⃣ 데이터 다운로드")
        csv = df.to_csv().encode("utf-8-sig")
        st.download_button("📥 전체 데이터 CSV", csv, "finance_data.csv", "text/csv")

    # 전체 데이터
    st.divider()
    with st.expander("📋 전체 데이터"):
        st.dataframe(df.round(2), width="stretch")

    # 푸터
    st.divider()
    st.caption("📊 금융 지표 대시보드 Pro  |  데이터: FRED, ECOS, Yahoo  |  Made with Streamlit")


if __name__ == "__main__":
    main()
