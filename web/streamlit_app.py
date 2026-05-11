import streamlit as st
import json
import os
import plotly.graph_objects as go
from collections import defaultdict

#python -m streamlit run web/streamlit_app.py

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
    
    /* Configuración base de todos los botones */
    .stButton button {
        border-radius: 50% !important;
        width: 40px !important;
        height: 40px !important;
        min-width: 40px !important;
        min-height: 40px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        padding: 0 !important;
        font-size: 20px !important;
        line-height: 1 !important;
        
        /* FUERZA EL FONDO TRANSPARENTE Y COLOR BLANCO */
        background-color: transparent !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
    }

    /* Efecto al pasar el ratón (Hover) */
    .stButton button:hover {
        background-color: rgba(0, 170, 255, 0.2) !important; /* Azul Viltrum suave */
        border-color: #00aaff !important;
        color: #00aaff !important;
    }

    /* Elimina el efecto de enfoque (borde rojo/naranja de Streamlit) */
    .stButton button:focus {
        box-shadow: none !important;
        color: white !important;
    }
    
    .stTextInput input {
        background-color: #12243a !important;
        color: white !important;
        border: 1px solid #2c3f57 !important;
        border-radius: 6px !important;
    }
            
    /* Los botones dentro de columnas de filtro serán rectangulares */
    div[data-testid="column"] .stButton button {
        border-radius: 8px !important;
        width: 100% !important;
        height: 35px !important;
        font-size: 14px !important;
    }
    /* Cambia el cursor a una mano cuando el botón tiene ayuda */
    .stButton button[title] {
        cursor: help !important;
    }
    /* Añade esto a tu bloque de style existente */
    div[data-testid="stMetric"], .stMarkdown div[style*="background-color: #12243a"] {
        border: 1px solid rgba(0, 170, 255, 0.2) !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3) !important;
        transition: transform 0.2s ease-in-out;
    }

    div[data-testid="stMetric"]:hover {
        transform: translateY(-5px);
        border-color: #00aaff !important;
    }
</style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    # Obtener el directorio del script actual
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)

    sp500_path = os.path.join(parent_dir, 'data', 'json_sp500.json')
    ibex35_path = os.path.join(parent_dir, 'data', 'json_ibex35.json')
    # Ajuste de ruta para noticias según tu estructura
    news_path = os.path.join(parent_dir, 'data', 'Tickets.json')

    # Cargar datos de índices
    with open(sp500_path, 'r') as f:
        sp500_data = json.load(f)
    with open(ibex35_path, 'r') as f:
        ibex35_data = json.load(f)
    
    # Cargar noticias
    try:
        with open(news_path, 'r', encoding='utf-8') as f:
            news_data = json.load(f)
    except Exception:
        news_data = {}
        
    # Un solo return al final con todo
    return sp500_data, ibex35_data, news_data
def get_sentiment_style(sentiment_label):
    """Asigna colores e iconos según el sentimiento de la noticia."""
    sentiments = {
        "positivo": {"color": "#00ff00", "icon": "🟢", "bg": "rgba(0, 255, 0, 0.1)"},
        "negativo": {"color": "#ff4444", "icon": "🔴", "bg": "rgba(255, 68, 68, 0.1)"},
        "neutral": {"color": "#8899ac", "icon": "⚪", "bg": "rgba(136, 153, 172, 0.1)"}
    }
    return sentiments.get(sentiment_label.lower(), sentiments["neutral"])

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
    """Sort stocks by popularity (volume) and then by value (price)"""
    return sorted(stock_stats.items(), key=lambda x: (-x[1]['volume'], -x[1]['latest_close']))

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
    if not data_points: # Evita errores si no hay datos
        return go.Figure()

    try:
        dates = [point[0] for point in data_points]
        prices = [point[1] for point in data_points]

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=dates, y=prices, mode='lines', name='Price', line=dict(color='#00aaff')))

        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Price",
            template='plotly_dark',
            paper_bgcolor='#0b1726', # Ajustado al color de tu fondo
            plot_bgcolor='#0b1726',
            height=300, # Redúcelo un poco para que quepa bien en las columnas
            margin=dict(l=10, r=10, t=10, b=10)
        )
        return fig
    except Exception as e:
        st.error(f"Error generando gráfica: {e}")
        return go.Figure()

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
def render_market_sentiment(all_stats):
    ups = len([s for s in all_stats.values() if s['percent_change'] > 0])
    downs = len([s for s in all_stats.values() if s['percent_change'] < 0])
    total = ups + downs
    
    st.write("📊 **Sentimiento del Mercado**")
    st.progress(ups / total if total > 0 else 0.5)
    st.caption(f"📈 {ups} Suben | 📉 {downs} Bajan")

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

