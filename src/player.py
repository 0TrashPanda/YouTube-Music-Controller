import vlc
import threading
import time
from vlc import EventType
from src.song_queue import Queue
from src.song import Song
from src.socket_client import socketio

class Player:
    def __init__(self):
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()
        self.queue = Queue()
        # Add event manager setup
        self.event_manager = self.player.event_manager()
        # Use a lambda to avoid potential deadlocks
        self.event_manager.event_attach(EventType.MediaPlayerEndReached,
                                        lambda x: threading.Thread(target=self._on_media_end, args=(x,)).start())

    def _on_media_end(self, event):
        """Handler for media end event"""
        # Run the next song logic in a separate thread to avoid VLC event handler deadlock
        self.queue.next_song()
        self.play_queue()

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
        try:
            self.current_song = song
            stream_url = song.get_stream_url()
            if not stream_url:
                print(f"Failed to get stream URL for {song.title}")
                return False

            media = self.instance.media_new(stream_url)
            self.player.set_media(media)

            # Add retry logic for play operation
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    if self.player.play() == 0:  # 0 indicates success
                        return True
                except Exception as e:
                    print(f"Attempt {attempt + 1} failed: {e}")
                    if attempt < max_retries - 1:
                        time.sleep(1)  # Wait before retry

                return False
        except Exception as e:
            print(f"Error playing {song.title}: {e}")
            return False

    def play_queue(self):
        current_song = self.queue.get_current_song()
        if not current_song:
            print("No song in queue to play")
            # Let the frontend know playback has ended
            socketio.emit('play_state', 'Ended')
            return

        self.play_song(current_song)
        song = current_song.toJSON()
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

    def get_current_song(self):
        song = self.queue.get_current_song()
        if not song:
            return None
        current_time = self.get_time()
        song = song.toJSON()
        song['current_time'] = current_time
        return song