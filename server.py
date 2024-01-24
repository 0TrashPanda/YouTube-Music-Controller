import os
import time
from flask import Flask, render_template, request
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from dotenv import load_dotenv
from classes import Song
from utils import song_length_to_sec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException



load_dotenv()

FIREFOX_PROFILE = os.getenv('FIREFOX_PROFILE')

app = Flask(__name__)

driver = None
song_elements = None
timeout=5

def start_selenium():
    global driver
    options = webdriver.FirefoxOptions()
    if FIREFOX_PROFILE is not None:
        options.profile = FIREFOX_PROFILE
    driver = webdriver.Firefox(options=options)
    driver.get('https://music.youtube.com/')

def control_youtube_music(action):
    if action == 'play/pause':
        try:
            play_pause_button = driver.find_element(By.ID, 'play-pause-button')
            play_pause_button.click()
        except:
            return '<p>Failed to find play/pause button.</p>'
        return '<p>Successfully sent play/pause command.</p>'

def init_songs():
    songs = []
    songs.append(Song('https://lh3.googleusercontent.com/Zq_05DOovkb1rka2hLAR6Gb5FwrQ2sdXI6HVRSYo-fOXeMUn4xA6Jb9eVYw6U3TaREccUV9F1iAI_qRK=w60-h60-l90-rj', 'TheFatRat - Monody (feat. Laura Brehm)', 'https://music.youtube.com/watch?v=2Vv-BfVoq4g', 'TheFatRat', 'Monody', '4:51', 0))
    songs.append(Song('https://lh3.googleusercontent.com/Zq_05DOovkb1rka2hLAR6Gb5FwrQ2sdXI6HVRSYo-fOXeMUn4xA6Jb9eVYw6U3TaREccUV9F1iAI_qRK=w60-h60-l90-rj', 'TheFatRat - Monody (feat. Laura Brehm)', 'https://music.youtube.com/watch?v=2Vv-BfVoq4g', 'TheFatRat', 'Monody', '4:51', 1))
    songs.append(Song('https://lh3.googleusercontent.com/Zq_05DOovkb1rka2hLAR6Gb5FwrQ2sdXI6HVRSYo-fOXeMUn4xA6Jb9eVYw6U3TaREccUV9F1iAI_qRK=w60-h60-l90-rj', 'TheFatRat - Monody (feat. Laura Brehm)', 'https://music.youtube.com/watch?v=2Vv-BfVoq4g', 'TheFatRat', 'Monody', '4:51', 2))
    songs.append(Song('https://lh3.googleusercontent.com/Zq_05DOovkb1rka2hLAR6Gb5FwrQ2sdXI6HVRSYo-fOXeMUn4xA6Jb9eVYw6U3TaREccUV9F1iAI_qRK=w60-h60-l90-rj', 'TheFatRat - Monody (feat. Laura Brehm)', 'https://music.youtube.com/watch?v=2Vv-BfVoq4g', 'TheFatRat', 'Monody', '4:51', 3))
    songs.append(Song('data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7', 'TheFatRat - Monody (feat. Laura Brehm)', 'https://music.youtube.com/watch?v=2Vv-BfVoq4g', 'TheFatRat', 'Monody', '4:51', 4))
    return songs

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/init')
def init():
    return render_template('songs.html', songs=init_songs())

@app.route('/player_bar')
def player_bar():
    ytmusic_player_bar = driver.find_element(By.CSS_SELECTOR, 'ytmusic-player-bar')
    thumbnail = ytmusic_player_bar.find_element(By.CSS_SELECTOR, 'img.image.style-scope.ytmusic-player-bar').get_attribute('src')
    lengths = ytmusic_player_bar.find_element(By.CSS_SELECTOR, 'span.time-info.style-scope.ytmusic-player-bar').text.split('/')
    current_time = song_length_to_sec(lengths[0])
    total_time = song_length_to_sec(lengths[1])
    title = ytmusic_player_bar.find_element(By.CSS_SELECTOR, 'yt-formatted-string.title.style-scope.ytmusic-player-bar').text
    artist = ytmusic_player_bar.find_element(By.CSS_SELECTOR, 'yt-formatted-string.byline.style-scope.ytmusic-player-bar.complex-string').find_element(By.XPATH, './/a[1]').text
    album = ytmusic_player_bar.find_element(By.CSS_SELECTOR, 'yt-formatted-string.byline.style-scope.ytmusic-player-bar.complex-string').find_element(By.XPATH, './/a[2]').text
    year = ytmusic_player_bar.find_element(By.CSS_SELECTOR, 'yt-formatted-string.byline.style-scope.ytmusic-player-bar.complex-string').find_element(By.XPATH, './/span[last()]').text
    return render_template('player_bar.html', thumbnail=thumbnail, current_time=current_time, total_time=total_time, title=title, artist=artist, album=album, year=year)

