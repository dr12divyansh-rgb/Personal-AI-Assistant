import os
import subprocess
import webbrowser

from core.base_skill import BaseSkill
from speech.speech import speak


class SystemSkill(BaseSkill):

    def __init__(self, context):

        self.context = context

    # =====================================================
    # CAN HANDLE
    # =====================================================

    def can_handle(self, query):

        query = query.lower().strip()

        keywords = [
            "chrome",
            "browser",
            "notepad",
            "calculator",
            "calc",
            "cmd",
            "command prompt",
            "spotify",
            "lock",
            "shutdown",
            "restart",
            "sleep",
            "laptop",
            "computer",
            "pc"
        ]

        return any(
            word in query
            for word in keywords
        )

    # =====================================================
    # CLOSE APPLICATION
    # =====================================================

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

    # =====================================================
    # HANDLE
    # =====================================================

    def handle(self, query):

        query = query.lower().strip()

        # =================================================
        # SEPTEMBER'S OWN SLEEP
        # =================================================

        assistant_sleep_commands = [

            "sleep",
            "go to sleep",
            "put yourself to sleep",
            "september sleep",
            "september go to sleep"

        ]

        if query in assistant_sleep_commands:

            self.context.set(
                "sleep_requested",
                True
            )

            return

        # =================================================
        # LAPTOP / COMPUTER SLEEP
        # =================================================

        has_laptop = (
            "laptop" in query
            or "computer" in query
            or "pc" in query
        )

        sleep_words = [

            "sleep",
            "to sleep",
            "on sleep",
            "into sleep"

        ]

        has_sleep = any(
            phrase in query
            for phrase in sleep_words
        )

        if has_laptop and has_sleep:

            speak(
                "Putting your laptop to sleep"
            )

            os.system(
                "rundll32.exe "
                "powrprof.dll,SetSuspendState 0,1,0"
            )

            return

        # =================================================
        # CLOSE COMMAND
        # =================================================

        close_command = any(
            word in query
            for word in [
                "close",
                "exit",
                "quit"
            ]
        )

        if close_command:

            if (
                "chrome" in query
                or "browser" in query
            ):

                self._close_application(
                    "chrome.exe",
                    "Chrome"
                )

            elif "spotify" in query:

                self._close_application(
                    "Spotify.exe",
                    "Spotify"
                )

            elif "notepad" in query:

                self._close_application(
                    "notepad.exe",
                    "Notepad"
                )

            elif (
                "calculator" in query
                or "calc" in query
            ):

                self._close_application(
                    "CalculatorApp.exe",
                    "Calculator"
                )

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

        # =================================================
        # LOCK LAPTOP
        # =================================================

        if (
            "lock" in query
            and (
                "laptop" in query
                or "computer" in query
                or "pc" in query
                or query == "lock"
            )
        ):

            speak(
                "Locking your laptop"
            )

            os.system(
                "rundll32.exe "
                "user32.dll,LockWorkStation"
            )

            return

        # =================================================
        # SHUTDOWN
        # =================================================

        if "shutdown" in query:

            speak(
                "Shutting down your laptop"
            )

            os.system(
                "shutdown /s /t 0"
            )

            return

        # =================================================
        # RESTART
        # =================================================

        if "restart" in query:

            speak(
                "Restarting your laptop"
            )

            os.system(
                "shutdown /r /t 0"
            )

            return

        # =================================================
        # NOTEPAD
        # =================================================

        if "notepad" in query:

            speak(
                "Opening Notepad"
            )

            subprocess.Popen(
                ["notepad.exe"]
            )

            return

        # =================================================
        # CALCULATOR
        # =================================================

        if (
            "calculator" in query
            or "calc" in query
        ):

            speak(
                "Opening Calculator"
            )

            subprocess.Popen(
                ["calc.exe"]
            )

            return

        # =================================================
        # COMMAND PROMPT
        # =================================================

        if (
            "cmd" in query
            or "command prompt" in query
        ):

            speak(
                "Opening Command Prompt"
            )

            subprocess.Popen(
                ["cmd.exe"]
            )

            return

        # =================================================
        # SPOTIFY
        # =================================================

        if "spotify" in query:

            speak(
                "Opening Spotify"
            )

            try:

                os.startfile(
                    "spotify:"
                )

            except Exception:

                webbrowser.open(
                    "https://open.spotify.com"
                )

            return

        # =================================================
        # UNKNOWN
        # =================================================

        speak(
            "Application not recognized"
        )