def get_stock_history(symbol, sp500_data, ibex35_data):
    """Busca los datos históricos de un ticker específico en ambos índices."""
    # Buscar en S&P 500, si no está, buscar en IBEX 35
    data = sp500_data.get(symbol) or ibex35_data.get(symbol)
    
    if not data:
        return []
    
    points = []
    for entry in data:
        # Usamos la misma lógica de fragmentos que ya tienes definida
        date = entry.get("('Date', '')")
        close_key = _find_key_with_fragment(entry, 'Close')
        if date and close_key:
            points.append((date, entry[close_key]))
            
    # Ordenar por fecha para que la gráfica sea correcta
    return sorted(points)
def init_favorites():
    """Inicializa la lista de favoritos en el estado de la sesión si no existe."""
    if 'favorites' not in st.session_state:
        st.session_state.favorites = []

def toggle_favorite(symbol):
    """Añade o elimina un ticker de la lista de favoritos."""
    if symbol in st.session_state.favorites:
        st.session_state.favorites.remove(symbol)
    else:
        st.session_state.favorites.append(symbol)
    st.rerun()

def render_favorites_section(sp500_stats, ibex35_stats):
    """Renderiza el bloque visual de los favoritos."""
    st.markdown("---")
    st.markdown("<h2 style='color: white;'>⭐ Mis Favoritos</h2>", unsafe_allow_html=True)
    
    if st.session_state.favorites:
        # Mostramos hasta 6 columnas por fila
        favs = st.session_state.favorites
        cols = st.columns(min(len(favs), 6))
        
        all_stats = {**sp500_stats, **ibex35_stats}
        
        for i, fav_symbol in enumerate(favs):
            stats = all_stats.get(fav_symbol, {})
            p_change = stats.get('percent_change', 0)
            p_color = '#00c853' if p_change >= 0 else '#d32f2f'
            
            with cols[i % 6]:
                st.markdown(f"""
                <div style="background-color: #12243a; padding: 10px; border-radius: 8px; border: 1px solid #00aaff; text-align: center;">
                    <div style="color: #00aaff; font-weight: bold;">{fav_symbol}</div>
                    <div style="color: {p_color}; font-size: 14px;">{p_change:+.2f}%</div>
                </div>
                """, unsafe_allow_html=True)
                if st.button("🚫",help = "Quitar", key=f"del_{fav_symbol}"):
                    toggle_favorite(fav_symbol)
    else:
        st.info("No tienes acciones en favoritos. Usa la estrella en el buscador.")
def create_comparison_graph(tickers_data):
    """Genera una gráfica comparativa de rendimientos porcentuales."""
    fig = go.Figure()
    for symbol, points in tickers_data.items():
        if not points: continue
        dates = [p[0] for p in points]
        prices = [p[1] for p in points]
        # Normalización a base 100 para comparar rendimiento real
        initial_price = prices[0]
        relative_returns = [((p / initial_price) - 1) * 100 for p in prices]
        fig.add_trace(go.Scatter(x=dates, y=relative_returns, mode='lines', name=symbol))

    fig.update_layout(
        xaxis_title="Fecha", yaxis_title="Rendimiento (%)",
        template='plotly_dark', hovermode="x unified",
        paper_bgcolor='#0b1726', plot_bgcolor='#0b1726'
    )
    return fig

