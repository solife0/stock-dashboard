import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import FinanceDataReader as fdr
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
                start_str = start.strftime("%Y-%m-%d")
                end_str = end.strftime("%Y-%m-%d")

                listing = fdr.StockListing("KRX")
                name_map = dict(zip(listing["Name"], listing["Code"]))
                code_map = dict(zip(listing["Code"], listing["Name"]))

                items = [x.strip() for x in tickers_input.split(",")]
                fig = go.Figure()

                for item in items:
                    if item.isdigit():
                        code = item.zfill(6)
                        name = code_map.get(code, code)
                    else:
                        code = name_map.get(item)
                        if not code:
                            st.warning(f"'{item}' 종목을 찾을 수 없습니다. 건너뜁니다.")
                            continue
                        name = item

                    df = fdr.DataReader(code, start_str, end_str)
                    if df.empty:
                        st.warning(f"'{name}' 데이터가 없습니다.")
                        continue

                    # 첫날 기준 정규화 (100 기준)
                    close = df["Close"]
                    normalized = close / close.iloc[0] * 100

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
