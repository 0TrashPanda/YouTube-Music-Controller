import threading
import time
import yt_dlp
from src.socket_client import socketio

class Song:
    def __init__(self, video_url, title, artists, duration_sec, videoId, thumbnail, duration_str, album):
        self.video_url = video_url
        self.title = title
        self.album = album
        self.artists = artists
        self.duration_sec = duration_sec
        self.videoId = videoId
        self.thumbnail = thumbnail
        self.release_year = None
        self.duration_str = duration_str
        self.stream_url = None
        # TODO kill all threads on new radio
        self.thread = threading.Thread(target=self.gen_data)
        self.thread_status = 0
        self._lock = threading.Lock()
        self._timeout = 30  # 30 second timeout

    def gen_data(self):
        self.thread_status = 1
        ydl_opts = {
            # Get the best audio only format (e.g., m4a)
            'format': 'bestaudio[ext=m4a]',
            'quiet': True,                   # Suppress output
            'skip_download': True,           # Don't download the video
            'noplaylist': True,              # Prevent downloading playlists
            'extract_flat': False,            # Prevent unnecessary metadata extraction
            # Skip DASH manifest to avoid extra downloads
            'youtube_include_dash_manifest': False,
        }

        try:
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
                    stream_url = [f for f in info_dict['formats']
                                  if f.get('audio_channels')][0]['url']
                except IndexError:
                    print('No stream URL found')
                    import json
                    print(json.dumps(info_dict['formats'], indent=4))
                    stream_url = None

                self.stream_url = stream_url
                self.release_year = info_dict['release_year']
                self.thumbnail = thumbnail_url
        except yt_dlp.utils.DownloadError:
            print('Failed to get stream URL')
            self.stream_url = ''
        self.thread_status = 2

    def toJSON(self):
        return {
            'title': self.title,
            'thumbnail': self.thumbnail,
            'artists': self.artists,
            'duration_sec': self.duration_sec,
            'videoId': self.videoId,
            'duration_str': self.duration_str,
            'album': self.album,
            'release_year': self.release_year,
            'uuid': id(self)
        }

    def get_id(self):
        return id(self)

    def get_stream_url(self):
        if self.thread_status == 0:
            self.thread.start()

        start_time = time.time()
        while self.thread_status != 2:
            if time.time() - start_time > self._timeout:
                print(f"Timeout getting stream URL for {self.title}")
                return None
            time.sleep(0.1)
        return self.stream_url

    def start_thread(self):
        if self.thread_status == 0:
            print('Starting thread ' + self.title)
            self.thread.start()