def render_comparison_page(sp500_data, ibex35_data):
    # Botón circular de volver en la esquina o arriba
    if st.button("←", key="back_to_main", help="Volver al panel principal"):
        st.session_state.current_page = "main"
        st.rerun()
        
    st.markdown("<h1 style='color: white; text-align: center;'>⚖️ Comparador</h1>", unsafe_allow_html=True)
    # ... resto de la lógica de comparación

    available_tickers = sorted(list(sp500_data.keys()) + list(ibex35_data.keys()))
    
    selected_tickers = st.multiselect(
        "Selecciona los tickers para comparar rendimiento:",
        options=available_tickers,
        default=st.session_state.favorites[:2] if st.session_state.favorites else None
    )

    if selected_tickers:
        comp_data = {}
        for t in selected_tickers:
            history = get_stock_history(t, sp500_data, ibex35_data)
            if history: comp_data[t] = history
        
        if comp_data:
            st.plotly_chart(create_comparison_graph(comp_data), use_container_width=True)
        else:
            st.info("No hay datos suficientes para los tickers seleccionados.")
def get_recommendation(symbol, sp500_data, ibex35_data):
    """Analiza la tendencia simple para recomendar Compra o Venta."""
    history = get_stock_history(symbol, sp500_data, ibex35_data)
    if len(history) < 5:
        return "NEUTRAL", "Faltan datos", "#8899ac"
    
    # Comparamos el precio actual con la media de los últimos 5 días
    latest_price = history[-1][1]
    last_5_days = [p[1] for p in history[-5:]]
    avg_5_days = sum(last_5_days) / 5
    
    if latest_price > avg_5_days * 1.02: # 2% por encima de la media
        return "COMPRAR", "Tendencia Alcista Fuerte", "#00c853"
    elif latest_price < avg_5_days * 0.98: # 2% por debajo de la media
        return "VENDER", "Tendencia Bajista Detectada", "#d32f2f"
    else:
        return "MANTENER", "Estabilidad de precio", "#ffab00"
