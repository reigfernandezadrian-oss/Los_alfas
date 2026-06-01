import json
import os
import streamlit as st
import plotly.graph_objects as go
from collections import defaultdict

DARK_CSS = """
<style>
    .main { background-color: #0b1726; color: white; }
    .stApp { background-color: #0b1726; color: white; }
    .stButton button {
        border-radius: 50% !important;
        width: 40px !important; height: 40px !important;
        min-width: 40px !important; min-height: 40px !important;
        display: flex !important; align-items: center !important;
        justify-content: center !important; padding: 0 !important;
        font-size: 20px !important; line-height: 1 !important;
        background-color: transparent !important; color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
    }
    .stButton button:hover {
        background-color: rgba(0, 170, 255, 0.2) !important;
        border-color: #00aaff !important; color: #00aaff !important;
    }
    .stButton button:focus { box-shadow: none !important; color: white !important; }
    .stTextInput input {
        background-color: #12243a !important; color: white !important;
        border: 1px solid #2c3f57 !important; border-radius: 6px !important;
    }
    div[data-testid="column"] .stButton button {
        border-radius: 8px !important; width: 100% !important;
        height: 35px !important; font-size: 14px !important;
    }
</style>
"""


def _find_key_with_fragment(mapping, fragment):
    return next((k for k in mapping if fragment in k), None)


def _safe_percent_change(first_value, latest_value):
    if first_value == 0:
        return 0
    return ((latest_value - first_value) / first_value) * 100


@st.cache_data
def load_data():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)

    sp500_path = os.path.join(parent_dir, 'data', 'json_sp500.json')
    ibex35_path = os.path.join(parent_dir, 'data', 'json_ibex35.json')
    news_path = os.path.join(parent_dir, 'data', 'Tickets.json')

    with open(sp500_path, 'r') as f:
        sp500_data = json.load(f)
    with open(ibex35_path, 'r') as f:
        ibex35_data = json.load(f)
    try:
        with open(news_path, 'r', encoding='utf-8') as f:
            news_data = json.load(f)
    except Exception:
        news_data = {}

    return sp500_data, ibex35_data, news_data


def get_sentiment_style(sentiment_label):
    sentiments = {
        "positivo": {"color": "#00ff00", "icon": "🟢", "bg": "rgba(0, 255, 0, 0.1)"},
        "negativo": {"color": "#ff4444", "icon": "🔴", "bg": "rgba(255, 68, 68, 0.1)"},
        "neutral":  {"color": "#8899ac", "icon": "⚪", "bg": "rgba(136, 153, 172, 0.1)"}
    }
    return sentiments.get(sentiment_label.lower(), sentiments["neutral"])


def calculate_stock_stats(data_dict):
    stock_stats = {}
    for symbol, data in data_dict.items():
        try:
            if len(data) >= 2:
                latest = data[-1]
                earliest = data[0]
                latest_close_key = _find_key_with_fragment(latest, 'Close')
                earliest_close_key = _find_key_with_fragment(earliest, 'Close')
                volume_key = _find_key_with_fragment(latest, 'Volume')
                if latest_close_key and earliest_close_key and volume_key:
                    stock_stats[symbol] = {
                        'latest_close': latest[latest_close_key],
                        'percent_change': _safe_percent_change(earliest[earliest_close_key], latest[latest_close_key]),
                        'volume': latest[volume_key]
                    }
        except (KeyError, IndexError, TypeError):
            continue
    return stock_stats


def sort_stocks_by_value(stock_stats):
    return sorted(stock_stats.items(), key=lambda x: (-x[1]['volume'], -x[1]['latest_close']))


def calculate_index_price(data_dict):
    date_prices = defaultdict(list)
    try:
        for symbol, data in data_dict.items():
            for entry in data:
                date = entry.get("('Date', '')")
                close_key = _find_key_with_fragment(entry, 'Close')
                if close_key and date:
                    date_prices[date].append(entry[close_key])

        avg_prices = {date: sum(prices) / len(prices) for date, prices in date_prices.items() if prices}
        sorted_data = sorted(avg_prices.items())

        if len(sorted_data) >= 2:
            percent_change = _safe_percent_change(sorted_data[0][1], sorted_data[-1][1])
        else:
            percent_change = 0

        return sorted_data, percent_change
    except Exception:
        return [], 0


def create_graph(data_points):
    if not data_points:
        return go.Figure()
    try:
        dates = [p[0] for p in data_points]
        prices = [p[1] for p in data_points]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=dates, y=prices, mode='lines', name='Price', line=dict(color='#00aaff')))
        fig.update_layout(
            xaxis_title="Date", yaxis_title="Price",
            template='plotly_dark',
            paper_bgcolor='#0b1726', plot_bgcolor='#0b1726',
            height=300, margin=dict(l=10, r=10, t=10, b=10)
        )
        return fig
    except Exception as e:
        st.error(f"Error generando gráfica: {e}")
        return go.Figure()


