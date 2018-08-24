import os
from argparse import ArgumentParser, ArgumentError


def fix_path_component(filename):
    DEFAULT_PLACEHOLDER = '_'
    SPECIAL_SYMBOLS = "<>:\"/\\|?*"
    MIN_CHAR_VALUE = 31
    NOT_PERMITTED_PREFIX_CHARS = "."
    WINDOWS_RESERVED_NAMES = [
        'CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
        'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9']

    if len(filename) == 0:
        return DEFAULT_PLACEHOLDER

    no_special_symbols =  ''.join(
        x if x not in SPECIAL_SYMBOLS and ord(x) > MIN_CHAR_VALUE else DEFAULT_PLACEHOLDER for x in filename)

    if no_special_symbols[0] in NOT_PERMITTED_PREFIX_CHARS or no_special_symbols in WINDOWS_RESERVED_NAMES:
        no_special_symbols =  DEFAULT_PLACEHOLDER + no_special_symbols

    return no_special_symbols


def get_unique_filename(partial_name, format):

    def make_suffix(num):
        return "" if num == 0 else " ({0})".format(num)

    attempt = 0
    while True:
        path = partial_name + make_suffix(attempt) + '.' + format
        if os.path.exists(path):
            attempt += 1
            continue

        return path

def get_settings():
    arguments = ArgumentParser(
        description="Popular music streaming service™ helper application. Can do things.")

    arguments.add_argument("--login",    dest="login",    required=True)
    arguments.add_argument("--password", dest="password", required=True)
    arguments.add_argument("--device",   dest="device",   required=True)
    arguments.add_argument("--mode",     dest="mode",     required=False, default='standalone')
    arguments.add_argument("--locale",   dest="locale",   required=False, default='en')
    arguments.add_argument("--path",     dest="path",     required=False)


    return arguments.parse_args()

def run_server(settings):
    from gmusiccache.server import Server
    from gmusiccache.service import Service
    from gmusiccache.service.context import ExecutionContext

    context = ExecutionContext(settings)

    Server(Service(context)).run()


def run_client(settings, standalone=False):
    from gmusiccache.client import Client
    from gmusiccache.service import Service
    from gmusiccache.service.context import ExecutionContext

    context = ExecutionContext(settings)

    with Service(context) if standalone else Client(context) as service:
        logged_in = service.is_logged_in()

        print('Is logged in: {0}'.format(logged_in))
        if not logged_in:
            print('logging in...')
            service.login(settings.login, settings.password, settings.device)
            print('Logged in!')

        print('Setting locale...')
        service.set_locale(settings.locale)

        print('Getting all songs...')
        songs = service.get_all_songs()
        for num, song in enumerate(songs):
            print('> Downloading song {0} of {1}'.format(num + 1, len(songs)))
            mp3 = service.download_song(song.id)

            artist_folder = fix_path_component(song.artist)
            album_folder = fix_path_component(song.album)
            song_name = fix_path_component(song.name)

            base_path = settings.path if settings.path else os.path.join(os.path.expanduser('~'), 'gmusic')

            song_dir = os.path.join(base_path, artist_folder, album_folder)
            os.makedirs(song_dir, exist_ok=True)
            song_filename = get_unique_filename(os.path.join(song_dir, song_name), 'mp3')

            with open(song_filename, 'wb') as file:
                print('Writing file to path {0}'.format(song_filename))
                file.write(mp3)


def main():
    settings = get_settings()

    if settings.mode == 'client':
        run_client(settings)
    elif settings.mode == 'server':
        run_server(settings)
    else:
        run_client(settings, True)


if __name__ == '__main__':
    main()