import typer

from giantmidi_piano import calculate_statistics

app = typer.Typer(name='stats')


@app.command()
def meta_info(
    workspace: str,
    surname_in_youtube_title: bool = False,
):
    """Get meta info."""
    calculate_statistics.meta_info(workspace, surname_in_youtube_title)


@app.command()
def plot_composer_works_num(
    workspace: str,
    surname_in_youtube_title: bool = False,
):
    """Plot composer works num."""
    calculate_statistics.plot_composer_works_num(workspace, surname_in_youtube_title)


@app.command()
def plot_composer_durations(
    workspace: str,
    surname_in_youtube_title: bool = False,
):
    """Plot composer durations."""
    calculate_statistics.plot_composer_durations(workspace, surname_in_youtube_title)


@app.command()
def plot_nationalities(
    workspace: str,
):
    """Plot nationalities."""
    calculate_statistics.plot_nationalities(workspace)


@app.command()
def calculate_music_events_from_midi(
    workspace: str,
):
    """Calculate music events from midi."""
    calculate_statistics.calculate_music_events_from_midi(workspace)


@app.command()
def plot_note_histogram(
    workspace: str,
    surname_in_youtube_title: bool = False,
):
    """Plot note histogram."""
    calculate_statistics.plot_note_histogram(workspace, surname_in_youtube_title)


@app.command()
def plot_mean_std_notes(
    workspace: str,
    surname_in_youtube_title: bool = False,
):
    """Plot mean std notes."""
    calculate_statistics.plot_mean_std_notes(workspace, surname_in_youtube_title)


@app.command()
def plot_notes_per_second_mean_std(
    workspace: str,
    surname_in_youtube_title: bool = False,
):
    """Plot notes per second mean std."""
    calculate_statistics.plot_notes_per_second_mean_std(workspace, surname_in_youtube_title)


@app.command()
def plot_pedals_per_piece_mean_std(
    workspace: str,
):
    """Plot pedals per piece mean std."""
    raise NotImplementedError


@app.command()
def plot_selected_composers_note_histogram(
    workspace: str,
    surname_in_youtube_title: bool = False,
):
    """Plot selected composers note histogram."""
    calculate_statistics.plot_selected_composers_note_histogram(workspace, surname_in_youtube_title)


@app.command()
def plot_selected_composers_chroma(
    workspace: str,
    surname_in_youtube_title: bool = False,
):
    """Plot selected composers chroma."""
    calculate_statistics.plot_selected_composers_chroma(workspace, surname_in_youtube_title)


@app.command()
def plot_selected_composers_intervals(
    workspace: str,
    surname_in_youtube_title: bool = False,
):
    """Plot selected composers intervals."""
    calculate_statistics.plot_selected_composers_intervals(workspace, surname_in_youtube_title)


@app.command()
def plot_selected_composers_chords(
    workspace: str,
    n_chords: int,
    surname_in_youtube_title: bool = False,
):
    """Plot selected composers chords."""
    calculate_statistics.plot_selected_composers_chords(workspace, n_chords, surname_in_youtube_title)


@app.command()
def note_intervals(
    workspace: str,
):
    """Note intervals."""
    raise NotImplementedError
