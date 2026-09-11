import time
import webbrowser
import spotipy

from spotipy.oauth2 import SpotifyOAuth
from spotipy.exceptions import SpotifyException

from core.base_skill import BaseSkill
from speech.speech import speak

from config.config import (
    SPOTIFY_CLIENT_ID,
    SPOTIFY_CLIENT_SECRET,
    SPOTIFY_REDIRECT_URI
)


class MusicSkill(BaseSkill):

    def __init__(self, context):

        self.context = context

        # =================================================
        # SPOTIFY USER AUTHENTICATION
        # =================================================

        self.sp = spotipy.Spotify(

            auth_manager=SpotifyOAuth(

                client_id=SPOTIFY_CLIENT_ID,
                client_secret=SPOTIFY_CLIENT_SECRET,
                redirect_uri=SPOTIFY_REDIRECT_URI,

                scope=(
                    "user-modify-playback-state "
                    "user-read-playback-state"
                )
            )
        )

    # =====================================================
    # CAN HANDLE
    # =====================================================

    def can_handle(self, query):

        query = query.lower().strip()

        # Let SystemSkill handle:
        #
        # Open Spotify
        # Close Spotify
        # Exit Spotify
        # Quit Spotify

        if "spotify" in query:

            app_commands = [
                "open",
                "close",
                "exit",
                "quit"
            ]

            if any(
                command in query
                for command in app_commands
            ):

                return False

        # Music-related commands
        keywords = [
            "play",
            "music",
            "song"
        ]

        return any(
            word in query
            for word in keywords
        )

    # =====================================================
    # FIND SPOTIFY DEVICE
    # =====================================================

    def _get_device(self):

        print(
            "\nChecking for Spotify device..."
        )

        # Spotify can take some time to become
        # available after opening the application.

        for attempt in range(15):

            try:

                devices = self.sp.devices()["devices"]

                print(
                    f"Spotify device check "
                    f"{attempt + 1}/15"
                )

                if devices:

                    # -------------------------------------
                    # Display devices
                    # -------------------------------------

                    for device in devices:

                        print(
                            f"  Device: "
                            f"{device['name']} | "
                            f"Type: "
                            f"{device['type']} | "
                            f"Active: "
                            f"{device['is_active']} | "
                            f"Restricted: "
                            f"{device['is_restricted']}"
                        )

                    # -------------------------------------
                    # Prefer active + unrestricted device
                    # -------------------------------------

                    for device in devices:

                        if (
                            device["is_active"]
                            and not device["is_restricted"]
                        ):

                            print(
                                "Using active device:",
                                device["name"]
                            )

                            return device

                    # -------------------------------------
                    # If no active device, use any
                    # unrestricted device
                    # -------------------------------------

                    for device in devices:

                        if not device["is_restricted"]:

                            print(
                                "Using available device:",
                                device["name"]
                            )

                            return device

            except Exception as e:

                print(
                    "Spotify device error:",
                    e
                )

            # Wait before checking again
            time.sleep(1)

        return None

    # =====================================================
    # SEARCH FOR TRACK
    # =====================================================

    def _search_track(self, song):

        try:

            print(
                "\nSearching Spotify for:",
                song
            )

            # Search for multiple results.
            # This prevents Spotify's first result
            # from automatically being selected.

            results = self.sp.search(

                q=song,

                type="track",

                limit=10
            )

            tracks = results[
                "tracks"
            ][
                "items"
            ]

            if not tracks:

                return None

            # =================================================
            # NORMALIZE SEARCH TEXT
            # =================================================

            search_text = song.lower().strip()

            # Remove unnecessary phrases

            search_text = search_text.replace(
                "the song",
                ""
            )

            search_text = search_text.replace(
                "song",
                ""
            )

            search_text = search_text.strip()

            # =================================================
            # EXACT TITLE MATCH
            # =================================================

            for track in tracks:

                title = track[
                    "name"
                ].lower().strip()

                if title == search_text:

                    print(
                        "Exact title match found:",
                        track["name"]
                    )

                    return track

            # =================================================
            # TITLE STARTS WITH SEARCH
            # =================================================

            for track in tracks:

                title = track[
                    "name"
                ].lower().strip()

                if title.startswith(
                    search_text
                ):

                    print(
                        "Title starts with search:",
                        track["name"]
                    )

                    return track

            # =================================================
            # SEARCH TERM EXISTS IN TITLE
            # =================================================

            for track in tracks:

                title = track[
                    "name"
                ].lower().strip()

                if search_text in title:

                    print(
                        "Search term found in title:",
                        track["name"]
                    )

                    return track

            # =================================================
            # TITLE EXISTS IN SEARCH TERM
            # =================================================

            for track in tracks:

                title = track[
                    "name"
                ].lower().strip()

                if title in search_text:

                    print(
                        "Title found in search text:",
                        track["name"]
                    )

                    return track

            # =================================================
            # FALLBACK
            # =================================================

            print(
                "No strong title match found."
            )

            print(
                "Using Spotify's first result:",
                tracks[0]["name"]
            )

            return tracks[0]

        except Exception as e:

            print(
                "Spotify Search Error:",
                e
            )

            return None

    # =====================================================
    # VERIFY CURRENT PLAYBACK
    # =====================================================

    def _verify_playback(self, expected_uri):

        try:

            current = self.sp.current_playback()

            if not current:

                return None

            item = current.get(
                "item"
            )

            if not item:

                return None

            current_uri = item.get(
                "uri"
            )

            current_song = item.get(
                "name",
                "Unknown"
            )

            current_artist = "Unknown"

            artists = item.get(
                "artists",
                []
            )

            if artists:

                current_artist = artists[0].get(
                    "name",
                    "Unknown"
                )

            print(
                "\nCurrent Spotify playback:"
            )

            print(
                "Song:",
                current_song
            )

            print(
                "Artist:",
                current_artist
            )

            print(
                "URI:",
                current_uri
            )

            # Check whether Spotify is playing
            # the exact requested track.

            if current_uri == expected_uri:

                return True

            return False

        except Exception as e:

            print(
                "Playback verification error:",
                e
            )

            return None

    # =====================================================
    # HANDLE MUSIC COMMAND
    # =====================================================

    def handle(self, query):

        query = query.lower().strip()

        # =================================================
        # PLAY PREVIOUS SONG
        # =================================================

        if "play it again" in query:

            last_song = self.context.get(
                "last_song"
            )

            if last_song:

                song = last_song

            else:

                speak(
                    "No previous song found"
                )

                return

        # =================================================
        # NORMAL PLAY COMMAND
        # =================================================

        else:

            song = query

            prefixes = [

                "play the song",
                "play song",
                "play music",
                "spotify play",
                "play"
            ]

            for prefix in prefixes:

                if song.startswith(prefix):

                    song = song[
                        len(prefix):
                    ].strip()

                    break

            # Remove "on spotify"

            if song.endswith(
                " on spotify"
            ):

                song = song[
                    :-11
                ].strip()

        # =================================================
        # CHECK SONG NAME
        # =================================================

        if not song:

            speak(
                "Which song should I play?"
            )

            return

        # =================================================
        # SEARCH FOR TRACK
        # =================================================

        track = self._search_track(
            song
        )

        if track is None:

            speak(
                f"I couldn't find {song}"
            )

            return

        # =================================================
        # TRACK INFORMATION
        # =================================================

        song_name = track[
            "name"
        ]

        artist = track[
            "artists"
        ][0]["name"]

        track_uri = track[
            "uri"
        ]

        spotify_url = track[
            "external_urls"
        ]["spotify"]

        print(
            "\nSelected Spotify track:"
        )

        print(
            "Song:",
            song_name
        )

        print(
            "Artist:",
            artist
        )

        print(
            "URI:",
            track_uri
        )

        # Save the song for:
        #
        # "Play it again"

        self.context.set(
            "last_song",
            song_name
        )

        # =================================================
        # FIND SPOTIFY DEVICE
        # =================================================

        print(
            "\nWaiting for Spotify device..."
        )

        device = self._get_device()

        # =================================================
        # NO DEVICE
        # =================================================

        if device is None:

            speak(
                "I couldn't find a Spotify device. "
                "Please open Spotify and try again."
            )

            return

        # =================================================
        # DEVICE INFORMATION
        # =================================================

        device_id = device[
            "id"
        ]

        print(
            "\nSelected device:",
            device["name"]
        )

        # =================================================
        # ACTIVATE DEVICE IF NECESSARY
        # =================================================

        if not device["is_active"]:

            try:

                print(
                    "Activating Spotify device..."
                )

                self.sp.transfer_playback(

                    device_id=device_id,

                    force_play=False
                )

                time.sleep(2)

            except SpotifyException as e:

                print(
                    "Transfer Playback Error:",
                    e
                )

        # =================================================
        # START REQUESTED TRACK
        # =================================================

        try:

            print(
                "\nSending playback command..."
            )

            print(
                "Requested:",
                song_name,
                "by",
                artist
            )

            self.sp.start_playback(

                device_id=device_id,

                uris=[
                    track_uri
                ]
            )

        except SpotifyException as e:

            print(
                "\nSpotify Playback Error:",
                e
            )

            if e.http_status == 403:

                speak(
                    "Spotify playback control "
                    "requires a Spotify Premium account."
                )

            else:

                speak(
                    "I couldn't start that song on Spotify."
                )

            return

        except Exception as e:

            print(
                "\nPlayback Error:",
                e
            )

            speak(
                "Something went wrong while "
                "starting Spotify."
            )

            return

        # =================================================
        # VERIFY PLAYBACK
        # =================================================

        print(
            "\nVerifying playback..."
        )

        playback_result = None

        # Give Spotify several seconds to update
        # its current playback information.

        for attempt in range(5):

            time.sleep(1)

            playback_result = (
                self._verify_playback(
                    track_uri
                )
            )

            print(
                f"Playback verification "
                f"{attempt + 1}/5"
            )

            # ---------------------------------------------
            # Correct song is playing
            # ---------------------------------------------

            if playback_result is True:

                speak(
                    f"Playing {song_name} by {artist}"
                )

                return

        # =================================================
        # DIFFERENT SONG IS PLAYING
        # =================================================

        if playback_result is False:

            speak(
                f"I sent {song_name} to Spotify, "
                f"but Spotify is playing a different song."
            )

        # =================================================
        # PLAYBACK COULD NOT BE VERIFIED
        # =================================================

        else:

            speak(
                f"I sent {song_name} to Spotify, "
                f"but I couldn't verify playback."
            )