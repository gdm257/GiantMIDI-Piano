import glob
import os
import pathlib
import re
import string
import time

import nltk
from bs4 import BeautifulSoup
from nltk.tokenize import RegexpTokenizer

from .config import nationalities

nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')


def space_to_underscore(s):
    return s.replace(' ', '_')


def underscore_to_space(s):
    return s.replace('_', ' ')


def download_imslp_htmls(
    workspace: str,
):
    """Download html pages of all composers on IMSLP. In total 18,399 html pages have been downloaded."""
    # Paths
    htmls_dir = os.path.join(workspace, 'htmls')
    os.makedirs(htmls_dir, exist_ok=True)

    # Download composer page
    html_path = os.path.join(workspace, 'Category:Composers.html')
    os.system(f'wget --quiet -O {html_path} https://imslp.org/wiki/Category:Composers')

    # Load html text
    text = pathlib.Path(html_path).read_text()

    # Get all composer names. Will looks like:
    # ['A., Jag', 'Aadler, C. A.', 'Aagesen, Truid', ...]
    names = []

    for ch in string.ascii_uppercase[:26]:
        """Search from A to Z. Get all composers by their surnames."""
        substring = text[re.search(rf'"{ch}":\[', text).end() :]
        substring = substring[: re.search(r'\]', substring).start()]
        substring = substring.encode('utf8').decode('unicode_escape')
        names += substring[1:-1].split('","')

    bgn_time = time.time()

    # Download html pages of all composers
    for n, name in enumerate(names):
        surname_firstname = name.split(', ')
        """E.g., ['A.', 'Jag']"""

        if len(surname_firstname) == 1:
            surname = surname_firstname[0]
            composer_link = f'https://imslp.org/wiki/Category:{space_to_underscore(surname)}'
            html_path = os.path.join(htmls_dir, f'{surname}.html')

        elif len(surname_firstname) == 2:
            [surname, firstname] = surname_firstname
            composer_link = f'https://imslp.org/wiki/Category:{space_to_underscore(surname)}%2C_{space_to_underscore(firstname)}'
            html_path = os.path.join(htmls_dir, f'{surname}, {firstname}.html')

        os.system(f'wget --quiet -O "{html_path}" "{composer_link}"')
        print(n, html_path, os.path.isfile(html_path))

    print(f'Finish! {time.time() - bgn_time:.3f} s')


def download_wikipedia_htmls(args):
    """Download wikipedia pages of composers if exist. In total 6,831 wikipedia pages are downloaded."""
    # Arguments & parameters
    workspace = args.workspace

    # Paths
    htmls_dir = os.path.join(workspace, 'htmls')
    html_names = sorted(os.listdir(htmls_dir))

    wikipedias_dir = os.path.join(workspace, 'wikipedias')
    os.makedirs(wikipedias_dir, exist_ok=True)

    # Download wikipedia of composers
    for n, html_name in enumerate(html_names):
        print(n, html_name)  # E.g., 'A., Jag.html'
        html_path = os.path.join(htmls_dir, html_name)

        surname_firstname = html_name[:-5].split(', ')
        if len(surname_firstname) == 2:
            [surname, firstname] = surname_firstname

        text = pathlib.Path(html_path).read_text()
        tmp = re.search('Detailed biography: <a href="', text)
        if tmp:  # Only part of composer has wikipedia page
            text = text[tmp.end() : tmp.end() + 500]
            wikipedia_link = text[: re.search('"', text).start()]
            print(wikipedia_link)

            out_path = os.path.join(wikipedias_dir, f'{surname}, {firstname}.html')
            os.system(f'wget --quiet -O "{out_path}" "{wikipedia_link}"')


