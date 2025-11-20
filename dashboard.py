import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
from datetime import datetime
from ai_oracle import AIOracleEngine
from streamlit_autorefresh import st_autorefresh

# --- KONFIGURACJA STRONY ---
st.set_page_config(
    page_title="Santander Quant Desk",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- REAL-TIME ENGINE (Auto-refresh co 30s) ---
count = st_autorefresh(interval=30000, limit=None, key="market_data_refresh")

# --- PREMIUM UI CSS (Glassmorphism & Neon) ---
st.markdown("""
    <style>
        /* Główny kontener i tło */
        .stApp {
            background-color: #000000;
            background-image: radial-gradient(circle at 50% 0%, #1a1a2e 0%, #000000 100%);
        }
        
        /* Glassmorphism Cards */
        .css-1r6slb0, .stMetric, .stDataFrame, .stPlotlyChart {
            background: rgba(255, 255, 255, 0.03);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 15px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        }
        
        /* Nagłówki */
        h1, h2, h3 {
            font-family: 'Roboto Mono', monospace;
            color: #ffffff;
            text-transform: uppercase;
            letter-spacing: 2px;
        }
        
        h1 {
            background: linear-gradient(90deg, #00f260 0%, #0575e6 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 900;
        }
        
        /* Metryki */
        div[data-testid="stMetricValue"] {
            font-family: 'Roboto Mono', monospace;
            font-size: 1.8rem !important;
            color: #00f260;
            text-shadow: 0 0 10px rgba(0, 242, 96, 0.3);
        }
        
        div[data-testid="stMetricLabel"] {
            color: #888;
            font-size: 0.8rem !important;
            text-transform: uppercase;
        }
        
        /* Tabela */
        .stDataFrame {
            border: none;
        }
        
        /* Przyciski */
        .stButton > button {
            background: linear-gradient(45deg, #00f260, #0575e6);
            color: white;
            border: none;
            border-radius: 5px;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 1px;
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 242, 96, 0.4);
        }
        
        /* Custom Scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        ::-webkit-scrollbar-track {
            background: #0e1117; 
        }
        ::-webkit-scrollbar-thumb {
            background: #333; 
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #555; 
        }
    </style>
""", unsafe_allow_html=True)

# --- LISTA SPÓŁEK (WIG20 + mWIG40 Selection) ---
TICKERS = [
    "XTB.WA", "CDR.WA", "LPP.WA", "DNP.WA", "PCO.WA", "BFT.WA", "CCC.WA",
    "PKO.WA", "PEO.WA", "KGH.WA", "ALE.WA", "KRU.WA", "JSW.WA", "CPS.WA",
    "MBK.WA", "ALR.WA", "BDX.WA", "TEN.WA"
]

# --- SILNIK DANYCH ---
@st.cache_data(ttl=25)  # Cache krótszy niż interwał odświeżania
def get_market_data():
    data_list = []
    
    # Initialize AI Oracle
    oracle = AIOracleEngine()
    
    # Pobieranie batchowe
    tickers_str = " ".join(TICKERS)
    try:
        df_bulk = yf.download(tickers_str, period="3mo", interval="1d", group_by='ticker', progress=False)
    except Exception:
        return pd.DataFrame()
    
    for ticker in TICKERS:
        try:
            df = df_bulk[ticker].copy()
            if df.empty: continue
            
            # Usuwanie MultiIndex jeśli jest
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.droplevel(0)
            
            # Obliczenia wskaźników
            df['SMA5'] = df['Close'].rolling(5).mean()
            df['SMA10'] = df['Close'].rolling(10).mean()
            df['SMA15'] = df['Close'].rolling(15).mean()
            df['SMA20'] = df['Close'].rolling(20).mean()
            
            # RSI
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))
            
            last_row = df.iloc[-1]
            prev_row = df.iloc[-2]
            
            # --- LOGIKA SCREENERA (WACHLARZ) ---
            score = 0
            price = last_row['Close']
            s5, s10, s15, s20 = last_row['SMA5'], last_row['SMA10'], last_row['SMA15'], last_row['SMA20']
            
            if price > s5: score += 1
            if s5 > s10: score += 2
            if s10 > s15: score += 2
            if s15 > s20: score += 2
            
            signal = "NEUTRAL"
            if score >= 7: signal = "STRONG BUY 🚀"
            elif score >= 4: signal = "BUY"
            elif price < s20: signal = "SELL"

            change_pct = ((price - prev_row['Close']) / prev_row['Close']) * 100
            
            # 🧠 AI ORACLE PREDICTION
            ai_pred = oracle.predict(df)

            data_list.append({
                "Ticker": ticker.replace(".WA", ""),
                "Price": round(price, 2),
                "Change %": round(change_pct, 2),
                "RSI": round(last_row['RSI'], 1),
                "Signal": signal,
                "Score": score,
                "Volume": last_row['Volume'],
                "History": df,
                "AI_Prediction": ai_pred['prediction'],
                "AI_Confidence": ai_pred['confidence'],
                "AI_Prob_Up": ai_pred['probability_up'],
                "AI_Prob_Down": ai_pred['probability_down']
            })
            
        except Exception as e:
            continue
            
    return pd.DataFrame(data_list)

