import streamlit as st

st.set_page_config(
    page_title="주식 대시보드",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("📈 KRX 주식 분석 대시보드")
st.markdown("---")

st.markdown("""
### 사용 방법
1. 왼쪽 메뉴에서 원하는 분석 화면을 선택하세요
2. 종목명 또는 종목코드를 입력하세요
3. 조회 기간을 설정하고 **조회** 버튼을 누르세요

### 제공 기능
| 메뉴 | 설명 |
|------|------|
| 📊 종가 차트 | 일별 / 주별 / 월별 종가 추이 |
| 👥 투자자 수급 | 기관·외국인·개인 순매수 현황 |
| 🔀 종목 비교 | 여러 종목 동시 비교 |
""")

st.info("💡 즐겨찾기에 종목을 추가하면 빠르게 조회할 수 있어요.")

# 즐겨찾기 초기화
if "favorites" not in st.session_state:
    st.session_state.favorites = [
        {"code": "005930", "name": "삼성전자"},
        {"code": "000660", "name": "SK하이닉스"},
        {"code": "035420", "name": "NAVER"},
    ]