def get_stock_history(symbol, sp500_data, ibex35_data):
    data = sp500_data.get(symbol) or ibex35_data.get(symbol)
    if not data:
        return []
    points = []
    for entry in data:
        date = entry.get("('Date', '')")
        close_key = _find_key_with_fragment(entry, 'Close')
        if date and close_key:
            points.append((date, entry[close_key]))
    return sorted(points)


def get_recommendation(symbol, sp500_data, ibex35_data):
    history = get_stock_history(symbol, sp500_data, ibex35_data)
    if len(history) < 5:
        return "NEUTRAL", "Faltan datos", "#8899ac"
    latest_price = history[-1][1]
    avg_5 = sum(p[1] for p in history[-5:]) / 5
    if latest_price > avg_5 * 1.02:
        return "COMPRAR", "Tendencia Alcista Fuerte", "#00c853"
    elif latest_price < avg_5 * 0.98:
        return "VENDER", "Tendencia Bajista Detectada", "#d32f2f"
    else:
        return "MANTENER", "Estabilidad de precio", "#ffab00"


def render_news_section(symbol, news_dict):
    data = news_dict.get(symbol)
    if not data:
        return
    noticias = data if isinstance(data, list) else [data]
    for noticia in noticias:
        title = noticia.get('title', 'Sin título')
        link = noticia.get('link', '#')
        publisher = noticia.get('publisher', 'Noticias')
        sentiment_label = noticia.get('sentiment', 'neutral')
        reason = noticia.get('reason', '')
        style = get_sentiment_style(sentiment_label)
        reason_html = f"<div style='color: #00aaff; font-size: 13px; margin-top: 6px;'>{reason}</div>" if reason else ""
        st.markdown(f"""
        <div style="background-color: #12243a; padding: 15px; border-radius: 10px; border-left: 4px solid {style['color']}; margin-bottom: 10px; display: flex; flex-direction: column; justify-content: space-between;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                <p style="color: #8899ac; font-size: 11px; margin: 0; text-transform: uppercase;">{publisher} • {symbol}</p>
                <span style="font-size: 12px; background-color: {style['bg']}; color: {style['color']}; padding: 2px 8px; border-radius: 10px; font-weight: bold;">
                    {style['icon']} {sentiment_label.upper()}
                </span>
            </div>
            <a href="{link}" target="_blank" style="color: white; text-decoration: none; font-weight: bold; font-size: 14px; line-height: 1.2;">{title}</a>
            {reason_html}
        </div>
        """, unsafe_allow_html=True)


def render_stock_detail(symbol, sp500_data, ibex35_data, news_data, all_stats, back_key="back_detail"):
    stats = all_stats.get(symbol, {})
    price = stats.get('latest_close', 0)
    pct = stats.get('percent_change', 0)
    vol = stats.get('volume', 0)
    color = '#00c853' if pct >= 0 else '#d32f2f'

    st.markdown(f"<h1 style='color: white; font-size: 48px;'>{symbol}</h1>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style='display: flex; gap: 20px; margin-bottom: 20px;'>
        <div style='background: #12243a; padding: 20px; border-radius: 10px; border: 1px solid #2c3f57; flex: 1; text-align: center;'>
            <div style='color: #8899ac; font-size: 12px; text-transform: uppercase;'>Precio</div>
            <div style='color: white; font-size: 28px; font-weight: bold;'>${price:,.2f}</div>
        </div>
        <div style='background: #12243a; padding: 20px; border-radius: 10px; border: 1px solid {color}; flex: 1; text-align: center;'>
            <div style='color: #8899ac; font-size: 12px; text-transform: uppercase;'>Cambio</div>
            <div style='color: {color}; font-size: 28px; font-weight: bold;'>{pct:+.2f}%</div>
        </div>
        <div style='background: #12243a; padding: 20px; border-radius: 10px; border: 1px solid #2c3f57; flex: 1; text-align: center;'>
            <div style='color: #8899ac; font-size: 12px; text-transform: uppercase;'>Volumen</div>
            <div style='color: white; font-size: 28px; font-weight: bold;'>{vol:,}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    history = get_stock_history(symbol, sp500_data, ibex35_data)
    if history:
        fig = create_graph(history)
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning(f"No hay datos históricos para {symbol}")

    rec, reason, rec_color = get_recommendation(symbol, sp500_data, ibex35_data)
    st.markdown(f"""
    <div style='background: #12243a; padding: 25px; border-radius: 12px; border: 2px solid {rec_color}; text-align: center; margin: 20px 0;'>
        <div style='color: #8899ac; font-size: 14px; text-transform: uppercase; margin-bottom: 8px;'>Señal</div>
        <div style='color: {rec_color}; font-size: 42px; font-weight: bold;'>{rec}</div>
        <div style='color: #8899ac; font-size: 16px; margin-top: 8px;'>{reason}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<h3 style='color: white;'>Última Noticia</h3>", unsafe_allow_html=True)
    render_news_section(symbol, news_data)
