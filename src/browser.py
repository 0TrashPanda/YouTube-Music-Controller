import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from src.classes import Player_bar, Song
from src.utils import song_length_to_sec

timeout = 5
max_songs = 15

songs = []
song_elements = []
player_bar = None
queue_list = []
queue_elements = []

def start_selenium(FIREFOX_PROFILE):
    options = webdriver.FirefoxOptions()
    if FIREFOX_PROFILE is not None:
        options.profile = FIREFOX_PROFILE
    driver = webdriver.Firefox(options=options)
    driver.get('https://music.youtube.com/')
    return driver

def get_play_state(driver):
    try:
        play_pause_button = driver.find_element(By.ID, 'play-pause-button')
        return play_pause_button.get_attribute('title')
    except:
        print('Failed to find play/pause button.')
        return None

def get_player_page_state(driver):
    try:
        player_page = driver.find_element(By.CSS_SELECTOR, 'tp-yt-paper-icon-button.toggle-player-page-button.style-scope.ytmusic-player-bar')
        return player_page.get_attribute('aria-label').split(' ')[0]
    except:
        print('Failed to find player page.')
        return None

def toggle_player_page(driver):
    try:
        player_page = driver.find_element(By.CSS_SELECTOR, 'tp-yt-paper-icon-button.toggle-player-page-button.style-scope.ytmusic-player-bar')
        player_page.click()
    except:
        print('Failed to find player page.')

def open_player_page(driver):
    if get_player_page_state(driver) == 'Close':
        return
    toggle_player_page(driver)

def close_player_page(driver):
    if get_player_page_state(driver) == 'Open':
        return
    toggle_player_page(driver)

def controll(driver, action):
    match action:
        case 'play/pause':
            try:
                play_pause_button = driver.find_element(By.ID, 'play-pause-button')
                play_pause_button.click()
            except:
                print('Failed to find play/pause button.')
        case 'next':
            try:
                next_button = driver.find_element(By.CSS_SELECTOR, 'tp-yt-paper-icon-button.next-button.style-scope.ytmusic-player-bar')
                next_button.click()
            except:
                print('Failed to find next button.')
        case 'prev':
            try:
                prev_button = driver.find_element(By.CSS_SELECTOR, 'tp-yt-paper-icon-button.previous-button.style-scope.ytmusic-player-bar')
                prev_button.click()
            except:
                print('Failed to find prev button.')
        case _:
            print('Invalid action.')

def get_player_bar(driver):
    global player_bar
    ytmusic_player_bar = driver.find_element(By.CSS_SELECTOR, 'ytmusic-player-bar')
    thumbnail = ytmusic_player_bar.find_element(By.CSS_SELECTOR, 'img.image.style-scope.ytmusic-player-bar').get_attribute('src')
    lengths = ytmusic_player_bar.find_element(By.CSS_SELECTOR, 'span.time-info.style-scope.ytmusic-player-bar').text.split('/')
    current_time = song_length_to_sec(lengths[0])
    total_time = song_length_to_sec(lengths[1])
    title = ytmusic_player_bar.find_element(By.CSS_SELECTOR, 'yt-formatted-string.title.style-scope.ytmusic-player-bar').text
    artist = ytmusic_player_bar.find_element(By.CSS_SELECTOR, 'yt-formatted-string.byline.style-scope.ytmusic-player-bar.complex-string').find_element(By.XPATH, './/a[1]').text
    album = ytmusic_player_bar.find_element(By.CSS_SELECTOR, 'yt-formatted-string.byline.style-scope.ytmusic-player-bar.complex-string').find_element(By.XPATH, './/a[2]').text
    year = ytmusic_player_bar.find_element(By.CSS_SELECTOR, 'yt-formatted-string.byline.style-scope.ytmusic-player-bar.complex-string').find_element(By.XPATH, './/span[last()]').text
    player_bar = Player_bar(thumbnail, current_time, total_time, title, artist, album, year)
    return player_bar

def search(driver, search_query):
    try:
        search_input = driver.find_element(By.CSS_SELECTOR, 'input#input.style-scope.ytmusic-search-box')
        search_input.clear()
        search_input.send_keys(search_query)
        search_input.send_keys(Keys.RETURN)
    except:
        print('Failed to find search input.')

    try:
        songs_button = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'a.yt-simple-endpoint.style-scope.ytmusic-chip-cloud-chip-renderer[title="Show song results"]'))
        )
        songs_button.click()
    except (TimeoutException, NoSuchElementException) as e:
        print(f"Couldn't click the element within {timeout} seconds. Error: {e}")

    wait_for_loading(driver)

    global song_elements

    song_container = driver.find_element(By.CSS_SELECTOR, 'div#contents.style-scope.ytmusic-shelf-renderer')
    song_elements = song_container.find_elements(By.CSS_SELECTOR, 'ytmusic-responsive-list-item-renderer.style-scope.ytmusic-shelf-renderer')

    global songs
    songs = []

    for index, song in enumerate(song_elements):
        print(f'Finding song {index + 1}/{max_songs}')
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
            print(f'Failed to find song {index + 1}')
            continue
        songs.append(Song(song_thumbnail_link, song_title, song_link, artist, album, song_length, index))
        print(f'Found song {index + 1}')
    return songs

