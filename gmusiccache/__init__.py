from argparse import ArgumentParser, ArgumentError


def get_settings():
    arguments = ArgumentParser(
        description="Popular music streaming service™ helper application. Can do things.")

    arguments.add_argument("--login",    "-l", dest="login",    required=True)
    arguments.add_argument("--password", "-p", dest="password", required=True)
    arguments.add_argument("--device",   "-d", dest="device",   required=True)
    arguments.add_argument("--mode",     "-m", dest="mode",     required=False, default='standalone')

    return arguments.parse_args()

def run_standalone(settings):
    from gmusiccache.service import Service
    from gmusiccache.service.context import ExecutionContext, MessageInteraction

    context = ExecutionContext(settings)
    service = Service(context)

    try:
        service.login(settings.login, settings.password, settings.device)
        for song in service.get_all_songs():
            context.interact(MessageInteraction("{0} - {1} - {2}".format(song.artist, song.album, song.name)))

    finally:
        service.shutdown()


def run_server(settings):
    from gmusiccache.server import Server
    from gmusiccache.service import Service
    from gmusiccache.service.context import ExecutionContext

    Server(Service(ExecutionContext(settings))).run()


def run_client(settings):
    from gmusiccache.client import Client

    with Client() as service:
        logged_in = service.is_logged_in()

        print("Is logged in: {0}".format(logged_in))
        if not logged_in:
            print("logging in...")
            service.login(settings.login, settings.password, settings.device)
            print("Logged in!")

        print("Getting all songs...")
        print(str(service.get_all_songs()))


def main():
    settings = get_settings()

    if settings.mode == 'client':
        run_client(settings)
    elif settings.mode == 'server':
        run_server(settings)
    else:
        run_standalone(settings)

if __name__ == '__main__':
    main()