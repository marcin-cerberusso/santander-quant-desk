# Santander Bot Pro 2025

Professional algorithmic trading bot structure for GPW (Warsaw Stock Exchange).

## Structure
- **`main.py`**: Entry point. Initializes data feed and UI.
- **`config.py`**: Configuration (Symbols, timeframes, indicators).
- **`core/`**:
  - `data.py`: Data Manager handling Stooq (Live) and yfinance (History/Fallback).
- **`strategies/`**:
  - `technical.py`: Technical analysis (RSI, MACD, SMA) and signal generation.
- **`ui/`**:
  - `terminal.py`: TUI implementation using `rich` and `plotext`.

## Features
- **Hybrid Data Feed**: Real-time (Stooq) + Historical (yfinance).
- **Technical Analysis**: Zero-dependency RSI and MACD calculation.
- **Visuals**: Matrix-themed candlestick charts in the terminal.
- **Signals**: Real-time BUY/SELL signals based on strategy.

## Running
```bash
export PYTHONPATH=$PYTHONPATH:.
.venv/bin/python santander_bot/main.py
```