def create_meta_csv(args):
    """Create GiantMIDI-Piano meta csv. This csv collects 144,079 music pieces from all composers."""
    # Arguments & parameters
    workspace = args.workspace

    # Paths
    htmls_dir = os.path.join(workspace, 'htmls')
    wikipedias_dir = os.path.join(workspace, 'wikipedias')
    out_csv_path = os.path.join(workspace, 'full_music_pieces.csv')

    html_names = sorted(os.listdir(htmls_dir))

    meta_dict = {'surname': [], 'firstname': [], 'music': [], 'nationality': [], 'birth': [], 'death': []}

    for n, html_name in enumerate(html_names):
        print(n, html_name)  # E.g., 'A., Jag.html'

        surname_firstname = html_name[:-5].split(', ')
        if len(surname_firstname) == 2:
            [surname, firstname] = surname_firstname

        # Parse nationality, birth and death from Wikipedia
        wikipedia_path = os.path.join(wikipedias_dir, f'{surname}, {firstname}.html')
        (nationality, birth, death) = get_composer_info_from_wikipedia(wikipedia_path)

        # Parse music pieces from IMSLP html
        html_path = os.path.join(htmls_dir, html_name)
        music_names = get_music_names_from_imslp(html_path)
        music_names = [remove_suffix(music_name, firstname, surname) for music_name in music_names]

        for music_name in music_names:
            meta_dict['surname'].append(surname)
            meta_dict['firstname'].append(firstname)
            meta_dict['music'].append(music_name)
            meta_dict['nationality'].append(nationality)
            meta_dict['birth'].append(birth)
            meta_dict['death'].append(death)

    write_meta_dict_to_csv(meta_dict, out_csv_path)
    print(f'Write out to {out_csv_path}')


def get_composer_info_from_wikipedia(wikipedia_path):
    """Get nationality, birth and death from wikipedia."""
    nationality = None
    years = []

    if os.path.isfile(wikipedia_path):
        text = pathlib.Path(wikipedia_path).read_text()
        text = text.replace(': ', ':')
        text = text.replace('", "', '","')
        bgn = re.search(r'wgCategories":\[', text)

        if not bgn:
            return 'unknown', 'unknown', 'unknown'

        bgn = bgn.end()
        text = text[bgn + 1 :]
        fin = re.search(r'\]', text).start()
        text = text[:fin - 1]
        text = text.split('","')
        sentence = ' '.join(text)
        words = nltk.word_tokenize(sentence)
        pairs = nltk.pos_tag(words)

        for pair in pairs:
            if pair[1] == 'JJ':  # Nationality
                if not nationality and pair[0] in nationalities:
                    nationality = pair[0]
            elif pair[1] == 'CD':  # Birth or death year
                try:
                    year = int(pair[0][:4])
                    if year >= 1000 and year <= 9999:
                        years.append(year)
                except:
                    pass

        years = sorted(years)

    if len(years) >= 2:
        birth = str(years[0])
        death = str(years[1])
    else:
        birth = 'unknown'
        death = 'unknown'

    if not nationality:
        nationality = 'unknown'

    return nationality, birth, death


def get_music_names_from_imslp(ismlp_path):
    """Get all music names of a composer by parsing his / her IMSLP html page."""
    text = pathlib.Path(ismlp_path).read_text()
    # All music pieces information are before catpagejs
    obj = re.search(r"</div><script>if\(typeof catpagejs=='undefined'\)", text)
    text = text[: obj.start()] if obj else text

    soup = BeautifulSoup(text, 'html.parser')
    links = soup.find_all('a')

    music_names = []

    for _link in links:
        link = str(_link)
        if 'categorypagelink' in link:
            # link looks like: '<a class="categorypagelink" href="/wiki/Je_t%27aime_Juliette_(A.,_Jag)" title="Je t\'aime Juliette (A., Jag)">Je t\'aime Juliette (A., Jag)</a>'  # noqa: E501
            bgn = re.search('title=', link).end()
            link = link[bgn + 1 :]
            fin = re.search('>', link).start()
            music_name = link[:fin - 1]
            music_names.append(music_name)

    for _link in links:
        link = str(_link)
        if 'next 200' in link:
            # link looks like: '<a class="categorypaginglink" href="/index.php?title=Category:Mozart,_Wolfgang_Amadeus&amp;pagefrom=Fantasia+in+f+minor%2C+k.0608%7E%7Emozart%2C+wolfgang+amadeus%0AFantasia+in+F+minor%2C+K.608+%28Mozart%2C+Wolfgang+Amadeus%29#mw-pages" title="Category:Mozart, Wolfgang Amadeus">next 200</a>'  # noqa: E501
            bgn = re.search('href="', link).end()
            link = link[bgn:]
            fin = re.search('"', link).start()
            link = link[:fin]
            link = f'https://imslp.org{link}'
            link = link.replace('&amp;', '&')
            print(link)
            os.system(f'wget --quiet -O _tmp.html "{link}"')
            music_names += get_music_names_from_imslp('_tmp.html')
            break

    return music_names


