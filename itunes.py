import logging
import os
import sys
import xml.etree.ElementTree as ET

logging.basicConfig(
    filename=os.path.join(os.getcwd(), "transfer.txt"),
    filemode='w',
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))


def _create_itunes_tuple(song):
    idx_song = 3
    idx_artist = 5
    idx_album = 9
    return song[idx_song].text, song[idx_artist].text, song[idx_album].text


def read_itunes_library(xml_file_path: str):
    tree = ET.parse(xml_file_path)
    root = tree.getroot()
    raw_song_details = root.findall('./dict/dict/dict')

    # Create dictionary of entire library for simpler access
    song_dicts = {}
    idx_track_id = 1
    for song in raw_song_details:
        """
        Store as tuple in dictionary
        key = track ID (iTunes form)
        value = (song, artist, album)  # composer?
        """
        key = song[idx_track_id].text
        song_dicts[key] = _create_itunes_tuple(song)

    # Create dictionary of playlist arrays
    raw_playlist_details = root.findall('./dict/array/dict')
    playlist_dicts = {}

    idx_playlist_id = 5
    idx_title = 1
    # TODO: Incorporate these as part of the input file
    playlists_to_ignore = ['Library', 'Purchased', 'Recently Added', 'Recently Played', 'Top 25 Most Played',
                           'New', 'Review', 'To Show Dad', 'All']
    debug_list = ['Lit']

    for playlist in raw_playlist_details:
        """
        Store as tuple in dictionary
        key = track ID (iTunes form)
        value = (song, artist, album)  # composer?
        """
        title = playlist[idx_title].text
        # Check if we're choosing to ignore this playlist in the transfer
        if title in playlists_to_ignore:
            continue
        # Check if folder (ignore folders)
        if 'Folder' in [entry.text for entry in playlist.findall('key')]:
            logging.warning("Ignoring folder '{}'".format(title))
            continue
        if title in debug_list:  # DEBUG
            pass
        key = playlist[idx_playlist_id].text
        song_ids = [entry[1].text for entry in playlist.findall('./array/dict')]
        playlist_dicts[key] = (title, song_ids)
        pass

    # FIXME: Locations of song albums are not in consistent locations
    #  Need to find way to locate *key* before finding matching value
    return song_dicts, playlist_dicts


if __name__ == '__main__':
    songs, playlists = read_itunes_library(sys.argv[1])
