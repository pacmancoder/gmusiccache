import getpass
from typing import List
from urllib import request as web_request

import gmusicapi

from argparse import ArgumentParser, ArgumentError


def get_settings():
    arguments = ArgumentParser(
        description="Popular music streaming service™ helper application. Can do things.")

    arguments.add_argument("--login",    "-l", dest="login",    required=True)
    arguments.add_argument("--password", "-p", dest="password", required=False)
    arguments.add_argument("--device",   "-d", dest="device",   required=True)
    arguments.add_argument("--folder",   "-f", dest="folder",   required=False)

    return arguments.parse_args()


class Message:
    def __init__(self, message):
        self.message = message

    class Result:
        pass


class GetPassword:
    def __init__(self, prompt):
        self.prompt = prompt

    class Result:
        def __init__(self, password):
            self.password = password


class QuerySettings:
    def __init__(self, key):
        self.key = key

    class Result:
        def __init__(self, value):
            self.value = value


class ExecutionContext:
    def __init__(self, settings, gmusic):
        self.__settings = settings
        self.__gmusic = gmusic

    def interact(self, interaction):
        if isinstance(interaction, Message):
            print(interaction.message)
            return Message.Result()
        elif isinstance(interaction, GetPassword):
            return GetPassword.Result(getpass.getpass(interaction.prompt + ': '))
        elif isinstance(interaction, QuerySettings):
            return QuerySettings.Result(getattr(self.__settings, interaction.key, None))

    @property
    def gmusic(self) -> gmusicapi.Mobileclient:
        return self.__gmusic

class SongInfo:
    pass

class GetSongsCommand:
    def execute(self, context: ExecutionContext) -> List[SongInfo]:
        songs = []
        context.interact(Message("Processing songs..."))
        for batch_id, batch in enumerate(context.gmusic.get_all_songs(incremental=True)):

            context.interact(
                Message("Processing songs {0}..{1}".format(batch_id * 1000, batch_id * 1000 + len(batch) - 1)))

            for song in batch:
                song_info = SongInfo()

                if not 'storeId' in song:
                    continue

                song_info.id = song['storeId']
                song_info.name = song['title']

                song_info.album = song['album']
                song_info.album_id = song['albumId']

                song_info.artist = song['artist']
                song_info.artists_ids = song['artistId']

                if len(song['albumArtRef']) > 0:
                    song_info.album_art = song['albumArtRef'][0]['url']
                else:
                    song_info.album_art = None

                song_info.size = song['estimatedSize']
                song_info.year = song.get('year', None)

                songs.append(song_info)

            return songs


class DownloadCommand:
    def __init__(self, song_info):
        self.__song_info = song_info


    def execute(self, context : ExecutionContext) -> None:
        stream = context.gmusic.get_stream_url(self.__song_info.id)
        web_request.urlretrieve(stream, context)

def get_command_arguments(arr):
    if len(arr) < 2:
        raise ArgumentError()
    return arr[1:]



def main():
    settings = get_settings()

    api = gmusicapi.Mobileclient(debug_logging=False)

    if not api.login(settings.login, settings.password, settings.device):
        raise RuntimeError("Login failed!")

    if not api.is_subscribed:
        raise RuntimeError("User not subscribed!")

    context = ExecutionContext(settings, api)

    songs = GetSongsCommand().execute(context)

    for song in songs:
        context.interact(Message("{0} - {1} - {2}".format(song.artist, song.album, song.name)))

if __name__ == '__main__':
    main()