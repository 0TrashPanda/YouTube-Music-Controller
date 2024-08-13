# from ytmusicapi import YTMusic
# import json

# ytmusic = YTMusic()
# # search_results = ytmusic.search("RDAMVM", filter="songs")
# search_results = ytmusic.get_watch_playlist(videoId = "GlEY7OhZxqA", radio = True)
# print(json.dumps(search_results, indent=2))

# import pafy
# import vlc

# url = "https://www.youtube.com/watch?v=J2SvnnVBDk0"
# video = pafy.new(url)
# best = video.getbest()
# playurl = best.url

# # Over here playurl is best URL to play. Then we use VLC to play it.

# Instance = vlc.Instance()
# player = Instance.media_player_new()
# Media = Instance.media_new(playurl)
# Media.get_mrl()
# player.set_media(Media)
# player.play()


# import yt_dlp


# URL = 'https://music.youtube.com/watch?v=fQ-UDFguLO0'

# ydl_opts = {}
# with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#     # get all information about the youtube video
#     info = ydl.extract_info(URL, download=False)

#     formats = info['formats']
#     print(f"Found {len(formats)} formats")
#     # iterate through all of the available formats
#     # for i,format in enumerate(formats):
#     #     # print the url
#     #     url = format['url']
#     #     print(f"{i}) {url}")
#         # each format has many other attributes. You can do print(format.keys()) to see all possibilities
# import yt_dlp
# ffmpeg_options = {'options': '-vn'}
# ydl_opts = {'format': 'bestaudio'}
# with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#     song_info = ydl.extract_info('https://music.youtube.com/watch?v=fQ-UDFguLO0', download=False)

# import vlc
# instance = vlc.Instance()
# player = instance.media_player_new()
# media = instance.media_new(formats[4]['url'])
# media.get_mrl()
# player.set_media(media)
# player.play()
# while media.get_state() != vlc.State.Ended:
#      pass
# print("done")


# import vlc
# media = vlc.MediaPlayer("YOO_JOSUKE.mp3")
# media.play()
# while media.get_state() != vlc.State.Ended:
#      pass
# print("done")



import yt_dlp

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

# # Example usage:

# exit()
# instance = vlc.Instance()
# player = instance.media_player_new()
# media = instance.media_new(audio_url)
# media.get_mrl()
# player.set_media(media)
# player.play()
# while media.get_state() != vlc.State.Ended:
#     pass
# print("done")




import vlc
from flask import render_template_string, request, jsonify, Flask, render_template

app = Flask(__name__)

video_url = "https://music.youtube.com/watch?v=fQ-UDFguLO0"
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
    print('player.get_time()')
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

# from ytmusicapi import YTMusic
# import json
# ytmusic = YTMusic()


# di = ytmusic.get_song(videoId = "fQ-UDFguLO0", signatureTimestamp = 0)
# print(json.dumps(di, indent=2))