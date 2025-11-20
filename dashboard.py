import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
from datetime import datetime
from ai_oracle import AIOracleEngine  # ML Predictions

# --- KONFIGURACJA STRONY (Musi być na samym początku) ---
st.set_page_config(
    page_title="Santander Quant Desk",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- STYLE CSS (Żeby wyglądało PRO) ---
st.markdown("""
    <style>
        .block-container { padding-top: 1rem; padding-bottom: 0rem; }
        h1 { margin-top: -2rem; }
        .stMetric { background-color: #0e1117; border: 1px solid #262730; padding: 10px; border-radius: 5px; }
        div[data-testid="stExpander"] details summary p { font-size: 1.2rem; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- LISTA SPÓŁEK (WIG20 + mWIG40 Selection) ---
TICKERS = [
    "XTB.WA", "CDR.WA", "LPP.WA", "DNP.WA", "PCO.WA", "BFT.WA", "CCC.WA",
    "PKO.WA", "PEO.WA", "KGH.WA", "ALE.WA", "KRU.WA", "JSW.WA", "CPS.WA",
    "MBK.WA", "ALR.WA", "BDX.WA", "TEN.WA"
]

# --- SILNIK DANYCH ---
@st.cache_data(ttl=60)  # Cache na 60 sekund, żeby nie zatykać API
def get_market_data():
    data_list = []
    
    # Initialize AI Oracle
    oracle = AIOracleEngine()
    
    # Pobieranie batchowe
    tickers_str = " ".join(TICKERS)
    df_bulk = yf.download(tickers_str, period="3mo", interval="1d", group_by='ticker', progress=False)
    
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
                "History": df,  # Przechowujemy cały DF do wykresu
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
col1, col2, col3 = st.columns([5, 1, 1])
with col1:
    st.title("⚡ SANTANDER QUANT DESK")
    st.caption(f"Market Overview | {datetime.now().strftime('%Y-%m-%d %H:%M')}")
with col3:
    if st.button("🔄 ODŚWIEŻ"):
        st.rerun()

# 2. Pobranie danych
df_market = get_market_data()
df_sorted = df_market.sort_values(by=["Score", "Change %"], ascending=False)

# 3. KPI Metrics (Top 3)
top_picks = df_sorted.head(3)
m1, m2, m3, m4 = st.columns(4)

if len(top_picks) >= 3:
    with m1:
        st.metric(label=f"🏆 LIDER: {top_picks.iloc[0]['Ticker']}", 
                  value=f"{top_picks.iloc[0]['Price']} PLN", 
                  delta=f"{top_picks.iloc[0]['Change %']}%")
    with m2:
        st.metric(label=f"🥈 WICE: {top_picks.iloc[1]['Ticker']}", 
                  value=f"{top_picks.iloc[1]['Price']} PLN", 
                  delta=f"{top_picks.iloc[1]['Change %']}%")
    with m3:
        avg_rsi = df_market['RSI'].mean()
        st.metric(label="Sentyment Rynku (RSI)", 
                  value=f"{avg_rsi:.1f}", 
                  delta="Przegrzany" if avg_rsi > 70 else "Wyprzedany" if avg_rsi < 30 else "Neutralny",
                  delta_color="inverse")

# 4. Layout: Tabela (Lewo) + Wykres (Prawo)
col_left, col_right = st.columns([4, 6])

with col_left:
    st.subheader("📊 Screener Wyników + 🧠 AI Oracle")
    
    # Stylizowanie Tabeli
    def color_signal(val):
        color = 'white'
        if 'STRONG BUY' in val: color = '#00ff00' # Bright Green
        elif 'BUY' in val: color = '#90ee90' # Light Green
        elif 'SELL' in val: color = '#ff4b4b' # Red
        return f'color: {color}; font-weight: bold'
    
    def color_change(val):
        color = '#ff4b4b' if val < 0 else '#00ff00'
        return f'color: {color}'
    
    def color_ai_prediction(val):
        if val == 'UP': return 'color: #00ff00; font-weight: bold'
        elif val == 'DOWN': return 'color: #ff4b4b; font-weight: bold'
        return 'color: white'

    # Przygotowanie DF do wyświetlenia
    display_df = df_sorted[["Ticker", "Price", "Change %", "RSI", "Signal", "AI_Prediction", "AI_Confidence"]].copy()
    display_df = display_df.rename(columns={
        "AI_Prediction": "AI 🧠",
        "AI_Confidence": "AI Conf%"
    })
    
    st.dataframe(
        display_df.style.applymap(color_signal, subset=['Signal'])
                        .applymap(color_change, subset=['Change %'])
                        .applymap(color_ai_prediction, subset=['AI 🧠'])
                        .format({"Price": "{:.2f}", "Change %": "{:+.2f}", "RSI": "{:.1f}", "AI Conf%": "{:.0f}%"}),
        height=600,
        use_container_width=True,
        hide_index=True
    )

with col_right:
    # Wybór spółki z listy
    selected_ticker = st.selectbox("🔍 Wybierz spółkę do analizy:", df_sorted['Ticker'].tolist())
    
    # Pobranie historii dla wybranej spółki
    stock_data = df_market[df_market['Ticker'] == selected_ticker].iloc[0]['History']
    
    # Rysowanie wykresu Plotly
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                        vertical_spacing=0.05, row_heights=[0.7, 0.3])

    # Świece
    fig.add_trace(go.Candlestick(
        x=stock_data.index,
        open=stock_data['Open'], high=stock_data['High'],
        low=stock_data['Low'], close=stock_data['Close'],
        name="Cena"
    ), row=1, col=1)

    # Średnie
    fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data['SMA5'], line=dict(color='yellow', width=1), name='SMA 5'), row=1, col=1)
    fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data['SMA20'], line=dict(color='blue', width=2), name='SMA 20'), row=1, col=1)

    # Wolumen
    colors = ['red' if row['Open'] - row['Close'] >= 0 else 'green' for index, row in stock_data.iterrows()]
    fig.add_trace(go.Bar(x=stock_data.index, y=stock_data['Volume'], marker_color=colors, name='Wolumen'), row=2, col=1)

    # Layout Wykresu
    fig.update_layout(
        title=f"Analiza Techniczna: {selected_ticker}",
        xaxis_rangeslider_visible=False,
        height=650,
        template="plotly_dark",
        margin=dict(l=0, r=0, t=40, b=0),
        legend=dict(orientation="h", y=1, x=0, xanchor="left", yanchor="bottom")
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 🧠 AI ORACLE BOX
    stock_row = df_market[df_market['Ticker'] == selected_ticker].iloc[0]
    ai_pred = stock_row['AI_Prediction']
    ai_conf = stock_row['AI_Confidence']
    ai_up = stock_row['AI_Prob_Up']
    ai_down = stock_row['AI_Prob_Down']
    
    ai_color = "green" if ai_pred == "UP" else "red"
    confidence_level = "🔥 STRONG" if ai_conf > 70 else "⚡ MODERATE" if ai_conf > 60 else "💤 WEAK"
    
    st.markdown(f"""
    ### 🧠 AI ORACLE PREDICTION
    """)
    
    col_ai1, col_ai2, col_ai3 = st.columns(3)
    with col_ai1:
        st.metric("Direction", f"{ai_pred}", delta=f"{ai_conf:.0f}% confidence")
    with col_ai2:
        st.metric("Prob UP ↗", f"{ai_up:.1f}%")
    with col_ai3:
        st.metric("Prob DOWN ↘", f"{ai_down:.1f}%")
    
    st.info(f"💡 **AI Analysis:** Model predicts **{ai_pred}** with **{confidence_level}** signal ({ai_conf:.0f}% confidence)")

# 5. Stopka z analizą automatyczną
st.divider()
best_stock = df_sorted.iloc[0]
best_ai = best_stock['AI_Prediction']
best_ai_conf = best_stock['AI_Confidence']

st.info(f"💡 **COMBINED SUGGESTION:** Najsilniejszy trend wykazuje **{best_stock['Ticker']}** (Score: {best_stock['Score']}). "
        f"RSI ({best_stock['RSI']}) wskazuje na siłę. "
        f"🧠 **AI Oracle predicts: {best_ai}** ({best_ai_conf:.0f}% confidence).")
