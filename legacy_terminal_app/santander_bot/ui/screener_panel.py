# santander_bot/ui/screener_panel.py
from rich.table import Table
from rich.panel import Panel
from rich.align import Align
import pandas as pd

class ScreenerPanel:
    @staticmethod
    def create_table(df: pd.DataFrame, title: str = "🔥 TOP PICKS - FAN FORMATION + GARP") -> Panel:
        """Tworzy elegancką tabelę z wynikami screenera"""
        
        if df.empty:
            return Panel(
                Align.center("[yellow]Brak spółek spełniających kryteria.\nSpróbuj zmniejszyć wymagania.[/]"),
                title="📊 Screener",
                border_style="yellow"
            )
        
        table = Table(show_header=True, header_style="bold magenta", 
                     border_style="cyan", expand=False)
        
        # Kolumny
        table.add_column("#", style="dim", width=3)
        table.add_column("Ticker", style="bold cyan", width=8)
        table.add_column("Price", justify="right", style="white", width=8)
        table.add_column("SMA5", justify="right", style="green", width=8)
        table.add_column("SMA20", justify="right", style="blue", width=8)
        table.add_column("P/E", justify="right", style="yellow", width=7)
        table.add_column("Strength", justify="right", style="magenta", width=9)
        table.add_column("Signal", justify="center", width=8)
        
        # Wiersze
        for idx, row in df.head(10).iterrows():
            strength = row['Strength']
            
            # Kolor strength
            if strength >= 70:
                strength_str = f"[bold green]{strength}%[/]"
            elif strength >= 50:
                strength_str = f"[yellow]{strength}%[/]"
            else:
                strength_str = f"[dim]{strength}%[/]"
            
            # Signal color
            signal = row['Signal']
            if '🔥' in signal:
                signal_str = f"[bold red]{signal}[/]"
            else:
                signal_str = f"[green]{signal}[/]"
            
            table.add_row(
                str(idx + 1),
                row['Ticker'],
                f"{row['Price']:.2f}",
                f"{row['SMA5']:.2f}",
                f"{row['SMA20']:.2f}",
                str(row['P/E']),
                strength_str,
                signal_str
            )
        
        return Panel(
            Align.center(table),
            title=title,
            border_style="gold1",
            subtitle=f"[dim]Showing top {len(df.head(10))} / {len(df)} matches[/]"
        )
