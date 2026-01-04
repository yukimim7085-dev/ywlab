"""
금융 지표 대시보드 (확장판)
한미 금리차, 환율, 주가, 원자재, 경제지표 등 종합 투자 지표
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import requests
from datetime import datetime, timedelta

# ============ 페이지 설정 ============
st.set_page_config(
    page_title="금융 지표 대시보드",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============ API 키 설정 ============
try:
    ECOS_API_KEY = st.secrets["ECOS_API_KEY"]
    FRED_API_KEY = st.secrets["FRED_API_KEY"]
except:
    ECOS_API_KEY = "QZIGLKAE4NXE2AH490NG"
    FRED_API_KEY = "4fb5dac909861e78d5e76dadeb5cf9d7"


# ============ 데이터 수집 함수 ============
@st.cache_data(ttl=3600)
def get_fred_data(series_id, name, start_date, end_date):
    """FRED API에서 데이터 가져오기"""
    url = "https://api.stlouisfed.org/fred/series/observations"
    params = {
        'series_id': series_id,
        'api_key': FRED_API_KEY,
        'file_type': 'json',
        'observation_start': start_date,
        'observation_end': end_date
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        if 'observations' in data:
            df = pd.DataFrame(data['observations'])
            df['date'] = pd.to_datetime(df['date'])
            df[name] = pd.to_numeric(df['value'], errors='coerce')
            df = df[['date', name]].dropna()
            df = df.set_index('date').resample('M').mean().reset_index()
            return df
    except:
        pass
    return None


@st.cache_data(ttl=3600)
def get_ecos_data(stat_code, item_code, name, start_date, end_date, cycle="M"):
    """ECOS API에서 데이터 가져오기"""
    start = start_date.replace("-", "")[:6]
    end = end_date.replace("-", "")[:6]
    url = f"https://ecos.bok.or.kr/api/StatisticSearch/{ECOS_API_KEY}/json/kr/1/1000/{stat_code}/{cycle}/{start}/{end}/{item_code}"

    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        if 'StatisticSearch' in data:
            rows = data['StatisticSearch']['row']
            df = pd.DataFrame(rows)
            df['date'] = pd.to_datetime(df['TIME'] + '01', format='%Y%m%d')
            df[name] = pd.to_numeric(df['DATA_VALUE'], errors='coerce')
            return df[['date', name]]
    except:
        pass
    return None


@st.cache_data(ttl=3600)
def load_all_data(start_date, end_date):
    """모든 데이터 로드 및 병합"""
    dataframes = []

    # ========== FRED 데이터 ==========
    fred_series = [
        # 금리
        ("FEDFUNDS", "미국기준금리"),
        ("GS10", "미국10년금리"),
        ("GS2", "미국2년금리"),
        ("T10Y2Y", "미국장단기스프레드"),

        # 환율
        ("DEXKOUS", "원달러환율"),
        ("DEXJPUS", "엔달러환율"),
        ("DEXUSEU", "유로달러환율"),
        ("DTWEXBGS", "달러인덱스"),

        # 공포/위험 지표
        ("VIXCLS", "VIX"),
        ("BAMLH0A0HYM2", "하이일드스프레드"),
        ("TEDRATE", "TED스프레드"),

        # 주가지수
        ("SP500", "S&P500"),
        ("NASDAQCOM", "나스닥"),

        # 원자재
        ("GOLDAMGBD228NLBM", "금시세"),
        ("DCOILWTICO", "WTI유가"),

        # 경제지표
        ("CPIAUCSL", "미국CPI"),
        ("UNRATE", "미국실업률"),
        ("GDPC1", "미국GDP"),
        ("INDPRO", "미국산업생산"),

        # 통화/유동성
        ("M2SL", "미국M2통화량"),
        ("WALCL", "연준총자산"),
    ]

    progress_bar = st.progress(0)
    status_text = st.empty()

    total = len(fred_series) + 8  # FRED + ECOS 개수

    for i, (series_id, name) in enumerate(fred_series):
        status_text.text(f"FRED 데이터 수집중... {name}")
        df = get_fred_data(series_id, name, start_date, end_date)
        if df is not None and len(df) > 0:
            dataframes.append(df)
        progress_bar.progress((i + 1) / total)

    # ========== ECOS 데이터 ==========
    ecos_series = [
        ("722Y001", "0101000", "한국기준금리"),      # 기준금리
        ("817Y002", "010200000", "국고채3년"),       # 국고채 3년
        ("817Y002", "010210000", "국고채10년"),      # 국고채 10년
        ("731Y004", "0000001", "원달러환율종가"),    # 원달러 환율(종가)
        ("732Y001", "99", "외환보유액"),             # 외환보유액
        ("901Y014", "*AA", "소비자물가지수"),        # CPI
        ("902Y015", "I16AA", "경상수지"),            # 경상수지
        ("028Y015", "1070000", "KOSPI"),             # KOSPI
    ]

    for i, (stat_code, item_code, name) in enumerate(ecos_series):
        status_text.text(f"ECOS 데이터 수집중... {name}")
        df = get_ecos_data(stat_code, item_code, name, start_date, end_date)
        if df is not None and len(df) > 0:
            dataframes.append(df)
        progress_bar.progress((len(fred_series) + i + 1) / total)

    progress_bar.empty()
    status_text.empty()

    # 데이터 병합
    if dataframes:
        result = dataframes[0]
        for df in dataframes[1:]:
            result = pd.merge(result, df, on='date', how='outer')
        result = result.sort_values('date').dropna(subset=['date'])

        # 파생 지표 계산
        if '한국기준금리' in result.columns and '미국기준금리' in result.columns:
            result['한미금리차'] = result['한국기준금리'] - result['미국기준금리']

        if '국고채10년' in result.columns and '국고채3년' in result.columns:
            result['한국장단기스프레드'] = result['국고채10년'] - result['국고채3년']

        if '미국CPI' in result.columns:
            result['미국CPI_YoY'] = result['미국CPI'].pct_change(12) * 100

        if '소비자물가지수' in result.columns:
            result['한국CPI_YoY'] = result['소비자물가지수'].pct_change(12) * 100

        return result
    return None


# ============ 차트 함수들 ============
def create_dual_axis_chart(df, col1, col2, title, y1_title, y2_title, color1='#FF6B6B', color2='#4ECDC4'):
    """듀얼 축 차트"""
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    if col1 in df.columns:
        fig.add_trace(
            go.Scatter(x=df['date'], y=df[col1], name=col1,
                       line=dict(color=color1, width=2)),
            secondary_y=False
        )
    if col2 in df.columns:
        fig.add_trace(
            go.Scatter(x=df['date'], y=df[col2], name=col2,
                       line=dict(color=color2, width=2)),
            secondary_y=True
        )

    fig.update_layout(
        title=title,
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        height=400
    )
    fig.update_yaxes(title_text=y1_title, secondary_y=False)
    fig.update_yaxes(title_text=y2_title, secondary_y=True)

    return fig


def create_multi_line_chart(df, columns, title, y_title, colors=None):
    """멀티 라인 차트"""
    fig = go.Figure()

    if colors is None:
        colors = px.colors.qualitative.Set2

    for i, col in enumerate(columns):
        if col in df.columns:
            fig.add_trace(
                go.Scatter(x=df['date'], y=df[col], name=col,
                           line=dict(color=colors[i % len(colors)], width=2))
            )

    fig.update_layout(
        title=title,
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        height=400,
        yaxis_title=y_title
    )

    return fig


def create_rate_spread_chart(df):
    """금리차 차트 (바 + 라인)"""
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    if '한국기준금리' in df.columns:
        fig.add_trace(
            go.Scatter(x=df['date'], y=df['한국기준금리'], name='한국 기준금리',
                       line=dict(color='#FF6B6B', width=2)),
            secondary_y=False
        )
    if '미국기준금리' in df.columns:
        fig.add_trace(
            go.Scatter(x=df['date'], y=df['미국기준금리'], name='미국 기준금리',
                       line=dict(color='#4ECDC4', width=2)),
            secondary_y=False
        )
    if '한미금리차' in df.columns:
        colors = ['#2ECC71' if x >= 0 else '#E74C3C' for x in df['한미금리차']]
        fig.add_trace(
            go.Bar(x=df['date'], y=df['한미금리차'], name='한미금리차',
                   marker_color=colors, opacity=0.5),
            secondary_y=True
        )

    fig.update_layout(
        title='한미 기준금리 및 금리차',
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        height=400
    )
    fig.update_yaxes(title_text="기준금리 (%)", secondary_y=False)
    fig.update_yaxes(title_text="금리차 (%p)", secondary_y=True)

    return fig


def create_fear_gauge(vix_value):
    """VIX 게이지 차트"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=vix_value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "VIX 공포지수"},
        gauge={
            'axis': {'range': [0, 50]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 15], 'color': '#2ECC71'},
                {'range': [15, 25], 'color': '#F1C40F'},
                {'range': [25, 35], 'color': '#E67E22'},
                {'range': [35, 50], 'color': '#E74C3C'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': vix_value
            }
        }
    ))
    fig.update_layout(height=300)
    return fig


