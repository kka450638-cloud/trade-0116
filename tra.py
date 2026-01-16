import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# 1. 페이지 설정
st.set_page_config(page_title="TradeOps Hub - 무역 통합 관리", layout="wide")

# 2. 데이터 초기화 (Session State)
if 'hs_df' not in st.session_state:
    st.session_state.hs_df = pd.DataFrame({
        "품명": ["전기전자제품", "의류(면)", "원두커피", "정밀기계"],
        "HS Code": ["8517.13.0000", "6109.10.0000", "0901.11.0000", "8479.89.0000"],
        "기본세율": ["0%", "13%", "2%", "0%"],
        "비고": ["-", "FTA 적용시 0%", "검역대상", "밀봉포장"]
    })

if 'exchange_rates' not in st.session_state:
    st.session_state.exchange_rates = {"USD": 1352.4, "EUR": 1465.2, "JPY": 9.12, "CNY": 188.5}

# 결과 시각화 함수
def display_trade_result(title, value, sub_text, color):
    st.markdown(f"""
        <div style="
            background-color: #ffffff;
            padding: 25px;
            border-radius: 15px;
            border-top: 8px solid {color};
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            text-align: center;
            margin-bottom: 20px;
        ">
            <h4 style="color: #555; margin-bottom: 10px; font-weight: 600;">{title}</h4>
            <h1 style="color: {color}; margin: 0; font-size: 2.2em; font-weight: 800;">{value}</h1>
            <p style="color: #888; margin-top: 10px; font-size: 0.9em;">{sub_text}</p>
        </div>
    """, unsafe_allow_html=True)

# 3. 사이드바 메뉴
with st.sidebar:
    st.title("🌐 TradeOps Hub")
    st.markdown("---")
    menu = st.radio("업무 카테고리", ["🚢 수입 원가 계산기", "📋 HS Code 관리", "💹 환율 설정 및 동향", "📦 선적 체크리스트"])
    st.markdown("---")
    st.write("📌 **현재 적용 환율**")
    for curr, rate in st.session_state.exchange_rates.items():
        st.caption(f"{curr}: {rate:,.2f} ₩")

# --- [메뉴 1] 수입 원가 계산기 ---
if menu == "🚢 수입 원가 계산기":
    st.header("🚢 수입 물품 원가 시뮬레이션")
    
    col_in1, col_in2 = st.columns(2)
    with col_in1:
        st.subheader("1. 송장 정보 (Invoice)")
        currency = st.selectbox("결제 통화", ["USD", "EUR", "JPY", "CNY"])
        default_rate = float(st.session_state.exchange_rates.get(currency, 1300.0))
        ex_rate = st.number_input(f"{currency} 적용 환율 (₩)", value=default_rate, step=0.1, format="%.2f")
        invoice_value = st.number_input("송장 총액 (외화)", value=10000.0, step=100.0)
        shipping_intl = st.number_input("국제 운송비 (외화)", value=500.0)

    with col_in2:
        st.subheader("2. 세금 및 부대비용")
        duty_rate = st.number_input("관세율 (%)", value=8.0, step=0.1)
        insurance = st.number_input("보험료 (₩)", value=50000)
        handling_fee = st.number_input("통관/내륙운송비 (₩)", value=250000)

    # 계산 로직
    cif_value_krw = (invoice_value + shipping_intl) * ex_rate + insurance
    duty_amount = cif_value_krw * (duty_rate / 100)
    vat_amount = (cif_value_krw + duty_amount) * 0.1
    total_cost = cif_value_krw + duty_amount + vat_amount + handling_fee

    st.markdown("### 📊 수입 비용 분석 결과")
    res_col1, res_col2, res_col3, res_col4 = st.columns(4)
    with res_col1: display_trade_result("과세가격 (CIF)", f"₩{cif_value_krw:,.0f}", "원화 환산액", "#2C3E50")
    with res_col2: display_trade_result("납부 관세", f"₩{duty_amount:,.0f}", f"세율 {duty_rate}%", "#E74C3C")
    with res_col3: display_trade_result("납부 부가세", f"₩{vat_amount:,.0f}", "세율 10%", "#F39C12")
    with res_col4: display_trade_result("최종 총 원가", f"₩{total_cost:,.0f}", "현금지출 총액", "#27AE60")

# --- [메뉴 2] HS Code 관리 ---
elif menu == "📋 HS Code 관리":
    st.header("📋 품목별 HS Code 및 세율 DB")
    edited_df = st.data_editor(st.session_state.hs_df, num_rows="dynamic", use_container_width=True)
    if st.button("💾 변경사항 저장"):
        st.session_state.hs_df = edited_df
        st.success("데이터베이스 업데이트 완료")

# --- [메뉴 3] 환율 설정 및 동향 (스케일 이슈 해결) ---
elif menu == "💹 환율 설정 및 동향":
    st.header("💹 시스템 환율 관리 및 트렌드")
    
    # 1. 환율 수정 섹션
    up_col1, up_col2, up_col3, up_col4 = st.columns(4)
    with up_col1: new_usd = st.number_input("USD (달러)", value=st.session_state.exchange_rates["USD"], step=0.1)
    with up_col2: new_eur = st.number_input("EUR (유로)", value=st.session_state.exchange_rates["EUR"], step=0.1)
    with up_col3: new_jpy = st.number_input("JPY (엔/1)", value=st.session_state.exchange_rates["JPY"], step=0.01)
    with up_col4: new_cny = st.number_input("CNY (위안)", value=st.session_state.exchange_rates["CNY"], step=0.1)

    if st.button("✅ 환율 일괄 업데이트"):
        st.session_state.exchange_rates.update({"USD": new_usd, "EUR": new_eur, "JPY": new_jpy, "CNY": new_cny})
        st.success("환율이 시스템에 적용되었습니다.")

    # 2. 역동적인 그래프 (탭으로 분리하여 엔화/위안화 가시성 확보)
    st.markdown("---")
    st.subheader("📈 최근 30일 환율 변동 추이 (시뮬레이션)")
    
    dates = pd.date_range(end=datetime.now(), periods=30)
    np.random.seed(42)
    def get_trend(base, vol): return base * (1 + np.cumsum(np.random.normal(0, vol, 30)))

    tab1, tab2 = st.tabs(["🇺🇸🇪🇺 USD / EUR", "🇯🇵🇨🇳 JPY / CNY"])
    
    with tab1:
        df_big = pd.DataFrame({'Date': dates, 'USD': get_trend(new_usd, 0.005), 'EUR': get_trend(new_eur, 0.004)}).set_index('Date')
        st.line_chart(df_big)
    with tab2:
        df_small = pd.DataFrame({'Date': dates, 'JPY': get_trend(new_jpy, 0.006), 'CNY': get_trend(new_cny, 0.005)}).set_index('Date')
        st.line_chart(df_small, color=["#FF5733", "#33FF57"])
# --- [메뉴 4] 선적 체크리스트 ---
elif menu == "📦 선적 체크리스트":
    st.header("📦 선적 서류 점검 리스트")
    col1, col2 = st.columns(2)
    with col1:
        st.checkbox("Invoice (상업송장)")
        st.checkbox("Packing List (포장명세서)")
        st.checkbox("B/L (선하증권)")
    with col2:
        st.checkbox("C/O (원산지증명서)")
        st.checkbox("보험증권")