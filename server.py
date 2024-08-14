from flask_socketio import SocketIO
from flask import jsonify, Flask, render_template, request
import socketio
from src.classes import Player, Song
from ytmusicapi import YTMusic

ytmusic = YTMusic()

app = Flask(__name__)
socketio = SocketIO(app)

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    # socketio.emit('innerHTML', {'html': render_template('songs.html', songs=browser.songs), 'div': '#song-container'})
    # socketio.emit('outerHTML', {'html': render_template('player_bar.html', song=browser.player_bar, play_status=browser.get_play_state(driver)), 'div': '#player-bar'})
    # socketio.emit('innerHTML', {'html': render_template('queue_item.html', queue=browser.queue_list), 'div': '#queue'})

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
    videoId = request.form.get('videoId')
    player.new_song(f'https://music.youtube.com/watch?v={videoId}')
    return 'OK', 200

@app.route('/get_time', methods=['GET'])
def get_time():
    print(player.get_time())
    if player.get_time() == -1:
        return jsonify({'current_time': 0, 'total_time': 0})
    return jsonify({'current_time': player.get_time() // 1000, 'total_time': player.get_length() // 1000})

@app.route('/play_pause', methods=['POST'])
def play_pause():
    player.play_pause()
    return 'OK', 200

@app.route('/searchr', methods=['POST'])
def searchr():
    search_query = request.form.get('search_query')
    print(search_query)
    if search_query == "":
        return '', 204
    # socketio.emit('innerHTML', {'html': render_template('songs.html', songs=songs), 'div': '#song-container'})
    jsons = ytmusic.search(search_query, filter='songs', limit=5)
    for song in jsons:
        print(song['title'])
        print([i['name'] for i in song['artists']])
        print(song['album']['name'])
        print(song['duration'])
        print(song['thumbnails'][-1]['url'])
        print()

    return render_template('songs.html', songs=jsons)


app.run(port=5000)
