import logging
import os
import sys
import time

import spotipy
from spotipy.oauth2 import SpotifyOAuth

from itunes import read_itunes_library

logging.basicConfig(
    filename=os.path.join(os.getcwd(), "transfer.log"),
    filemode='w',
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))


def get_credentials(filename: str = 'spotify_credentials.txt'):
    """
    Confirm Spotify credentials and set environment variables appropriately
    Both SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET environment variables must be set
    :param filename: File that contains credentials
    :return: Authorization manager
    """
    fpath = os.path.join(os.getcwd(), 'res', filename)
    if not os.path.exists(fpath):
        raise IOError("File path does not exist: {}".format(fpath))
    with open(fpath, 'r') as f:
        lines = f.readlines()
        username = lines[0].replace('\n', '')
        id_num = lines[1].replace('\n', '')
        secret = lines[2].replace('\n', '')
        playlists_to_ignore = []
        if len(lines) > 3:
            playlists_to_ignore = lines[3].split(',')
            logging.info("Ignoring playlists: {}".format([i for i in playlists_to_ignore]))
        redirect_uri = "http://localhost:8080"  # This should open a browser for you
        logging.info("Acquired credentials")
        return username, SpotifyOAuth(client_id=id_num, client_secret=secret, redirect_uri=redirect_uri), \
               playlists_to_ignore


def create_playlist(auth_mgr: SpotifyOAuth, username: str, playlist_name: str):
    """
    Create Spotify playlist
    :param auth_mgr: Authorization manager
    :param username: Name of user
    :param playlist_name: Name of playlist to create
    :return: Playlist ID
    """
    auth_mgr.scope = "playlist-modify-public"
    sp = spotipy.Spotify(auth_manager=auth_mgr)
    result = sp.user_playlist_create(username, playlist_name)
    return result['id']


def delete_playlist(auth_mgr: SpotifyOAuth, playlist_name: str):
    """
    Delete Spotify playlist
    :param auth_mgr: Authorization manager
    :param playlist_name: Name of playlist to delete
    :return: None
    """
    auth_mgr.scope = "playlist-modify-public"
    sp = spotipy.Spotify(auth_manager=auth_mgr)
    sp.current_user_unfollow_playlist(playlist_name)
    return


def clear_all_playlists(auth_mgr: SpotifyOAuth):
    """
    Clear all existing playlists under current user
    :param auth_mgr: Authorization manager
    :return: None
    """
    auth_mgr.scope = "playlist-modify-public"
    playlists = get_user_playlists(auth_mgr)
    # TODO: Seems dangerous...maybe find a way to make this safer...only delete playlists that match my Library.xml?
    while playlists.items():
        for key, value in playlists.items():
            delete_playlist(auth_mgr, key)
        playlists = get_user_playlists(auth_mgr)
    logging.info("All Spotify playlists deleted")
    return


def get_user_playlists(auth_mgr: SpotifyOAuth, limit: int = 50):
    """
    Get current user playlists
    :param auth_mgr: Authorization manager
    :param limit: Limit to the number of playlists to query. Max of 50
    :return: None
    """
    if limit > 50:
        raise IOError("Spotify limits the number of playlists you can request to 50 playlists")
    auth_mgr.scope = "user-read-recently-played"
    sp = spotipy.Spotify(auth_manager=auth_mgr)
    res = sp.current_user_playlists(limit=limit)
    playlists = {item['id']: item['name'] for item in res['items']}
    return playlists


def get_playlist_tracks(auth_mgr: SpotifyOAuth, username: str):
    pass  # TODO


def add_tracks(auth_mgr: SpotifyOAuth, playlist_id: str, track_ids: list):
    """
    Add tracks to playlist
    :param auth_mgr: Authorization manager
    :param playlist_id: Spotify playlist ID
    :param track_ids: List of Spotify track IDs
    :return: Result of POST
    """
    auth_mgr.scope = "playlist-modify-public"
    sp = spotipy.Spotify(auth_manager=auth_mgr)
    res = sp.playlist_add_items(playlist_id, track_ids)
    return res


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
        if track_name is not None and track_name.lower() != res_track.lower():
            continue
        res_artist = listing['artists'][0]['name']
        if artist is not None and artist.lower() != res_artist.lower():
            continue
        res_album = listing['album']['name']
        if album is not None and album.lower() != res_album.lower():
            continue
        res_id = listing['id']
        logging.info("\tFound '{}' by {} on album {} with ID = {}".format(res_track, res_artist, res_album, res_id))
        id_matches.append(res_id)

    if not id_matches:
        logging.warning("\tNo matches found")
    if len(id_matches) > 1:
        logging.warning("\tAmbiguous matches found")

    return id_matches


def main():
    """
    Main executor
    :return: None
    """

    debug = False
    start = time.time()

    # Acquire credentials
    username, auth_mgr, playlists_to_ignore = get_credentials()

    # Read in iTunes Library XML
    xml_path = os.path.join(os.getcwd(), 'res', 'Library.xml')
    itunes_songs, itunes_playlists = read_itunes_library(xml_path, playlists_to_ignore)

    # Clear all existing Spotify playlists
    clear_all_playlists(auth_mgr)

    # Statistics variables
    num_no_matches = 0
    num_ambiguous_matches = 0
    num_tracks_added = 0

    # Populate each iTunes playlist in Spotify
    itunes_to_spotify_song_ids = {}  # Dictionary/map of iTunes song ID's to Spotify song ID's
    for key, (playlist_name, itunes_song_ids) in itunes_playlists.items():

        # Create empty playlist in Spotify
        playlist_id = create_playlist(auth_mgr, username, playlist_name)

        # Collect Spotify track IDs to add to new playlist
        tracks_to_add = []
        for song_id in itunes_song_ids:  # These are iTunes song IDS

            # Check our local dictionary/map between iTunes and Spotify, as we may already know the ID
            if song_id in itunes_to_spotify_song_ids.keys():
                logging.info("Match already exists")
                tracks_to_add.append(itunes_to_spotify_song_ids[song_id])
                continue

            # We haven't found this track yet. Let's find it and update accordingly
            track_name, artist, album = itunes_songs[song_id]  # Get iTunes song data
            id_matches = search(auth_mgr=auth_mgr, track_name=track_name, artist=artist, album=album)
            if not id_matches:  # No match found
                num_no_matches += 1
                continue
            else:  # Just pick the first one. Sloppy coding? We'll see...
                num_tracks_added += 1
                itunes_to_spotify_song_ids[song_id] = id_matches[0]  # Update iTunes-Spotify-ID map
                tracks_to_add.append(itunes_to_spotify_song_ids[song_id])  # Update list of tracks to add
                if len(id_matches) > 1:
                    num_ambiguous_matches += 1

        # Add to Spotify playlist
        add_tracks(auth_mgr, playlist_id, tracks_to_add)

    end = time.time()
    logging.info("Total transfer duration: {} seconds".format(round(end - start, 2)))
    logging.info("{} tracks had no match".format(num_no_matches))
    logging.info("{} tracks had ambiguous matches".format(num_ambiguous_matches))
    logging.info("{} tracks added".format(num_tracks_added))

    if debug:
        # Search for "Feel Good Inc" by Gorillaz
        id_matches = search(auth_mgr=auth_mgr, track_name="On Melancholy Hill", artist='Gorillaz')
        # Create playlist
        create_playlist(auth_mgr, username, 'testAPI')
        matches = search(auth_mgr, track_name=itunes_songs['5140'][0], artist=itunes_songs['5140'][1], album=itunes_songs['5140'][2])

    pass


if __name__ == '__main__':
    main()
