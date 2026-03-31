import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.gridspec as gridspec
from matplotlib.patches import Rectangle
import matplotlib.ticker as mticker
from pykrx import stock
from datetime import datetime, timedelta

st.set_page_config(page_title="종가 차트", page_icon="📊", layout="wide")

st.title("📊 종가 차트")
st.markdown("---")

col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    ticker_input = st.text_input("종목명 또는 종목코드", placeholder="예: 삼성전자 또는 005930")

with col2:
    period = st.selectbox("조회 기간", ["1개월", "3개월", "6개월", "1년", "3년"])

with col3:
    interval = st.selectbox("주기", ["일별", "주별", "월별"])

period_map = {"1개월": 30, "3개월": 90, "6개월": 180, "1년": 365, "3년": 1095}

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

                df = stock.get_market_ohlcv_by_date(start_str, end_str, code)

                if interval == "주별":
                    df = df.resample("W").agg({
                        "시가": "first", "고가": "max",
                        "저가": "min", "종가": "last", "거래량": "sum"
                    }).dropna()
                elif interval == "월별":
                    df = df.resample("ME").agg({
                        "시가": "first", "고가": "max",
                        "저가": "min", "종가": "last", "거래량": "sum"
                    }).dropna()

                vol_colors = [
                    "#26a69a" if c >= o else "#ef5350"
                    for o, c in zip(df["시가"], df["종가"])
                ]

                dates = mdates.date2num(df.index.to_pydatetime())

                if interval == "월별":
                    major_locator = mdates.MonthLocator(interval=1)
                    date_fmt = "%Y-%m"
                elif interval == "주별":
                    major_locator = mdates.WeekdayLocator(byweekday=0, interval=1)
                    date_fmt = "%m-%d"
                else:
                    major_locator = mticker.FixedLocator(dates)
                    date_fmt = "%m-%d"

                if interval == "월별":
                    width = 15
                elif interval == "주별":
                    width = 3.5
                else:
                    width = 0.6

                # ── GridSpec: 캔들(위) / 거래량(아래) ──────────
                # hspace=0으로 완전히 붙이고
                # ax1의 bottom을 날짜 글자 높이만큼 내려서 공간 확보
                fig = plt.figure(figsize=(14, 9))
                gs = gridspec.GridSpec(
                    2, 1,
                    height_ratios=[3, 1],
                    hspace=0,           # 두 차트 간격 0
                    left=0.07, right=0.97, top=0.95, bottom=0.02
                )
                ax1 = fig.add_subplot(gs[0])
                ax2 = fig.add_subplot(gs[1], sharex=ax1)

                # ax1 하단을 날짜 공간만큼 올려서 날짜 라벨 표시 공간 확보
                # 세로 날짜(rotation=90) 높이 ≈ figure의 약 12%
                pos1 = ax1.get_position()
                pos2 = ax2.get_position()
                date_space = 0.10   # figure 비율 기준 날짜 공간

                ax1.set_position([
                    pos1.x0, pos2.y1 + date_space,
                    pos1.width, pos1.height - date_space
                ])

                # ── 캔들스틱 ─────────────────────────────────
                for date, row in zip(dates, df.itertuples()):
                    o, h, l, c = row.시가, row.고가, row.저가, row.종가
                    color = "#26a69a" if c >= o else "#ef5350"
                    ax1.plot([date, date], [l, h], color=color, linewidth=1)
                    rect = Rectangle(
                        (date - width / 2, min(o, c)),
                        width, abs(c - o),
                        facecolor=color, edgecolor=color, linewidth=0.5
                    )
                    ax1.add_patch(rect)

                ax1.set_title(f"{name} ({code}) 종가 차트", fontsize=14, loc="left", pad=10)
                ax1.set_ylabel("가격 (원)", fontsize=10)
                ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
                ax1.set_xlim(dates[0] - width * 2, dates[-1] + width * 2)
                ax1.grid(True, alpha=0.3)
                ax1.set_facecolor("white")

                # 날짜: ax1 하단에 세로로 표시
                ax1.xaxis.set_major_locator(major_locator)
                if interval == "일별":
                    ax1.xaxis.set_major_formatter(
                        mticker.FuncFormatter(
                            lambda x, _: mdates.num2date(x).strftime(date_fmt) if x > 0 else ""
                        )
                    )
                else:
                    ax1.xaxis.set_major_formatter(mdates.DateFormatter(date_fmt))

                ax1.tick_params(axis="x", labelbottom=True, labeltop=False, pad=2)
                plt.setp(ax1.xaxis.get_majorticklabels(), rotation=90, ha="center", fontsize=8)

                # ── 거래량 ────────────────────────────────────
                ax2.bar(dates, df["거래량"], width=width * 0.8, color=vol_colors, alpha=0.8)
                ax2.set_ylabel("거래량", fontsize=10)
                ax2.yaxis.set_major_formatter(
                    mticker.FuncFormatter(
                        lambda x, _: f"{x/1e6:.0f}M" if x >= 1e6 else f"{x/1e3:.0f}K"
                    )
                )
                ax2.grid(True, alpha=0.3)
                ax2.set_facecolor("white")
                # ax2 x축 날짜 라벨 숨김
                ax2.tick_params(axis="x", labelbottom=False, length=0)

                fig.patch.set_facecolor("white")
                st.pyplot(fig)
                plt.close(fig)

                st.dataframe(df.tail(20), use_container_width=True)

            except Exception as e:
                st.error(f"오류 발생: {e}")