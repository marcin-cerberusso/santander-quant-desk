# 🚀 SANTANDER QUANT DESK - Cloud Deployment

Professional stock screening and analysis platform for Warsaw Stock Exchange (GPW).

## 🎯 Features

- **Live Market Screener**: WIG20 + mWIG40 real-time analysis
- **Fan Formation Detection**: Automated technical pattern recognition (SMA5 > SMA10 > SMA15 > SMA20)
- **Interactive Charts**: Plotly-powered candlestick charts with zoom, pan, and hover tooltips
- **Technical Indicators**: RSI, SMA overlays, Volume analysis
- **Signal Generation**: Automated BUY/SELL/NEUTRAL recommendations
- **Professional UI**: Dark mode, responsive design, institutional-grade aesthetics

## 🛠️ Tech Stack

- **Backend**: Python 3.12
- **Frontend**: Streamlit
- **Data**: yfinance API
- **Visualization**: Plotly
- **Analysis**: Pandas, NumPy

## 🚀 Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the dashboard
streamlit run dashboard.py
```

## 🌐 Deployment (Railway)

1. Push to GitHub
2. Connect Railway to your repo
3. Railway auto-detects Streamlit and deploys
4. Access via Railway-provided URL

## 📊 Trading Strategy

The platform implements a **GARP (Growth at Reasonable Price)** strategy:

1. **Screen** for stocks with Fan Formation (strong uptrend)
2. **Verify** P/E ratio is reasonable (< 15 default)
3. **Confirm** with RSI and volume patterns
4. **Execute** on pullbacks to SMA5 or SMA10
5. **Exit** when SMA5 crosses below SMA20

## ⚠️ Disclaimer

This tool is for educational and informational purposes only. Not financial advice. Always do your own research before making investment decisions.

---

**Built with** 💚 **by Quant Engineers**

*"In trends we trust, in Excel we don't."*
