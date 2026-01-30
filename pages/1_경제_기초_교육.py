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

# GitHub Pages URL
EDUCATION_URL = "https://yukimim7085-dev.github.io/finance-dashboard/education.html"

st.markdown("## 📚 주식 입문자를 위한 경제 기초 교육")
st.markdown("경제 기초부터 자산배분 전략까지 한 번에 배우는 투자 가이드")

st.divider()

# 전체 화면 보기 버튼
st.markdown(f"""
<a href="{EDUCATION_URL}" target="_blank" style="
    display: inline-block;
    background: linear-gradient(90deg, #4facfe, #00f2fe);
    color: #1a1a2e;
    padding: 16px 32px;
    border-radius: 10px;
    text-decoration: none;
    font-weight: bold;
    font-size: 1.2em;
    margin: 20px 0;
">
    🚀 전체 화면으로 보기 (새 탭)
</a>
""", unsafe_allow_html=True)

st.markdown("")
st.info("👆 버튼을 클릭하면 새 탭에서 전체 화면 교육 자료가 열립니다.")

st.divider()

# 목차 미리보기
st.markdown("### 📋 목차")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **PART 1: 경제 기초**
    - 중앙은행과 연준
    - 단리와 복리

    **PART 2: 자산 이해**
    - 안전자산 vs 위험자산
    - 경제 상황별 자산 움직임

    **PART 3: 채권과 경기사이클**
    - 채권의 기초
    - 경기사이클

    **PART 4: 환율과 세금**
    - 환율과 투자
    - 배당 투자 기초
    - 주식 세금 기초

    **PART 5: 주식 시장 이해**
    - 주요 증시 & 지수
    - 주식 용어 총정리
    """)

with col2:
    st.markdown("""
    **PART 6: 기업 분석 지표**
    - 시가총액
    - PER / PBR / ROE / EPS

    **PART 7: 기술적 분석**
    - 이동평균선 & 크로스
    - RSI / MACD / 볼린저밴드
    - 피보나치 되돌림

    **PART 8: 투자 전략**
    - ETF 투자
    - 올웨더 포트폴리오
    - 투자 전략 종합

    **PART 9~11: 심화**
    - 재무제표, 어닝 시즌
    - 공매도, IPO, 섹터 분류
    - 절세 계좌, 리스크 관리
    """)

st.divider()
st.caption("총 26개 섹션 | v5.0")
