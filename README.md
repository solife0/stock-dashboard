# 📈 KRX 주식 분석 대시보드

KRX(한국거래소) 데이터를 활용한 주식 분석 웹 대시보드입니다.  
Streamlit Cloud에 무료 배포하여 PC/모바일 어디서나 접속할 수 있습니다.

## 주요 기능

- 📊 **종가 차트** — 일별 / 주별 / 월별 종가, 라인·캔들스틱 전환
- 👥 **투자자 수급** — 기관 / 외국인 / 개인 순매수 막대·라인 차트
- 🔀 **종목 비교** — 여러 종목 수익률 비교

## 로컬 실행 방법

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Streamlit Cloud 배포 방법

1. 이 저장소를 GitHub에 Push
2. [share.streamlit.io](https://share.streamlit.io) 접속
3. 저장소 선택 → `app.py` 선택 → Deploy
