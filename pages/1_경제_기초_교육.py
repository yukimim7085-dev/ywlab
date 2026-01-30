"""
경제 기초 교육 페이지
주식 입문자를 위한 기초 경제 교육 자료
"""

import streamlit as st
import streamlit.components.v1 as components
import os

# 페이지 설정 - 와이드 레이아웃
st.set_page_config(
    page_title="경제 기초 교육",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed"  # 사이드바 숨김
)

# 사이드바 숨기기 CSS
st.markdown("""
<style>
    [data-testid="stSidebar"] {
        display: none;
    }
    [data-testid="stSidebarNav"] {
        display: none;
    }
    .stApp > header {
        background-color: transparent;
    }
    .main .block-container {
        padding: 0;
        max-width: 100%;
    }
    iframe {
        border: none;
    }
</style>
""", unsafe_allow_html=True)

# 상단 네비게이션
col1, col2, col3 = st.columns([1, 6, 1])
with col1:
    if st.button("← 대시보드로 돌아가기"):
        st.switch_page("app.py")

# HTML 파일 로드 및 표시
html_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "주식_기초_교육자료_최종판.html")

try:
    with open(html_file_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    # 전체 화면으로 HTML 표시
    components.html(html_content, height=2000, scrolling=True)

except FileNotFoundError:
    st.error("❌ 교육 자료 파일을 찾을 수 없습니다.")
    st.info("📁 '주식_기초_교육자료_최종판.html' 파일이 필요합니다.")
