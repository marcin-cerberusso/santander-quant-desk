# santander_bot/main.py
import time
import sys
import os
from rich.live import Live
from rich.console import Console
from rich.layout import Layout
from santander_bot.config import SYMBOLS
from santander_bot.core.data import DataManager
from santander_bot.ui.terminal import TerminalUI
from santander_bot.strategies.screener import ScreenerEngine
from santander_bot.ui.screener_panel import ScreenerPanel
from santander_bot.core.tracing import setup_tracing, tracer
import threading

console = Console()

class SantanderTerminal:
    def __init__(self):
        self.dm = DataManager()
        self.ui = TerminalUI(self.dm)
        self.screener = ScreenerEngine()
        self.screener_results = None
        self.screener_lock = threading.Lock()
    
    def update_screener(self):
        """Aktualizuj screener co 60 sekund (background)"""
        while True:
            try:
                with tracer.start_as_current_span("update_screener"):
                    console.print("[dim]Uruchamianie screenera...[/]")
                    results = self.screener.run_screener(max_pe=15.0, require_fan=True)
                    with self.screener_lock:
                        self.screener_results = results
                    console.print(f"[dim green]✓ Screener: {len(results)} spółek znaleziono[/]")
            except Exception as e:
                console.print(f"[dim red]⚠ Screener error: {e}[/]")
            
            time.sleep(60)  # Co minutę
    
    def make_full_layout(self):
        """Layout: Header + Screener + Charts"""
        from rich.panel import Panel
        from rich.align import Align
        from datetime import datetime
        
        layout = Layout()
        
        # Header
        header_text = f"[bold gold1]SANTANDER TERMINAL PRO 2025 - GARP SCREENER[/]\n{datetime.now().strftime('%H:%M:%S')}"
        
        # Screener panel
        with self.screener_lock:
            if self.screener_results is not None and not self.screener_results.empty:
                screener_panel = ScreenerPanel.create_table(self.screener_results)
            else:
                screener_panel = Panel("[yellow]Screener ładuje dane...[/]", title="📊 Screener")
        
        # Charts layout
        charts_layout = Layout()
        charts = [self.ui.draw_chart(s) for s in SYMBOLS]
        
        if len(charts) <= 3:
            charts_layout.split_row(*charts)
        else:
            top = Layout()
            bottom = Layout()
            top.split_row(*charts[:3])
            bottom.split_row(*charts[3:])
            charts_layout.split_column(top, bottom)
        
        # Final layout
        layout.split_column(
            Layout(Panel(Align.center(header_text), style="white on black"), size=3),
            Layout(screener_panel, size=16),  # Screener table
            Layout(charts_layout, ratio=1)     # Charts grid
        )
        
        return layout

def main():
    console.print("[bold cyan]🔥 Inicjalizacja Santander Terminal Pro + GARP Screener...[/]")
    
    # 0. Setup Tracing
    setup_tracing()

    # 1. Init Terminal
    terminal = SantanderTerminal()
    
    # 2. Start data feed
    terminal.dm.start()
    
    # 3. Start screener w tle
    threading.Thread(target=terminal.update_screener, daemon=True).start()
    
    console.print("[green]✓ System gotowy. Uruchamianie...[/]")
    time.sleep(3)

    try:
        with Live(terminal.make_full_layout(), refresh_per_second=1, screen=True) as live:
            while True:
                live.update(terminal.make_full_layout())
                time.sleep(1)
    except KeyboardInterrupt:
        console.print("\n[red]🛑 Terminal zamknięty. May the trend be with you! 🚀[/]")
        sys.exit(0)

if __name__ == "__main__":
    main()
