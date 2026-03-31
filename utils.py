import streamlit as st
import pandas as pd
from pykrx import stock
from datetime import datetime, timedelta


@st.cache_data(ttl=3600)
def get_ticker_list():
    """KOSPI + KOSDAQ 전체 종목 목록 반환 (캐시 1시간)"""
    try:
        kospi  = stock.get_market_ticker_list(market="KOSPI")
        kosdaq = stock.get_market_ticker_list(market="KOSDAQ")
        tickers = list(kospi) + list(kosdaq)
        name_map = {}
        for t in tickers:
            try:
                name = stock.get_market_ticker_name(t)
                name_map[name] = t
            except Exception:
                pass
        return name_map  # {"삼성전자": "005930", ...}
    except Exception as e:
        st.error(f"종목 목록 로딩 실패: {e}")
        return {}


def resolve_code(query: str, name_map: dict) -> tuple[str, str]:
    """종목명 또는 코드 입력 → (코드, 종목명) 반환"""
    query = query.strip()
    # 코드로 입력한 경우
    if query.isdigit():
        try:
            name = stock.get_market_ticker_name(query)
            return query, name
        except Exception:
            return query, query
    # 종목명으로 입력한 경우
    code = name_map.get(query)
    if code:
        return code, query
    # 부분 일치 검색
    matches = {k: v for k, v in name_map.items() if query in k}
    if matches:
        name = list(matches.keys())[0]
        return matches[name], name
    return query, query


@st.cache_data(ttl=1800)
def get_ohlcv(code: str, start: str, end: str) -> pd.DataFrame:
    """일별 OHLCV 데이터 반환 (캐시 30분)"""
    df = stock.get_market_ohlcv(start, end, code)
    df.index = pd.to_datetime(df.index)
    return df


@st.cache_data(ttl=1800)
def get_investor_data(code: str, start: str, end: str) -> pd.DataFrame:
    """투자자별 순매수 데이터 반환 (캐시 30분)"""
    df = stock.get_market_trading_value_by_investor(start, end, code)
    df.index = pd.to_datetime(df.index)
    return df


def resample_price(ohlcv: pd.DataFrame, freq: str) -> pd.Series:
    """일별 데이터를 주별/월별로 리샘플링"""
    close = ohlcv["종가"]
    if freq == "주별":
        return close.resample("W").last().dropna()
    elif freq == "월별":
        return close.resample("ME").last().dropna()
    return close


def default_dates() -> tuple:
    """기본 조회 기간: 최근 1년"""
    end   = datetime.today()
    start = end - timedelta(days=365)
    return start.date(), end.date()


def search_ui(name_map: dict, key_prefix: str = "") -> tuple[str, str]:
    """종목 검색 공통 UI 컴포넌트"""
    # 즐겨찾기 빠른 선택
    favs = st.session_state.get("favorites", [])
    if favs:
        fav_labels = ["직접 입력"] + [f["name"] for f in favs]
        selected = st.selectbox("⭐ 즐겨찾기", fav_labels, key=f"{key_prefix}_fav")
        if selected != "직접 입력":
            fav = next(f for f in favs if f["name"] == selected)
            return fav["code"], fav["name"]

    query = st.text_input(
        "종목명 또는 코드 입력",
        value="삼성전자",
        key=f"{key_prefix}_query",
        placeholder="예: 삼성전자 / 005930"
    )
    code, name = resolve_code(query, name_map)
    return code, name


def add_favorite(code: str, name: str):
    """즐겨찾기 추가"""
    if "favorites" not in st.session_state:
        st.session_state.favorites = []
    exists = any(f["code"] == code for f in st.session_state.favorites)
    if not exists:
        st.session_state.favorites.append({"code": code, "name": name})
        st.success(f"⭐ {name} 즐겨찾기 추가 완료!")
    else:
        st.info(f"{name}은 이미 즐겨찾기에 있어요.")
