from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt
from rich.console import Console
from rich.table import Table
from config import *
import os
from rich.progress import (
    SpinnerColumn,
    BarColumn,
    Progress,
    TextColumn,
    TimeRemainingColumn,
)
console = Console()


def create_loading(msg, color, process, *args):
    with console.status(f"[bold {color}]{msg}") as status:
        return process(*args)


def create_msg(msg_title, msg, colors,):
    console.print(
        f"[bold {colors['title']}]{msg_title}: [/bold {colors['title']}][bold {colors['text']}]{msg}")


def create_list(index, first, second, colors):
    console.print(
        f"{index}. [bold {colors['title']}]{first} [/bold {colors['title']}] [bold {colors['text']}]({second})")


def create_prompt(prompt_msg):
    return Prompt.ask(f"[{USER_PROMPT}]{prompt_msg}")


def create_panel(banner_msg, banner_inner_text):
    Panel(Text(f"{banner_msg}",
               justify="center", style=f"bold {BANNER['banner_border']}"), title=f"[bold {BANNER['banner_title']}]{banner_inner_text}", border_style=f"{BANNER['banner_border']}", padding=1)


def display_results(results):
    for i, e in enumerate(results):
        create_list(i+1, e['title'], e['year'], TEXT_MSG_COLOR[2])


def displayQualities(available_qualities):
    table = Table(
        title=f"[bold {TEXT_MSG_COLOR[1]}]Available Qualities[/bold {TEXT_MSG_COLOR[1]}]")

    table.add_column("[red]Index[/red]", justify="center",
                     style="cyan", no_wrap=True)
    table.add_column("[blue]Resolution[/blue]",
                     justify="center", style="cyan")
    table.add_column("[#3e28b8]Fansub[/#3e28b8]",
                     justify="center", style="magenta")
    table.add_column("[#2af5a0]Audio[#/2af5a0]",
                     justify="center", style="green")

    for e, i in enumerate(available_qualities):
        table.add_row(f"[red]{e+1}[/red]",
                      f"[blue]{i['quality']}[/blue]", f"[#3e28b8]{i['fansub']}[/#3e28b8]", f"[#2af5a0]{i['audio']}[/#2af5a0]")
    console.print(table)


def createDirectory(anime_name):
    anime_name = anime_name.replace(":", "").replace("/", "")
    parent_dir = "downloads"
    if not os.path.isdir(f"{parent_dir}/{anime_name}"):
        path = os.path.join(parent_dir, anime_name)
        os.mkdir(path)
        create_msg('Success', 'Directory created.', TEXT_MSG_COLOR[0])


progress = Progress(
    TextColumn("[blue]Scraping download links", justify="right"),
    SpinnerColumn(),
    BarColumn(bar_width=40),
    "[progress.percentage]{task.percentage:>3.1f}%",
    "•",
    TimeRemainingColumn(),
)
