import logging
import os
import sys

import spotipy
from spotipy.oauth2 import SpotifyOAuth
import xml.etree.ElementTree as ET

logging.basicConfig(
    filename=os.path.join(os.getcwd(), "transfer.txt"),
    filemode='w',
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))


def get_credentials(directory: str = os.path.expanduser('~'), filename: str = '.spotify_credentials'):
    """
    Confirm Spotify credentials and set environment variables appropriately
    Both SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET environment variables must be set
    :param directory: Directory in which file exists
    :param filename: File that contains credentials
    :return: Authorization Mananger
    """
    fpath = os.path.join(directory, filename)
    if not os.path.exists(fpath):
        raise IOError("File path does not exist: {}".format(fpath))
    with open(fpath, 'r') as f:
        lines = f.readlines()
        username = lines[0].replace('\n', '')
        id_num = lines[1].replace('\n', '')
        secret = lines[2].replace('\n', '')
        if len(lines) > 3:
            redirect_uri = lines[3].replace('\n', '')
        else:
            redirect_uri = "http://localhost:8080"
        logging.info("Acquired credentials")
        return username, SpotifyOAuth(client_id=id_num, client_secret=secret, redirect_uri=redirect_uri)


def create_playlist(auth_mgr: SpotifyOAuth, username: str, playlist_name: str):
    """
    Create Spotify playlist
    :param auth_mgr: Authorization manager
    :param username: Name of user
    :param playlist_name: Name of playlist to create
    :return: None
    """
    auth_mgr.scope = "playlist-modify-public"
    sp = spotipy.Spotify(auth_manager=auth_mgr)
    sp.user_playlist_create(username, playlist_name)
    return


def view_recently_played(auth_mgr: SpotifyOAuth):
    auth_mgr.scope = "user-read-recently-played"
    sp = spotipy.Spotify(auth_manager=auth_mgr)
    print(sp.current_user_recently_played())
    return


def search(auth_mgr: SpotifyOAuth, track_name: str = None, artist: str = None, album: str = None):
    """
    Search for track ID
    :param auth_mgr: Authorization manager
    :param track_name: Name of track
    :param artist: Name of artist
    :param album: Name of album
    :return: List of matching IDs
    """
    logging.info("Searching for '{}' by {}".format(track_name, artist))
    sp = spotipy.Spotify(auth_manager=auth_mgr)

    # TODO: Figure out if spotipy actually works with the the more advanced queries. For now just searching track name.
    # query = ""
    # for search_field in [track_name, artist, album]:
    #     if search_field is not None:
    #         query += search_field + " "
    # query = quote(query.strip())  # Remove trailing white-spaces and codify for URL query

    results = sp.search(track_name.strip())
    id_matches = []
    for n, listing in enumerate(results['tracks']['items']):
        res_track = listing['name']
        if track_name is not None and track_name != res_track:
            continue
        res_artist = listing['artists'][0]['name']
        if artist is not None and artist != res_artist:
            continue
        res_album = listing['album']['name']
        if album is not None and album != res_album:
            continue
        res_id = listing['id']
        logging.info("\tFound '{}' by {} on album {} with ID = {}".format(res_track, res_artist, res_album, res_id))
        id_matches.append(res_id)

    if not id_matches:
        raise RuntimeWarning("No matches found")
    if len(id_matches) > 1:
        raise RuntimeWarning("Ambiguous matches found")

    return id_matches


def _create_itunes_tuple(song):
    idx_song = 3
    idx_artist = 5
    idx_album = 9
    return song[idx_song].text, song[idx_artist].text, song[idx_album].text


def read_itunes_library(xml_file_path: str):
    tree = ET.parse(xml_file_path)
    root = tree.getroot()

    """
    Apple's Library XML current lists all songs and their associated library number. Later it lists playlists and an
    associated <array> of track ID's that correspond to their unique library numbers.
    A sample is below with added comments for explanation:
    
    <!--- Near top of XML --->
    <plist>
    <dict>
        <key>
        <!--- Numerous other keys --->
        <dict>
            <!--- Here's where the tracks each start. Each with a <key> (UID) and a <dict> (track info)
    
    <!--- Later, we see playlists defined --->
    
    <dict>
        <!--- Numerous description keys --->
        <key>Playlist ID</key><integer>...</integer
        <!--- Numerous description keys --->
        <array>
            <dict>
                <key>Track ID</key><integer>...</integer>
            </dict>
            ...
    """
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


def main():
    """
    Main executor
    :return: None
    """

    # Acquire credentials
    username, auth_mgr = get_credentials()

    # Read in iTunes Library XML
    xml_path = os.path.join(os.getcwd(), 'Library.xml')
    itunes_lib = read_itunes_library(xml_path)

    # Search for "Feel Good Inc" by Gorillaz
    id_matches = search(auth_mgr=auth_mgr, track_name="On Melancholy Hill", artist='Gorillaz')

    # # Create playlist
    # create_playlist(auth_mgr, username, 'testAPI')
    #
    # # View recently played
    # view_recently_played(auth_mgr)


if __name__ == '__main__':
    main()
