from typing import List, Dict

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
        self.track_number = None
        self.tracks_in_album = None
        self.deleted = None


class Service:
    def __init__(self, context):
        """

        :param context: execution context
        :type context: gmusiccache.service.context.ExecutionContext
        """

        self.__context = context
        self.__gmusic_client = self.__gmusic_client = gmusicapi.Mobileclient()
        self.__song_cache = {}

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

    @staticmethod
    def __make_song_info(song: Dict) -> SongInfo:
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

        song_info.track_number = song.get('trackNumber', 1)
        song_info.tracks_in_album = song.get('totalTrackCount', 1)


        song_info.deleted = song.get('deleted', False)

        return song_info


    def __get_songs(self, updated_after: datetime = None) -> List[SongInfo]:
        from gmusiccache.service.context import StatusInteraction

        songs = []
        self.__context.interact(StatusInteraction("Processing songs..."))
        for batch_id, batch in enumerate(
                self.__gmusic_client.get_all_songs(incremental=True, updated_after=updated_after)):

            self.__context.interact(StatusInteraction(
                "Processing songs {0}..{1}".format(batch_id * 1000, batch_id * 1000 + len(batch) - 1)))

            for song in batch:
                if not 'storeId' in song:
                    continue

                songs.append(Service.__make_song_info(song))

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

    def download_song(self, id) -> bytes:
        from gmusiccache.service.context import StatusInteraction
        from urllib.request import urlretrieve, urlopen
        from tempfile import mkstemp
        import os
        import eyed3
        from eyed3.mp3 import Mp3AudioFile
        from eyed3.id3 import Tag
        from eyed3.id3.frames import ImageFrame
        from datetime import datetime

        self.__context.interact(StatusInteraction("Retrieving song info..."))
        song_info = Service.__make_song_info(self.__gmusic_client.get_track_info(id))

        album_art = None
        if song_info.album_art:
            self.__context.interact(StatusInteraction("Reading album cover..."))
            try:
                with urlopen(song_info.album_art) as stream:
                    album_art = stream.read()
            except:
                self.__context.interact(StatusInteraction("Album art download failed!"))

        self.__context.interact(StatusInteraction("Making id3 tags..."))

        id3_tags = Tag()

        id3_tags.title = song_info.name
        id3_tags.artist = song_info.artist
        id3_tags.album = song_info.album

        id3_tags.release_date = song_info.year
        id3_tags.recording_date = song_info.year
        id3_tags.original_release_date = song_info.year
        id3_tags.tagging_date = datetime.now().year
        id3_tags.encoding_date = datetime.now().year

        id3_tags.track_num = song_info.track_number, song_info.tracks_in_album

        if album_art:
            id3_tags.images.set(ImageFrame.FRONT_COVER, album_art, 'image/jpeg')


        self.__context.interact(StatusInteraction("Downloading stream..."))
        stream_url = self.__gmusic_client.get_stream_url(song_info.id)

        fd, path = None, None

        try:
            try:
                fd, path = mkstemp(prefix='gmusiccache_')
                urlretrieve(stream_url, path)
            finally:
                if fd:
                    os.close(fd)


            self.__context.interact(StatusInteraction("Fixing metadata on file {0}...".format(path)))

            mp3_file = eyed3.load(path)
            mp3_file.initTag()  # update to the newest version
            mp3_file.tag = id3_tags
            mp3_file.tag.save()

            self.__context.interact(StatusInteraction("Done. Returning file with metadata."))

            with open(path, 'rb') as file:
                return file.read()

        finally:
            self.__context.interact(StatusInteraction("Removing temp file {0}...".format(path)))
            if path:
                os.remove(path)




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
        api_function(Service.download_song)

        return api

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown()