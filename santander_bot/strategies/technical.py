# santander_bot/strategies/technical.py
import pandas as pd
import pandas as pd
# import pandas_ta as ta  # Opcjonalnie, ale zrobimy manualnie dla lekkości
from santander_bot.config import RSI_PERIOD, SMA_FAST, SMA_SLOW

class TechnicalAnalyzer:
    @staticmethod
    def add_indicators(df: pd.DataFrame):
        if df.empty or len(df) < SMA_SLOW:
            return df
        
        # SMA
        df['SMA_FAST'] = df['Close'].rolling(window=SMA_FAST).mean()
        df['SMA_SLOW'] = df['Close'].rolling(window=SMA_SLOW).mean()
        
        # RSI (Manual calculation to avoid heavy deps if needed, but pandas is fine)
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=RSI_PERIOD).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=RSI_PERIOD).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # MACD
        exp1 = df['Close'].ewm(span=12, adjust=False).mean()
        exp2 = df['Close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = exp1 - exp2
        df['SIGNAL'] = df['MACD'].ewm(span=9, adjust=False).mean()
        
        return df

    @staticmethod
    def get_signal(df: pd.DataFrame):
        if df.empty or 'RSI' not in df.columns:
            return "NEUTRAL"
        
        last = df.iloc[-1]
        prev = df.iloc[-2]
        
        # Prosta strategia RSI + MACD
        rsi_buy = last['RSI'] < 30
        rsi_sell = last['RSI'] > 70
        
        macd_cross_up = prev['MACD'] < prev['SIGNAL'] and last['MACD'] > last['SIGNAL']
        macd_cross_down = prev['MACD'] > prev['SIGNAL'] and last['MACD'] < last['SIGNAL']
        
        if rsi_buy and macd_cross_up:
            return "STRONG BUY"
        if rsi_sell and macd_cross_down:
            return "STRONG SELL"
        if rsi_buy:
            return "BUY (RSI)"
        if rsi_sell:
            return "SELL (RSI)"
            
        return "HOLD"
