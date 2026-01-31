"""
경제 기초 교육 페이지
GitHub Pages로 호스팅된 전체 화면 교육 자료로 이동
"""

import streamlit as st

# 페이지 설정
st.set_page_config(
    page_title="경제 기초 교육",
    page_icon="📚",
    layout="centered"
)

# GitHub Pages URLs
BASE_URL = "https://yukimim7085-dev.github.io/finance-dashboard/education"
FULL_URL = "https://yukimim7085-dev.github.io/finance-dashboard/education.html"

st.markdown("## 📚 주식 입문자를 위한 경제 기초 교육")
st.markdown("경제 기초부터 자산배분 전략까지 단계별로 배우는 체계적인 가이드")

st.divider()

# 주제별 학습 섹션
st.markdown("### 📖 주제별 학습")
st.markdown("원하는 주제를 선택해서 학습하세요.")

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
    <a href="{BASE_URL}/1_economics.html" target="_blank" style="
        display: block;
        background: rgba(79, 172, 254, 0.15);
        border-left: 4px solid #4facfe;
        color: #e8e8e8;
        padding: 16px;
        border-radius: 8px;
        text-decoration: none;
        margin: 8px 0;
    ">
        <strong style="color: #4facfe;">1. 경제학 기초</strong><br>
        <span style="font-size: 0.9em; color: #a0a0a0;">금리, 채권, 경기사이클</span>
    </a>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <a href="{BASE_URL}/2_assets.html" target="_blank" style="
        display: block;
        background: rgba(0, 255, 136, 0.1);
        border-left: 4px solid #00ff88;
        color: #e8e8e8;
        padding: 16px;
        border-radius: 8px;
        text-decoration: none;
        margin: 8px 0;
    ">
        <strong style="color: #00ff88;">2. 자산과 시장</strong><br>
        <span style="font-size: 0.9em; color: #a0a0a0;">자산분류, 환율, 증시</span>
    </a>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <a href="{BASE_URL}/3_stocks.html" target="_blank" style="
        display: block;
        background: rgba(254, 202, 87, 0.1);
        border-left: 4px solid #feca57;
        color: #e8e8e8;
        padding: 16px;
        border-radius: 8px;
        text-decoration: none;
        margin: 8px 0;
    ">
        <strong style="color: #feca57;">3. 주식 기초</strong><br>
        <span style="font-size: 0.9em; color: #a0a0a0;">용어, PER/PBR, 재무제표</span>
    </a>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <a href="{BASE_URL}/4_technical.html" target="_blank" style="
        display: block;
        background: rgba(255, 107, 107, 0.1);
        border-left: 4px solid #ff6b6b;
        color: #e8e8e8;
        padding: 16px;
        border-radius: 8px;
        text-decoration: none;
        margin: 8px 0;
    ">
        <strong style="color: #ff6b6b;">4. 기술적 분석</strong><br>
        <span style="font-size: 0.9em; color: #a0a0a0;">이동평균선, RSI, MACD</span>
    </a>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <a href="{BASE_URL}/5_strategy.html" target="_blank" style="
        display: block;
        background: rgba(162, 89, 255, 0.1);
        border-left: 4px solid #a259ff;
        color: #e8e8e8;
        padding: 16px;
        border-radius: 8px;
        text-decoration: none;
        margin: 8px 0;
    ">
        <strong style="color: #a259ff;">5. 투자 전략</strong><br>
        <span style="font-size: 0.9em; color: #a0a0a0;">ETF, 올웨더, 섹터분류</span>
    </a>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <a href="{BASE_URL}/6_practical.html" target="_blank" style="
        display: block;
        background: rgba(255, 159, 67, 0.1);
        border-left: 4px solid #ff9f43;
        color: #e8e8e8;
        padding: 16px;
        border-radius: 8px;
        text-decoration: none;
        margin: 8px 0;
    ">
        <strong style="color: #ff9f43;">6. 실전과 리스크</strong><br>
        <span style="font-size: 0.9em; color: #a0a0a0;">세금, IPO, 리스크관리</span>
    </a>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <a href="{BASE_URL}/7_advanced.html" target="_blank" style="
        display: block;
        background: rgba(233, 69, 96, 0.1);
        border-left: 4px solid #e94560;
        color: #e8e8e8;
        padding: 16px;
        border-radius: 8px;
        text-decoration: none;
        margin: 8px 0;
    ">
        <strong style="color: #e94560;">7. 고급 경제학</strong><br>
        <span style="font-size: 0.9em; color: #a0a0a0;">거시경제, 미시경제</span>
    </a>
    """, unsafe_allow_html=True)

st.divider()

# 전체 보기 버튼
st.markdown("### 📋 전체 보기")
col_a, col_b = st.columns(2)

with col_a:
    st.markdown(f"""
    <a href="{BASE_URL}/index.html" target="_blank" style="
        display: inline-block;
        background: linear-gradient(90deg, #4facfe, #00f2fe);
        color: #1a1a2e;
        padding: 14px 28px;
        border-radius: 10px;
        text-decoration: none;
        font-weight: bold;
        margin: 10px 0;
    ">
        📚 주제별 목차 페이지
    </a>
    """, unsafe_allow_html=True)

with col_b:
    st.markdown(f"""
    <a href="{FULL_URL}" target="_blank" style="
        display: inline-block;
        background: linear-gradient(90deg, #667eea, #764ba2);
        color: white;
        padding: 14px 28px;
        border-radius: 10px;
        text-decoration: none;
        font-weight: bold;
        margin: 10px 0;
    ">
        📖 전체 내용 한 번에 보기
    </a>
    """, unsafe_allow_html=True)

st.markdown("")
st.info("👆 원하는 주제를 선택하거나, 전체 내용을 한 번에 볼 수 있습니다.")

st.divider()
st.caption("총 33개 섹션 | 7개 주제별 페이지 | v7.0")
