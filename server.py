from flask import Flask, render_template, request
from src.classes import Song
import src.browser as browser
import json
from flask_socketio import SocketIO
from flask_cors import CORS
import time

driver = None
user = None

with open('users.json', 'r') as file:
    data = json.load(file)
    user_data = data.get('users', [])

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
CORS(app,resources={r"/*":{"origins":"*"}})
socketio = SocketIO(app,cors_allowed_origins="*")

def init_songs():
    songs = []
    songs.append(Song('https://lh3.googleusercontent.com/Zq_05DOovkb1rka2hLAR6Gb5FwrQ2sdXI6HVRSYo-fOXeMUn4xA6Jb9eVYw6U3TaREccUV9F1iAI_qRK=w60-h60-l90-rj', 'TheFatRat - Monody (feat. Laura Brehm)', 'https://music.youtube.com/watch?v=2Vv-BfVoq4g', 'TheFatRat', 'Monody', '4:51', 0))
    songs.append(Song('https://lh3.googleusercontent.com/Zq_05DOovkb1rka2hLAR6Gb5FwrQ2sdXI6HVRSYo-fOXeMUn4xA6Jb9eVYw6U3TaREccUV9F1iAI_qRK=w60-h60-l90-rj', 'TheFatRat - Monody (feat. Laura Brehm)aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', 'https://music.youtube.com/watch?v=2Vv-BfVoq4g', 'TheFatRat', 'Monody', '4:51', 1))
    songs.append(Song('https://lh3.googleusercontent.com/Zq_05DOovkb1rka2hLAR6Gb5FwrQ2sdXI6HVRSYo-fOXeMUn4xA6Jb9eVYw6U3TaREccUV9F1iAI_qRK=w60-h60-l90-rj', 'TheFatRat - Monody (feat. Laura Brehm)', 'https://music.youtube.com/watch?v=2Vv-BfVoq4g', 'TheFatRat', 'Monody', '4:51', 2))
    songs.append(Song('https://lh3.googleusercontent.com/Zq_05DOovkb1rka2hLAR6Gb5FwrQ2sdXI6HVRSYo-fOXeMUn4xA6Jb9eVYw6U3TaREccUV9F1iAI_qRK=w60-h60-l90-rj', 'TheFatRat - Monody (feat. Laura Brehm)', 'https://music.youtube.com/watch?v=2Vv-BfVoq4g', 'TheFatRat', 'Monody', '4:51', 3))
    songs.append(Song('data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7', 'TheFatRat - Monody (feat. Laura Brehm)', 'https://music.youtube.com/watch?v=2Vv-BfVoq4g', 'TheFatRat', 'Monody', '4:51', 4))
    return songs


