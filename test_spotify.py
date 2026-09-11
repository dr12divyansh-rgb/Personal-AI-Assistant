import spotipy

from spotipy.oauth2 import SpotifyOAuth

from config.config import (
    SPOTIFY_CLIENT_ID,
    SPOTIFY_CLIENT_SECRET,
    SPOTIFY_REDIRECT_URI
)


sp = spotipy.Spotify(

    auth_manager=SpotifyOAuth(

        client_id=SPOTIFY_CLIENT_ID,

        client_secret=SPOTIFY_CLIENT_SECRET,

        redirect_uri=SPOTIFY_REDIRECT_URI,

        scope=(
            "user-read-playback-state "
            "user-modify-playback-state"
        )
    )
)


print("\nSPOTIFY DEVICES:")
print("=" * 50)

devices = sp.devices()

for device in devices["devices"]:

    print(
        "Name:",
        device["name"]
    )

    print(
        "Type:",
        device["type"]
    )

    print(
        "Active:",
        device["is_active"]
    )

    print(
        "Restricted:",
        device["is_restricted"]
    )

    print(
        "ID:",
        device["id"]
    )

    print("-" * 50)