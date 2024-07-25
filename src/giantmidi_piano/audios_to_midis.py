import os
import time

import librosa
import numpy as np
import piano_transcription_inference
import torch

from . import piano_detection_model
from .dataset import read_csv_to_meta_dict, write_meta_dict_to_csv
from .utilities import get_filename


def calculate_piano_solo_prob(
    workspace: str,
    mp3s_dir: str,
    mini_data: bool,
):
    """Calculate the piano solo probability of all downloaded mp3s, and append the probability to the meta csv file."""
    # Arguments & parameters
    sample_rate = piano_detection_model.SR
    prefix = 'minidata_' if mini_data else ''

    # Paths
    similarity_csv_path = os.path.join(workspace, f'{prefix}full_music_pieces_youtube_similarity.csv')

    piano_prediction_path = os.path.join(workspace, f'{prefix}full_music_pieces_youtube_similarity_pianosoloprob.csv')

    # Meta info
    meta_dict = read_csv_to_meta_dict(similarity_csv_path)

    meta_dict['piano_solo_prob'] = []
    meta_dict['audio_name'] = []
    meta_dict['audio_duration'] = []

    piano_solo_detector = piano_detection_model.PianoSoloDetector()

    for n in range(len(meta_dict['surname'])):
        mp3_path = os.path.join(
            mp3s_dir,
            f"{meta_dict['surname'][n]}, {meta_dict['firstname'][n]}, {meta_dict['music'][n]}, {meta_dict['youtube_id'][n]}.mp3".replace(  # noqa: E501
                '/', '_'
            ),
        )

        if os.path.exists(mp3_path):
            (audio, _) = librosa.core.load(mp3_path, sr=sample_rate, mono=True)

            try:
                probs = piano_solo_detector.predict(audio)
                prob = np.mean(probs)
            except:
                prob = 0

            print(n, mp3_path, prob)
            meta_dict['audio_name'].append(get_filename(mp3_path))
            meta_dict['piano_solo_prob'].append(prob)
            meta_dict['audio_duration'].append(len(audio) / sample_rate)
        else:
            meta_dict['piano_solo_prob'].append('')
            meta_dict['audio_name'].append('')
            meta_dict['audio_duration'].append('')

    write_meta_dict_to_csv(meta_dict, piano_prediction_path)
    print(f'Write out to {piano_prediction_path}')


def transcribe_piano(
    workspace: str,
    mp3s_dir: str,
    midis_dir: str,
    begin_index: int,
    end_index: int,
    mini_data: bool,
):
    """Transcribe piano solo mp3s to midi files."""
    # Arguments & parameters
    device = 'cuda' if torch.cuda.is_available() else 'cpu'

    # Paths
    csv_path = os.path.join('./resources/full_music_pieces_youtube_similarity_pianosoloprob_split.csv')

    os.makedirs(midis_dir, exist_ok=True)

    # Meta info
    meta_dict = read_csv_to_meta_dict(csv_path)

    # Transcriptor
    transcriptor = piano_transcription_inference.PianoTranscription(device=device)

    count = 0
    transcribe_time = time.time()
    audios_num = len(meta_dict['surname'])

    for n in range(begin_index, min(end_index, audios_num)):
        if meta_dict['giant_midi_piano'][n] and int(meta_dict['giant_midi_piano'][n]) == 1:
            count += 1

            mp3_path = os.path.join(mp3s_dir, f"{meta_dict['audio_name'][n]}.mp3")
            print(n, mp3_path)
            midi_path = os.path.join(midis_dir, f"{meta_dict['audio_name'][n]}.mid")

            (audio, _) = piano_transcription_inference.load_audio(
                mp3_path, sr=piano_transcription_inference.sample_rate, mono=True
            )

            try:
                # Transcribe
                transcriptor.transcribe(audio, midi_path)
            except:
                print('Failed for this audio!')

    print(f'Time: {time.time() - transcribe_time:.3f} s')
