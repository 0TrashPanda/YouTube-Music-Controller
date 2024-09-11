class Songs():
    def __init__(self, song_data):
        self.type = 'songs'
        self.has_main = False
        self.list_items = []
        for song in song_data:
            song = self.create_song(song)
            self.list_items.append(song)

    def create_song(self, song):
        title = self.set_title(song)
        artist = self.set_artist(song)
        album = self.set_album(song)
        thumbnail = self.set_thumbnail(song)
        videoId = self.set_videoId(song)
        duration_str = self.set_duration_str(song)
        duration_sec = self.set_duration_sec(song)
        song = {
            'title': title,
            'artists': artist,
            'album': album,
            'thumbnail': thumbnail,
            'videoId': videoId,
            'duration_str': duration_str,
            'duration_sec': duration_sec,
            'secondary': {
                'artist': artist,
                'album': album,
                'duration_str': duration_str,
            }
        }
        return song

    def set_title(self, song):
        return song['title']

    def set_artist(self, song):
        return [artist['name'] for artist in song['artists']]

    def set_album(self, song):
        return song.get('album', {}).get('name', 'no album found')

    def set_thumbnail(self, song):
        return song['thumbnails'][-1]['url']

    def set_videoId(self, song):
        return song['videoId']

    def set_duration_str(self, song):
        return song['duration']

    def set_duration_sec(self, song):
        return song['duration_seconds']

    def get_songs(self):
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
            song = self.create_song(song)
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
