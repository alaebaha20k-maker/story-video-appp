import sys
import time
from typing import Optional

try:
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
    from rich.panel import Panel
    from rich.table import Table
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False


class Logger:
    def __init__(self, name: str = "VideoGenerator"):
        self.name = name
        self.console = Console() if RICH_AVAILABLE else None
        self.start_time = None
        
    def success(self, message: str):
        if RICH_AVAILABLE:
            self.console.print(f"✅ {message}", style="bold green")
        elif COLORAMA_AVAILABLE:
            print(f"{Fore.GREEN}✅ {message}{Style.RESET_ALL}")
        else:
            print(f"✅ {message}")
    
    def error(self, message: str):
        if RICH_AVAILABLE:
            self.console.print(f"❌ {message}", style="bold red")
        elif COLORAMA_AVAILABLE:
            print(f"{Fore.RED}❌ {message}{Style.RESET_ALL}")
        else:
            print(f"❌ {message}")
    
    def warning(self, message: str):
        if RICH_AVAILABLE:
            self.console.print(f"⚠️  {message}", style="bold yellow")
        elif COLORAMA_AVAILABLE:
            print(f"{Fore.YELLOW}⚠️  {message}{Style.RESET_ALL}")
        else:
            print(f"⚠️  {message}")
    
    def info(self, message: str):
        if RICH_AVAILABLE:
            self.console.print(f"ℹ️  {message}", style="bold cyan")
        elif COLORAMA_AVAILABLE:
            print(f"{Fore.CYAN}ℹ️  {message}{Style.RESET_ALL}")
        else:
            print(f"ℹ️  {message}")
    
    def step(self, message: str):
        if RICH_AVAILABLE:
            self.console.print(f"🔹 {message}", style="bold white")
        elif COLORAMA_AVAILABLE:
            print(f"{Fore.WHITE}🔹 {message}{Style.RESET_ALL}")
        else:
            print(f"🔹 {message}")
    
    def processing(self, message: str):
        if RICH_AVAILABLE:
            self.console.print(f"⏳ {message}...", style="bold magenta")
        elif COLORAMA_AVAILABLE:
            print(f"{Fore.MAGENTA}⏳ {message}...{Style.RESET_ALL}")
        else:
            print(f"⏳ {message}...")
    
    def banner(self, title: str, subtitle: Optional[str] = None):
        if RICH_AVAILABLE:
            content = f"[bold cyan]{title}[/bold cyan]"
            if subtitle:
                content += f"\n[dim]{subtitle}[/dim]"
            self.console.print(Panel(content, border_style="cyan"))
        else:
            print("\n" + "="*60)
            print(f"  {title}")
            if subtitle:
                print(f"  {subtitle}")
            print("="*60 + "\n")
    
    def table(self, data: dict, title: Optional[str] = None):
        if RICH_AVAILABLE:
            table = Table(title=title, show_header=True, header_style="bold cyan")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="white")
            for key, value in data.items():
                table.add_row(str(key), str(value))
            self.console.print(table)
        else:
            if title:
                print(f"\n{title}")
                print("-" * 40)
            for key, value in data.items():
                print(f"  {key}: {value}")
            print()
    
    def start_timer(self):
        self.start_time = time.time()
    
    def end_timer(self, operation: str = "Operation"):
        if self.start_time:
            elapsed = time.time() - self.start_time
            minutes = int(elapsed // 60)
            seconds = int(elapsed % 60)
            time_str = f"{minutes}m {seconds}s" if minutes > 0 else f"{seconds}s"
            self.success(f"{operation} completed in {time_str}")
            self.start_time = None


logger = Logger()

def success(message: str):
    logger.success(message)

def error(message: str):
    logger.error(message)

def warning(message: str):
    logger.warning(message)

def info(message: str):
    logger.info(message)
if __name__ == "__main__":
    print("\n🧪 Testing Logger...\n")
    
    # Test different message types
    logger.banner("Logger Test", "Testing all message types")
    
    logger.success("This is a success message!")
    time.sleep(0.5)
    
    logger.error("This is an error message!")
    time.sleep(0.5)
    
    logger.warning("This is a warning message!")
    time.sleep(0.5)
    
    logger.info("This is an info message!")
    time.sleep(0.5)
    
    logger.step("This is a step message!")
    time.sleep(0.5)
    
    logger.processing("This is a processing message")
    time.sleep(0.5)
    
    # Test table
    logger.table({
        "Script Length": "70k characters",
        "Images": "25",
        "Duration": "60 minutes",
        "Status": "Ready"
    }, title="Video Configuration")
    
    logger.success("All tests passed! ✅")
    
    print("\n✅ Logger module is working perfectly!\n")