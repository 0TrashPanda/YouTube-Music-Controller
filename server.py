from src.search_builder import Album, Albums, Artists, Playlist, Playlists, Songs, Radio
from src.song import Song
from src.player import Player
from src.socket_client import app, socketio
from flask import jsonify, render_template, request, json
from ytmusicapi import YTMusic
from typing import Dict, Any

ytmusic = YTMusic()
player = Player()

# Socket Event Handlers
@socketio.on('connect')
def handle_connect():
    print('Client connected')
    socketio.emit('update_queue', player.queue.get_queues())
    if player.get_play_state() == 'Ended':
        return

    # Send initial state to client
    socketio.emit('current_song', player.get_current_song())
    socketio.emit('play_state', player.get_play_state())
    socketio.emit('current_time', player.get_time())
    socketio.emit('volume', player.player.audio_get_volume())

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('volume')
def handle_volume(volume: int):
    try:
        player.player.audio_set_volume(int(volume))
        socketio.emit('volume', volume)
    except:
        return

@socketio.on('reorder')
def handle_reorder(data):
    player.queue.reorder(data)
    socketio.emit('update_queue', player.queue.get_queues())

@socketio.on('seek')
def handle_seek(pos: float):
    player.player.set_position(float(pos))
    socketio.emit('current_time', player.get_time())

@socketio.on('search_suggestions')
def search_suggestions(request_data: Dict[str, str]):
    search_query = request_data.get('q', '').strip()
    sid = request.sid

    if not search_query:
        socketio.emit('search_suggestions', [], room=sid)
        return

    suggestions = ytmusic.get_search_suggestions(search_query, detailed_runs=True)
    socketio.emit('search_suggestions', suggestions, room=sid)

# Helper Functions
def parse_search_filter(search_query: str) -> Dict[str, str]:
    """Parse search query to determine filter type and actual search term"""
    parts = search_query.split('/')
    if len(parts) == 1:
        return {'filter': 'songs', 'search_query': search_query}

    filter_map = {
        'a': 'artists',
        'b': 'albums',
        'p': 'playlists',
        'v': 'videos',
        's': 'songs',
        'u': 'url',
        'r': 'radio'
    }

    filter_letter = parts[0].casefold()
    filter_type = filter_map.get(filter_letter, 'songs')
    return {
        'filter': filter_type,
        'search_query': '/'.join(parts[1:])
    }

def create_song(song_data: Dict[str, Any]) -> Song:
    """Create a Song object from song data"""
    if isinstance(song_data, str):
        song_data = json.loads(song_data)

    videoId = song_data['videoId']
    duration_str = song_data.get('duration_str', song_data.get('duration', '0:00'))
    duration_sec = song_data.get('duration_sec', song_data.get('duration_seconds', 0))
    video_url = f'https://music.youtube.com/watch?v={videoId}'

    # Handle artists
    artists = [artist if isinstance(artist, str) else artist['name']
               for artist in song_data['artists']]

    # Handle album
    if song_data.get('secondary'):
        artists = song_data['artists']
        album = song_data['album']
    else:
        album = (song_data.get('album', {}).get('name', '')
                if isinstance(song_data['album'], dict)
                else song_data.get('album', ''))

    # Handle thumbnail
    if song_data.get('thumbnail'):
        thumbnail = song_data['thumbnail']
    elif song_data['thumbnails'] is None:
        thumbnail = json.loads(request.form.get('thumbnails')).get('url')
    else:
        thumbnail = song_data['thumbnails'][-1]['url']

    return Song(
        video_url=video_url,
        title=song_data['title'],
        artists=artists,
        duration_str=duration_str,
        videoId=videoId,
        thumbnail=thumbnail,
        duration_sec=duration_sec,
        album=album
    )

# Route Handlers
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
    return jsonify({
        'current_time': player.get_time() // 1000,
        'total_time': player.get_length() // 1000
    })

@app.route('/play_pause', methods=['POST'])
def play_pause():
    player.play_pause()
    socketio.emit('current_time', player.get_time())
    return 'OK', 200

@app.route('/search', methods=['POST'])
def search():
    search_query = request.form.get('search_query')
    if not search_query:
        return '', 204

    results = parse_search_filter(search_query)
    filter_type = results['filter']
    search_query = results['search_query']

    if filter_type == 'url':
        pl = ytmusic.get_playlist(playlistId=search_query, limit=5)
        return render_template('search.html', search=Playlist(pl).get_items())

    if filter_type == 'radio':
        radio = ytmusic.get_watch_playlist(search_query, radio=True)
        return render_template('search.html', search=Radio(radio).get_items())

    search_results = ytmusic.search(search_query, filter=filter_type)

    result_handlers = {
        'playlists': lambda x: Playlists(x).get_items(),
        'artists': lambda x: Artists(x).get_items(),
        'albums': lambda x: Albums(x).get_items(),
        'songs': lambda x: Songs(x).get_items()
    }

    handler = result_handlers.get(filter_type, result_handlers['songs'])
    return render_template('search.html', search=handler(search_results))

