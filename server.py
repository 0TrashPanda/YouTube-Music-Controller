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
from src.search_builder import Album, Albums, Playlist, Songs, Radio

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    socketio.emit('update_queue', player.queue.get_queues())
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
    try:
        player.player.audio_set_volume(int(volume))
    except:
        return
    socketio.emit('volume', volume)

@socketio.on('reorder')
def handle_reorder(data):
    player.queue.reorder(data)
    socketio.emit('update_queue', player.queue.get_queues())

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

def spit_filter(search_query):
    spit = search_query.split('/')
    if len(spit) == 1:
        return {'filter': 'songs', 'search_query': search_query}
    filter_letter = spit[0]
    match filter_letter.casefold():
        case 'a':
            filter = 'artists'
        case 'b':
            filter = 'albums'
        case 'p':
            filter = 'playlists'
        case 'v':
            filter = 'videos'
        case 's':
            filter = 'songs'
        case 'u':
            filter = 'url'
        case 'r':
            filter = 'radio'
        case _:
            return {'filter': 'songs', 'search_query': search_query}
    return {'filter': filter, 'search_query': '/'.join(spit[1:])}

def create_song(song_data):
    if isinstance(song_data, str):
        song_data = json.loads(song_data)
    videoId = song_data['videoId']
    duration_str = song_data.get('duration_str', song_data.get('duration', '0:00'))
    duration_sec = song_data.get('duration_sec', song_data.get('duration_seconds', 0))
    video_url = f'https://music.youtube.com/watch?v={videoId}'
    artists = [artist if isinstance(artist, str) else artist['name'] for artist in song_data['artists']]
    if song_data.get('secondary'):
        artists = song_data['artists']
        album = song_data['album']
    else:
        if isinstance(song_data['album'], dict):
            album = song_data.get('album', {}).get('name', '')
        else:
            album = song_data.get('album', '')


    if song_data.get('thumbnail'):
        thumbnail = [song_data['thumbnail']]
    elif song_data['thumbnails'] == None:
        thumbnail = json.loads(request.form.get('thumbnails')).get('url')
    else:
        thumbnail = song_data['thumbnails'][-1]['url']

    song = Song(video_url=video_url, title=song_data['title'], artists=artists, duration_str=duration_str, videoId=song_data['videoId'], thumbnail=thumbnail, duration_sec=duration_sec, album=album)
    return song

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

@app.route('/search', methods=['POST'])
def search():
    search_query = request.form.get('search_query')
    if search_query == "":
        return '', 204
    results = spit_filter(search_query)
    filter = results['filter']
    search_query = results['search_query']
    if filter == 'url':
        pl = ytmusic.get_playlist(playlistId=search_query, limit=5)
        return render_template('search.html', search=Playlist(pl).get_items())
    if filter == 'radio':
        radio = ytmusic.get_watch_playlist(search_query, radio=True)
        return render_template('search.html', search=Radio(radio).get_items())
    jsons = ytmusic.search(search_query, filter=filter)
    if filter == 'playlists':
        return render_template('playlists.html', playlists=jsons)
    if filter == 'artists':
        return render_template('artists.html', artists=jsons)
    if filter == 'albums':
        return render_template('search.html', search=Albums(jsons).get_items())
    return render_template('search.html', search=Songs(jsons).get_items())

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
    json_song_data = json.loads(song_data)
    if json_song_data.get('type') == 'Album':
        album = ytmusic.get_album(json_song_data['videoId'])
        socketio.emit('alert', f'Added album to queue: {json_song_data["title"]} by {", ".join(json_song_data["artists"])}')
        for song in album.get('tracks', []):
            song['thumbnail'] = json_song_data['thumbnail']
            s = create_song(song)
            player.queue.add_song_at_end(s)
            socketio.emit('update_queue', player.queue.get_queues())
        if player.get_play_state() == 'Ended':
            player.play_queue()
        return 'OK', 200
    song = create_song(song_data)
    player.queue.add_song_after_current(song)
    if player.get_play_state() == 'Ended':
        player.play_queue()
    socketio.emit('alert', f'Playing next: {song.title} by {", ".join(song.artists)}')
    socketio.emit('update_queue', player.queue.get_queues())
    return 'OK', 200

@app.route('/add_to_queue', methods=['POST'])
def add_to_queue():
    song_data = request.form.get('song')
    json_song_data = json.loads(song_data)
    if json_song_data.get('type') == 'Album':
        album = ytmusic.get_album(json_song_data['videoId'])
        socketio.emit('alert', f'Added album to queue: {json_song_data["title"]} by {", ".join(json_song_data["artists"])}')
        for song in album.get('tracks', []):
            song['thumbnail'] = json_song_data['thumbnail']
            s = create_song(song)
            player.queue.add_song_at_end(s)
            socketio.emit('update_queue', player.queue.get_queues())
        if player.get_play_state() == 'Ended':
            player.play_queue()
        return 'OK', 200
    song = create_song(song_data)
    player.queue.add_song_at_end(song)
    if player.get_play_state() == 'Ended':
        player.play_queue()
    socketio.emit('alert', f'Added to queue: {song.title} by {", ".join(song.artists)}')
    socketio.emit('update_queue', player.queue.get_queues())
    return 'OK', 200

@app.route('/radio', methods=['POST'])
def radio():
    socketio.emit('alert', 'adding radio')
    videoId = request.form.get('videoId')
    radio = ytmusic.get_watch_playlist(videoId, radio=True)
    player.queue.set_radio(radio)
    socketio.emit('update_queue', player.queue.get_queues())
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

@app.route('/open_album', methods=['POST'])
def open_album():
    browseId = request.form.get('browseId')
    album = ytmusic.get_album(browseId)
    album = Album(album)
    return render_template('search.html', search=album.get_items())

@app.route('/clear_queue', methods=['POST'])
def clear_queue():
    player.queue.clear_queue()
    socketio.emit('update_queue', player.queue.get_queues())
    return 'OK', 200

@app.route('/play_all', methods=['POST'])
def play_all():
    songs = json.loads(request.form.get('songs')).get('tracks')
    for index, song_data in enumerate(songs):
        videoId = song_data['videoId']
        video_url = f'https://music.youtube.com/watch?v={videoId}'
        artists = [artist['name'] for artist in song_data['artists']]
        album_dict = song_data.get('album') or {}
        album =  album_dict.get('name', 'no album found')
        song = Song(video_url=video_url, title=song_data['title'], artists=artists, duration=song_data['duration_seconds'], videoId=song_data['videoId'], thumbnail=song_data['thumbnails'][-1]['url'], duration_string=song_data['duration'], album=album)
        player.queue.add_song_at_end(song)
        if index == 0 and player.get_play_state() == 'Ended':
            player.play_queue()
        socketio.emit('update_queue', player.queue.get_queues())
    return 'OK', 200

# Start the VLC monitor in a separate thread
vlc_thread = threading.Thread(target=vlc_monitor, daemon=True)
vlc_thread.start()

if __name__ == '__main__':
    app.run(port=5000, host='0.0.0.0')
