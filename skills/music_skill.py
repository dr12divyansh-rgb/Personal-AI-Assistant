import webbrowser
import spotipy
import time

from spotipy.oauth2 import SpotifyClientCredentials

from core.base_skill import BaseSkill
from speech.speech import speak

from config.config import (
    SPOTIFY_CLIENT_ID,
    SPOTIFY_CLIENT_SECRET
)


class MusicSkill(BaseSkill):

    def __init__(self,context):

        self.context=context
        self.sp = spotipy.Spotify(

            auth_manager=SpotifyClientCredentials(

                client_id=SPOTIFY_CLIENT_ID,
                client_secret=SPOTIFY_CLIENT_SECRET
            )
        )

    def can_handle(self, query):

        keywords = [

            "play",
            "music",
            "spotify",
            "song"
        ]

        return any(word in query for word in keywords)

    def handle(self, query):

        query = query.lower()

        if "play it again" in query:
            last_song=self.context.get("last_song")
            if last_song:
                song=last_song
            else:
                speak("No previous song found")
                return
        else:
            song=query.replace("play", "").strip()

        if not song:

            speak("Which song should I play?")
            return

        try:
            time.sleep(1)
            results = self.sp.search(
            q=song,
            type="track",
            limit=1
            )

        except Exception as e:
            print("Spotify Error: ",e)
            speak("Spotify is temporarily unavailable")
            return

        tracks = results["tracks"]["items"]

        if tracks:

            track = tracks[0]

            song_name = track["name"]
            self.context.set("last_song", song_name)

            artist = track["artists"][0]["name"]

            spotify_url = track["external_urls"]["spotify"]

            speak(f"Playing {song_name} by {artist}")

            webbrowser.open(spotify_url)

        else:

            speak("Song not found")