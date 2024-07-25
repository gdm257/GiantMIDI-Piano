import typer

from giantmidi_piano import audios_to_midis

app = typer.Typer(
    name='convert',
)


@app.command()
def calculate_piano_solo_prob(
    workspace: str = typer.Option(..., help='Directory of your workspace.'),
    mp3s_dir: str = typer.Option(..., help='Directory of the downloaded YouTube mp3s.'),
    mini_data: bool = typer.Option(False, help='Use mini data or not.'),
):
    """Calculate the piano solo probability of all downloaded mp3s, and append the probability to the meta csv file."""
    audios_to_midis.calculate_piano_solo_prob(workspace, mp3s_dir, mini_data)


@app.command()
def transcribe_piano(  # noqa: PLR0913
    workspace: str = typer.Option(None, help='Directory of your workspace.'),
    mp3s_dir: str = typer.Option(None, help='Directory of the downloaded YouTube mp3s.'),
    midis_dir: str = typer.Option(None, help='Directory to save the transcribed midi files.'),
    begin_index: int = typer.Option(None, help='Beginning index of mp3s to transcribe.'),
    end_index: int = typer.Option(None, help='Ending index (exclusive) of mp3s to transcribe.'),
    mini_data: bool = typer.Option(False, help='Use mini data or not.'),
):
    """Transcribe piano solo mp3s to midi files.

    Args:
        workspace (str): Directory of your workspace.
        mp3s_dir (str): Directory of the downloaded YouTube mp3s.
        midis_dir (str): Directory to save the transcribed midi files.
        begin_index (int): Beginning index of mp3s to transcribe.
        end_index (int): Ending index (exclusive) of mp3s to transcribe.
        mini_data (bool): Use mini data or not.
    """
    audios_to_midis.transcribe_piano(workspace, mp3s_dir, midis_dir, begin_index, end_index, mini_data)
