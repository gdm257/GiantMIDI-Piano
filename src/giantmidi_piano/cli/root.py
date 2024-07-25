from typer import Typer

from .download import app as download_command

root_command = Typer()
root_command.add_typer(download_command)