# ============ 메인 앱 ============
def main():
    # 헤더
    st.title("📊 금융 지표 대시보드")
    st.markdown("**금리 | 환율 | 주가 | 원자재 | 경제지표 - 핵심 투자 지표 종합**")
    st.markdown("---")

    # 사이드바
    st.sidebar.header("⚙️ 설정")

    # 기간 선택
    period = st.sidebar.selectbox(
        "기간 선택",
        ["최근 1년", "최근 2년", "최근 3년", "최근 5년", "직접 입력"]
    )

    today = datetime.now()
    if period == "최근 1년":
        start_date = (today - timedelta(days=365)).strftime("%Y-%m-%d")
    elif period == "최근 2년":
        start_date = (today - timedelta(days=730)).strftime("%Y-%m-%d")
    elif period == "최근 3년":
        start_date = (today - timedelta(days=1095)).strftime("%Y-%m-%d")
    elif period == "최근 5년":
        start_date = (today - timedelta(days=1825)).strftime("%Y-%m-%d")
    else:
        start_date = st.sidebar.date_input("시작일", value=datetime(2022, 1, 1)).strftime("%Y-%m-%d")

    end_date = today.strftime("%Y-%m-%d")

    st.sidebar.markdown("---")
    st.sidebar.markdown("**데이터 출처**")
    st.sidebar.markdown("- 🇺🇸 FRED (미국 연준)")
    st.sidebar.markdown("- 🇰🇷 ECOS (한국은행)")

    # 데이터 로드
    df = load_all_data(start_date, end_date)

    if df is None or len(df) == 0:
        st.error("데이터를 불러올 수 없습니다.")
        return

    # 수집된 지표 수 표시
    available_cols = [c for c in df.columns if c != 'date' and df[c].notna().sum() > 0]
    st.success(f"✅ {len(available_cols)}개 지표 수집 완료 | {len(df)}개월 데이터")

    # ============ 핵심 지표 카드 ============
    latest = df.iloc[-1]
    prev = df.iloc[-2] if len(df) > 1 else latest

    st.subheader("📈 핵심 지표 현황")

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        val = latest.get('한미금리차', 0)
        delta = val - prev.get('한미금리차', val) if pd.notna(val) else 0
        st.metric("한미금리차", f"{val:.2f}%p" if pd.notna(val) else "N/A", f"{delta:+.2f}")

    with col2:
        val = latest.get('원달러환율', latest.get('원달러환율종가', 0))
        prev_val = prev.get('원달러환율', prev.get('원달러환율종가', val))
        delta = val - prev_val if pd.notna(val) else 0
        st.metric("원/달러", f"{val:,.0f}원" if pd.notna(val) else "N/A", f"{delta:+.0f}", delta_color="inverse")

    with col3:
        val = latest.get('VIX', 0)
        delta = val - prev.get('VIX', val) if pd.notna(val) else 0
        st.metric("VIX", f"{val:.1f}" if pd.notna(val) else "N/A", f"{delta:+.1f}", delta_color="inverse")

    with col4:
        val = latest.get('KOSPI', 0)
        delta = val - prev.get('KOSPI', val) if pd.notna(val) else 0
        st.metric("KOSPI", f"{val:,.0f}" if pd.notna(val) else "N/A", f"{delta:+.0f}")

    with col5:
        val = latest.get('S&P500', 0)
        delta = val - prev.get('S&P500', val) if pd.notna(val) else 0
        st.metric("S&P500", f"{val:,.0f}" if pd.notna(val) else "N/A", f"{delta:+.0f}")

    with col6:
        val = latest.get('WTI유가', 0)
        delta = val - prev.get('WTI유가', val) if pd.notna(val) else 0
        st.metric("WTI유가", f"${val:.1f}" if pd.notna(val) else "N/A", f"{delta:+.1f}")

    st.markdown("---")

    # ============ 차트 탭 ============
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "💰 금리", "💱 환율", "📈 주가", "🛢️ 원자재", "📊 경제지표", "😱 공포지표"
    ])

    # 금리 탭
    with tab1:
        col1, col2 = st.columns(2)

        with col1:
            st.plotly_chart(create_rate_spread_chart(df), use_container_width=True)

        with col2:
            st.plotly_chart(
                create_multi_line_chart(
                    df, ['국고채3년', '국고채10년', '미국2년금리', '미국10년금리'],
                    '한미 국채금리 비교', '금리 (%)'
                ),
                use_container_width=True
            )

        # 장단기 스프레드
        st.plotly_chart(
            create_dual_axis_chart(
                df, '한국장단기스프레드', '미국장단기스프레드',
                '장단기 금리 스프레드 (10년-2/3년)', '한국 (%p)', '미국 (%p)'
            ),
            use_container_width=True
        )

        # 금리 해석
        rate_diff = latest.get('한미금리차', 0)
        if pd.notna(rate_diff):
            if rate_diff < -1.5:
                st.error("🚨 금리차 역전폭 확대 (-1.5%p 이상) - 자본유출 압력 심화, 원화 약세 지속 우려")
            elif rate_diff < 0:
                st.warning("⚠️ 금리차 역전 중 - 외국인 자금 유출 가능성, 환율 상승 압력")
            else:
                st.success("✅ 금리차 정상 - 자본유입 우호적 환경")

    # 환율 탭
    with tab2:
        col1, col2 = st.columns(2)

        with col1:
            usd_col = '원달러환율' if '원달러환율' in df.columns else '원달러환율종가'
            st.plotly_chart(
                create_dual_axis_chart(
                    df, usd_col, '달러인덱스',
                    '원/달러 환율 vs 달러인덱스', '원/달러 (KRW)', '달러인덱스 (DXY)'
                ),
                use_container_width=True
            )

        with col2:
            st.plotly_chart(
                create_multi_line_chart(
                    df, ['엔달러환율', '유로달러환율'],
                    '주요 통화 환율', '환율'
                ),
                use_container_width=True
            )

        # 환율 vs 금리차
        usd_col = '원달러환율' if '원달러환율' in df.columns else '원달러환율종가'
        st.plotly_chart(
            create_dual_axis_chart(
                df, usd_col, '한미금리차',
                '원/달러 환율 vs 한미금리차 (상관관계)', '원/달러', '금리차 (%p)',
                '#3498DB', '#E74C3C'
            ),
            use_container_width=True
        )

    # 주가 탭
    with tab3:
        col1, col2 = st.columns(2)

        with col1:
            st.plotly_chart(
                create_dual_axis_chart(
                    df, 'KOSPI', 'S&P500',
                    'KOSPI vs S&P500', 'KOSPI', 'S&P500',
                    '#E74C3C', '#3498DB'
                ),
                use_container_width=True
            )

        with col2:
            st.plotly_chart(
                create_dual_axis_chart(
                    df, '나스닥', 'VIX',
                    '나스닥 vs VIX', '나스닥', 'VIX',
                    '#9B59B6', '#E67E22'
                ),
                use_container_width=True
            )

        # 주가 vs 금리
        st.plotly_chart(
            create_dual_axis_chart(
                df, 'S&P500', '미국10년금리',
                'S&P500 vs 미국 10년 국채금리', 'S&P500', '금리 (%)',
                '#2ECC71', '#E74C3C'
            ),
            use_container_width=True
        )

    # 원자재 탭
    with tab4:
        col1, col2 = st.columns(2)

        with col1:
            st.plotly_chart(
                create_dual_axis_chart(
                    df, '금시세', '달러인덱스',
                    '금 가격 vs 달러인덱스 (역상관)', '금 ($/oz)', '달러인덱스',
                    '#F1C40F', '#3498DB'
                ),
                use_container_width=True
            )

        with col2:
            st.plotly_chart(
                create_dual_axis_chart(
                    df, 'WTI유가', 'S&P500',
                    'WTI 유가 vs S&P500', 'WTI ($/배럴)', 'S&P500',
                    '#1ABC9C', '#E74C3C'
                ),
                use_container_width=True
            )

    # 경제지표 탭
    with tab5:
        col1, col2 = st.columns(2)

        with col1:
            st.plotly_chart(
                create_dual_axis_chart(
                    df, '한국CPI_YoY', '미국CPI_YoY',
                    '소비자물가 상승률 (YoY)', '한국 CPI (%)', '미국 CPI (%)',
                    '#FF6B6B', '#4ECDC4'
                ),
                use_container_width=True
            )

        with col2:
            st.plotly_chart(
                create_dual_axis_chart(
                    df, '미국실업률', '미국기준금리',
                    '미국 실업률 vs 기준금리', '실업률 (%)', '기준금리 (%)',
                    '#9B59B6', '#3498DB'
                ),
                use_container_width=True
            )

        # 외환보유액 & 경상수지
        st.plotly_chart(
            create_dual_axis_chart(
                df, '외환보유액', '경상수지',
                '한국 외환보유액 vs 경상수지', '외환보유액 (백만$)', '경상수지 (백만$)',
                '#1ABC9C', '#E67E22'
            ),
            use_container_width=True
        )

    # 공포지표 탭
    with tab6:
        col1, col2 = st.columns([1, 2])

        with col1:
            vix_val = latest.get('VIX', 20)
            if pd.notna(vix_val):
                st.plotly_chart(create_fear_gauge(vix_val), use_container_width=True)

                if vix_val > 35:
                    st.error("🔴 극심한 공포 - 시장 패닉 상태")
                elif vix_val > 25:
                    st.warning("🟠 높은 불안 - 조정 가능성")
                elif vix_val > 15:
                    st.info("🟡 보통 수준 - 정상 범위")
                else:
                    st.success("🟢 낙관적 - 과열 주의")

        with col2:
            st.plotly_chart(
                create_multi_line_chart(
                    df, ['VIX', '하이일드스프레드', 'TED스프레드'],
                    '공포/위험 지표 추이', '지수/스프레드'
                ),
                use_container_width=True
            )

        # 유동성 지표
        st.plotly_chart(
            create_dual_axis_chart(
                df, '연준총자산', 'S&P500',
                '연준 총자산 vs S&P500 (유동성 효과)', '연준자산 (백만$)', 'S&P500',
                '#9B59B6', '#2ECC71'
            ),
            use_container_width=True
        )

    st.markdown("---")

    # 데이터 테이블
    with st.expander("📋 전체 데이터 보기"):
        # 컬럼 선택
        all_cols = [c for c in df.columns if c != 'date']
        selected_cols = st.multiselect("표시할 컬럼 선택", all_cols, default=all_cols[:10])

        if selected_cols:
            display_df = df[['date'] + selected_cols].copy()
            display_df['date'] = display_df['date'].dt.strftime('%Y-%m')
            st.dataframe(display_df.round(2), use_container_width=True, height=400)

            # 다운로드
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 전체 데이터 CSV 다운로드", csv, "finance_data.csv", "text/csv")

    # 푸터
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: gray; font-size: 12px;'>
        📊 데이터 출처: 한국은행 ECOS, 미국 연준 FRED |
        ⏰ 데이터는 1시간 캐시됨 |
        Made with Streamlit
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
