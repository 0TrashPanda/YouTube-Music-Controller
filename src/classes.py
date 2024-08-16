from dataclasses import dataclass
import yt_dlp
import vlc
from ytmusicapi import YTMusic
from flask_socketio import SocketIO
from server import socketio
import time

ytmusic = YTMusic()

class Song:
    def __init__(self, video_url):
        self.video_url = video_url
        data = self.get_data(video_url)
        self.stream_url = data.get('stream_url', None)
        self.title = data.get('title', None)
        self.artists = data.get('artists', None)
        self.duration = data.get('duration', None)
        self.videoId = data.get('videoId', None)
        self.thumbnail = data.get('thumbnail', None)
        self.duration_string = data.get('duration_string', None)
        self.album = data.get('album', None)
        self.release_year = data.get('release_year', None)


    def get_data(self, video_url):
        ydl_opts = {
            'format': 'bestaudio[ext=m4a]',  # Get the best audio only format (e.g., m4a)
            'quiet': True,                   # Suppress output
            'skip_download': True,           # Don't download the video
            'noplaylist': True,              # Prevent downloading playlists
            'extract_flat': False,            # Prevent unnecessary metadata extraction
            'youtube_include_dash_manifest': False,  # Skip DASH manifest to avoid extra downloads
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=False)

            # get the thumbnail with the highest resolution that is square
            thumbnails = info_dict.get('thumbnails', [{}])
            thumbnail = thumbnails[0]
            for thumb in thumbnails:
                resolution = thumb.get('resolution', None)
                if not resolution:
                    break
                if resolution.split('x')[0] == resolution.split('x')[1]:
                    thumbnail = thumb
                    continue
                break
            thumbnail_url = thumbnail.get('url', None)

            return {
                'stream_url': [f for f in info_dict['formats'] if f.get('format_note') == 'Default'][0]['url'],
                'title': info_dict.get('title', None),
                'thumbnail': thumbnail_url,
                'artists': info_dict.get('artists', None),
                'duration': info_dict.get('duration', None),
                'videoId': info_dict.get('id', None),
                'duration_string': info_dict.get('duration_string', None),
                'album': info_dict.get('album', None),
                'release_year': info_dict.get('release_year', None),
            }

    def toJSON(self):
        return {
            'title': self.title,
            'thumbnail': self.thumbnail,
            'artists': self.artists,
            'duration': self.duration,
            'videoId': self.videoId,
            'duration_string': self.duration_string,
            'album': self.album,
            'release_year': self.release_year,\
            'uuid': id(self)
        }

    def get_id(self):
        return id(self)


class Player:
    def __init__(self):
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()
        self.media = None
        self.queue = Queue()
        event_manager = self.player.event_manager()
        event_manager.event_attach(vlc.EventType.MediaPlayerEndReached, self.on_song_end)
        self.song_end = False

    def get_time(self):
        return self.player.get_time()

    def get_length(self):
        return self.player.get_length()

    def set_media(self, media):
        if not self.media:
            self.media = self.instance.media_new(media)
            return
        self.instance.set_media(media)

    def play_pause(self):
        self.player.pause()

    def get_state(self):
        return self.media.get_state()

    def new_song(self, video_url):
        self.play_song(Song(video_url))

    def play_song(self, song):
        print("Playing next song6.")
        self.current_song = song
        print("Playing next song7." + song.stream_url)
        if self.media is not None:
            self.media.release()
        self.media = self.instance.media_new(self.queue.get_current_song().stream_url)
        print("Playing next song8.")

        print(self.player.get_state())
        self.player.set_media(self.instance.media_new(self.queue.get_current_song().stream_url))
        print("Playing next song9.")
        self.player.play()

    def play_queue(self):
        print("Playing next song4.")
        self.queue.get_current_song()
        print("Playing next song5.")
        self.play_song(self.queue.get_current_song())
        print("Playing next song3.")
        socketio.emit('current_song', self.queue.get_current_song().toJSON())

    def get_play_state(self):
        state = self.player.get_state()
        if state == vlc.State.Playing:
            return 'Paused' # reversed because broki atm
        elif state == vlc.State.Paused:
            return 'Playing'
        else:
            return 'Ended'

    def on_song_end(self, event):
        self.song_end = True


class Queue:
    def __init__(self):
        self.queue = []
        self.current_song = 0

    def add_song_at_end(self, song):
        self.queue.append(song)

    def add_song_after_current(self, song):
        self.queue.insert(self.current_song + 1, song)

    def remove_song(self, uuid):
        for index, song in enumerate(self.queue):
            if str(song.get_id()) == str(uuid):
                self.remove_song_at_index(index)
                break
        socketio.emit('update_queue', self.get_queue())

    def remove_song_at_index(self, index):
        if index == self.current_song:
            self.next_song()
            from server import player
            player.play_queue()
        self.queue.pop(index)
        if self.current_song > index:
            self.current_song -= 1

    def get_queue(self):
        return [song.toJSON() for song in self.queue]

    def clear_queue(self):
        self.queue.clear()

    def get_current_song(self):
        if self.queue:
            return self.queue[self.current_song]
        else:
            return None

    def set_current_song(self, index):
        self.current_song = index

    def next_song(self):
        if self.current_song + 1 >= len(self.queue):
            self.current_song = 0
        else:
            self.current_song += 1

    def previous_song(self):
        if self.current_song - 1 < 0:
            self.current_song = len(self.queue) - 1
        else:
            self.current_song -= 1

    def add_song_at_end(self, song):
        self.queue.append(song)

    def set_radio(self, radio):
        self.clear_queue()
        for index, song in enumerate(radio['tracks']):
            print(f'Adding song {index + 1} of {len(radio["tracks"])}')
            self.add_song_at_end(Song(song['videoId']))