# --- INTERFEJS GŁÓWNY ---

# 1. Header
col1, col2 = st.columns([6, 1])
with col1:
    st.title("⚡ SANTANDER QUANT DESK")
    st.caption(f"LIVE MARKET DATA | LAST UPDATE: {datetime.now().strftime('%H:%M:%S')} | REFRESH: 30s")
with col2:
    if st.button("🔄 RELOAD"):
        st.rerun()

# 2. Pobranie danych
with st.spinner("Fetching market data..."):
    df_market = get_market_data()

if df_market.empty:
    st.error("Błąd pobierania danych. Spróbuj odświeżyć.")
    st.stop()

df_sorted = df_market.sort_values(by=["Score", "Change %"], ascending=False)

# 3. KPI Metrics (Top 3)
top_picks = df_sorted.head(4)
m1, m2, m3, m4 = st.columns(4)

if len(top_picks) >= 3:
    with m1:
        st.metric(label=f"🏆 TOP PICK: {top_picks.iloc[0]['Ticker']}", 
                  value=f"{top_picks.iloc[0]['Price']}", 
                  delta=f"{top_picks.iloc[0]['Change %']}%")
    with m2:
        st.metric(label=f"🥈 RUNNER UP: {top_picks.iloc[1]['Ticker']}", 
                  value=f"{top_picks.iloc[1]['Price']}", 
                  delta=f"{top_picks.iloc[1]['Change %']}%")
    with m3:
        avg_rsi = df_market['RSI'].mean()
        st.metric(label="MARKET SENTIMENT (RSI)", 
                  value=f"{avg_rsi:.1f}", 
                  delta="OVERBOUGHT" if avg_rsi > 70 else "OVERSOLD" if avg_rsi < 30 else "NEUTRAL",
                  delta_color="inverse")
    with m4:
        strong_buys = len(df_market[df_market['Signal'].str.contains("STRONG BUY")])
        st.metric(label="STRONG SIGNALS", 
                  value=f"{strong_buys}", 
                  delta="ACTIVE OPPORTUNITIES")

st.markdown("---")

# 4. Layout: Tabela (Lewo) + Wykres (Prawo)
col_left, col_right = st.columns([5, 7])

with col_left:
    st.subheader("📊 LIVE SCREENER")
    
    # Stylizowanie Tabeli
    def color_signal(val):
        color = '#ffffff'
        if 'STRONG BUY' in val: color = '#00f260' # Neon Green
        elif 'BUY' in val: color = '#90ee90'
        elif 'SELL' in val: color = '#ff4b4b' # Neon Red
        return f'color: {color}; font-weight: bold; text-shadow: 0 0 5px {color}40;'
    
    def color_change(val):
        color = '#ff4b4b' if val < 0 else '#00f260'
        return f'color: {color}'
    
    def color_ai_prediction(val):
        if val == 'UP': return 'color: #00f260; font-weight: bold'
        elif val == 'DOWN': return 'color: #ff4b4b; font-weight: bold'
        return 'color: white'

    # Przygotowanie DF do wyświetlenia
    display_df = df_sorted[["Ticker", "Price", "Change %", "RSI", "Signal", "AI_Prediction", "AI_Confidence"]].copy()
    display_df = display_df.rename(columns={
        "AI_Prediction": "AI",
        "AI_Confidence": "Conf%"
    })
    
    st.dataframe(
        display_df.style.map(color_signal, subset=['Signal'])
                        .map(color_change, subset=['Change %'])
                        .map(color_ai_prediction, subset=['AI'])
                        .format({"Price": "{:.2f}", "Change %": "{:+.2f}", "RSI": "{:.1f}", "Conf%": "{:.0f}%"}),
        height=700,
        use_container_width=True,
        hide_index=True
    )

