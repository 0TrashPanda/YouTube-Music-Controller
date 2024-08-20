import time
from flask_socketio import SocketIO
from flask import jsonify, Flask, render_template, request, json
import socketio
from ytmusicapi import YTMusic
import threading


ytmusic = YTMusic()

app = Flask(__name__)
socketio = SocketIO(app)
from src.classes import Player, Song

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    socketio.emit('update_queue', player.queue.get_queue())
    if player.get_play_state() == 'Ended':
        return
    socketio.emit('current_song', player.get_current_song())
    socketio.emit('play_state', player.get_play_state())
    socketio.emit('current_time', player.get_time())
    socketio.emit('volume', player.player.audio_get_volume())

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('volume')
def handle_volume(volume):
    player.player.audio_set_volume(int(volume))
    socketio.emit('volume', player.player.audio_get_volume())

@socketio.on('reorder')
def handle_reorder(data):
    player.queue.reorder(data)
    socketio.emit('update_queue', player.queue.get_queue())

@socketio.on('seek')
def handle_seek(pos):
    player.player.set_position(float(pos))
    socketio.emit('current_time', player.get_time())

player = Player()

video_url = "https://music.youtube.com/watch?v=fQ-UDFguLO0"

def vlc_monitor():
    while True:
        if player.song_end:
            player.queue.next_song()
            player.play_queue()
            player.song_end = False
        time.sleep(0.2)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/play', methods=['POST'])
def play():
    player.play_queue()
    return 'OK', 200

@app.route('/get_time', methods=['GET'])
def get_time():
    if player.get_time() == -1:
        return jsonify({'current_time': 0, 'total_time': 0})
    return jsonify({'current_time': player.get_time() // 1000, 'total_time': player.get_length() // 1000})

@app.route('/play_pause', methods=['POST'])
def play_pause():
    player.play_pause()
    socketio.emit('current_time', player.get_time())
    return 'OK', 200

@app.route('/searchr', methods=['POST'])
def searchr():
    search_query = request.form.get('search_query')
    if search_query == "":
        return '', 204
    jsons = ytmusic.search(search_query, filter='songs', limit=5)
    return render_template('songs.html', songs=jsons)
# fetch('/search_suggestions?q=' + value)
@app.route('/search_suggestions')
def search_suggestions():
    search_query = request.args.get('q', '').strip()
    if search_query == "":
        return '', 204
    jsons = ytmusic.get_search_suggestions(search_query, detailed_runs=True)
    return jsonify(jsons)

@app.route('/play_next', methods=['POST'])
def play_next():
    song_data = request.form.get('song')
    song_data = json.loads(song_data)
    videoId = song_data['videoId']
    video_url = f'https://music.youtube.com/watch?v={videoId}'
    artists = [artist['name'] for artist in song_data['artists']]
    song = Song(video_url=video_url, title=song_data['title'], artists=artists, duration=song_data['duration_seconds'], videoId=song_data['videoId'], thumbnail=song_data['thumbnails'][-1]['url'], duration_string=song_data['duration'], album=song_data['album']['name'])
    player.queue.add_song_after_current(song)
    if player.get_play_state() == 'Ended':
        player.play_queue()
    socketio.emit('update_queue', player.queue.get_queue())
    return 'OK', 200

@app.route('/add_to_queue', methods=['POST'])
def add_to_queue():
    song_data = request.form.get('song')
    song_data = json.loads(song_data)
    videoId = song_data['videoId']
    video_url = f'https://music.youtube.com/watch?v={videoId}'
    artists = [artist['name'] for artist in song_data['artists']]
    song = Song(video_url=video_url, title=song_data['title'], artists=artists, duration=song_data['duration_seconds'], videoId=song_data['videoId'], thumbnail=song_data['thumbnails'][-1]['url'], duration_string=song_data['duration'], album=song_data['album']['name'])
    player.queue.add_song_at_end(song)
    if player.get_play_state() == 'Ended':
        player.play_queue()
    socketio.emit('update_queue', player.queue.get_queue())
    return 'OK', 200

@app.route('/radio', methods=['POST'])
def radio():
    videoId = request.form.get('videoId')
    radio = ytmusic.get_watch_playlist(videoId, radio=True)
    player.queue.set_radio(radio)
    socketio.emit('update_queue', player.queue.get_queue())
    return 'OK', 200

@app.route('/skip', methods=['POST'])
def skip():
    player.queue.next_song()
    player.play_queue()
    return 'OK', 200

@app.route('/back', methods=['POST'])
def back():
    if player.get_time() < 5000:
        player.queue.previous_song()
    player.play_queue()
    return 'OK', 200

@app.route('/remove', methods=['POST'])
def remove():
    uuid = request.form.get('uuid')
    try:
        player.queue.remove_song(uuid)
    except ValueError:
        return '', 404
    return 'OK', 200

@app.route('/jump_queue', methods=['POST'])
def jump_queue():
    uuid = request.form.get('uuid')
    player.queue.jump_queue(uuid)
    return 'OK', 200

# Start the VLC monitor in a separate thread
vlc_thread = threading.Thread(target=vlc_monitor, daemon=True)
vlc_thread.start()

if __name__ == '__main__':
    app.run(port=5000, host='0.0.0.0')
