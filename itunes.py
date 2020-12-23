import logging
import os
import sys
import xml.etree.ElementTree as ET
from pprint import pprint


# logging.basicConfig(
#     filename=os.path.join(os.getcwd(), "transfer.txt"),
#     filemode='w',
#     format='%(asctime)s %(levelname)-8s %(message)s',
#     level=logging.INFO,
#     datefmt='%Y-%m-%d %H:%M:%S')
# logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))


def _create_itunes_tuple(song):
    keys = [entry.text for entry in song.findall('key')]

    # Get song name. Assuming all songs have a name here.
    idx_song = 2 * keys.index('Name') + 1
    song_name = song[idx_song].text

    # Get artist -- which may not be known/present
    try:
        idx_artist = 2 * keys.index('Artist') + 1
        artist = song[idx_artist].text
    except ValueError:
        logging.warning("\tNo artist present for '{}'".format(song_name))
        artist = None

    # Get album -- which may not be known/present
    try:
        idx_album = 2 * keys.index('Album') + 1
        album = song[idx_album].text
    except ValueError:
        logging.warning("\tNo album present for '{}'".format(song_name))
        album = None

    return song_name, artist, album


def read_itunes_library(exported_library_filename: str = "Library.xml", playlists_to_ignore: list = None):
    """
    Read the iTunes library from a provided XML filepath
    NOTE: You CANNOT assume the ORDER or NUMBER of keys in each song or playlist
    :param exported_library_filename: Name of XML file from iTunes library export
    :param playlists_to_ignore: Playlist titles to ignore while importing
    :return: None
    """
    xml_file_path = os.path.join(os.getcwd(), 'res', exported_library_filename)
    logging.info("Loading iTunes library from {}".format(xml_file_path))

    tree = ET.parse(xml_file_path)
    root = tree.getroot()
    raw_song_details = root.findall('./dict/dict/dict')

    # Create dictionary of entire library for simpler access
    song_dicts = {}
    for song in raw_song_details:
        """
        Store as tuple in dictionary
        key = track ID (iTunes form)
        value = (song, artist, album)  # composer?
        """
        all_keys = [entry.text for entry in song.findall('key')]
        idx_track_id = 2 * all_keys.index('Track ID') + 1
        key = song[idx_track_id].text
        song_dicts[key] = _create_itunes_tuple(song)

    # Create dictionary of playlist arrays
    raw_playlist_details = root.findall('./dict/array/dict')
    playlist_dicts = {}

    for playlist in raw_playlist_details:
        """
        Store as tuple in dictionary
        key = track ID (iTunes version)
        value = (song, artist, album)  # composer?
        """
        all_keys = [entry.text for entry in playlist.findall('key')]  # Get keys in playlist

        # Get title
        idx_title = 2 * all_keys.index('Name') + 1
        title = playlist[idx_title].text

        # Check if we're choosing to ignore this playlist in the transfer
        if title in playlists_to_ignore:
            continue

        # Check if folder (ignore folders)
        if 'Folder' in all_keys:
            logging.warning("\tIgnoring folder '{}'".format(title))
            continue

        # Get playlist ID
        idx_playlist_id = 2 * all_keys.index('Playlist ID') + 1
        key = playlist[idx_playlist_id].text

        # Get song ID's in playlist. Always in <key/><integer/> form.
        song_ids = [entry[1].text for entry in playlist.findall('./array/dict')]

        playlist_dicts[key] = (title, song_ids)  # Add to dictionary

    # Display information about playlist count
    logging.info("{} iTunes playlists set for transfer".format(len(playlist_dicts)))
    pnames = [name for _, (name, _) in playlist_dicts.items()]
    pprint(pnames)

    return song_dicts, playlist_dicts


if __name__ == '__main__':
    if len(sys.argv) < 3:
        raise IOError("Not enough input arguments. See README for usage.")
    playlists_to_ignore = sys.argv[2].split(',')
    songs, playlists = read_itunes_library(sys.argv[1], playlists_to_ignore)
    pass
