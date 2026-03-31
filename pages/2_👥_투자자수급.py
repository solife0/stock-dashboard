import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pykrx import stock
from datetime import datetime, timedelta

st.set_page_config(page_title="투자자 수급", page_icon="👥", layout="wide")

st.title("👥 투자자 수급")
st.markdown("---")

col1, col2 = st.columns([2, 1])

with col1:
    ticker_input = st.text_input("종목명 또는 종목코드", placeholder="예: 삼성전자 또는 005930")

with col2:
    period = st.selectbox("조회 기간", ["1개월", "3개월", "6개월", "1년"])

period_map = {"1개월": 30, "3개월": 90, "6개월": 180, "1년": 365}

if st.button("조회", type="primary"):
    if not ticker_input:
        st.warning("종목명 또는 종목코드를 입력하세요.")
    else:
        with st.spinner("데이터 불러오는 중..."):
            try:
                end = datetime.today()
                start = end - timedelta(days=period_map[period])
                start_str = start.strftime("%Y%m%d")
                end_str = end.strftime("%Y%m%d")

                if ticker_input.isdigit():
                    code = ticker_input.zfill(6)
                    name = stock.get_market_ticker_name(code)
                else:
                    tickers = stock.get_market_ticker_list()
                    code = None
                    for t in tickers:
                        if stock.get_market_ticker_name(t) == ticker_input:
                            code = t
                            name = ticker_input
                            break
                    if not code:
                        st.error("종목을 찾을 수 없습니다.")
                        st.stop()

                df = stock.get_market_trading_volume_by_date(start_str, end_str, code)

                fig = go.Figure()
                fig.add_trace(go.Bar(x=df.index, y=df["기관합계"], name="기관", marker_color="blue"))
                fig.add_trace(go.Bar(x=df.index, y=df["외국인합계"], name="외국인", marker_color="red"))
                fig.add_trace(go.Bar(x=df.index, y=df["개인"], name="개인", marker_color="green"))
                fig.update_layout(
                    title=f"{name} ({code}) 투자자별 순매수",
                    barmode="group",
                    xaxis_title="날짜",
                    yaxis_title="거래량",
                    height=500
                )
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(df[["기관합계", "외국인합계", "개인"]].tail(20), use_container_width=True)

            except Exception as e:
                st.error(f"오류 발생: {e}")