def song_length_to_sec(song_length):
        song_length = song_length.split(':')
        if len(song_length) == 3:
            return int(song_length[0]) * 3600 + int(song_length[1]) * 60 + int(song_length[2])
        elif len(song_length) == 2:
            return int(song_length[0]) * 60 + int(song_length[1])
        else:
            return int(song_length[0])