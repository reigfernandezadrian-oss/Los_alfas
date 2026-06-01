import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from helpers import (
    DARK_CSS, load_data, calculate_stock_stats, calculate_index_price,
    create_graph, render_stock_detail
)

st.set_page_config(
    page_title="S&P 500 - Viltrum",
    page_icon="🇺🇸",
    layout="wide",
    initial_sidebar_state="collapsed"
)
st.markdown(DARK_CSS, unsafe_allow_html=True)

sp500_data, ibex35_data, news_data = load_data()
sp500_stats = calculate_stock_stats(sp500_data)
all_stats = {**sp500_stats, **calculate_stock_stats(ibex35_data)}

if 'sp500_stock' not in st.session_state:
    st.session_state.sp500_stock = None

if st.session_state.sp500_stock:
    symbol = st.session_state.sp500_stock
    if st.button("← Volver al S&P 500", key="back_sp500"):
        st.session_state.sp500_stock = None
        st.rerun()
    render_stock_detail(symbol, sp500_data, ibex35_data, news_data, all_stats)
    st.stop()

if st.button("← Inicio", key="back_main_sp500"):
    st.switch_page("Inicio.py")

points, percent = calculate_index_price(sp500_data)
percent_color = "#00ff00" if percent >= 0 else "#ff4444"
sign = "+" if percent >= 0 else ""

st.markdown(f"""
<div style='background: #001a33; padding: 25px; border-radius: 10px; border-top: 3px solid #00aaff; margin-bottom: 20px;'>
    <div style='display: flex; align-items: center; gap: 12px;'>
        <h1 style='color: white; margin: 0; font-size: 44px;'>🇺🇸 S&P 500</h1>
        <div style='color: {percent_color}; font-size: 22px; font-weight: bold;'>{sign}{percent:.2f}%</div>
    </div>
    <div style='color: #8899ac; font-size: 14px; margin-top: 6px;'>Standard & Poor's 500 — {len(sp500_data)} empresas</div>
</div>
""", unsafe_allow_html=True)

if points:
    fig = create_graph(points)
    fig.update_layout(height=350)
    st.plotly_chart(fig, use_container_width=True)

st.markdown("<h2 style='color: white; margin-top: 30px;'>Empresas del Índice</h2>", unsafe_allow_html=True)

search = st.text_input("", placeholder="Buscar símbolo...", label_visibility="collapsed", key="sp500_search")

hcols = st.columns([2, 2, 2, 2, 1])
for col, label in zip(hcols, ["Símbolo", "Precio", "Cambio %", "Volumen", ""]):
    col.markdown(
        f"<span style='color: #8899ac; font-size: 12px; text-transform: uppercase; font-weight: bold;'>{label}</span>",
        unsafe_allow_html=True
    )
st.markdown("<hr style='border: 1px solid #2c3f57; margin: 5px 0;'>", unsafe_allow_html=True)

filtered = {k: v for k, v in sp500_stats.items() if search.upper() in k} if search else sp500_stats

for symbol in sorted(filtered.keys()):
    s = filtered[symbol]
    pct = s['percent_change']
    c = '#00c853' if pct >= 0 else '#d32f2f'
    row = st.columns([2, 2, 2, 2, 1])
    row[0].markdown(f"<span style='color: white; font-weight: bold;'>{symbol}</span>", unsafe_allow_html=True)
    row[1].markdown(f"<span style='color: white;'>${s['latest_close']:,.2f}</span>", unsafe_allow_html=True)
    row[2].markdown(f"<span style='color: {c}; font-weight: bold;'>{pct:+.2f}%</span>", unsafe_allow_html=True)
    row[3].markdown(f"<span style='color: #8899ac;'>{s['volume']:,}</span>", unsafe_allow_html=True)
    if row[4].button("→", key=f"sp500_{symbol}"):
        st.session_state.sp500_stock = symbol
        st.rerun()
