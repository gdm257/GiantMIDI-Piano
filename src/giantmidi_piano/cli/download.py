import typer

from giantmidi_piano import dataset

app = typer.Typer(name='download')

_workspace_option = typer.Option(None, '--workspace', '-w', help='Working directory')


@app.command()
def download_imslp_htmls(
    workspace: str = _workspace_option,
):
    """Download IMSLP htmls."""
    dataset.download_imslp_htmls(workspace)


@app.command()
def download_wikipedia_htmls(
    workspace: str = _workspace_option,
):
    """Download Wikipedia htmls."""
    dataset.download_wikipedia_htmls(workspace)


@app.command()
def create_meta_csv(
    workspace: str = _workspace_option,
):
    """Create meta csv."""
    dataset.create_meta_csv(workspace)


@app.command()
def search_youtube(
    workspace: str = _workspace_option,
    mini_data: bool = False
):
    """Search YouTube."""
    dataset.search_youtube(workspace, mini_data)


@app.command()
def calculate_similarity(
    workspace: str = _workspace_option,
    mini_data: bool = False
):
    """Calculate similarity."""
    dataset.calculate_similarity(workspace, mini_data)


@app.command()
def download_youtube(
    workspace: str = _workspace_option,
    begin_index: int = 0,
    end_index: int = 0,
    mini_data: bool = False
):
    """Download YouTube."""
    dataset.download_youtube(workspace, begin_index, end_index, mini_data)


@app.command()
def download_youtube_piano_solo(
    workspace: str = _workspace_option,
    begin_index: int = 0,
    end_index: int = 0,
    mini_data: bool = False
):
    """Download YouTube piano solo."""
    dataset.download_youtube_piano_solo(workspace, begin_index, end_index, mini_data)
