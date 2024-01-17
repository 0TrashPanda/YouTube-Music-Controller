from dataclasses import dataclass


@dataclass
class Song:
    song_thumbnail_link : str
    song_title : str
    song_link : str
    artist : str
    album : str
    song_length : int
    song_length_minutes : int
    index : int

    def __init__(self, song_thumbnail_link, song_title, song_link, artist, album, song_length, index):
        if song_thumbnail_link == "data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7":
            song_thumbnail_link = "https://i.imgur.com/7fOzFIgs.jpg"
        self.song_thumbnail_link = song_thumbnail_link
        self.song_thumbnail_link = song_thumbnail_link
        self.song_title = song_title
        self.song_link = song_link
        self.artist = artist
        self.album = album
        if song_length == "":
            song_length = "0:00"
        self.song_length = song_length
        self.set_song_length_minuts(song_length)
        self.index = index

    def set_song_length_minuts(self, song_length):
        song_length = song_length.split(':')
        if len(song_length) == 3:
            self.song_length_minutes = int(song_length[0]) * 3600 + int(song_length[1]) * 60 + int(song_length[2])
        elif len(song_length) == 2:
            self.song_length_minutes = int(song_length[0]) * 60 + int(song_length[1])
        else:
            self.song_length_minutes = int(song_length[0])

