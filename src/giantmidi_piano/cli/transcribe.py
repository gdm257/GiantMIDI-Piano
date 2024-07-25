import typer

from giantmidi_piano import evaluate_transcribed_midis

app = typer.Typer(name='transcribe')


@app.command()
def align(
    csv_path: str = typer.Argument(
        'midis_for_evaluation/groundtruth_maestro_giantmidi-piano.csv',
        help='groundtruth csv path',
    ),
):
    """Align groundtruth csv with transcribed midis."""
    evaluate_transcribed_midis.align()


@app.command()
def plot_box_plot(
    fig_path: str = typer.Argument('results/transcribed_metrics_box_plot.pdf', help='figure path to save'),
):
    """Plot box plot of aligned results."""
    evaluate_transcribed_midis.plot_box_plot()