def remove_suffix(music_name, firstname, surname):
    loct = re.search(rf' \({surname}, {firstname}\)', music_name)
    music_name = music_name[:loct.start()] if loct else music_name
    return music_name


def write_meta_dict_to_csv(meta_dict, out_csv_path):
    """Write meta dict to csv path."""
    with open(out_csv_path, 'w') as fw:
        line = '\t'.join(list(meta_dict.keys()))
        fw.write(f'{line}\n')

        for n in range(len(meta_dict['firstname'])):
            line = '\t'.join([str(meta_dict[key][n]) for key in meta_dict.keys()])
            fw.write(f'{line}\n')


def read_csv_to_meta_dict(csv_path):
    """Read csv file to meta_dict."""
    lines = []
    with open(csv_path) as fr:
        for line in fr:
            _line = line.split('\n')[0].split('\t')
            lines.append(_line)

    meta_dict = {key: [] for key in lines[0]}

    lines = lines[1:]
    for line in lines:
        for k, key in enumerate(meta_dict.keys()):
            meta_dict[key].append(line[k])

    return meta_dict


def _read_title_id(path):
    with open(path) as fr:
        lines = fr.readlines()

    if len(lines) != 2:
        return 'none', 'none'
    title = lines[0].split('\n')[0]
    _id = lines[1].split('\n')[0]
    return title, _id


def _too_many_requests(path):
    with open(path) as fr:
        lines = fr.readlines()

    for line in lines:
        print(line)
        if 'HTTP Error 429: Too Many Requests' in line:
            return True

    return False


def search_youtube(
    workspace: str,
    mini_data: bool = False,
):
    """Search music names on YouTube, and append searched YouTube titles and IDs to meta csv."""
    # Arguments & parameters
    prefix = 'minidata_' if mini_data else ''

    # Paths
    csv_path = os.path.join(workspace, 'full_music_pieces.csv')

    stdout_path = os.path.join(workspace, '_tmp', 'stdout.txt')
    error_path = os.path.join(workspace, '_tmp', 'error.txt')
    os.makedirs(os.path.dirname(stdout_path), exist_ok=True)

    youtube_csv_path = os.path.join(workspace, f'{prefix}full_music_pieces_youtube.csv')

    meta_dict = read_csv_to_meta_dict(csv_path)

    youtube_meta_dict = {key: [] for key in meta_dict.keys()}
    youtube_meta_dict['youtube_title'] = []
    youtube_meta_dict['youtube_id'] = []

    n = 0
    while n < len(meta_dict['surname']):
        print(n, meta_dict['surname'][n])
        search_str = f"{meta_dict['firstname'][n]} {meta_dict['surname'][n]}, {meta_dict['music'][n]}"

        youtube_simulate_str = f'youtube-dl --get-id --get-title ytsearch$1:"{search_str}" 1>"{stdout_path}" 2>"{error_path}"'

        os.system(youtube_simulate_str)

        if _too_many_requests(error_path):
            sleep_seconds = 3600
            print(f'Too many requests! Sleep for {sleep_seconds} s ...')
            time.sleep(sleep_seconds)
            continue

        (title, id) = _read_title_id(stdout_path)
        youtube_meta_dict['youtube_title'].append(title)
        youtube_meta_dict['youtube_id'].append(id)

        for key in meta_dict.keys():
            youtube_meta_dict[key].append(meta_dict[key][n])
        print(', '.join([youtube_meta_dict[key][n] for key in youtube_meta_dict]))

        n += 1
        if mini_data and n == 10:
            break

    write_meta_dict_to_csv(youtube_meta_dict, youtube_csv_path)
    print(f'Write out to {youtube_csv_path}')


