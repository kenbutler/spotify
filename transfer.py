import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
import os
import logging


def get_credentials(directory: str = os.path.join(os.path.expanduser('~')), filename: str = '.spotify_credentials'):
    """
    Confirm Spotify credentials and set environment variables appropriately
    Note that both SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET environment variables must be set
    :param directory: Directory in which file exists
    :param filename: File that contains credentials
    :return:
    """
    logging.info("Acquiring credentials")
    fpath = os.path.join(directory, filename)
    if not os.path.exists(fpath):
        raise IOError("File path does not exist: {}".format(fpath))
    with open(fpath, 'r') as f:
        lines = f.readlines()
        id = lines[0].replace('\n', '')
        secret = lines[1].replace('\n', '')
        redirect_uri = lines[2].replace('\n', '')
        return id, secret, redirect_uri


def main():
    """
    Main executor
    :return: None
    """

    # Acquire credentials
    client_id, client_secret, redirect_uri = get_credentials()

    scope = "playlist-modify-public"
    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(client_id=client_id, client_secret=client_secret,
                                  redirect_uri="http://localhost:8080",
                                  scope=scope))

    sp.user_playlist_create('kenbutler4', 'testAPI')
    # sp0 = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())


if __name__ == '__main__':
    main()
