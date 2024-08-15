from flask_socketio import SocketIO
from flask import jsonify, Flask, render_template, request
import socketio
from ytmusicapi import YTMusic

ytmusic = YTMusic()

app = Flask(__name__)
socketio = SocketIO(app)
from src.classes import Player, Song

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    if player.get_play_state() == 'Error':
        return
    socketio.emit('play_state', player.get_play_state())
    socketio.emit('update_queue', player.queue.get_queue())
    socketio.emit('current_song', player.queue.get_current_song().toJSON())

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')


player = Player()

video_url = "https://music.youtube.com/watch?v=fQ-UDFguLO0"


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
    socketio.emit('play_state', player.get_play_state())
    return 'OK', 200

@app.route('/searchr', methods=['POST'])
def searchr():
    search_query = request.form.get('search_query')
    if search_query == "":
        return '', 204
    jsons = ytmusic.search(search_query, filter='songs', limit=5)
    return render_template('songs.html', songs=jsons)

@app.route('/play_next', methods=['POST'])
def play_next():
    videoId = request.form.get('videoId')
    song = Song(f'https://music.youtube.com/watch?v={videoId}')
    player.queue.add_song_after_current(song)
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


app.run(port=5000)