@app.route('/play_pause', methods=['POST'])
def play_pause():
    return control_youtube_music('play/pause')


@app.route('/control', methods=['POST'])
def control():
    action = request.form.get('action')
    if action == 'start':
        start_selenium()
    elif action == 'stop':
        global driver
        if driver is None:
            return render_template('index.html', status='Driver was already Stopped.')
        else:
            driver.quit()
            driver = None
    elif driver is None:
        return render_template('index.html', status='Failed to find driver.')
    return render_template('index.html', status=f'sent {action} command.')

@app.route('/search', methods=['POST'])
def search():
    search_query = request.form.get('search_query')
    if search_query == "":
        return render_template('index.html', status='search_query was empty.')
    try:
        search_input = driver.find_element(By.CSS_SELECTOR, 'input#input.style-scope.ytmusic-search-box')
        search_input.clear()
        search_input.send_keys(search_query)
        search_input.send_keys(Keys.RETURN)
    except:
        return render_template('index.html', status='Failed to find search input.')

    try:
        songs_button = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'a.yt-simple-endpoint.style-scope.ytmusic-chip-cloud-chip-renderer[title="Show song results"]'))
        )
        songs_button.click()
    except (TimeoutException, NoSuchElementException) as e:
        print(f"Couldn't click the element within {timeout} seconds. Error: {e}")
    time.sleep(0.3)

    song_container = driver.find_element(By.CSS_SELECTOR, 'div#contents.style-scope.ytmusic-shelf-renderer')
    global song_elements
    song_elements = song_container.find_elements(By.CSS_SELECTOR, 'ytmusic-responsive-list-item-renderer.style-scope.ytmusic-shelf-renderer')
    songs = []
    for index, song in enumerate(song_elements):
        print(f'Finding song {index}')
        try :
            song_thumbnail_link = song.find_element(By.CSS_SELECTOR, 'img#img.style-scope.yt-img-shadow').get_attribute('src')
            song_title_div = song.find_element(By.CSS_SELECTOR, 'yt-formatted-string.title.style-scope.ytmusic-responsive-list-item-renderer.complex-string')
            song_title = song_title_div.get_attribute('title')
            song_link = song.find_element(By.CSS_SELECTOR, 'a.yt-simple-endpoint.style-scope.yt-formatted-string').get_attribute('href')
            song_info_div = song.find_element(By.CSS_SELECTOR, 'yt-formatted-string.flex-column.style-scope.ytmusic-responsive-list-item-renderer.complex-string')
            artist = song_info_div.find_element(By.XPATH, './/a[1]').text
            album = song_info_div.find_element(By.XPATH, './/a[2]').text
            song_length = song_info_div.find_element(By.XPATH, './/span[last()]').text
        except:
            print(f'Failed to find song {index}')
            continue

        songs.append(Song(song_thumbnail_link, song_title, song_link, artist, album, song_length, index))

    return render_template('songs.html', songs=songs)

@app.route('/song_controll', methods=['POST'])
def song_controll():
    index = request.form.get('index')
    action = request.form.get('action')
    # if action == 'radio':
    #     driver.get(request.form.get('link'))
    #     return render_template('index.html', status=f'Successfully sent {action} command.')
    global song_elements
    kebab_menu = song_elements[int(index)].find_element(By.CSS_SELECTOR, 'div.yt-spec-touch-feedback-shape.yt-spec-touch-feedback-shape--touch-response')
    center_element_vertically(kebab_menu)
    time.sleep(0.3)
    ActionChains(driver).move_to_element(kebab_menu).perform()
    kebab_menu.click()
    menu = driver.find_element(By.CSS_SELECTOR, 'tp-yt-iron-dropdown.style-scope.ytmusic-popup-container')
    if action == 'radio':
        start_radio = driver.find_element(By.XPATH, "//yt-formatted-string[text()='Start radio']")
        start_radio.click()
    if action == 'add_to_queue':
        add_to_queue = driver.find_element(By.XPATH, "//yt-formatted-string[text()='Add to queue']")
        add_to_queue.click()
    if action == 'play_next':
        play_next = driver.find_element(By.XPATH, "//yt-formatted-string[text()='Play next']")
        play_next.click()
    return render_template('index.html', status=f'Successfully sent {action} command.')

def center_element_vertically(element):
    element_y = element.location['y']
    window_height = driver.execute_script("return window.innerHeight;")
    target_y = element_y - (window_height / 2)
    driver.execute_script(f"window.scrollTo(0, {int(target_y)});")



if __name__ == '__main__':
    app.run(debug=False, port=5001)
    if driver is not None:
        driver.quit()
