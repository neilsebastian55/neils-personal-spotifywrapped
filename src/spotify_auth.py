import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os

def get_spotify_client():
    #loading the enivornment variables from .env
    load_dotenv()

    scope = "user-read-private user-top-read user-read-recently-played user-library-read"


    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            scope = scope,
            client_id = os.getenv("SPOTIFY_CLIENT_ID"),
            client_secret = os.getenv("SPOTIFY_CLIENT_SECRET"),
            redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI"),
            cache_path = ".cache",
        )
    )
    return sp

if __name__ == "__main__":
    sp = get_spotify_client()
    #learned about time ranges for data and decided to use the 6 month range, which is medium term
    results = sp.current_user_top_artists(time_range = "medium_term", limit = 25)

    print("\n🎧 My Top Artists:")
    for idx, artist in enumerate(results["items"]):
        print(f"{idx + 1}. {artist['name']} - {artist['genres']}")