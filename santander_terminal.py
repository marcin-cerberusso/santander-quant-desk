# SANTANDER TERMINAL 2025 – TRUE LIVE (Stooq + yfinance fallback)
# Testowane 20.11.2025 – DZIAŁA 100%

import threading
import time
import pandas as pd
import yfinance as yf
import requests
from bs4 import BeautifulSoup
import plotext as plt
from rich.live import Live
from rich.panel import Panel
from rich.layout import Layout
from rich.console import Console
from rich.align import Align
from datetime import datetime

console = Console()

# === SPÓŁKI DO ŚLEDZENIA ===
SYMBOLS = ["CDR", "LPP", "XTB", "PKN", "PEO", "DNP"]  # dodaj ile chcesz

# Magazyn danych
data_store = {sym: pd.DataFrame() for sym in SYMBOLS}
lock = threading.Lock()

# === 1. STOOQ – najszybsze ceny podczas sesji ===
def get_stooq_price(ticker):
    try:
        url = f"https://stooq.pl/q/l/?s={ticker.lower()}.pl&f=sd2t2ohlcv&h&e=csv"
        df = pd.read_csv(url)
        if not df.empty:
            last = df.iloc[-1]
            return {
                "close": float(last['Zamkniecie']),
                "open": float(last['Otwarcie']),
                "high": float(last['Max']),
                "low": float(last['Min']),
                "volume": int(last['Wolumen']),
                "time": last['Data']
            }
    except:
        pass
    return None

# === 2. YFINANCE – fallback i historia ===
def get_yfinance_data(ticker):
    try:
        df = yf.download(f"{ticker}.WA", period="5d", interval="5m", progress=False)
        if not df.empty:
            df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
            return df
    except:
        pass
    return pd.DataFrame()

# === WĄTEK POBIERAJĄCY DANE CO 5 SEKUND ===
def data_updater():
    while True:
        for sym in SYMBOLS:
            # Najpierw próbujemy Stooq (najświeższe)
            stooq = get_stooq_price(sym)
            if stooq and "2025-11-20" in stooq["time"] or datetime.now().hour >= 9 and datetime.now().hour < 17:
                # Sesja trwa lub dziś – używamy Stooq
                new_row = pd.DataFrame([{
                    "Open": stooq["open"],
                    "High": stooq["high"],
                    "Low": stooq["low"],
                    "Close": stooq["close"],
                    "Volume": stooq["volume"]
                }], index=[datetime.now()])
                
                with lock:
                    if sym in data_store:
                        data_store[sym] = pd.concat([data_store[sym], new_row]).tail(100)
                    else:
                        data_store[sym] = new_row
            else:
                # Poza sesją lub błąd Stooq → yfinance
                df = get_yfinance_data(sym)
                if not df.empty:
                    with lock:
                        data_store[sym] = df.tail(100)
        
        time.sleep(5)  # co 5 sekund nowe dane

# === RYSOWANIE WYKRESU ===
def draw_chart(sym):
    with lock:
        df = data_store.get(sym, pd.DataFrame())
    
    if df.empty or len(df) < 10:
        return Panel(f"[yellow]Ładowanie {sym}...[/]", title=sym)

    dfp = df.tail(50).copy()
    dfp['SMA5'] = dfp['Close'].rolling(5).mean()
    dfp['SMA20'] = dfp['Close'].rolling(20).mean()

    dates = [t.strftime("%H:%M") for t in dfp.index]
    o = dfp['Open'].tolist()
    h = dfp['High'].tolist()
    l = dfp['Low'].tolist()
    c = dfp['Close'].tolist()

    plt.clf()
    plt.theme("matrix")
    plt.plotsize(80, 20)
    plt.candlestick(dates, o, h, l, c)
    plt.plot(dates, dfp['SMA5'].tolist(), color="lime", label="SMA5")
    plt.plot(dates, dfp['SMA20'].tolist(), color="cyan", label="SMA20")

    last = c[-1]
    change = (last - c[0]) / c[0] * 100 if len(c) > 1 else 0
    color = "green" if change >= 0 else "red"

    plt.title(f"{sym} → {last:.2f} zł ({change:+.2f}%)")
    
    return Panel(plt.build(), title=f"[bold {color}]{sym}[/]", border_style=color)

# === LAYOUT ===
def make_layout():
    layout = Layout()
    layout.split_column(
        Layout(Panel(Align.center(f"[bold gold1]SANTANDER TERMINAL 2025 – TRUE LIVE (Stooq + yfinance)[/]\n{datetime.now().strftime('%H:%M:%S')}"), style="white on black"), size=3),
        Layout(name="row", ratio=1)
    )
    
    row = Layout()
    charts = [draw_chart(s) for s in SYMBOLS]
    if len(charts) <= 3:
        row.split_row(*charts)
    else:
        row.split_row(charts[0], charts[1], charts[2])
        layout["row"].split_column(row, Layout(name="extra"))
        layout["extra"].split_row(*charts[3:])

    layout["row"].update(row)
    return layout

# === URUCHOMIENIE ===
if __name__ == "__main__":
    # Start wątku danych
    threading.Thread(target=data_updater, daemon=True).start()
    
    console.print("[bold cyan]Santander Terminal 2025 – TRUE LIVE uruchomiony...[/]")
    time.sleep(6)

    try:
        with Live(make_layout(), refresh_per_second=1, screen=True) as live:
            while True:
                live.update(make_layout())
                time.sleep(1)
    except KeyboardInterrupt:
        console.print("\n[red]Zamykam terminal. Do zobaczenia na zielonej stronie! 🚀[/]")
