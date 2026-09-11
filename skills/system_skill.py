import os
import subprocess
import webbrowser

from core.base_skill import BaseSkill
from speech.speech import speak


class SystemSkill(BaseSkill):

    def __init__(self, context):

        self.context = context

    def can_handle(self, query):

        query = query.lower().strip()

        keywords = [

            # Applications
            "chrome",
            "browser",
            "notepad",
            "calculator",
            "calc",
            "cmd",
            "command prompt",
            "spotify",

            # System controls
            "lock",
            "shutdown",
            "restart"
        ]

        return any(word in query for word in keywords)

    # ==============================================
    # CLOSE WINDOWS APPLICATIONS
    # ==============================================

    def _close_application(
        self,
        process_name,
        application_name
    ):

        try:

            result = subprocess.run(

                [
                    "taskkill",
                    "/IM",
                    process_name,
                    "/F"
                ],

                capture_output=True,
                text=True
            )

            if result.returncode == 0:

                speak(
                    f"Closing {application_name}"
                )

            else:

                speak(
                    f"{application_name} is not running"
                )

        except Exception as e:

            print(
                f"Error closing {application_name}:",
                e
            )

            speak(
                f"I couldn't close {application_name}"
            )

    def handle(self, query):

        query = query.lower().strip()

        # ==========================================
        # CLOSE / EXIT / QUIT
        # ==========================================

        close_command = any(

            word in query

            for word in [
                "close",
                "exit",
                "quit"
            ]
        )

        if close_command:

            # Chrome / Browser
            if (
                "chrome" in query
                or "browser" in query
            ):

                self._close_application(
                    "chrome.exe",
                    "Chrome"
                )

            # Spotify
            elif "spotify" in query:

                self._close_application(
                    "Spotify.exe",
                    "Spotify"
                )

            # Notepad
            elif "notepad" in query:

                self._close_application(
                    "notepad.exe",
                    "Notepad"
                )

            # Calculator
            elif (
                "calculator" in query
                or "calc" in query
            ):

                self._close_application(
                    "CalculatorApp.exe",
                    "Calculator"
                )

            # Command Prompt
            elif (
                "cmd" in query
                or "command prompt" in query
            ):

                self._close_application(
                    "cmd.exe",
                    "Command Prompt"
                )

            else:

                speak(
                    "I don't know which application to close"
                )

            return

        # ==========================================
        # LOCK LAPTOP
        # ==========================================

        if "lock" in query:

            speak("Locking your laptop")

            os.system(
                "rundll32.exe "
                "user32.dll,LockWorkStation"
            )

            return

        # ==========================================
        # SHUTDOWN
        # ==========================================

        if "shutdown" in query:

            speak("Shutting down your laptop")

            os.system(
                "shutdown /s /t 0"
            )

            return

        # ==========================================
        # RESTART
        # ==========================================

        if "restart" in query:

            speak("Restarting your laptop")

            os.system(
                "shutdown /r /t 0"
            )

            return

        # ==========================================
        # OPEN NOTEPAD
        # ==========================================

        if "notepad" in query:

            speak("Opening Notepad")

            subprocess.Popen(
                ["notepad.exe"]
            )

            return

        # ==========================================
        # OPEN CALCULATOR
        # ==========================================

        if (
            "calculator" in query
            or "calc" in query
        ):

            speak("Opening Calculator")

            subprocess.Popen(
                ["calc.exe"]
            )

            return

        # ==========================================
        # OPEN COMMAND PROMPT
        # ==========================================

        if (
            "cmd" in query
            or "command prompt" in query
        ):

            speak("Opening Command Prompt")

            subprocess.Popen(
                ["cmd.exe"]
            )

            return

        # ==========================================
        # OPEN SPOTIFY
        # ==========================================

        if "spotify" in query:

            speak("Opening Spotify")

            try:

                os.startfile("spotify:")

            except Exception:

                webbrowser.open(
                    "https://open.spotify.com"
                )

            return

        # ==========================================
        # UNKNOWN APPLICATION
        # ==========================================

        speak("Application not recognized")