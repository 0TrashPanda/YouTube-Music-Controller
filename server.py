from flask import Flask, render_template, request
from dotenv import load_dotenv
from src.classes import Song
from src.utils import song_length_to_sec
import src.browser as browser
import json

driver = None
user = None

with open('users.json', 'r') as file:
    data = json.load(file)
    user_data = data.get('users', [])

app = Flask(__name__)

def init_songs():
    songs = []
    songs.append(Song('https://lh3.googleusercontent.com/Zq_05DOovkb1rka2hLAR6Gb5FwrQ2sdXI6HVRSYo-fOXeMUn4xA6Jb9eVYw6U3TaREccUV9F1iAI_qRK=w60-h60-l90-rj', 'TheFatRat - Monody (feat. Laura Brehm)', 'https://music.youtube.com/watch?v=2Vv-BfVoq4g', 'TheFatRat', 'Monody', '4:51', 0))
    songs.append(Song('https://lh3.googleusercontent.com/Zq_05DOovkb1rka2hLAR6Gb5FwrQ2sdXI6HVRSYo-fOXeMUn4xA6Jb9eVYw6U3TaREccUV9F1iAI_qRK=w60-h60-l90-rj', 'TheFatRat - Monody (feat. Laura Brehm)aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', 'https://music.youtube.com/watch?v=2Vv-BfVoq4g', 'TheFatRat', 'Monody', '4:51', 1))
    songs.append(Song('https://lh3.googleusercontent.com/Zq_05DOovkb1rka2hLAR6Gb5FwrQ2sdXI6HVRSYo-fOXeMUn4xA6Jb9eVYw6U3TaREccUV9F1iAI_qRK=w60-h60-l90-rj', 'TheFatRat - Monody (feat. Laura Brehm)', 'https://music.youtube.com/watch?v=2Vv-BfVoq4g', 'TheFatRat', 'Monody', '4:51', 2))
    songs.append(Song('https://lh3.googleusercontent.com/Zq_05DOovkb1rka2hLAR6Gb5FwrQ2sdXI6HVRSYo-fOXeMUn4xA6Jb9eVYw6U3TaREccUV9F1iAI_qRK=w60-h60-l90-rj', 'TheFatRat - Monody (feat. Laura Brehm)', 'https://music.youtube.com/watch?v=2Vv-BfVoq4g', 'TheFatRat', 'Monody', '4:51', 3))
    songs.append(Song('data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7', 'TheFatRat - Monody (feat. Laura Brehm)', 'https://music.youtube.com/watch?v=2Vv-BfVoq4g', 'TheFatRat', 'Monody', '4:51', 4))
    return songs

@app.route('/')
def index():
    global user
    print(user)
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
    return render_template('songs.html', songs=init_songs())

@app.route('/player_bar')
def player_bar():
    song = browser.player_bar(driver)
    return render_template('player_bar.html', song=song)

@app.route('/play_pause', methods=['POST'])
def play_pause():
    browser.controll(driver, 'play/pause')

@app.route('/next', methods=['POST'])
def next():
    browser.controll(driver, 'next')

@app.route('/prev', methods=['POST'])
def prev():
    browser.controll(driver, 'prev')

@app.route('/stop_selenium', methods=['POST'])
def stop_selenium():
    global driver
    if driver is not None:
        driver.quit()
    return '', 204

@app.route('/search', methods=['POST'])
def search():
    search_query = request.form.get('search_query')
    if search_query == "":
        return render_template('index.html', status='search_query was empty.')
    songs = browser.search(driver, search_query)
    return render_template('songs.html', songs=songs)

@app.route('/radio/<int:index>', methods=['POST'])
def radio(index):
    song = browser.radio(driver, int(index))
    return '', 204

@app.route('/add_to_queue/<int:index>', methods=['POST'])
def add_to_queue(index):
    browser.add_to_queue(driver, int(index))
    return '', 204

@app.route('/play_next/<int:index>', methods=['POST'])
def play_next(index):
    browser.play_next(driver, int(index))
    return '', 204

@app.route('/get_queue', methods=['GET'])
def get_queue():
    queue = browser.queue(driver)
    return render_template('queue_item.html', queue=queue)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
    if driver is not None:
        driver.quit()