@socketio.on('connect')
def handle_connect():
    print('Client connected')
    socketio.emit('innerHTML', {'html': render_template('songs.html', songs=browser.songs), 'div': '#song-container'})
    socketio.emit('outerHTML', {'html': render_template('player_bar.html', song=browser.player_bar, play_status=browser.get_play_state(driver)), 'div': '#player-bar'})
    socketio.emit('innerHTML', {'html': render_template('queue_item.html', queue=browser.queue_list), 'div': '#queue'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')


@app.route('/')
def index():
    global user
    if user is None:
        return render_template('login.html', users=user_data)
    # user = [user for user in user_data if user.get('id') == '1'][0]
    return render_template('index.html', user=user)

@app.route('/login/<int:user_id>', methods=['POST'])
def login(user_id):
    if user_id is None:
        return '', 400
    global driver
    if driver is not None:
        driver.quit()
    _user = [user for user in user_data if user.get('id') == str(user_id)][0]
    driver = browser.start_selenium(_user.get('firefox_profile'))
    global user
    user = _user
    return render_template('index.html', user=user)

@app.route('/logout', methods=['POST'])
def logout():
    global driver
    if driver is not None:
        driver.quit()
        driver = None
    global user
    user = None
    return render_template('login.html', users=user_data)

@app.route('/init')
def init():
    browser.songs = init_songs()
    # return render_template('songs.html', songs=init_songs())
    socketio.emit('innerHTML', {'html': render_template('songs.html', songs=init_songs()), 'div': '#song-container'})
    return '', 204

@app.route('/player_bar')
def player_bar():
    song = browser.get_player_bar(driver)
    socketio.emit('innerHTML', {'html': render_template('player_bar.html', song=song, play_status=browser.get_play_state(driver)), 'div': '#player-bar'})
    return '', 204

@app.route('/play_pause', methods=['POST'])
def play_pause():
    browser.controll(driver, 'play/pause')
    time.sleep(.3)
    socketio.emit('outerHTML', {'html': render_template('player_bar.html', song=browser.get_player_bar(driver), play_status=browser.get_play_state(driver)), 'div': '#player-bar'})
    return '', 204

@app.route('/next', methods=['POST'])
def next():
    browser.controll(driver, 'next')
    time.sleep(.3)
    socketio.emit('outerHTML', {'html': render_template('player_bar.html', song=browser.get_player_bar(driver), play_status=browser.get_play_state(driver)), 'div': '#player-bar'})
    socketio.emit('innerHTML', {'html': render_template('queue_item.html', queue=browser.queue(driver)), 'div': '#queue'})
    return '', 204

@app.route('/prev', methods=['POST'])
def prev():
    browser.controll(driver, 'prev')
    time.sleep(.3)
    socketio.emit('outerHTML', {'html': render_template('player_bar.html', song=browser.get_player_bar(driver), play_status=browser.get_play_state(driver)), 'div': '#player-bar'})
    socketio.emit('innerHTML', {'html': render_template('queue_item.html', queue=browser.queue(driver)), 'div': '#queue'})
    return '', 204

@app.route('/stop_selenium', methods=['POST'])
def stop_selenium():
    global driver
    if driver is not None:
        driver.quit()
    browser.songs = []
    browser.song_elements = []
    browser.player_bar = None
    browser.queue_list = []
    return '', 204

@app.route('/search', methods=['POST'])
def search():
    search_query = request.form.get('search_query')
    if search_query == "":
        return render_template('index.html', status='search_query was empty.')
    songs = browser.search(driver, search_query)
    # return render_template('songs.html', songs=songs)
    socketio.emit('innerHTML', {'html': render_template('songs.html', songs=songs), 'div': '#song-container'})
    return '', 204

@app.route('/radio/<int:index>', methods=['POST'])
def radio(index):
    browser.radio(driver, int(index))
    time.sleep(2)
    socketio.emit('outerHTML', {'html': render_template('player_bar.html', song=browser.get_player_bar(driver), play_status=browser.get_play_state(driver)), 'div': '#player-bar'})
    socketio.emit('innerHTML', {'html': render_template('queue_item.html', queue=browser.queue(driver)), 'div': '#queue'})
    return '', 204

@app.route('/add_to_queue/<int:index>', methods=['POST'])
def add_to_queue(index):
    browser.add_to_queue(driver, int(index))
    time.sleep(0.3)
    socketio.emit('innerHTML', {'html': render_template('queue_item.html', queue=browser.queue(driver)), 'div': '#queue'})
    return '', 204

@app.route('/play_next/<int:index>', methods=['POST'])
def play_next(index):
    browser.play_next(driver, int(index))
    time.sleep(0.3)
    socketio.emit('innerHTML', {'html': render_template('queue_item.html', queue=browser.queue(driver)), 'div': '#queue'})
    return '', 204

@app.route('/get_queue', methods=['GET'])
def get_queue():
    # return render_template('queue_item.html', queue=queue)
    socketio.emit('innerHTML', {'html': render_template('queue_item.html', queue=browser.queue(driver)), 'div': '#queue'})
    return '', 204

if __name__ == '__main__':
    socketio.run(app, debug=False, port=5001)
    if driver is not None:
        driver.quit()
