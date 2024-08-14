from dataclasses import dataclass
import yt_dlp
import vlc
from ytmusicapi import YTMusic

ytmusic = YTMusic()

class Song:
    def __init__(self, video_url):
        self.video_url = video_url
        self.stream_url = self.get_stream_url(video_url)


    def get_stream_url(self, video_url):
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

            # Find the audio-only format
            audio_formats = [f for f in info_dict['formats'] if f.get('format_note') == 'Default']

            if audio_formats:
                # Get the first/best audio format URL
                audio_url = audio_formats[0]['url']
                print(audio_url)
                return audio_url
            else:
                return None


class Player:
    def __init__(self):
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()
        self.media = None

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
        self.current_song = Song(video_url)
        self.media = self.instance.media_new(self.current_song.stream_url)
        self.player.set_media(self.media)
        self.player.play()

