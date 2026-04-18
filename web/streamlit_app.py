import streamlit as st
import json
import os
import plotly.graph_objects as go
from collections import defaultdict


def _find_key_with_fragment(mapping, fragment):
    """Return the first key that contains the given fragment."""
    return next((k for k in mapping if fragment in k), None)


def _safe_percent_change(first_value, latest_value):
    if first_value == 0:
        return 0
    return ((latest_value - first_value) / first_value) * 100

# Set page config
st.set_page_config(
    page_title="Viltrum Stocks",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS (simplified)
st.markdown("""
<style>
    .main {
        background-color: #0b1726;
        color: white;
    }
    .stApp {
        background-color: #0b1726;
        color: white;
    }
    .stTextInput input {
        background-color: #12243a !important;
        color: white !important;
        border: 1px solid #2c3f57 !important;
        border-radius: 6px !important;
    }
    .stButton button {
        background-color: #1a2d44 !important;
        color: white !important;
        border: 1px solid #2c3f57 !important;
        border-radius: 6px !important;
    }
</style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    # Get the parent directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)

    sp500_path = os.path.join(parent_dir, 'data', 'json_sp500.json')
    ibex35_path = os.path.join(parent_dir, 'data', 'json_ibex35.json')

    with open(sp500_path, 'r') as f:
        sp500_data = json.load(f)
    with open(ibex35_path, 'r') as f:
        ibex35_data = json.load(f)
    return sp500_data, ibex35_data

def calculate_stock_stats(data_dict):
    """Calculate latest price, percent change, and volume for each stock"""
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
                    latest_close = latest[latest_close_key]
                    earliest_close = earliest[earliest_close_key]
                    latest_volume = latest[volume_key]

                    stock_stats[symbol] = {
                        'latest_close': latest_close,
                        'percent_change': _safe_percent_change(earliest_close, latest_close),
                        'volume': latest_volume
                    }
        except (KeyError, IndexError, TypeError):
            continue

    return stock_stats

def sort_stocks_by_value(stock_stats):
    """Sort stocks by value (price) and then by volume (popularity)"""
    return sorted(stock_stats.items(), key=lambda x: (-x[1]['latest_close'], -x[1]['volume']))

def calculate_index_price(data_dict):
    """Calculate average closing price across all stocks for each date"""
    date_prices = defaultdict(list)

    try:
        for symbol, data in data_dict.items():
            for entry in data:
                date = entry.get("('Date', '')")
                close_key = _find_key_with_fragment(entry, 'Close')
                if close_key:
                    close_price = entry[close_key]
                    if date:
                        date_prices[date].append(close_price)

        avg_prices = {}
        for date, prices in date_prices.items():
            if prices:
                avg_prices[date] = sum(prices) / len(prices)

        sorted_data = sorted(avg_prices.items())

        if len(sorted_data) >= 2:
            first_price = sorted_data[0][1]
            latest_price = sorted_data[-1][1]
            percent_change = _safe_percent_change(first_price, latest_price)
        else:
            percent_change = 0

        return sorted_data, percent_change
    except Exception:
        return [], 0

def create_graph(data_points):
    dates = [point[0] for point in data_points]
    prices = [point[1] for point in data_points]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dates, y=prices, mode='lines', name='Price', line=dict(color='#00aaff')))

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Price",
        hovermode='x unified',
        template='plotly_dark',
        paper_bgcolor='#002244',
        plot_bgcolor='#001122',
        font=dict(color='white'),
        showlegend=False,
        height=600,
        margin=dict(l=40, r=40, t=40, b=40)
    )

    return fig


def render_index_panel(title, data_dict):
    points, percent = calculate_index_price(data_dict)
    percent_color = "#00ff00" if percent >= 0 else "#ff4444"
    sign = "+" if percent >= 0 else ""
    st.markdown(
        f'<div style="background-color: #001a33; padding: 20px; border-radius: 8px; border-top: 3px solid #00aaff;"><div style="display: flex; align-items: center; gap: 8px;"><h1 style="color: white; margin: 0; font-size: 40px;">{title}</h1><div style="color: {percent_color}; font-size: 18px; font-weight: bold;">{sign}{percent:.2f}%</div></div></div>',
        unsafe_allow_html=True
    )
    if points:
        st.plotly_chart(create_graph(points), use_container_width=False)

def main():
    sp500_data, ibex35_data = load_data()

    col1, col2 = st.columns([2, 3])
    with col1:
        st.markdown('<h2 style="margin: 0; color: white;">VILTRUM STOCKS</h2>', unsafe_allow_html=True)
    with col2:
        search_term = st.text_input("", placeholder="Search", label_visibility="collapsed")

    sp500_stats = calculate_stock_stats(sp500_data)
    ibex35_stats = calculate_stock_stats(ibex35_data)

    all_stocks = sort_stocks_by_value({**sp500_stats, **ibex35_stats})
    if search_term:
        filtered_stocks = [(symbol, stats) for symbol, stats in all_stocks if search_term.lower() in symbol.lower()]
    else:
        filtered_stocks = all_stocks

    if 'last_search' not in st.session_state:
        st.session_state.last_search = ""
    
    if search_term != st.session_state.last_search:
        st.session_state.page = 0
        st.session_state.last_search = search_term

    stocks_per_page = 10
    total_pages = (len(filtered_stocks) + stocks_per_page - 1) // stocks_per_page

    if 'page' not in st.session_state:
        st.session_state.page = 0

    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        if st.button("←", disabled=st.session_state.page == 0, key="prev_btn", use_container_width=True):
            st.session_state.page -= 1
            st.rerun()

    with col2:
        st.markdown(f"<p style='text-align: center; margin-top: 8px;'>Page {st.session_state.page + 1} of {max(1, total_pages)}</p>", unsafe_allow_html=True)

    with col3:
        if st.button("→", disabled=st.session_state.page >= total_pages - 1, key="next_btn", use_container_width=True):
            st.session_state.page += 1
            st.rerun()

    start_idx = st.session_state.page * stocks_per_page
    end_idx = start_idx + stocks_per_page
    current_stocks = filtered_stocks[start_idx:end_idx]

    if current_stocks:
        cols = st.columns(len(current_stocks))
        for j, (symbol, stats) in enumerate(current_stocks):

            with cols[j]:
                st.markdown(f"""
                <div style="padding: 6px 4px; text-align: center; font-size: 12px;">
                    <div style="font-weight: bold; color: white;">{symbol}</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        if search_term:
            st.markdown(f"<div style='text-align: center; color: #ff4444; font-size: 16px; padding: 20px;'>No stocks found matching '{search_term}'</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='text-align: center; color: #ff4444; font-size: 16px; padding: 20px;'>No stocks to display</div>", unsafe_allow_html=True)

    st.markdown("<div style='margin: 30px 0;'></div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        render_index_panel("S&P 500", sp500_data)

    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 150px 20px 20px 20px;">
            <svg viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg" style="width: 266px; height: 266px;">
                <circle cx="100" cy="95" r="75" stroke="white" stroke-width="12" />
                <path d="M 35 60 L 65 60 L 95 120 L 95 180 Z" fill="white" />
                <path d="M 165 60 L 135 60 L 105 120 L 105 180 Z" fill="white" />
            </svg>
            <div style="margin-top: 12px; font-size: 30px; font-weight: 700; color: #ffffff; letter-spacing: 3px; text-transform: uppercase;">VILTRUM</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        render_index_panel("IBEX 35", ibex35_data)

if __name__ == "__main__":
    main()