from rich.console import Console
from src.interfaces.notifier import INotifier

class RichNotifier(INotifier):
    def __init__(self):
        self.console = Console()
        
    def info(self, msg: str) -> None:
        self.console.print(f"[bold blue]INFO[/]: {msg}")
        
    def success(self, msg: str) -> None:
        self.console.print(f"[bold green]SUCCESS[/]: {msg}")
        
    def error(self, msg: str, exception: Exception = None) -> None:
        self.console.print(f"[bold red]ERROR[/]: {msg}")
        if exception:
            self.console.print(f"[red]{str(exception)}[/]")
            
    def progress(self, current: int, total: int, prefix: str = "") -> None:
        self.console.print(f"[bold cyan]PROGRESS[/]: {prefix} ({current}/{total})")
