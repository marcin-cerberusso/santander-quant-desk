# santander_bot/core/data.py
import threading
import time
import pandas as pd
import yfinance as yf
import requests
from datetime import datetime
from santander_bot.config import SYMBOLS, MARKET_OPEN_HOUR, MARKET_CLOSE_HOUR, REFRESH_RATE

class DataManager:
    def __init__(self):
        self.data_store = {sym: pd.DataFrame() for sym in SYMBOLS}
        self.lock = threading.Lock()
        self.running = True

    def get_stooq_price(self, ticker):
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
        except Exception:
            pass
        return None

    def get_yfinance_data(self, ticker):
        try:
            df = yf.download(f"{ticker}.WA", period="5d", interval="5m", progress=False)
            if not df.empty:
                # Fix for yfinance returning MultiIndex
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.droplevel(1)
                
                df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
                return df
        except Exception:
            pass
        return pd.DataFrame()

    def update_loop(self):
        while self.running:
            for sym in SYMBOLS:
                # 1. Stooq (Live)
                stooq = self.get_stooq_price(sym)
                now = datetime.now()
                is_market_hours = MARKET_OPEN_HOUR <= now.hour < MARKET_CLOSE_HOUR
                
                # Sprawdź czy dane ze Stooq są dzisiejsze
                is_today = stooq and now.strftime("%Y-%m-%d") in str(stooq["time"])

                if stooq and (is_today or is_market_hours):
                    new_row = pd.DataFrame([{
                        "Open": stooq["open"],
                        "High": stooq["high"],
                        "Low": stooq["low"],
                        "Close": stooq["close"],
                        "Volume": stooq["volume"]
                    }], index=[now])
                    
                    with self.lock:
                        if sym in self.data_store:
                            self.data_store[sym] = pd.concat([self.data_store[sym], new_row]).tail(100)
                        else:
                            self.data_store[sym] = new_row
                else:
                    # 2. Fallback yfinance
                    df = self.get_yfinance_data(sym)
                    if not df.empty:
                        with self.lock:
                            self.data_store[sym] = df.tail(100)
            
            time.sleep(REFRESH_RATE)

    def start(self):
        threading.Thread(target=self.update_loop, daemon=True).start()

    def get_data(self, sym):
        with self.lock:
            return self.data_store.get(sym, pd.DataFrame()).copy()