def render_advisor_page(sp500_data, ibex35_data):
    if st.button("←", key="back_from_advisor"):
        st.session_state.current_page = "main"
        st.rerun()
        
    st.markdown("<h1 style='text-align: center; color: white;'>🤖 Stock Advisor</h1>", unsafe_allow_html=True)
    
    available_tickers = sorted(list(sp500_data.keys()) + list(ibex35_data.keys()))
    selected = st.selectbox("Selecciona una acción para analizar:", available_tickers)
    
    if selected:
        rec, reason, color = get_recommendation(selected, sp500_data, ibex35_data)
        
        st.markdown(f"""
            <div style="background-color: #12243a; padding: 30px; border-radius: 15px; border: 2px solid {color}; text-align: center; margin-top: 20px;">
                <h2 style="color: white; margin: 0;">{selected}</h2>
                <h1 style="color: {color}; font-size: 60px; margin: 10px 0;">{rec}</h1>
                <p style="color: #8899ac; font-size: 18px;">{reason}</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Mostrar pequeño gráfico de contexto
        history = get_stock_history(selected, sp500_data, ibex35_data)
        st.plotly_chart(create_graph(history), use_container_width=True)
def render_stock_detail_page(symbol, sp500_data, ibex35_data, news_data, all_stats):
    """Página de detalle completo de una acción."""
    prev_page = st.session_state.get('prev_page', 'main')
    if st.button("←", key="back_from_stock_detail"):
        st.session_state.current_page = prev_page
        st.rerun()

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


def render_index_page(title, index_key, data_dict, stats, news_data, sp500_data, ibex35_data):
    """Página de detalle de un índice con tabla de empresas clickeables."""
    if st.button("←", key=f"back_from_{index_key}"):
        st.session_state.current_page = "main"
        st.rerun()

    points, percent = calculate_index_price(data_dict)
    percent_color = "#00ff00" if percent >= 0 else "#ff4444"
    sign = "+" if percent >= 0 else ""

    st.markdown(f"""
    <div style='background: #001a33; padding: 25px; border-radius: 10px; border-top: 3px solid #00aaff; margin-bottom: 20px;'>
        <div style='display: flex; align-items: center; gap: 12px;'>
            <h1 style='color: white; margin: 0; font-size: 44px;'>{title}</h1>
            <div style='color: {percent_color}; font-size: 22px; font-weight: bold;'>{sign}{percent:.2f}%</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if points:
        fig = create_graph(points)
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("<h2 style='color: white; margin-top: 30px;'>Empresas del Índice</h2>", unsafe_allow_html=True)

    # Header de la tabla
    hcols = st.columns([2, 2, 2, 2, 1])
    for col, label in zip(hcols, ["Símbolo", "Precio", "Cambio %", "Volumen", ""]):
        col.markdown(f"<span style='color: #8899ac; font-size: 12px; text-transform: uppercase; font-weight: bold;'>{label}</span>", unsafe_allow_html=True)
    st.markdown("<hr style='border: 1px solid #2c3f57; margin: 5px 0;'>", unsafe_allow_html=True)

    for symbol in sorted(stats.keys()):
        s = stats[symbol]
        pct = s['percent_change']
        price = s['latest_close']
        vol = s['volume']
        c = '#00c853' if pct >= 0 else '#d32f2f'
        row = st.columns([2, 2, 2, 2, 1])
        row[0].markdown(f"<span style='color: white; font-weight: bold;'>{symbol}</span>", unsafe_allow_html=True)
        row[1].markdown(f"<span style='color: white;'>${price:,.2f}</span>", unsafe_allow_html=True)
        row[2].markdown(f"<span style='color: {c}; font-weight: bold;'>{pct:+.2f}%</span>", unsafe_allow_html=True)
        row[3].markdown(f"<span style='color: #8899ac;'>{vol:,}</span>", unsafe_allow_html=True)
        if row[4].button("→", key=f"idx_{index_key}_{symbol}"):
            st.session_state.selected_stock = symbol
            st.session_state.prev_page = index_key
            st.session_state.current_page = "stock_detail"
            st.rerun()


def render_full_graph_page(title, data_dict, is_index=True, symbol=None):
    """Página para ver cualquier gráfica en grande."""
    if st.button("←", key=f"back_from_{title}"):
        st.session_state.current_page = "main"
        st.rerun()
    
    st.markdown(f"<h1 style='text-align: center; color: white;'>📈 Detalle: {title}</h1>", unsafe_allow_html=True)
    
    if is_index:
        points, _ = calculate_index_price(data_dict)
    else:
        points = get_stock_history(symbol, data_dict[0], data_dict[1]) # data_dict sería una tupla (sp500, ibex)

    if points:
        fig = create_graph(points)
        fig.update_layout(height=600) # Gráfica mucho más grande
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("No se pudieron cargar los datos de la gráfica.")
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
        # Botón para ver en grande
        if st.button("→", key=f"full_{title}", help=f"Ver {title} en grande"):
            if "500" in title:
                st.switch_page("pages/SP500.py")
            else:
                st.switch_page("pages/IBEX_35.py")
# Ejemplo de lógica para el "Market Pulse"
def render_market_pulse(all_stats):
    ups = len([s for s in all_stats.values() if s['percent_change'] > 0])
    total = len(all_stats)
    ratio = (ups / total) * 100 if total > 0 else 50
    
    color = "#00ff00" if ratio > 50 else "#ff4444"
    st.markdown(f"""
        <div style="background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(10px); border-radius: 15px; padding: 15px; border: 1px solid {color}33; margin-bottom: 25px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="color: #8899ac; font-size: 14px;">ESTADO DEL MERCADO</span>
                <span style="color: {color}; font-weight: bold;">{ratio:.1f}% ALCISTA</span>
            </div>
            <div style="background: #12243a; height: 6px; border-radius: 3px; margin-top: 8px;">
                <div style="background: {color}; width: {ratio}%; height: 100%; border-radius: 3px; transition: width 0.5s;"></div>
            </div>
        </div>
    """, unsafe_allow_html=True)

def main():
    init_favorites()
    # 1. Gestión de navegación
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "main"

    sp500_data, ibex35_data, news_data = load_data()
    sp500_stats = calculate_stock_stats(sp500_data)
    ibex35_stats = calculate_stock_stats(ibex35_data)
    all_stats = {**sp500_stats, **ibex35_stats}

    # 2. Selector de página
    if st.session_state.current_page == "comparison":
        render_comparison_page(sp500_data, ibex35_data)
    elif st.session_state.current_page == "advisor":
        render_advisor_page(sp500_data, ibex35_data)
    elif st.session_state.current_page == "full_sp500":
        render_full_graph_page("S&P 500", sp500_data)
    elif st.session_state.current_page == "full_ibex35":
        render_full_graph_page("IBEX 35", ibex35_data)
    elif st.session_state.current_page == "full_ticker":
        render_full_graph_page(st.session_state.selected_ticker_full, (sp500_data, ibex35_data), is_index=False, symbol=st.session_state.selected_ticker_full)
    elif st.session_state.current_page == "stock_detail":
        render_stock_detail_page(st.session_state.selected_stock, sp500_data, ibex35_data, news_data, all_stats)
    elif st.session_state.current_page == "index_sp500":
        render_index_page("S&P 500", "index_sp500", sp500_data, sp500_stats, news_data, sp500_data, ibex35_data)
    elif st.session_state.current_page == "index_ibex35":
        render_index_page("IBEX 35", "index_ibex35", ibex35_data, ibex35_stats, news_data, sp500_data, ibex35_data)
    else:
        # Si estamos en la página principal, ejecutamos todo el código original
        # Aquí empieza el bloque de tu código original:
        col1, col2 = st.columns([2, 3])
        with col1:
            st.markdown('<h2 style="margin: 0; color: white; font-family: Sharp;">VILTRUM STOCKS</h2>', unsafe_allow_html=True)
        with col2:
            search_term = st.text_input("", placeholder="Search", label_visibility="collapsed")

        all_stocks = sort_stocks_by_value(all_stats)

        # --- ALERTAS MEJORADAS ---
        for fav in st.session_state.favorites:
            stats = all_stats.get(fav)
            if stats:
                color = "#00ff00" if stats['percent_change'] > 0 else "#ff4444"
                if abs(stats['percent_change']) > 3.0:
                    st.markdown(f"""
                        <div style="background-color: rgba(255,255,255,0.05); border: 1px solid {color}; padding: 10px; border-radius: 5px; margin-bottom: 10px; text-align: center;">
                            ⚠️ <b>ALERTA VOLATILIDAD:</b> {fav} ha movido un <span style="color:{color}">{stats['percent_change']:.2f}%</span>
                        </div>
                    """, unsafe_allow_html=True)
                # Alerta por noticia negativa
                news = news_data.get(fav)
                if news:
                    noticia = news[0] if isinstance(news, list) else news
                    if noticia.get('sentiment', '').lower() == 'negativo':
                        st.markdown(f"""
                            <div style="background-color: #2c1a1a; border: 1px solid #ff4444; padding: 10px; border-radius: 5px; margin-bottom: 10px; text-align: center; color: #ff4444;">
                                🚨 <b>ALERTA NOTICIA NEGATIVA:</b> {fav} tiene una noticia negativa reciente.
                            </div>
                        """, unsafe_allow_html=True)

        # --- IDEA 2: FILTROS RÁPIDOS ---
        if 'filter_mode' not in st.session_state: 
            st.session_state.filter_mode = "Todos"
        
        st.write("🔍 **Filtros rápidos:**")
        f_cols = st.columns(4)
        if f_cols[0].button("🌐",help= "Todos"): 
            st.session_state.filter_mode = "Todos"
            st.session_state.page = 0
        if f_cols[1].button("🚀", help= "Ganadores"): 
            st.session_state.filter_mode = "Ganadores"
            st.session_state.page = 0
        if f_cols[2].button("📉", help= "Perdedores"): 
            st.session_state.filter_mode = "Perdedores"
            st.session_state.page = 0
        if f_cols[3].button("📊", help= "Volatilidad"): 
            st.session_state.filter_mode = "Volatilidad"
            st.session_state.page = 0

        # Lógica de filtrado y búsqueda
        if search_term:
            filtered_stocks = [(symbol, stats) for symbol, stats in all_stocks if search_term.lower() in symbol.lower()]
        else:
            if st.session_state.filter_mode == "Ganadores":
                filtered_stocks = sorted(all_stocks, key=lambda x: x[1]['percent_change'], reverse=True)
            elif st.session_state.filter_mode == "Perdedores":
                filtered_stocks = sorted(all_stocks, key=lambda x: x[1]['percent_change'])
            elif st.session_state.filter_mode == "Volatilidad":
                filtered_stocks = sorted(all_stocks, key=lambda x: x[1]['volume'], reverse=True)
            else:
                filtered_stocks = all_stocks

        stocks_per_page = 10
        total_pages = (len(filtered_stocks) + stocks_per_page - 1) // stocks_per_page

        if 'page' not in st.session_state:
            st.session_state.page = 0


        start_idx = st.session_state.page * stocks_per_page
        end_idx = start_idx + stocks_per_page
        current_stocks = filtered_stocks[start_idx:end_idx]

        # Create a row with left button, stocks, right button (make arrows closer)
        row = st.columns([0.5, 11, 0.5])
        with row[0]:
            if st.button("←", disabled=st.session_state.page == 0, key="left", help="Previous"):
                st.session_state.page -= 1
                st.rerun()
        with row[1]:
            if current_stocks:
                cols = st.columns(len(current_stocks))
                for j, (symbol, stats) in enumerate(current_stocks):
                    percent = stats.get('percent_change', 0)
                    percent_color = '#00c853' if percent >= 0 else '#d32f2f'
                    sign = '+' if percent >= 0 else ''
                    with cols[j]:
                        st.markdown(f"""
                        <div style="padding: 6px 4px; text-align: center; font-size: 12px; border: 2px solid white; border-radius: 8px; box-sizing: border-box;">
                            <div style="font-weight: bold; color: white;">{symbol}</div>
                            <div style="color: {percent_color}; font-size: 12px; font-weight: bold;">{sign}{percent:.2f}%</div>
                        </div>
                        """, unsafe_allow_html=True)
                        btn_a, btn_b = st.columns(2)
                        with btn_a:
                            is_fav = symbol in st.session_state.favorites
                            if st.button("⭐" if is_fav else "☆", key=f"btn_{symbol}"):
                                toggle_favorite(symbol)
                        with btn_b:
                            if st.button("→", key=f"detail_{symbol}", help=f"Ver {symbol}"):
                                st.session_state.selected_stock = symbol
                                st.session_state.prev_page = "main"
                                st.session_state.current_page = "stock_detail"
                                st.rerun()
            else:
                if search_term:
                    st.markdown(f"<div style='text-align: center; color: #ff4444; font-size: 16px; padding: 20px;'>No stocks found matching '{search_term}'</div>", unsafe_allow_html=True)
                else:
                    st.markdown("<div style='text-align: center; color: #ff4444; font-size: 16px; padding: 20px;'>No stocks to display</div>", unsafe_allow_html=True)
        with row[2]:
            if st.button("→", disabled=st.session_state.page == total_pages - 1, key="right", help="Next"):
                st.session_state.page += 1
                st.rerun()

        st.markdown("---")
        
        # ... (continúa con el bloque col1, col2, col3 de los índices)

        col1, col2, col3 = st.columns([1, 1, 1])

        with col1:
            render_index_panel("S&P 500", sp500_data) # Asegúrate que dentro use use_container_width=True

        with col2:
            st.markdown("""
            <div style="text-align: center; padding: 150px 20px 20px 20px;">
                <svg viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg" style="width: 266px; height: 266px;">
                    <circle cx="100" cy="95" r="75" stroke="white" stroke-width="12" />
                    <path d="M 35 60 L 65 60 L 95 120 L 95 180 Z" fill="white" />
                    <path d="M 165 60 L 135 60 L 105 120 L 105 180 Z" fill="white" />
                </svg>
                <div style="margin-top: 12px; font-size: 30px; font-weight: 700; color: #ffffff; letter-spacing: 3px; text-transform: uppercase; font-family: Sharp;">VILTRUM</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            render_index_panel("IBEX 35", ibex35_data)
        # ... (Después de que se dibujen los paneles de S&P500 e IBEX)
        
        # --- TOP MOVERS (BOTTOM) ---
        st.markdown("<hr style='margin: 40px 0 10px 0; border: 1px solid #222;'>", unsafe_allow_html=True)
        st.markdown("<h2 style='color: white; font-size: 22px;'>Top Acciones del Día</h2>", unsafe_allow_html=True)
        top_gainers = sorted(all_stocks, key=lambda x: x[1]['percent_change'], reverse=True)[:3]
        top_losers = sorted(all_stocks, key=lambda x: x[1]['percent_change'])[:3]
        mover_cols = st.columns(6)
        for i, (symbol, stats) in enumerate(top_gainers):
            percent = stats.get('percent_change', 0)
            mover_cols[i].markdown(f"""
                <div style='background: #193a1a; border-radius: 8px; padding: 10px; text-align: center; border: 1px solid #00ff00;'>
                    <b style='color: #00ff00;'>{symbol}</b><br>
                    <span style='color: #00ff00;'>{percent:+.2f}%</span>
                </div>
            """, unsafe_allow_html=True)
        for i, (symbol, stats) in enumerate(top_losers):
            percent = stats.get('percent_change', 0)
            mover_cols[i+3].markdown(f"""
                <div style='background: #3a1a1a; border-radius: 8px; padding: 10px; text-align: center; border: 1px solid #ff4444;'>
                    <b style='color: #ff4444;'>{symbol}</b><br>
                    <span style='color: #ff4444;'>{percent:+.2f}%</span>
                </div>
            """, unsafe_allow_html=True)

        # --- SECCIÓN DE NOTICIAS HORIZONTAL UNIFICADA ---
        st.markdown("<h2 style='color: white; font-size: 24px; text-align: center;'>Últimas Noticias</h2>", unsafe_allow_html=True)
        news_symbols = [stock_tuple[0] for stock_tuple in current_stocks]
        # Cargar noticias de Gemini-code.json
        try:
            gemini_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'Gemini-code.json')
            with open(gemini_path, 'r', encoding='utf-8') as f:
                gemini_news = json.load(f)
        except Exception:
            gemini_news = {}

        # Mostrar las primeras cinco noticias de Gemini justo debajo del título
        gemini_items = []
        for symbol, news_list in gemini_news.items():
            for noticia in news_list:
                gemini_items.append((symbol, noticia))
        st.markdown("<div style='display: flex; flex-direction: row; gap: 18px; overflow-x: auto; width: 100%; margin-bottom: 18px;'>", unsafe_allow_html=True)
        for symbol, noticia in gemini_items:
            title = noticia.get('title', 'Sin título')
            link = noticia.get('link', '#')
            publisher = noticia.get('publisher', 'Gemini')
            sentiment_label = noticia.get('sentiment', 'neutral')
            style = get_sentiment_style(sentiment_label)
            st.markdown(f"""
            <div style='min-width: 340px; flex: 0 0 340px;'>
                <div style=\"background-color: #12243a; padding: 15px; border-radius: 10px; border-left: 4px solid {style['color']}; margin-bottom: 10px; min-height: 120px; display: flex; flex-direction: column; justify-content: space-between;\">
                    <div style=\"display: flex; justify-content: space-between; margin-bottom: 5px;\">
                        <p style=\"color: #8899ac; font-size: 11px; margin: 0; text-transform: uppercase;\">{publisher} • {symbol}</p>
                        <span style=\"font-size: 12px; background-color: {style['bg']}; color: {style['color']}; padding: 2px 8px; border-radius: 10px; font-weight: bold;\">
                            {style['icon']} {sentiment_label.upper()}
                        </span>
                    </div>
                    <a href=\"{link}\" target=\"_blank\" style=\"color: white; text-decoration: none; font-weight: bold; font-size: 14px; line-height: 1.2;\">{title}</a>
                </div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # Ahora el carrusel de noticias principal (news.json + resto de Gemini)
        st.markdown("<div style='display: flex; flex-direction: row; gap: 18px; overflow-x: auto; width: 100%;'>", unsafe_allow_html=True)
        # Noticias principales (news.json)
        for symbol in news_symbols:
            st.markdown(f"<div style='min-width: 340px; flex: 0 0 340px;'>", unsafe_allow_html=True)
            render_news_section(symbol, news_data)
            st.markdown("</div>", unsafe_allow_html=True)
        # Noticias destacadas (Gemini-code.json) - Eliminado para evitar repeticiones
        # st.markdown("</div>", unsafe_allow_html=True)
        render_favorites_section(sp500_stats, ibex35_stats)
  
if __name__ == "__main__":
    main()