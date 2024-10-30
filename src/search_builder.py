from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

@dataclass
class BaseItem:
    title: str
    artists: List[str]
    album: str
    thumbnail: str
    videoId: str
    duration_str: Optional[str]
    duration_sec: Optional[int]
    year: Optional[int]
    type: Optional[str]
    secondary: Dict[str, Any]

class BaseSearchResult:
    type: str = 'base'
    has_main: bool = False

    def create_item(self, data: Dict) -> Dict:
        return {
            'title': self.set_title(data),
            'artists': self.set_artist(data),
            'album': self.set_album(data),
            'thumbnail': self.set_thumbnail(data),
            'videoId': self.set_videoId(data),
            'duration_str': self.set_duration_str(data),
            'duration_sec': self.set_duration_sec(data),
            'year': self.set_year(data),
            'type': self.set_type(data),
            'secondary': self.set_secondary(data)
        }

    def set_title(self, data: Dict) -> str:
        return data['title']

    def set_artist(self, data: Dict) -> List[str]:
        return [artist['name'] for artist in data['artists']]

    def set_album(self, data: Dict) -> str:
        return data.get('album', {}).get('name', 'no album found')

    def set_thumbnail(self, data: Dict) -> str:
        return data['thumbnails'][-1]['url']

    def set_videoId(self, data: Dict) -> str:
        return data['videoId']

    def set_duration_str(self, data: Dict) -> Optional[str]:
        return data.get('duration')

    def set_duration_sec(self, data: Dict) -> Optional[int]:
        return data.get('duration_seconds')

    def set_year(self, data: Dict) -> Optional[int]:
        return data.get('year')

    def set_type(self, data: Dict) -> Optional[str]:
        return data.get('type')

    def set_secondary(self, data: Dict) -> Dict:
        return {
            'artist': self.set_artist(data),
            'album': self.set_album(data),
            'duration_str': self.set_duration_str(data),
        }

class Songs(BaseSearchResult):
    def __init__(self, song_data: List[Dict]):
        self.type = 'songs'
        self.has_main = False
        self.list_items = [self.create_item(song) for song in song_data]

    def get_items(self) -> Dict:
        return {
            'type': self.type,
            'has_main': self.has_main,
            'list_items': self.list_items
        }

class Radio(Songs):
    def __init__(self, song_data: Dict):
        self.type = 'radio'
        self.has_main = False
        self.list_items = [self.create_item(song) for song in song_data['tracks']]

    def set_thumbnail(self, data: Dict) -> str:
        return data['thumbnail'][-1]['url']

    def set_duration_str(self, data: Dict) -> str:
        return data['length']

    def set_duration_sec(self, data: Dict) -> int:
        return self._time_str_to_sec(data['length'])

    @staticmethod
    def _time_str_to_sec(time_str: str) -> int:
        parts = time_str.split(':')
        if len(parts) == 3:
            h, m, s = map(int, parts)
            return h * 3600 + m * 60 + s
        m, s = map(int, parts)
        return m * 60 + s

class Albums(Songs):
    def __init__(self, search_data: List[Dict]):
        self.type = 'albums'
        self.has_main = False
        self.list_items = [self.create_item(album) for album in search_data]

    def set_videoId(self, data: Dict) -> str:
        return data['browseId']

    def set_secondary(self, data: Dict) -> Dict:
        return {
            'type': self.set_type(data),
            'artist': self.set_artist(data),
            'year': self.set_year(data)
        }

@dataclass
class Album(Songs):
    def __init__(self, song_data: Dict):
        self.type = 'album'
        self.has_main = True
        self.title = song_data['title']
        self.thumbnail = song_data['thumbnails'][-1]['url']
        self.artists = [artist['name'] for artist in song_data['artists']]
        self.year = song_data.get('year')
        self.list_items = [self.create_item(song) for song in song_data['tracks']]

    def set_thumbnail(self, _) -> str:
        return self.thumbnail

    def set_album(self, _) -> str:
        return self.title

    def set_secondary(self, data: Dict) -> Dict:
        return {
            'artist': self.artists,
            'duration_str': self.set_duration_str(data),
        }

    def get_items(self) -> Dict:
        return {
            'type': self.type,
            'has_main': self.has_main,
            'title': self.title,
            'thumbnail': self.thumbnail,
            'artists': self.artists,
            'year': self.year,
            'list_items': self.list_items
        }

@dataclass
class Playlist(Songs):
    def __init__(self, search_data: Dict):
        self.type = 'playlist'
        self.has_main = True
        self.title = search_data['title']
        self.thumbnail = search_data.get('thumbnails', [{}])[-1].get('url')
        self.duration_str = search_data['duration']
        self.track_count = search_data['trackCount']
        self.list_items = [self.create_item(track) for track in search_data['tracks']]

    def get_items(self) -> Dict:
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
    def __init__(self, search_data: List[Dict]):
        self.type = 'playlists'
        self.has_main = False
        self.list_items = [self.create_item(playlist) for playlist in search_data]

    def set_artist(self, data: Dict) -> str:
        return data['author']

    def set_videoId(self, data: Dict) -> str:
        return data['browseId']

    def set_type(self, _) -> str:
        return 'playlist'

    def set_secondary(self, data: Dict) -> Dict:
        return {
            'artist': self.set_artist(data),
            'view_count': f"{data.get('itemCount', 0)} views"
        }

class Artists(Songs):
    def __init__(self, search_data: List[Dict]):
        self.type = 'artists'
        self.has_main = False
        self.list_items = [self.create_item(artist) for artist in search_data]

    def set_title(self, data: Dict) -> str:
        return data['artist']

    def set_album(self, _) -> str:
        return 'no album'

    def set_artist(self, _) -> str:
        return 'no artist'

    def set_videoId(self, data: Dict) -> str:
        return data['browseId']

    def set_duration_str(self, _) -> str:
        return 'no duration'

    def set_duration_sec(self, _) -> str:
        return 'no duration'

    def set_year(self, _) -> str:
        return 'no year'

    def set_type(self, _) -> str:
        return 'artist'

    def set_secondary(self, _) -> Dict:
        return {}
