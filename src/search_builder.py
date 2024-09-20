class Songs():
    def __init__(self, song_data):
        self.type = 'songs'
        self.has_main = False
        self.list_items = []
        for song in song_data:
            song = self.create_item(song)
            self.list_items.append(song)

    def create_item(self, song):
        title = self.set_title(song)
        artist = self.set_artist(song)
        album = self.set_album(song)
        thumbnail = self.set_thumbnail(song)
        videoId = self.set_videoId(song)
        duration_str = self.set_duration_str(song)
        duration_sec = self.set_duration_sec(song)
        year = self.set_year(song)
        type = self.set_type(song)
        secondary = self.set_secondary(song)
        song = {
            'title': title,
            'artists': artist,
            'album': album,
            'thumbnail': thumbnail,
            'videoId': videoId,
            'duration_str': duration_str,
            'duration_sec': duration_sec,
            'year': year,
            'type': type,
            'secondary': secondary
        }
        return song

    def set_title(self, song):
        return song['title']

    def set_artist(self, song):
        return [artist['name'] for artist in song['artists']]

    def set_album(self, song):
        if song.get('album', None) is None:
            return 'no album found'
        return song.get('album', {}).get('name', 'no album found')

    def set_thumbnail(self, song):
        return song['thumbnails'][-1]['url']

    def set_videoId(self, song):
        return song['videoId']

    def set_duration_str(self, song):
        return song.get('duration', None)

    def set_duration_sec(self, song):
        return song.get('duration_seconds', None)

    def set_year(self, song):
        return song.get('year', None)

    def set_type(self, song):
        return song.get('type', None)

    def set_secondary(self, song):
        return {
                'artist': self.set_artist(song),
                'album': self.set_album(song),
                'duration_str': self.set_duration_str(song),
            }

    def get_items(self):
        return {
            'type': self.type,
            'has_main': self.has_main,
            'list_items': self.list_items
        }

class Radio(Songs):
    def __init__(self, song_data):
        self.type = 'radio'
        self.has_main = False
        self.list_items = []
        for song in song_data['tracks']:
            song = self.create_item(song)
            self.list_items.append(song)

    def set_thumbnail(self, song):
        return song['thumbnail'][-1]['url']

    def set_duration_str(self, song):
        return song['length']

    def set_duration_sec(self, song):
        timeStrToSec(song['length'])

def timeStrToSec(timeStr):
    timeStr = timeStr.split(':')
    if len(timeStr) == 3:
        return int(timeStr[0]) * 3600 + int(timeStr[1]) * 60 + int(timeStr[2])
    return int(timeStr[0]) * 60 + int(timeStr[1])

class Albums(Songs):
    def __init__(self, search_data):
        self.type = 'albums'
        self.has_main = False
        self.list_items = []
        for album in search_data:
            album = self.create_item(album)
            self.list_items.append(album)

    def set_videoId(self, song):
        return song['browseId']

    def set_secondary(self, song):
        return {
            'type': self.set_type(song),
            'artist': self.set_artist(song),
            'year': self.set_year(song)
        }

    def get_items(self):
        return {
            'type': self.type,
            'has_main': self.has_main,
            'list_items': self.list_items
        }


class Album(Songs):
    def __init__(self, song_data):
        self.type = 'album'
        self.has_main = True
        self.title = song_data['title']
        self.thumbnail = song_data['thumbnails'][-1]['url']
        self.artists = [artist['name'] for artist in song_data['artists']]
        self.year = song_data.get('year', None)
        self.list_items = []
        for song in song_data['tracks']:
            song = self.create_item(song)
            self.list_items.append(song)

    def set_thumbnail(self, song):
        return self.thumbnail

    def set_album(self, song):
        return self.title

    def set_secondary(self, song):
        return {
            'artist': self.artists,
            'duration_str': self.set_duration_str(song),
        }

    def get_items(self):
        return {
            'type': self.type,
            'has_main': self.has_main,
            'title': self.title,
            'thumbnail': self.thumbnail,
            'artists': self.artists,
            'year': self.year,
            'list_items': self.list_items
        }

class Playlist(Songs):
    def __init__(self, search_data):
        self.type = 'playlist'
        self.has_main = True
        self.title = search_data['title']
        self.thumbnail = search_data.get('thumbnails', [{}])[-1].get('url', None)
        self.duration_str = search_data['duration']
        self.track_count = search_data['trackCount']
        self.list_items = []
        for playlist in search_data['tracks']:
            playlist = self.create_item(playlist)
            self.list_items.append(playlist)

    def get_items(self):
        return {
            'type': self.type,
            'has_main': self.has_main,
            'title': self.title,
            'thumbnail': self.thumbnail,
            'duration_str': self.duration_str,
            'track_count': self.track_count,
            'list_items': self.list_items
        }

class Playlists(Songs):
    def __init__(self, search_data):
        self.type = 'playlists'
        self.has_main = False
        self.list_items = []
        for playlist in search_data:
            playlist = self.create_item(playlist)
            self.list_items.append(playlist)

    def set_artist(self, song):
        return song['author']

    def set_videoId(self, song):
        return song['browseId']

    def set_type(self, song):
        return 'playlist'

    def set_secondary(self, song):
        return {
            'artist': self.set_artist(song),
            'view_count': str(song.get('itemCount', None)) + ' views'
        }

    def get_items(self):
        return {
            'type': self.type,
            'has_main': self.has_main,
            'list_items': self.list_items
        }

class Artists(Songs):
    def __init__(self, search_data):
        self.type = 'artists'
        self.has_main = False
        self.list_items = []
        for artist in search_data:
            artist = self.create_item(artist)
            self.list_items.append(artist)

    def set_title(self, song):
        return song['artist']

    def set_album(self, song):
        return 'no album'

    def set_artist(self, song):
        return 'no artist'

    def set_videoId(self, song):
        return song['browseId']

    def set_duration_str(self, song):
        return 'no duration'

    def set_duration_sec(self, song):
        return 'no duration'

    def set_year(self, song):
        return 'no year'

    def set_type(self, song):
        return 'artist'

    def set_secondary(self, song):
        return {}

    def get_items(self):
        return {
            'type': self.type,
            'has_main': self.has_main,
            'list_items': self.list_items
        }