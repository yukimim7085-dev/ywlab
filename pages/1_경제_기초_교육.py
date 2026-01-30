"""
경제 기초 교육 페이지
주식 입문자를 위한 기초 경제 교육 자료
"""

import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path

# 페이지 설정 - 와이드 레이아웃
st.set_page_config(
    page_title="경제 기초 교육",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS 스타일
st.markdown("""
<style>
    .main .block-container {
        padding-top: 1rem;
        padding-left: 1rem;
        padding-right: 1rem;
        max-width: 100%;
    }
    iframe {
        border: none;
    }
</style>
""", unsafe_allow_html=True)

# 상단 제목
st.markdown("## 📚 주식 입문자를 위한 경제 기초 교육")
st.caption("경제 기초부터 자산배분 전략까지 한 번에 배우는 투자 가이드")
st.divider()

# HTML 파일 로드 및 표시
try:
    # 현재 파일 기준으로 상위 폴더의 HTML 파일 찾기
    current_dir = Path(__file__).parent.parent
    html_file_path = current_dir / "주식_기초_교육자료_최종판.html"

    with open(html_file_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    # 전체 화면으로 HTML 표시
    components.html(html_content, height=2000, scrolling=True)

except FileNotFoundError:
    st.error("❌ 교육 자료 파일을 찾을 수 없습니다.")
    st.info("📁 '주식_기초_교육자료_최종판.html' 파일이 필요합니다.")
except Exception as e:
    st.error(f"❌ 오류 발생: {str(e)}")
