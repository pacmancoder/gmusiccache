from argparse import ArgumentParser, ArgumentError


def get_settings():
    arguments = ArgumentParser(
        description="Popular music streaming service™ helper application. Can do things.")

    arguments.add_argument("--login",    "-l", dest="login",    required=True)
    arguments.add_argument("--password", "-p", dest="password", required=True)
    arguments.add_argument("--device",   "-d", dest="device",   required=True)
    arguments.add_argument("--mode",     "-m", dest="mode",     required=False, default='standalone')

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
    import os

    context = ExecutionContext(settings)

    with Service(context) if standalone else Client(context) as service:
        logged_in = service.is_logged_in()

        print("Is logged in: {0}".format(logged_in))
        if not logged_in:
            print("logging in...")
            service.login(settings.login, settings.password, settings.device)
            print("Logged in!")

        print("Getting all songs...")
        songs = service.get_all_songs()
        for num, song in enumerate(songs):
            print('> Downloading song {0} of {1}'.format(num + 1, len(songs)))
            mp3 = service.download_song(song.id)
            dir = os.path.join(os.path.expanduser('~'), 'gmusic/{0}/{1}'.format(song.artist, song.album))
            os.makedirs(dir, exist_ok=True)
            path = os.path.join(dir, '{0}.mp3'.format(song.name))

            with open(path, 'wb') as file:
                print('Writing file to path {0}'.format(path))
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