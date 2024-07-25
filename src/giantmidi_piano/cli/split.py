import typer

from giantmidi_piano import create_split

app = typer.Typer(name='split')


@app.command()
def create_piano_split(
    workspace: str = typer.Option(..., help='Directory of your workspace.'),
):
    """Create piano split."""
    create_split.create_piano_split(workspace)


@app.command()
def create_surname_checked_subset(
    workspace: str = typer.Option(..., help='Directory of your workspace.'),
):
    """Create surname checked subset."""
    create_split.create_surname_checked_subset(workspace)
