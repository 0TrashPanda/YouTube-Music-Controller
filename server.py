import yt_dlp
import vlc
from flask import jsonify, Flask, render_template

app = Flask(__name__)

video_url = "https://music.youtube.com/watch?v=fQ-UDFguLO0"

def get_audio_stream_url(video_url):
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

audio_url = get_audio_stream_url(video_url)

instance = vlc.Instance()
player = instance.media_player_new()
media = instance.media_new(audio_url)
media.get_mrl()


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/play', methods=['POST'])
def play():
    player.set_media(media)
    player.play()
    return 'OK', 200

@app.route('/get_time')
def get_time():
    print(player.get_time())
    if player.get_time() == -1:
        return jsonify({'current_time': 0, 'total_time': 0})
    current_time = player.get_time() // 1000
    total_time = player.get_length() // 1000
    return jsonify({'current_time': current_time, 'total_time': total_time})

@app.route('/play_pause', methods=['POST'])
def play_pause():
    player.pause()
    return 'OK', 200


app.run(port=5000)