def intersection(lst1, lst2):
    return [value for value in lst1 if value in lst2]


def jaccard_similarity(x, y):
    intersect = intersection(x, y)
    return len(intersect) / max(float(len(x)), 1e-8)


def calculate_similarity(
    workspace: str,
    mini_data: bool,
):
    """Calculate and append the similarity between YouTube titles and IMSLP music names to meta csv."""
    # Arguments & parameters
    prefix = 'minidata_' if mini_data else ''

    # Paths
    youtube_csv_path = os.path.join(workspace, f'{prefix}full_music_pieces_youtube.csv')

    similarity_csv_path = os.path.join(workspace, f'{prefix}full_music_pieces_youtube_similarity.csv')

    # Meta info to be downloaded
    meta_dict = read_csv_to_meta_dict(youtube_csv_path)
    meta_dict['similarity'] = []
    meta_dict['surname_in_youtube_title'] = []

    tokenizer = RegexpTokenizer('[A-Za-z0-9ÇéâêîôûàèùäëïöüÄß]+')

    for n in range(len(meta_dict['surname'])):
        target_str_without_firstname = (
            f"{meta_dict['surname'][n]}, {meta_dict['music'][n]}"
        )

        searched_str = meta_dict['youtube_title'][n]

        target_words = tokenizer.tokenize(target_str_without_firstname.lower())
        searched_words = tokenizer.tokenize(searched_str.lower())

        similarity = jaccard_similarity(target_words, searched_words)
        meta_dict['similarity'].append(str(similarity))

        if meta_dict['surname'][n] in meta_dict['youtube_title'][n]:
            meta_dict['surname_in_youtube_title'].append(1)
        else:
            meta_dict['surname_in_youtube_title'].append(0)

        if meta_dict['surname'][n] in meta_dict['youtube_title'][n]:
            meta_dict['surname_in_youtube_title'].append(1)
        else:
            meta_dict['surname_in_youtube_title'].append(0)

    write_meta_dict_to_csv(meta_dict, similarity_csv_path)
    print(f'Write out to {similarity_csv_path}')


def download_youtube(
    workspace: str,
    begin_index: int = 0,
    end_index: int = 0,
    mini_data: bool = False
):
    """Download IMSLP music pieces from YouTube. 59,969 files are downloaded in Jan. 2020."""
    # Arguments & parameters
    prefix = 'minidata_' if mini_data else ''

    # Paths
    similarity_csv_path = os.path.join(workspace, f'{prefix}full_music_pieces_youtube_similarity.csv')

    mp3s_dir = os.path.join(workspace, 'mp3s')
    os.makedirs(mp3s_dir, exist_ok=True)

    stdout_path = os.path.join(workspace, '_tmp', 'stdout.txt')
    error_path = os.path.join(workspace, '_tmp', 'error.txt')
    os.makedirs(os.path.dirname(stdout_path), exist_ok=True)

    # Meta info to be downloaded
    meta_dict = read_csv_to_meta_dict(similarity_csv_path)

    count = 0
    download_time = time.time()

    n = begin_index
    while n < min(end_index, len(meta_dict['surname'])):
        print(
            f"{n}; {meta_dict['firstname'][n]} {meta_dict['surname'][n]}; {meta_dict['music'][n]}; {meta_dict['youtube_title'][n]}"  # noqa: E501
        )

        if float(meta_dict['similarity'][n]) > 0.6:
            count += 1

            bare_name = os.path.join(
                f"{meta_dict['surname'][n]}, {meta_dict['firstname'][n]}, {meta_dict['music'][n]}, {meta_dict['youtube_id'][n]}".replace(  # noqa: E501, E501
                    '/', '_'
                )
            )

            youtube_str = f"""youtube-dl -f bestaudio -o "{mp3s_dir}/{bare_name}.%(ext)s" https://www.youtube.com/watch?v={meta_dict['youtube_id'][n]} 1>"{stdout_path}" 2>"{error_path}\""""  # noqa: E501

            os.system(youtube_str)

            if _too_many_requests(error_path):
                sleep_seconds = 3600
                print(f'Too many requests! Sleep for {sleep_seconds} s ...')
                time.sleep(sleep_seconds)
                continue

            # Convert to MP3
            audio_paths = glob.glob(os.path.join(mp3s_dir, f'{bare_name}*'))
            print(audio_paths)

            if audio_paths:
                audio_path = audio_paths[0]

                mp3_path = os.path.join(mp3s_dir, f'{bare_name}.mp3')

                os.system(f'ffmpeg -i "{audio_path}" -loglevel panic -y -ac 1 -ar 32000 "{mp3_path}" ')

                if os.path.splitext(audio_path)[-1] != '.mp3':
                    os.system(f'rm "{audio_path}"')

        n += 1

    print(f'{count} out of {end_index - begin_index} audios are downloaded!')
    print(f'Time: {time.time() - download_time:.3f}')


