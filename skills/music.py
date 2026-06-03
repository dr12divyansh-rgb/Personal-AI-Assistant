import os
import random
from speech.speech import speak
from config.config import MUSIC_PATH

def play_music():
    songs = os.listdir(MUSIC_PATH)

    if songs:
        song = random.choice(songs)
        os.startfile(os.path.join(MUSIC_PATH, song))
        speak("Playing music")
    else:
        speak("No music found")