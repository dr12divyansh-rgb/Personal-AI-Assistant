import pyttsx3

engine = pyttsx3.init()

# Optional tuning
engine.setProperty('rate', 170)   # speed of speech
engine.setProperty('volume', 1)

def speak(text):
    engine.say(text)
    engine.runAndWait()
