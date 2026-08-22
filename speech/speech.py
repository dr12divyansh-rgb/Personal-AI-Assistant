import time
import speech_recognition as sr
import pyttsx3


# Create recognizer once
recognizer = sr.Recognizer()

#Speech detection settings
recognizer.pause_threshold = 1.0
recognizer.non_speaking_duration = 0.5
recognizer.phrase_threshold = 0.3


def speak(text):
    try:
        text = str(text)
        print("Assistant:", text)

        # Create engine for each speech call
        engine = pyttsx3.init()

        voices = engine.getProperty("voices")

        if len(voices) > 1:
            engine.setProperty("voice", voices[1].id)

        engine.setProperty("rate", 170)

        engine.say(text)
        engine.runAndWait()
        engine.stop()

    except Exception as e:
        print("TTS error:", e)


def take_command(silent=False):

    with sr.Microphone() as source:

        print("Listening...")

        # Keep your original calibration for now
        recognizer.adjust_for_ambient_noise(
            source,
            duration=0.5
        )

        try:

            listen_start = time.time()

            audio = recognizer.listen(
                source,
                timeout=5,
                phrase_time_limit=12
            )
            print(f"Listening time: {time.time() - listen_start:.2f} seconds")

            print("Recognizing...")

            recognize_time = time.time()

            query = recognizer.recognize_google(
                audio,
                language="en-in"
            )
            print(f"Recognition time: {time.time() - recognize_time:.2f} seconds")

            print("You said:", query)

            return query.lower()

        except sr.WaitTimeoutError:

            return ""

        except sr.UnknownValueError:

            if not silent:
                speak("Sorry, I didn't catch that.")

            return ""

        except sr.RequestError:

            if not silent:
                speak("Network error")

            return ""