def queue(driver):
    global queue_list
    queue_list = []
    open_player_page(driver)
    time.sleep(0.1)
    global queue_elements
    queue_container = driver.find_element(By.CSS_SELECTOR, 'div#contents.style-scope.ytmusic-player-queue')
    queue_elements = queue_container.find_elements(By.CSS_SELECTOR, 'ytmusic-player-queue-item')
    for index, queue_element in enumerate(queue_elements):
        try:
            thumbnail = queue_element.find_element(By.CSS_SELECTOR, 'img.style-scope.yt-img-shadow').get_attribute('src')
            title = queue_element.find_element(By.CSS_SELECTOR, 'yt-formatted-string.song-title.style-scope.ytmusic-player-queue-item').text
            artist = queue_element.find_element(By.CSS_SELECTOR, 'yt-formatted-string.byline.style-scope.ytmusic-player-queue-item').text
            length = queue_element.find_element(By.CSS_SELECTOR, 'yt-formatted-string.duration.style-scope.ytmusic-player-queue-item').text
            queue_list.append(Song(thumbnail, title, '', artist, '', length, index))
        except:
            print(f'Failed to find song {index}')
            continue
    return queue_list

def radio(driver, index):
    close_player_page(driver)
    time.sleep(0.1)
    menu = kebab_menu(driver, index, 'songs')
    start_radio = menu.find_element(By.XPATH, "//yt-formatted-string[text()='Start radio']")
    start_radio.click()

def add_to_queue(driver, index):
    close_player_page(driver)
    time.sleep(0.1)
    menu = kebab_menu(driver, index, 'songs')
    add_to_queue = menu.find_element(By.XPATH, "//yt-formatted-string[text()='Add to queue']")
    add_to_queue.click()

def play_next(driver, index):
    close_player_page(driver)
    time.sleep(0.1)
    menu = kebab_menu(driver, index, 'songs')
    play_next = menu.find_element(By.XPATH, "//yt-formatted-string[text()='Play next']")
    play_next.click()

def kebab_menu(driver, index, list):
    if list == 'songs':
        global song_elements
        list = song_elements
    elif list == 'queue':
        global queue_elements
        list = queue_elements
    kebab_menu = list[index].find_element(By.CSS_SELECTOR, 'div.yt-spec-touch-feedback-shape.yt-spec-touch-feedback-shape--touch-response')
    center_element_vertically(driver, kebab_menu)
    time.sleep(0.1)
    ActionChains(driver).move_to_element(kebab_menu).perform()
    time.sleep(0.1)
    kebab_menu.click()
    wait_for_style_change(driver, 'tp-yt-iron-dropdown.style-scope.ytmusic-popup-container', 'z-index')
    return driver.find_element(By.CSS_SELECTOR, 'tp-yt-iron-dropdown.style-scope.ytmusic-popup-container')

def remove_from_queue(driver, index):
    open_player_page(driver)
    time.sleep(0.1)
    menu = kebab_menu(driver, index, 'queue')
    remove_from_queue = menu.find_element(By.XPATH, "//yt-formatted-string[text()='Remove from queue']")
    remove_from_queue.click()

def wait_for_loading(driver):
    start_loading(driver)
    stop_loading(driver)

def center_element_vertically(driver, element):
    element_y = element.location['y']
    window_height = driver.execute_script("return window.innerHeight;")
    target_y = element_y - (window_height / 2)
    driver.execute_script(f"window.scrollTo(0, {int(target_y)});")

def start_loading(driver):
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script(
                "return document.querySelector('yt-page-navigation-progress.style-scope.ytmusic-app').getAttribute('aria-valuenow')"
            ) <= str(100)
        )
    except TimeoutException:
        print("loading took too long")

def stop_loading(driver):
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script(
                "return document.querySelector('yt-page-navigation-progress.style-scope.ytmusic-app').getAttribute('aria-valuenow')"
            ) == str(100)
        )
    except TimeoutException:
        print("loading took too long")

def wait_for_style_change(driver, target_element_selector, target_property):
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: target_property in d.find_element(By.CSS_SELECTOR, target_element_selector).get_attribute("style")
        )
    except TimeoutException:
        print(f"Timed out waiting for style change: {target_property}")
