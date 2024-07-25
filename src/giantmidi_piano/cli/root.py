from typer import Typer

from .convert import app as convert_command
from .download import app as download_command
from .split import app as split_command
from .stats import app as stats_command

root_command = Typer()
root_command.add_typer(convert_command)
root_command.add_typer(download_command)
root_command.add_typer(split_command)
root_command.add_typer(stats_command)
