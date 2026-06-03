import os
import webbrowser

from core.base_skill import BaseSkill
from speech.speech import speak


class SystemSkill(BaseSkill):

    def __init__(self, context):
        self.context = context
    
    def can_handle(self, query):

        if "lock" in query:
            return True
        elif "shutdown" in query:
            return True
        elif "restart" in query:
            return True
        elif "chrome" in query:
            return True
        elif "notepad" in query:
            return True
        return False
        
    def handle(self, query):

        query = query.lower()

        if "chrome" in query or "browser" in query:

            speak("Opening Chrome")

            webbrowser.open("https://google.com")

        elif "notepad" in query:

            speak("Opening Notepad")

            os.system("notepad")

        elif "calculator" in query:

            speak("Opening Calculator")

            os.system("calc")

        elif "cmd" in query:

            speak("Opening Command Prompt")

            os.system("start cmd")
        elif "lock" in query:
            speak("Locking your laptop")
            os.system("rundll32.exe user32.dll,LockWorkStation")

        else:

            speak("Application not recognized")