with col_right:
    # Wybór spółki z listy
    selected_ticker = st.selectbox("🔍 SELECT ASSET:", df_sorted['Ticker'].tolist())
    
    # Pobranie historii dla wybranej spółki
    stock_data = df_market[df_market['Ticker'] == selected_ticker].iloc[0]['History']
    
    # Rysowanie wykresu Plotly
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                        vertical_spacing=0.03, row_heights=[0.75, 0.25])

    # Świece
    fig.add_trace(go.Candlestick(
        x=stock_data.index,
        open=stock_data['Open'], high=stock_data['High'],
        low=stock_data['Low'], close=stock_data['Close'],
        name="Price",
        increasing_line_color='#00f260', decreasing_line_color='#ff4b4b'
    ), row=1, col=1)

    # Średnie
    fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data['SMA5'], line=dict(color='#ffff00', width=1), name='SMA 5'), row=1, col=1)
    fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data['SMA20'], line=dict(color='#00ffff', width=2), name='SMA 20'), row=1, col=1)

    # Wolumen
    colors = ['#ff4b4b' if row['Open'] - row['Close'] >= 0 else '#00f260' for index, row in stock_data.iterrows()]
    fig.add_trace(go.Bar(x=stock_data.index, y=stock_data['Volume'], marker_color=colors, name='Volume'), row=2, col=1)

    # Layout Wykresu - Dark Theme
    fig.update_layout(
        title=dict(text=f"{selected_ticker} - TECHNICAL ANALYSIS", font=dict(color="white", size=20)),
        xaxis_rangeslider_visible=False,
        height=700,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="white"),
        margin=dict(l=10, r=10, t=40, b=10),
        legend=dict(orientation="h", y=1, x=0, xanchor="left", yanchor="bottom"),
        xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)')
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 🧠 AI ORACLE BOX
    stock_row = df_market[df_market['Ticker'] == selected_ticker].iloc[0]
    ai_pred = stock_row['AI_Prediction']
    ai_conf = stock_row['AI_Confidence']
    ai_up = stock_row['AI_Prob_Up']
    ai_down = stock_row['AI_Prob_Down']
    
    confidence_level = "🔥 STRONG" if ai_conf > 70 else "⚡ MODERATE" if ai_conf > 60 else "💤 WEAK"
    
    st.markdown(f"""
    <div style="background: rgba(0, 242, 96, 0.05); border: 1px solid rgba(0, 242, 96, 0.2); border-radius: 10px; padding: 15px; margin-top: 10px;">
        <h3 style="margin: 0; color: #00f260;">🧠 AI ORACLE PREDICTION</h3>
        <div style="display: flex; justify-content: space-between; margin-top: 10px;">
            <div>
                <div style="font-size: 0.8rem; color: #888;">DIRECTION</div>
                <div style="font-size: 1.5rem; font-weight: bold; color: {'#00f260' if ai_pred == 'UP' else '#ff4b4b'};">{ai_pred}</div>
            </div>
            <div>
                <div style="font-size: 0.8rem; color: #888;">CONFIDENCE</div>
                <div style="font-size: 1.5rem; font-weight: bold; color: white;">{ai_conf:.0f}%</div>
            </div>
            <div>
                <div style="font-size: 0.8rem; color: #888;">PROBABILITY</div>
                <div style="font-size: 1.2rem; color: white;">↗ {ai_up:.0f}% | ↘ {ai_down:.0f}%</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# 5. Stopka
st.markdown("---")
st.caption("© 2025 SANTANDER QUANT DESK | POWERED BY AI & STREAMLIT | DATA DELAYED 15 MIN")