def download_youtube_piano_solo(
    workspace: str,
    begin_index: int,
    end_index: int,
    mini_data: bool,
):
    """Download piano solo of GiantMIDI-Piano. 10,848 files can be downloaded in Jan. 2020."""
    # Arguments & parameters
    prefix = 'minidata_' if mini_data else ''

    # Paths
    similarity_csv_path = os.path.join(
        workspace, f'{prefix}full_music_pieces_youtube_similarity_pianosoloprob.csv'
    )

    mp3s_dir = os.path.join(workspace, 'mp3s_piano_solo')
    os.makedirs(mp3s_dir, exist_ok=True)

    stdout_path = os.path.join(workspace, '_tmp', 'stdout.txt')
    error_path = os.path.join(workspace, '_tmp', 'error.txt')
    os.makedirs(os.path.dirname(stdout_path), exist_ok=True)

    # Meta info to be downloaded
    meta_dict = read_csv_to_meta_dict(similarity_csv_path)

    count = 0
    download_time = time.time()

    n = begin_index
    while n < min(end_index, len(meta_dict['surname'])):
        print(
            f"{n}; {meta_dict['firstname'][n]} {meta_dict['surname'][n]}; {meta_dict['music'][n]}; {meta_dict['youtube_title'][n]}"  # noqa: E501
        )

        if float(meta_dict['piano_solo_prob'][n]) >= 0.5:
            count += 1

            bare_name = os.path.join(
                f"{meta_dict['surname'][n]}, {meta_dict['firstname'][n]}, {meta_dict['music'][n]}, {meta_dict['youtube_id'][n]}".replace(  # noqa: E501
                    '/', '_'
                )
            )

            youtube_str = f"""youtube-dl -f bestaudio -o "{mp3s_dir}/{bare_name}.%(ext)s" https://www.youtube.com/watch?v={meta_dict['youtube_id'][n]} 1>"{stdout_path}" 2>"{error_path}\""""  # noqa: E501

            os.system(youtube_str)

            if _too_many_requests(error_path):
                sleep_seconds = 3600
                print(f'Too many requests! Sleep for {sleep_seconds} s ...')
                time.sleep(sleep_seconds)
                continue

            # Convert to MP3
            audio_paths = glob.glob(os.path.join(mp3s_dir, f'{bare_name}*'))
            print(audio_paths)

            if audio_paths:
                audio_path = audio_paths[0]

                mp3_path = os.path.join(mp3s_dir, f'{bare_name}.mp3')

                os.system(f'ffmpeg -i "{audio_path}" -loglevel panic -y -ac 1 -ar 32000 "{mp3_path}" ')

                if os.path.splitext(audio_path)[-1] != '.mp3':
                    os.system(f'rm "{audio_path}"')

        n += 1

    print(f'{count} out of {end_index - begin_index} audios are downloaded!')
    print(f'Time: {time.time() - download_time:.3f}')
