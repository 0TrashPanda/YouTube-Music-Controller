import time
import yt_dlp
import vlc
from ytmusicapi import YTMusic
from server import socketio
import threading

ytmusic = YTMusic()

class Song:
    def __init__(self, video_url, title, artists, duration, videoId, thumbnail, duration_string, album):
        self.video_url = video_url
        self.title = title
        self.album = album
        self.artists = artists
        self.duration = duration
        self.videoId = videoId
        self.thumbnail = thumbnail
        self.release_year = None
        self.duration_string = duration_string
        self.stream_url = None
        threading.Thread(target=self.gen_data, daemon=True).start() # TODO kill all threads on new radio

    def gen_data(self):
        ydl_opts = {
            'format': 'bestaudio[ext=m4a]',  # Get the best audio only format (e.g., m4a)
            'quiet': True,                   # Suppress output
            'skip_download': True,           # Don't download the video
            'noplaylist': True,              # Prevent downloading playlists
            'extract_flat': False,            # Prevent unnecessary metadata extraction
            'youtube_include_dash_manifest': False,  # Skip DASH manifest to avoid extra downloads
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(self.video_url, download=False)

            # get the thumbnail with the highest resolution that is square
            # todo: make this better
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

            try:
                stream_url = [f for f in info_dict['formats'] if f.get('audio_channels')][0]['url']
            except IndexError:
                print('No stream URL found')
                import json
                print(json.dumps(info_dict['formats'], indent=4))
                stream_url = None

            self.stream_url = stream_url
            self.release_year = info_dict['release_year']
            self.thumbnail = thumbnail_url

    def toJSON(self):
        return {
            'title': self.title,
            'thumbnail': self.thumbnail,
            'artists': self.artists,
            'duration': self.duration,
            'videoId': self.videoId,
            'duration_string': self.duration_string,
            'album': self.album,
            'release_year': self.release_year,
            'uuid': id(self)
        }

    def get_id(self):
        return id(self)

    def get_stream_url(self):
        while not self.stream_url:
            time.sleep(0.1)
        return self.stream_url

class Player:
    def __init__(self):
        self.instance = vlc.Instance()
        self.instance.log_unset() # stop vlc from printing to console
        self.player = self.instance.media_player_new()
        self.media = None
        self.queue = Queue()
        event_manager = self.player.event_manager()
        event_manager.event_attach(vlc.EventType.MediaPlayerEndReached, self.on_song_end)
        self.song_end = False
        self.player.audio_set_volume(50)

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
        time.sleep(0.1)
        socketio.emit('play_state', self.get_play_state())

    def get_state(self):
        return self.media.get_state()

    def new_song(self, video_url):
        self.play_song(Song(video_url))

    def play_song(self, song):
        self.current_song = song
        self.media = self.instance.media_new(self.queue.get_current_song().get_stream_url())
        self.player.set_media(self.instance.media_new(self.queue.get_current_song().get_stream_url()))
        self.player.play()


    def play_queue(self):
        self.queue.get_current_song()
        self.play_song(self.queue.get_current_song())
        song = self.queue.get_current_song().toJSON()
        song['current_time'] = 0
        socketio.emit('current_song', song)
        socketio.emit('play_state', 'Playing')
        socketio.emit('current_time', 0)


    def get_play_state(self):
        state = self.player.get_state()
        if state == vlc.State.Playing:
            return 'Playing'
        elif state == vlc.State.Paused:
            return 'Paused'
        else:
            return 'Ended'

    def on_song_end(self, event):
        self.song_end = True

    def get_current_song(self):
        song = self.queue.get_current_song()
        if not song:
            return None
        current_time = self.get_time()
        song = song.toJSON()
        song['current_time'] = current_time
        return song


class Queue:
    def __init__(self):
        self.queue = []
        self.current_song = None

    def add_song_at_end(self, song):
        self.queue.append(song)

    def add_song_after_current(self, song, offset=0):
        self.queue.insert(self.get_current_index() + 1 + offset, song)

    def remove_song(self, uuid):
        for index, song in enumerate(self.queue):
            if str(song.get_id()) == str(uuid):
                self.remove_song_at_index(index)
                break
        socketio.emit('update_queue', self.get_queue())

    def remove_song_at_index(self, index):
        current_song_index = self.get_current_index()
        if index == current_song_index:
            self.next_song()
            from server import player
            player.play_queue()
        self.queue.pop(index)
        if current_song_index > index:
            current_song_index -= 1

    def get_queue(self):
        return [song.toJSON() for song in self.queue]

    def clear_queue(self):
        self.queue.clear()

    def get_current_song(self):
        if self.queue:
            return self.queue[self.get_current_index()]
        else:
            return None

    def set_current_song(self, index):
        self.current_song = str(self.queue[index].get_id())

    def next_song(self):
        current_song_index = self.get_current_index()
        if current_song_index + 1 >= len(self.queue):
            current_song_index = 0
        else:
            self.set_current_song(current_song_index + 1)

    def previous_song(self):
        current_song_index = self.get_current_index()
        if current_song_index - 1 < 0:
            current_song_index = len(self.queue) - 1
        else:
            self.set_current_song(current_song_index - 1)

    def add_song_at_end(self, song):
        self.queue.append(song)

    def set_radio(self, radio):
        for index, song_data in enumerate(radio['tracks']):
            videoId = song_data['videoId']
            video_url = f'https://music.youtube.com/watch?v={videoId}'
            artists = [artist['name'] for artist in song_data['artists']]
            length = song_data['length']
            duration = sum(x * 60 ** i for i, x in enumerate(reversed(list(map(int, length.split(':'))))))
            song = Song(video_url=video_url, title=song_data['title'], artists=artists, duration=duration, videoId=song_data['videoId'], thumbnail=song_data['thumbnail'][-1]['url'], duration_string=length, album=song_data.get('album', {}).get('name', ''))
            # current_song + index + 1, song
            self.add_song_after_current(song, index)
            if index == 0:
                from server import player
                if player.get_play_state() == 'Ended':
                    player.play_queue()
            if index % 5 == 0:
                socketio.emit('update_queue', self.get_queue())

    def jump_queue(self, uuid):
        for index, song in enumerate(self.queue):
            if str(song.get_id()) == str(uuid):
                self.current_song = str(uuid)
                from server import player
                player.play_queue()
                break

    def reorder(self, uuid_list):
        new_queue = []
        for uuid in uuid_list:
            for song in self.queue:
                if str(song.get_id()) == str(uuid):
                    new_queue.append(song)
                    break
        self.queue = new_queue

    def get_current_index(self):
        for index, song in enumerate(self.queue):
            if str(song.get_id()) == self.current_song:
                return index
        return 0
