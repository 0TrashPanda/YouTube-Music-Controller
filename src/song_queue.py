from src.socket_client import socketio
from src.song import Song

class Queue:
    def __init__(self):
        self.queue = []
        self.radio_queue = []
        self.current_song = None

    def add_song_at_end(self, song, radio=False):
        if radio:
            self.radio_queue.append(song)
            if len(self.radio_queue) < 5:
                song.start_thread()
            return
        self.queue.append(song)
        song.start_thread()

    def add_song_after_current(self, song, offset=0):
        self.queue.insert(self.get_current_index() + 1 + offset, song)
        song.start_thread()

    def remove_song(self, uuid):
        for index, song in enumerate(self.queue):
            if str(song.get_id()) == str(uuid):
                self.remove_song_at_index(index)
                break
        for index, song in enumerate(self.radio_queue):
            if str(song.get_id()) == str(uuid):
                self.remove_song_at_index(index, radio=True)
                break
        socketio.emit('update_queue', self.get_queues())
        self.start_threads()

    def remove_song_at_index(self, index, radio=False):
        current_song_index = self.get_current_index()
        if index == current_song_index:
            self.next_song()
            from server import player
            player.play_queue()
        queue = self.queue if not radio else self.radio_queue
        queue.pop(index)
        if current_song_index > index and not radio:
            current_song_index -= 1

    def get_queue(self):
        return [song.toJSON() for song in self.queue]

    def get_radio_queue(self):
        return [song.toJSON() for song in self.radio_queue]

    def clear_queue(self, radio=False):
        print(radio)
        if radio is True:
            self.radio_queue.clear()
            print('cleared radio')
        else:
            self.queue.clear()
            print('cleared queue')

    def get_current_song(self):
        if self.queue:
            return self.queue[self.get_current_index()]
        else:
            return None

    def set_current_song(self, index):
        self.current_song = str(self.queue[index].get_id())

    def next_song(self):
        current_song_index = self.get_current_index()
        if current_song_index + 1 < len(self.queue):
            self.set_current_song(current_song_index + 1)
            return
        if len(self.radio_queue) > 0:
            self.add_song_at_end(self.radio_queue.pop(0))
            self.set_current_song(len(self.queue) - 1)
            socketio.emit('update_queue', self.get_queues())
            self.start_threads()
            return
        if len(self.queue) > 0:
            self.set_current_song(0)
        else:
            self.current_song = None

    def previous_song(self):
        current_song_index = self.get_current_index()
        if current_song_index - 1 < 0:
            current_song_index = len(self.queue) - 1
        else:
            self.set_current_song(current_song_index - 1)

    def set_radio(self, radio):
        self.radio_queue = []
        song_titles = [song.title for song in self.queue]
        for index, song_data in enumerate(radio['tracks']):
            if song_data['title'] in song_titles:
                continue
            videoId = song_data['videoId']
            video_url = f'https://music.youtube.com/watch?v={videoId}'
            artists = [artist['name'] for artist in song_data['artists']]
            length = song_data['length']
            duration_sec = sum(
                x * 60 ** i for i, x in enumerate(reversed(list(map(int, length.split(':'))))))
            song = Song(video_url=video_url, title=song_data['title'], artists=artists, duration_sec=duration_sec, videoId=song_data['videoId'],
                        thumbnail=song_data['thumbnail'][-1]['url'], duration_str=length, album=song_data.get('album', {}).get('name', ''))
            # current_song + index + 1, song
            self.add_song_at_end(song, radio=True)
            if index == 0:
                from server import player
                if player.get_play_state() == 'Ended':
                    player.queue.next_song()
        socketio.emit('update_queue', self.get_queues())

    def jump_queue(self, uuid):
        for song in self.queue:
            if str(song.get_id()) == str(uuid):
                self.current_song = str(uuid)
                from server import player
                player.play_queue()
                break
        for song in self.radio_queue:
            if str(song.get_id()) == str(uuid):
                self.add_song_after_current(
                    self.radio_queue.pop(self.radio_queue.index(song)))
                self.current_song = str(uuid)
                from server import player
                player.play_queue()
                socketio.emit('update_queue', self.get_queues())
                self.start_threads()
                break

    def reorder(self, uuid_list):
        queue = uuid_list.get('queue', [])
        radio_queue = uuid_list.get('radio_queue', [])
        uuid_map_queue = {str(song.get_id()): song for song in self.queue}
        uuid_map_radio = {
            str(song.get_id()): song for song in self.radio_queue}

        def rm_dupes(x):
            return list(dict.fromkeys(x))

        self.queue = [uuid_map_queue.pop(uuid) if uuid_map_queue.get(uuid) else uuid_map_radio.pop(uuid) for uuid in rm_dupes(queue) if uuid_map_queue.get(
            uuid) or uuid_map_radio.get(uuid)] + [song for song in uuid_map_queue.values() if str(song.get_id()) not in radio_queue]
        self.radio_queue = [uuid_map_radio.pop(uuid) if uuid_map_radio.get(uuid) else uuid_map_queue.pop(uuid) for uuid in rm_dupes(
            radio_queue) if uuid_map_queue.get(uuid) or uuid_map_radio.get(uuid)] + list(uuid_map_radio.values())

        self.start_threads()

    def get_current_index(self):
        for index, song in enumerate(self.queue):
            if str(song.get_id()) == self.current_song:
                return index
        return 0

    def get_queues(self):
        return {
            'queue': self.get_queue(),
            'radio_queue': self.get_radio_queue()
        }

    def start_threads(self):
        for song in self.queue:
            song.start_thread()
        for song in self.radio_queue[:5]:
            song.start_thread()
