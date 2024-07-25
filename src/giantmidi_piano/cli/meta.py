import typer

from giantmidi_piano import evaluate_meta

app = typer.Typer(name='meta')

_workspace_option = typer.Option(None, '--workspace', '-w', help='Working directory')


@app.command()
def create_subset200_eval_csv(
    workspace: str = _workspace_option,
):
    """Create subset of 200 evaluation csv."""
    evaluate_meta.create_subset200_eval_csv(workspace)


@app.command()
def plot_piano_solo_p_r_f1(
    subset200_eval_with_labels_path: str,
    surname_in_youtube_title: bool = typer.Option(False, help='Whether to check surname in youtube title.'),
):
    """Plot precision, recall, F1 score for piano solo."""
    evaluate_meta.plot_piano_solo_p_r_f1(subset200_eval_with_labels_path, surname_in_youtube_title)


@app.command()
def create_subset200_piano_solo_eval_csv(
    workspace: str = _workspace_option,
):
    """Create subset of 200 piano solo evaluation csv."""
    evaluate_meta.create_subset200_piano_solo_eval_csv(workspace)


@app.command()
def piano_solo_meta_accuracy(
    subset200_piano_solo_eval_with_labels_path: str,
    surname_in_youtube_title: bool = typer.Option(False, help='Whether to check surname in youtube title.'),
):
    """Calculate piano solo meta accuracy."""
    evaluate_meta.piano_solo_meta_accuracy(subset200_piano_solo_eval_with_labels_path, surname_in_youtube_title)


@app.command()
def piano_solo_performed_ratio(
    subset200_piano_solo_eval_with_labels_path: str,
    surname_in_youtube_title: bool = typer.Option(False, help='Whether to check surname in youtube title.'),
):
    """Calculate piano solo performance ratio."""
    evaluate_meta.piano_solo_performed_ratio(subset200_piano_solo_eval_with_labels_path, surname_in_youtube_title)


@app.command()
def individual_composer_piano_solo_meta_accuracy(
    workspace: str = _workspace_option,
    surname: str = typer.Argument(..., help='Surname of the composer.'),
    firstname: str = typer.Argument(..., help='Firstname of the composer.'),
    surname_in_youtube_title: bool = typer.Option(False, help='Whether to check surname in youtube title.'),
):
    """Calculate individual composer piano solo meta accuracy."""
    evaluate_meta.individual_composer_piano_solo_meta_accuracy(workspace, surname, firstname, surname_in_youtube_title)
