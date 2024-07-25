from typer import Typer

from .convert import app as convert_command
from .download import app as download_command

root_command = Typer()
root_command.add_typer(convert_command)
root_command.add_typer(download_command)
