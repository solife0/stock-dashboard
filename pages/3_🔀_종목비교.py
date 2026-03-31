import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pykrx import stock
from datetime import datetime, timedelta

st.set_page_config(page_title="종목 비교", page_icon="🔀", layout="wide")

st.title("🔀 종목 비교")
st.markdown("---")

col1, col2 = st.columns([3, 1])

with col1:
    tickers_input = st.text_input(
        "종목명 또는 종목코드 (쉼표로 구분)",
        placeholder="예: 삼성전자, SK하이닉스, NAVER"
    )

with col2:
    period = st.selectbox("조회 기간", ["1개월", "3개월", "6개월", "1년", "3년"])

period_map = {"1개월": 30, "3개월": 90, "6개월": 180, "1년": 365, "3년": 1095}

if st.button("조회", type="primary"):
    if not tickers_input:
        st.warning("종목명 또는 종목코드를 입력하세요.")
    else:
        with st.spinner("데이터 불러오는 중..."):
            try:
                end = datetime.today()
                start = end - timedelta(days=period_map[period])
                start_str = start.strftime("%Y%m%d")
                end_str = end.strftime("%Y%m%d")

                items = [x.strip() for x in tickers_input.split(",")]
                fig = go.Figure()

                for item in items:
                    if item.isdigit():
                        code = item.zfill(6)
                        name = stock.get_market_ticker_name(code)
                    else:
                        tickers = stock.get_market_ticker_list()
                        code = None
                        for t in tickers:
                            if stock.get_market_ticker_name(t) == item:
                                code = t
                                name = item
                                break
                        if not code:
                            st.warning(f"'{item}' 종목을 찾을 수 없습니다. 건너뜁니다.")
                            continue

                    df = stock.get_market_ohlcv_by_date(start_str, end_str, code)
                    # 첫날 기준 정규화 (100 기준)
                    normalized = df["종가"] / df["종가"].iloc[0] * 100

                    fig.add_trace(go.Scatter(
                        x=df.index,
                        y=normalized,
                        mode="lines",
                        name=f"{name} ({code})"
                    ))

                fig.update_layout(
                    title="종목 비교 (첫날 기준 정규화)",
                    xaxis_title="날짜",
                    yaxis_title="상대 수익률 (기준: 100)",
                    height=500
                )
                st.plotly_chart(fig, use_container_width=True)

            except Exception as e:
                st.error(f"오류 발생: {e}")