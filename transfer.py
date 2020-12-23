import logging
import os
import sys

import spotipy
from spotipy.oauth2 import SpotifyOAuth

from itunes import read_itunes_library

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


def main():
    """
    Main executor
    :return: None
    """

    # Acquire credentials
    username, auth_mgr = get_credentials()

    # Read in iTunes Library XML
    xml_path = os.path.join(os.getcwd(), 'Library.xml')
    songs, playlists = read_itunes_library(xml_path)

    # Search for "Feel Good Inc" by Gorillaz
    id_matches = search(auth_mgr=auth_mgr, track_name="On Melancholy Hill", artist='Gorillaz')

    # # Create playlist
    # create_playlist(auth_mgr, username, 'testAPI')
    #
    # # View recently played
    # view_recently_played(auth_mgr)


if __name__ == '__main__':
    main()