@app.route('/play_next', methods=['POST'])
def play_next():
    song_data = json.loads(request.form.get('song'))

    # Handle playlist
    if song_data.get('type') == 'playlist':
        playlist = ytmusic.get_playlist(song_data['videoId'])
        socketio.emit('alert',
                     f'Added playlist to queue: {song_data["title"]} by {", ".join(song_data["artists"])}')

        for song in playlist.get('tracks', []):
            s = create_song(song)
            player.queue.add_song_at_end(s)

        socketio.emit('update_queue', player.queue.get_queues())
        if player.get_play_state() == 'Ended':
            player.play_queue()
        return 'OK', 200

    # Handle album
    if song_data.get('type') == 'Album':
        album = ytmusic.get_album(song_data['videoId'])
        socketio.emit('alert',
                     f'Added album to queue: {song_data["title"]} by {", ".join(song_data["artists"])}')

        for song in album.get('tracks', []):
            song['thumbnail'] = song_data['thumbnail']
            s = create_song(song)
            player.queue.add_song_at_end(s)

        socketio.emit('update_queue', player.queue.get_queues())
        if player.get_play_state() == 'Ended':
            player.play_queue()
        return 'OK', 200

    # Handle single song
    song = create_song(request.form.get('song'))
    player.queue.add_song_after_current(song)

    if player.get_play_state() == 'Ended':
        player.play_queue()

    socketio.emit('alert', f'Playing next: {song.title} by {", ".join(song.artists)}')
    socketio.emit('update_queue', player.queue.get_queues())
    return 'OK', 200

@app.route('/add_to_queue', methods=['POST'])
def add_to_queue():
    song_data = json.loads(request.form.get('song'))

    # Handle artist
    if song_data.get('type') == 'artist':
        artist = ytmusic.get_artist(song_data['videoId'])
        songs = ytmusic.get_playlist(artist['songs']['browseId'])
        socketio.emit('alert', f'Added all songs from {song_data["title"]} to queue')

        player.queue.radio_queue = []
        for song in songs.get('tracks', []):
            s = create_song(song)
            player.queue.add_song_at_end(s, radio=True)

        socketio.emit('update_queue', player.queue.get_queues())
        if player.get_play_state() == 'Ended':
            player.play_queue()
        return 'OK', 200

    # Handle playlist and album (similar to play_next)
    if song_data.get('type') in ['playlist', 'Album']:
        return play_next()

    # Handle single song
    song = create_song(request.form.get('song'))
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
        return 'OK', 200
    except ValueError:
        return '', 404

@app.route('/jump_queue', methods=['POST'])
def jump_queue():
    uuid = request.form.get('uuid')
    player.queue.jump_queue(uuid)
    return 'OK', 200

@app.route('/open_album', methods=['POST'])
def open_album():
    browseId = request.form.get('browseId')
    album = Album(ytmusic.get_album(browseId))
    return render_template('search.html', search=album.get_items())

@app.route('/open_playlist', methods=['POST'])
def open_playlist():
    browseId = request.form.get('browseId')
    playlist = Playlist(ytmusic.get_playlist(browseId))
    return render_template('search.html', search=playlist.get_items())

@app.route('/open_artist', methods=['POST'])
def open_artist():
    browseId = request.form.get('browseId')
    artist = ytmusic.get_artist(browseId)
    songs = ytmusic.get_playlist(artist['songs']['browseId'])
    playlist = Playlist(songs)
    return render_template('search.html', search=playlist.get_items())

@app.route('/clear_queue', methods=['POST'])
def clear_queue():
    is_radio = json.loads(request.form.get('isRadio'))
    player.queue.clear_queue(radio=is_radio)
    socketio.emit('update_queue', player.queue.get_queues())
    return 'OK', 200

@app.route('/play_all', methods=['POST'])
def play_all():
    songs = json.loads(request.form.get('songs')).get('tracks')

    for index, song_data in enumerate(songs):
        videoId = song_data['videoId']
        video_url = f'https://music.youtube.com/watch?v={videoId}'

        song = Song(
            video_url=video_url,
            title=song_data['title'],
            artists=[artist['name'] for artist in song_data['artists']],
            duration=song_data['duration_seconds'],
            videoId=videoId,
            thumbnail=song_data['thumbnails'][-1]['url'],
            duration_string=song_data['duration'],
            album=song_data.get('album', {}).get('name', 'no album found')
        )

        player.queue.add_song_at_end(song)

        if index == 0 and player.get_play_state() == 'Ended':
            player.play_queue()

        socketio.emit('update_queue', player.queue.get_queues())

    return 'OK', 200

if __name__ == '__main__':
    app.run(port=5000, host='0.0.0.0')
