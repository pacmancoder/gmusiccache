from typing import List

from datetime import datetime
from functools import partial, update_wrapper, wraps

import gmusicapi


class SongInfo:
    def __init__(self):
        self.id = None
        self.name = None

        self.album = None
        self.album_id = None

        self.artist = None
        self.artists_id = None

        self.album_art = None

        self.size = None
        self.year = None

        self.deleted = None


class Service:
    def __init__(self, context):
        """

        :param context: execution context
        :type context: gmusiccache.service.context.ExecutionContext
        """

        self.__context = context
        self.__gmusic_client = self.__gmusic_client = gmusicapi.Mobileclient()

    def login(self, email, password, device_id):
        if not self.__gmusic_client.login(email, password, device_id):
            raise RuntimeError("Login failed!")

        if not self.__gmusic_client.is_subscribed:
            raise RuntimeError("User not subscribed!")

        return True

    def logout(self):
        self.__gmusic_client.logout()

        return True

    def shutdown(self):
        if self.__gmusic_client:
            self.__gmusic_client.logout()

        return True

    def __get_songs(self, updated_after: datetime = None) -> List[SongInfo]:
        from gmusiccache.service.context import MessageInteraction

        songs = []
        self.__context.interact(MessageInteraction("Processing songs..."))
        for batch_id, batch in enumerate(
                self.__gmusic_client.get_all_songs(incremental=True, updated_after=updated_after)):

            self.__context.interact(MessageInteraction(
                "Processing songs {0}..{1}".format(batch_id * 1000, batch_id * 1000 + len(batch) - 1)))

            for song in batch:
                if not 'storeId' in song:
                    continue

                song_info = SongInfo()

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

                song_info.deleted = song['deleted']

                songs.append(song_info)

            return songs

    def get_all_songs(self) -> List[SongInfo]:
        """
        Return all user songs
        """

        return self.__get_songs()

    def get_songs_diff(self, updated_after) -> List[SongInfo]:
        """
        Return songs difference

        :param updated_after: diff start date
        :type updated_after datetime.datetime
        """

        return self.__get_songs(updated_after)

    def is_logged_in(self):
        return self.__gmusic_client.is_authenticated()


    def get_api(self):
        api = []

        # bind api to the current instance
        def api_function(fn):
            api.append(update_wrapper(partial(fn, self), fn))


        # Register api functions
        api_function(Service.login)
        api_function(Service.logout)
        api_function(Service.is_logged_in)
        api_function(Service.get_all_songs)
        api_function(Service.get_songs_diff)

        return api