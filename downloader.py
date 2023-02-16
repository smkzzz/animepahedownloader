from rich.progress import (
    SpinnerColumn,
    BarColumn,
    DownloadColumn,
    Progress,
    TaskID,
    TextColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
)
from fileinput import filename
import requests
import time
from pathlib import Path
from rich.progress import Progress
import signal
from typing import Iterable
from concurrent.futures import ThreadPoolExecutor
from threading import Event
import os
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
progress_table = Table.grid()

done_event = Event()


def handle_sigint(signum, frame):
    done_event.set()


signal.signal(signal.SIGINT, handle_sigint)

# try:
#     text = requests.get(url, timeout=10.0).text
# except requests.exceptions.Timeout:
#     print("No interne")


progress = Progress(
    TextColumn("[blue]{task.fields[filename]}", justify="right"),
    BarColumn(bar_width=40),
    "[progress.percentage]{task.percentage:>3.1f}%",
    "•",
    DownloadColumn(),
    "•",
    TransferSpeedColumn(),
    "•",
    TimeRemainingColumn(),
)


class Downloader():
    def __init__(self, urls: Iterable[str], filename: str, directory: str, max: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attempts = 5
        self.downloads = urls
        self.filename = filename
        self.directory = directory
        self.max = max

    def downloader(self, task_id: TaskID, url, name, directory, ref=None, resume_byte_pos: int = None):
        byte = resume_byte_pos

        DOWNLOAD_FOLDER = Path(directory)

        try:

            r = requests.head(url, timeout=2)
            file_size = int(r.headers.get('content-length', 0))
            file = DOWNLOAD_FOLDER / f"{name}.mp4"
            if ref == "fail":
                resume_byte_pos = file.stat().st_size
            resume_header = ({'Range': f'bytes={resume_byte_pos}-'}
                             if resume_byte_pos else None)
            self.attempts += 1
            try:
                r = requests.get(url, stream=True,
                                 headers=resume_header, timeout=10)
                block_size = 1024
                initial_pos = resume_byte_pos if resume_byte_pos else 0
                mode = 'ab' if resume_byte_pos else 'wb'

                progress.update(task_id, total=file_size)
                with open(file, mode) as f:
                    progress.start_task(task_id)

                    # download = progress.add_task("[green]Downloading "+file.name+" ",total=file_size)
                    progress.update(task_id, advance=resume_byte_pos)
                    for chunk in r.iter_content(32 * block_size):
                        f.write(chunk)
                        progress.update(task_id, advance=len(chunk))
                        if done_event.is_set():
                            return

                return "1"
            except Exception as e:
                print(e)
                if self.attempts > 0:
                    print(
                        f"Connection timeout, retrying to reconnect... {self.attempts} left.")
                    self.attempts -= 1
                    self.downloader(url, name, directory, "fail", byte)
                time.sleep(3)
            # Set configuration

        except Exception as e:
            if self.attempts == 0:
                print("0")
                return 0
            print(f"way net {self.attempts} left.")
            if self.attempts > 0:
                self.attempts -= 1
                self.downloader(url, name, directory, "fail", byte)
            time.sleep(3)

    def download_file(self, task_id: TaskID, url, name, directory, attemps=5) -> None:

        DOWNLOAD_FOLDER = Path(directory)
        try:
            r = requests.head(url)
            file_size_online = int(r.headers.get('content-length', 0))
            file = DOWNLOAD_FOLDER / f"{name}.mp4"
            if file.exists():
                file_size_offline = file.stat().st_size

                if file_size_online != file_size_offline:
                 #   print("\t\tResuming Download")
                    self.downloader(task_id, url, name, directory,
                                    "s", file_size_offline)
                else:
                    #print("\t\tDownload is already complete.")
                    pass
            else:
                self.downloader(task_id, url, name, directory)
        except Exception as e:
            if self.attempts > 0:
                print(e)
               # print(f"\t\tConnection timeout retrying... {self.attempts} left")
                self.attempts -= 1
                time.sleep(5)
                self.download_file(task_id, url, name, directory, attemps)
            else:
               # print("\t\tTry again later")
                return

    def start(self):
        os.system("cls")
        tasks = []
        progress_table = Table.grid(expand=True)
        for i, download in enumerate(self.downloads):
            directory = self.directory
            filename = self.filename + \
                " Episode "+str(download['episode'])
            task_id = progress.add_task(
                "download", filename=filename, start=False)
            tasks.insert(i, {'filename': filename,
                         'url': download['url'], 'task': task_id})
        progress_table.add_column(justify="center")
        progress_table.add_row(
            Panel.fit(progress, title="[b][#2af5a0]Downloading Episodes[/#2af5a0]",
                      border_style="#2af5a0", padding=(1, 2), subtitle="Developed By Allan :sunglasses:."),
        )
        with Live(progress_table, refresh_per_second=10):
            with ThreadPoolExecutor(max_workers=self.max) as pool:
                for task in tasks:
                    directory = self.directory
                    pool.submit(
                        self.download_file, task['task'], task['url'], task['filename'], directory)

            # for i in tasks:
            #     progress.remove_task(i)

            return [tasks, progress]
