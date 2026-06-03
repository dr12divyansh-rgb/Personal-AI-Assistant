import speech_recognition as sr
import pyttsx3




def speak(text):
    try:
        text=str(text)
        print("Assistant: ",text)
        engine = pyttsx3.init()
        # Optional: change voice (0 = male, 1 = female depending on system)
        voices = engine.getProperty('voices')
        engine.setProperty('voice', voices[1].id)
        # Speed of speech
        engine.setProperty('rate', 170)
        engine.say(text)
        engine.runAndWait()
        engine.stop()
    except Exception as e:
        print("TTS error: ",e)


def take_command(silent=False):
    """
    Takes voice input from user and converts to text
    """
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("Listening...")

        # Reduce noise impact
        recognizer.adjust_for_ambient_noise(source, duration=0.5)

        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=7)
            print("Recognizing...")

            query = recognizer.recognize_google(audio, language='en-in')
            print(f"You said: {query}")

            return query.lower()

        except sr.WaitTimeoutError:
            # No speech detected
            return ""

        except sr.UnknownValueError:
            # Couldn't understand
            if not silent:
                speak("Sorry, I didn't catch that.")
            return ""
        
        except sr.RequestError:
            # API issue
            if not silent:
                speak("Network error")
            return ""