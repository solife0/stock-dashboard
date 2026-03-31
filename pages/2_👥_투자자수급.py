import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import FinanceDataReader as fdr
import requests
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


def get_investor_data(code: str, start: str, end: str) -> pd.DataFrame:
    """KRX 정보데이터시스템 투자자별 거래실적 조회"""
    url = "http://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "http://data.krx.co.kr/",
    }
    params = {
        "bld": "dbms/MDC/STAT/standard/MDCSTAT02302",
        "locale": "ko_KR",
        "isuCd": code,
        "isuCd2": "",
        "strtDd": start,
        "endDd": end,
        "connxSeqs": "2",
        "share": "1",
        "money": "1",
        "csvxls_isNo": "false",
    }
    resp = requests.post(url, data=params, headers=headers, timeout=10)
    data = resp.json()
    rows = data.get("output", [])
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    df = df.rename(columns={
        "TRD_DD": "날짜",
        "INST_NETBID_TRDVOL": "기관",
        "FRGN_NETBID_TRDVOL": "외국인",
        "INDIV_NETBID_TRDVOL": "개인",
    })
    df["날짜"] = pd.to_datetime(df["날짜"], format="%Y/%m/%d")
    for col in ["기관", "외국인", "개인"]:
        if col in df.columns:
            df[col] = df[col].str.replace(",", "").str.replace("-", "0").astype(float)
    df = df.set_index("날짜").sort_index()
    return df[["기관", "외국인", "개인"]]


if st.button("조회", type="primary"):
    if not ticker_input:
        st.warning("종목명 또는 종목코드를 입력하세요.")
    else:
        with st.spinner("데이터 불러오는 중..."):
            try:
                end = datetime.today()
                start = end - timedelta(days=period_map[period])

                # 종목코드 조회
                listing = fdr.StockListing("KRX")
                if ticker_input.isdigit():
                    code = ticker_input.zfill(6)
                    row = listing[listing["Code"] == code]
                    name = row["Name"].values[0] if len(row) > 0 else code
                else:
                    row = listing[listing["Name"] == ticker_input]
                    if len(row) == 0:
                        st.error("종목을 찾을 수 없습니다.")
                        st.stop()
                    code = row["Code"].values[0]
                    name = ticker_input

                df = get_investor_data(
                    code,
                    start.strftime("%Y%m%d"),
                    end.strftime("%Y%m%d")
                )

                if df.empty:
                    st.warning("투자자 수급 데이터를 가져올 수 없습니다.")
                else:
                    fig = go.Figure()
                    fig.add_trace(go.Bar(x=df.index, y=df["기관"], name="기관", marker_color="steelblue"))
                    fig.add_trace(go.Bar(x=df.index, y=df["외국인"], name="외국인", marker_color="#ef5350"))
                    fig.add_trace(go.Bar(x=df.index, y=df["개인"], name="개인", marker_color="#26a69a"))
                    fig.update_layout(
                        title=f"{name} ({code}) 투자자별 순매수",
                        barmode="group",
                        xaxis_title="날짜",
                        yaxis_title="거래량",
                        height=500
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    st.dataframe(df.tail(20), use_container_width=True)

            except Exception as e:
                st.error(f"오류 발생: {e}")
