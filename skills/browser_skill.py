import webbrowser

from core.base_skill import BaseSkill
from speech.speech import speak


class BrowserSkill(BaseSkill):

    def __init__(self, context):
        self.context = context
    
    def can_handle(self, query):

        keywords = [
            "google",
            "search",
            "browser",
            "chrome"
        ]

        return any(word in query for word in keywords)

    def handle(self, query):

        if "search" in query:

            search_query = query.replace(
                "search",
                ""
            )

            webbrowser.open(
                f"https://google.com/search?q={search_query}"
            )

            speak("Showing search results")

        else:

            webbrowser.open("https://google.com")

            speak("Opening browser")