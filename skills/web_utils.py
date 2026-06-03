import webbrowser
import wikipedia
from speech.speech import speak

def search_wikipedia(query):
    query = query.replace("wikipedia", "")
    result = wikipedia.summary(query, sentences=2)
    speak(result)

def search_google(query):
    query = query.replace("search", "")
    webbrowser.open(f"https://www.google.com/search?q={query}")
    speak("Here are the results")