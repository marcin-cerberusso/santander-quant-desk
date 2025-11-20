# santander_bot/ui/terminal.py
import plotext as plt
from rich.panel import Panel
from rich.layout import Layout
from rich.align import Align
from rich.table import Table
from datetime import datetime
from santander_bot.strategies.technical import TechnicalAnalyzer

class TerminalUI:
    def __init__(self, data_manager):
        self.dm = data_manager

    def draw_chart(self, sym):
        df = self.dm.get_data(sym)
        
        if df.empty or len(df) < 20:
            return Panel(f"[yellow]Ładowanie {sym}...[/]", title=sym)

        # Oblicz wskaźniki
        df = TechnicalAnalyzer.add_indicators(df)
        dfp = df.tail(60)

        dates = [t.strftime("%d/%m/%Y %H:%M") for t in dfp.index]
        o = dfp['Open'].tolist()
        h = dfp['High'].tolist()
        l = dfp['Low'].tolist()
        c = dfp['Close'].tolist()

        plt.clf()
        # plt.date_form("%d/%m/%Y %H:%M")  # Disable buggy date parsing
        plt.theme("matrix")
        plt.plotsize(80, 20)
        
        # Use integer indices for X axis to avoid date parsing errors
        x_axis = list(range(len(dates)))
        data = {"Open": o, "High": h, "Low": l, "Close": c}
        
        # Plotext candlestick with integer X
        plt.candlestick(x_axis, data)
        
        # Set x-ticks manually (show every Nth label to avoid clutter)
        step = max(1, len(dates) // 5)
        plt.xticks(x_axis[::step], dates[::step])
        
        # Rysuj SMA
        if 'SMA_FAST' in dfp.columns:
            plt.plot(x_axis, dfp['SMA_FAST'].tolist(), color="lime", label="SMA5")
        if 'SMA_SLOW' in dfp.columns:
            plt.plot(x_axis, dfp['SMA_SLOW'].tolist(), color="cyan", label="SMA20")

        last_price = c[-1]
        start_price = c[0]
        change = (last_price - start_price) / start_price * 100
        color = "green" if change >= 0 else "red"
        
        # Sygnał
        signal = TechnicalAnalyzer.get_signal(df)
        sig_color = "white"
        if "BUY" in signal: sig_color = "green"
        if "SELL" in signal: sig_color = "red"

        plt.title(f"{sym} : {last_price:.2f} zł ({change:+.2f}%) | SIG: {signal}")
        
        return Panel(plt.build(), title=f"[bold {color}]{sym}[/]", border_style=color)

    def make_layout(self, symbols):
        layout = Layout()
        
        # Header
        header_text = f"[bold gold1]SANTANDER BOT PRO 2025[/]\n{datetime.now().strftime('%H:%M:%S')}"
        layout.split_column(
            Layout(Panel(Align.center(header_text), style="white on black"), size=3),
            Layout(name="body")
        )
        
        # Charts Grid
        row = Layout()
        charts = [self.draw_chart(s) for s in symbols]
        
        # Simple grid logic (max 6)
        if len(charts) <= 3:
            row.split_row(*charts)
            layout["body"].update(row)
        else:
            top = Layout()
            bottom = Layout()
            top.split_row(*charts[:3])
            bottom.split_row(*charts[3:])
            layout["body"].split_column(top, bottom)

        return layout
