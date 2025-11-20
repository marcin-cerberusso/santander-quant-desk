# santander_bot/strategies/screener.py
import pandas as pd
import yfinance as yf
from typing import List, Dict
import numpy as np

# WIG20 + mWIG40 Top Liquid (hardcoded dla szybkości)
WIG20_TICKERS = [
    "CDR", "PKN", "PEO", "PZU", "PKO", "PGE", "LPP", "KGH", 
    "DNP", "JSW", "XTB", "ALE", "CCC", "OPL", "LTS", 
    "MBK", "SPL", "TPS", "11B", "CPS"
]

MWIG40_TOP = [
    "BDX", "EAT", "KER", "MRC", "PLW", "SNX", "VRG", "WLT",
    "ASE", "BOS", "CLN", "DVL", "ENA", "EUR", "GTC", "IMC"
]

ALL_TICKERS = WIG20_TICKERS + MWIG40_TOP

class ScreenerEngine:
    def __init__(self):
        self.cache = {}
    
    def get_stock_data(self, ticker: str, period: str = "3mo") -> pd.DataFrame:
        """Pobierz dane OHLCV dla tickera"""
        try:
            stock = yf.Ticker(f"{ticker}.WA")
            df = stock.history(period=period)
            
            if df.empty:
                return pd.DataFrame()
            
            # Fix MultiIndex if needed
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.droplevel(1)
            
            return df
        except Exception as e:
            return pd.DataFrame()
    
    def calculate_smas(self, df: pd.DataFrame) -> Dict[str, float]:
        """Oblicz SMA 5/10/15/20"""
        if df.empty or len(df) < 20:
            return {}
        
        close = df['Close']
        return {
            'SMA5': close.rolling(5).mean().iloc[-1],
            'SMA10': close.rolling(10).mean().iloc[-1],
            'SMA15': close.rolling(15).mean().iloc[-1],
            'SMA20': close.rolling(20).mean().iloc[-1],
            'Price': close.iloc[-1]
        }
    
    def check_fan_formation(self, smas: Dict[str, float]) -> bool:
        """Sprawdź Fan Formation: SMA5 > SMA10 > SMA15 > SMA20"""
        if not smas or len(smas) < 4:
            return False
        
        return (smas['SMA5'] > smas['SMA10'] > 
                smas['SMA15'] > smas['SMA20'])
    
    def get_pe_ratio(self, ticker: str) -> float:
        """Pobierz C/Z (P/E ratio)"""
        try:
            stock = yf.Ticker(f"{ticker}.WA")
            info = stock.info
            
            # yfinance może zwrócić różne klucze
            pe = info.get('trailingPE') or info.get('forwardPE') or None
            
            if pe and pe > 0:
                return round(pe, 2)
            return None
        except Exception:
            return None
    
    def calculate_strength_score(self, smas: Dict[str, float]) -> float:
        """
        Oblicz siłę sygnału (0-100)
        Im większy spacing między SMA, tym silniejszy trend
        """
        if not smas or len(smas) < 4:
            return 0
        
        price = smas['Price']
        sma5 = smas['SMA5']
        sma20 = smas['SMA20']
        
        # % odległość ceny od SMA20 (im większa, tym silniejszy trend)
        distance = ((price - sma20) / sma20) * 100
        
        # Sprawdź spacing między SMA
        spacing_score = 0
        if sma5 > smas['SMA10']:
            spacing_score += 25
        if smas['SMA10'] > smas['SMA15']:
            spacing_score += 25
        if smas['SMA15'] > sma20:
            spacing_score += 25
        
        # Price > SMA5 = bonus
        if price > sma5:
            spacing_score += 25
        
        # Final score = weighted average
        strength = (distance * 0.6) + (spacing_score * 0.4)
        
        return max(0, min(100, strength))  # Clamp 0-100
    
    def run_screener(self, 
                     tickers: List[str] = None,
                     max_pe: float = 12.0,
                     require_fan: bool = True) -> pd.DataFrame:
        """
        🔥 GŁÓWNA FUNKCJA SCREENERA
        
        Args:
            tickers: Lista tickerów (default: WIG20)
            max_pe: Maks C/Z (default: 12)
            require_fan: Wymóg Fan Formation (default: True)
        
        Returns:
            DataFrame z rankingiem spółek
        """
        if tickers is None:
            tickers = WIG20_TICKERS
        
        results = []
        
        for ticker in tickers:
            # 1. Pobierz dane
            df = self.get_stock_data(ticker)
            if df.empty:
                continue
            
            # 2. Oblicz SMA
            smas = self.calculate_smas(df)
            if not smas:
                continue
            
            # 3. Sprawdź Fan Formation
            has_fan = self.check_fan_formation(smas)
            
            if require_fan and not has_fan:
                continue
            
            # 4. Pobierz P/E
            pe = self.get_pe_ratio(ticker)
            
            # Filtr P/E (jeśli dane dostępne)
            if pe is not None and pe > max_pe:
                continue
            
            # 5. Oblicz siłę sygnału
            strength = self.calculate_strength_score(smas)
            
            # 6. Dodaj do wyników
            results.append({
                'Ticker': ticker,
                'Price': round(smas['Price'], 2),
                'SMA5': round(smas['SMA5'], 2),
                'SMA10': round(smas['SMA10'], 2),
                'SMA15': round(smas['SMA15'], 2),
                'SMA20': round(smas['SMA20'], 2),
                'P/E': pe if pe else 'N/A',
                'Strength': round(strength, 1),
                'Signal': '🔥 BUY' if has_fan and strength > 50 else '✓ OK'
            })
        
        # Sortuj po sile sygnału
        df_results = pd.DataFrame(results)
        if not df_results.empty:
            df_results = df_results.sort_values('Strength', ascending=False)
        
        return df_results


# === QUICK RUNNER ===
def quick_screen(max_results: int = 10) -> pd.DataFrame:
    """Szybki screen top 10 spółek"""
    screener = ScreenerEngine()
    df = screener.run_screener(tickers=WIG20_TICKERS, max_pe=15.0, require_fan=True)
    return df.head(max_results)


if __name__ == "__main__":
    # Test
    print("🔥 SANTANDER SCREENER - Fan Formation + GARP")
    print("=" * 80)
    
    screener = ScreenerEngine()
    results = screener.run_screener(max_pe=15.0)
    
    if not results.empty:
        print(results.to_string(index=False))
        print(f"\n✅ Znaleziono {len(results)} spółek spełniających kryteria")
    else:
        print("⚠️  Brak spółek spełniających kryteria (spróbuj zwiększyć max_pe)")
