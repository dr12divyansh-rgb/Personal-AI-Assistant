import os
import subprocess
import webbrowser
from urllib.parse import quote_plus

from core.base_skill import BaseSkill
from speech.speech import speak


class BrowserSkill(BaseSkill):

    def __init__(self, context):

        self.context = context

    def can_handle(self, query):

        query = query.lower().strip()

        # Close/Exit/Quit commands should go to SystemSkill
        close_commands = [
            "close",
            "exit",
            "quit"
        ]

        if any(command in query for command in close_commands):

            return False

        keywords = [
            "google",
            "search",
            "browser",
            "chrome"
        ]

        return any(word in query for word in keywords)

    def _find_chrome(self):

        # Common Chrome installation locations
        chrome_paths = [

            os.path.join(
                os.environ.get("PROGRAMFILES", ""),
                "Google",
                "Chrome",
                "Application",
                "chrome.exe"
            ),

            os.path.join(
                os.environ.get("PROGRAMFILES(X86)", ""),
                "Google",
                "Chrome",
                "Application",
                "chrome.exe"
            ),

            os.path.join(
                os.environ.get("LOCALAPPDATA", ""),
                "Google",
                "Chrome",
                "Application",
                "chrome.exe"
            )
        ]

        for path in chrome_paths:

            if os.path.exists(path):

                return path

        return None

    def _open_chrome(self, url):

        chrome_path = self._find_chrome()

        if chrome_path:

            try:

                subprocess.Popen(
                    [
                        chrome_path,
                        url
                    ]
                )

                return True

            except Exception as e:

                print("Chrome Error:", e)

        # Fallback to default browser
        webbrowser.open(url)

        return False

    def handle(self, query):

        query = query.lower().strip()

        # ==========================================
        # GOOGLE SEARCH
        # ==========================================

        if "search" in query:

            search_query = query

            # Remove common search phrases
            search_query = search_query.replace(
                "search for",
                ""
            )

            search_query = search_query.replace(
                "search",
                ""
            )

            search_query = search_query.strip()

            # Remove "on google"
            if search_query.endswith("on google"):

                search_query = search_query[:-9].strip()

            # Remove leading "for" if left behind
            if search_query.startswith("for "):

                search_query = search_query[4:].strip()

            if not search_query:

                speak(
                    "What should I search for?"
                )

                return

            encoded_query = quote_plus(
                search_query
            )

            url = (
                "https://www.google.com/search?q="
                + encoded_query
            )

            self._open_chrome(url)

            speak(
                f"Searching for {search_query}"
            )

        # ==========================================
        # OPEN CHROME
        # ==========================================

        else:

            self._open_chrome(
                "https://www.google.com"
            )

            speak("Opening Chrome")