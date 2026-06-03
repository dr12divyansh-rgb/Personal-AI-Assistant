from skills.music import play_music
from skills.web_utils import search_google, search_wikipedia
from skills.ai_chat_skill import ask_ai

from speech.speech import speak

import os
import datetime
import webbrowser

def open_app(query):
    query=query.lower()
    if "chrome" in query or "browser" in query:
        speak("Opening Chrome")
        webbrowser.open("https://www.google.com")

    elif "notepad" in query or "note pad" in query:
        speak("Opening Notepad")
        os.system("notepad")

    else:
        speak("Application not recognized")

def tell_time():
    time = datetime.datetime.now().strftime("%H:%M")
    speak(f"The time is {time}")

def process_command(query):
    print("Processing:", query)
    query = query.lower()

    if "open" in query:
        open_app(query)

    elif "time" in query:
        tell_time()

    elif "play music" in query:
        play_music()

    elif "wikipedia" in query:
        search_wikipedia(query)

    elif "search" in query:
        search_google(query)

    else:
        ask_ai(query)