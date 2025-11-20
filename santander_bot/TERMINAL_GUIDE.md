# SANTANDER TERMINAL PRO 2025 - DOCUMENTATION

## 🚀 QUICK START

```bash
cd /home/marcin/Downloads/CopyW
./santander_bot/RUN_TERMINAL.sh
```

## 🎯 CO ROBI TEN TERMINAL?

### 1. **GARP SCREENER** (Growth at Reasonable Price)
- Skanuje **WIG20 + mWIG40** co 60 sekund
- Filtruje spółki według:
  - **Fan Formation**: SMA5 > SMA10 > SMA15 > SMA20
  - **P/E < 15** (można zmienić)
  - **Strength Score**: 0-100% (siła trendu)
- Pokazuje **TOP 10** najlepszych okazji

### 2. **LIVE CHARTS** (6 watchlist stocks)
- Wykresy świecowe w czasie rzeczywistym
- SMA5 (zielona) + SMA20 (cyan)
- Dual data feed: Stooq (live) + yfinance (backup)
- Automatyczne sygnały BUY/SELL/HOLD

### 3. **TECHNICAL ANALYSIS**
- RSI (14-period)
- MACD (12/26/9)
- Moving averages convergence
- Real-time signal generation

---

## 📊 INTERPRETACJA WYNIKÓW

### Screener Table:
```
Ticker | Price | SMA5 | SMA20 | P/E | Strength | Signal
CDR    | 258   | 260  | 240   | 8.5 | 89.2%    | 🔥 BUY
```

**Strength Score**:
- **70-100%** 🟢 = Silny trend wzrostowy (BUY)
- **50-70%** 🟡 = Umiarkowany trend (HOLD)
- **0-50%** 🔴 = Słaby sygnał (SKIP)

**Fan Formation**:
- Im większy spacing między SMA, tym silniejszy trend
- Cena powyżej wszystkich SMA = maximum strength

### Sygnały:
- **🔥 BUY** = Fan Formation + Strength > 50% + P/E OK
- **✓ OK** = Fan Formation, ale niższa siła

---

## ⚙️ KONFIGURACJA

### Zmień watchlist (wykresy):
```python
# santander_bot/config.py
SYMBOLS = ["CDR", "LPP", "XTB", "11B", "PKO", "ALE"]  # Twoje spółki
```

### Zmień kryteria screenera:
```python
# W santander_bot/main.py, linia ~28
results = self.screener.run_screener(
    max_pe=15.0,        # Zwiększ dla więcej wyników
    require_fan=True    # False = pokaż wszystkie z dobrym P/E
)
```

### Zmień częstotliwość screenera:
```python
# santander_bot/main.py, linia ~35
time.sleep(60)  # 60s = co minutę, zmień na 30/120/etc
```

---

## 🧠 STRATEGIA TRADING

### GARP Strategy (Warren Buffett style):
1. **Screener wskazuje** spółki z Fan Formation + P/E < 15
2. **Sprawdź wykres** czy trend wciąż trwa (SMA rosnące)
3. **Czekaj na pullback** do SMA5 lub SMA10
4. **Kup** gdy RSI < 40 i MACD cross up
5. **Sprzedaj** gdy:
   - SMA5 przecina SMA20 w dół (Fan breakdown)
   - RSI > 70 (overbought)
   - Strength < 30%

### Risk Management:
- **Stop Loss**: -5% od entry
- **Take Profit**: +15-20% lub trailing stop na SMA10
- **Position size**: Max 10% portfolio per stock

---

## 📂 STRUKTURA PROJEKTU

```
santander_bot/
├── main.py                    # Entry point
├── config.py                  # Settings
├── RUN_TERMINAL.sh           # Quick launcher
├── core/
│   └── data.py               # Data feed (Stooq + yfinance)
├── strategies/
│   ├── technical.py          # RSI, MACD, SMA
│   └── screener.py           # Fan Formation screener
└── ui/
    ├── terminal.py           # Charts UI
    └── screener_panel.py     # Screener table UI
```

---

## 🔧 TROUBLESHOOTING

### "Brak spółek spełniających kryteria"
→ Zwiększ `max_pe` do 20-25 lub ustaw `require_fan=False`

### "Screener ładuje dane..."
→ Poczekaj 60s, pierwszy scan trwa dłużej (pobiera dane dla 36 spółek)

### Błędy yfinance
→ Normalne dla niektórych tickerów (delisted/nieaktywne)

### Wykresy nie pokazują danych
→ Poczekaj 5-10s, data feed startuje w tle

---

## 💡 ROADMAP v2.0

- [ ] Alert system (Telegram/Email)
- [ ] Backtesting engine
- [ ] Portfolio tracker
- [ ] Sentiment analysis (Twitter/Reddit)
- [ ] ML predictions (LSTM)
- [ ] Options flow integration

---

**Made with 🔥 by Santander Quant Team**

*"In trends we trust, in Excel we don't."*
