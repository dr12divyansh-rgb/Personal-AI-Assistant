import time
import speech_recognition as sr
import pyttsx3
import json


# =========================================================
# SPEECH RECOGNIZER
# =========================================================

# Create recognizer once
recognizer = sr.Recognizer()


# =========================================================
# SPEECH DETECTION SETTINGS
# =========================================================

# How long silence must continue before September
# considers that you have finished speaking.
#
# Increase this if September stops too early.
recognizer.pause_threshold = 5.0

# Minimum amount of speech required before recognition
# considers it a real phrase.
recognizer.phrase_threshold = 0.3

# Amount of silence used when determining the beginning
# of a phrase.
recognizer.non_speaking_duration = 0.5


# =========================================================
# TEXT TO SPEECH
# =========================================================

def speak(text):

    try:

        text = str(text)

        print("Assistant:", text)

        # Create engine for each speech call
        engine = pyttsx3.init()

        voices = engine.getProperty("voices")

        if len(voices) > 1:

            engine.setProperty(
                "voice",
                voices[1].id
            )

        engine.setProperty(
            "rate",
            170
        )

        engine.say(text)

        engine.runAndWait()

        engine.stop()

    except Exception as e:

        print("TTS error:", e)


# =========================================================
# TAKE COMMAND
# =========================================================

def take_command(silent=False):

    with sr.Microphone() as source:

        print("\nListening...")

        # -------------------------------------------------
        # AMBIENT NOISE CALIBRATION
        # -------------------------------------------------

        recognizer.adjust_for_ambient_noise(
            source,
            duration=0.5
        )

        try:

            # -------------------------------------------------
            # START LISTENING
            # -------------------------------------------------

            listen_start = time.time()

            audio = recognizer.listen(

                source,

                # Maximum time September waits for you
                # to START speaking.
                timeout=5

                # IMPORTANT:
                # No phrase_time_limit.
                #
                # This means there is NO 12-second
                # hard limit on your speech.
            )

            listening_time = (
                time.time() - listen_start
            )

            print(
                f"Listening time: "
                f"{listening_time:.2f} seconds"
            )

            # -------------------------------------------------
            # SPEECH RECOGNITION
            # -------------------------------------------------

            print("Recognizing...")

            recognize_start = time.time()

            query = recognizer.recognize_google(

                audio,

                language="en-in"
            )

            recognition_time = (
                time.time() - recognize_start
            )

            print(
                f"Recognition time: "
                f"{recognition_time:.2f} seconds"
            )

            # -------------------------------------------------
            # COMPLETE COMMAND
            # -------------------------------------------------

            print(
                "You said:",
                query
            )

            return query.lower()

        # -------------------------------------------------
        # USER DID NOT START SPEAKING
        # -------------------------------------------------

        except sr.WaitTimeoutError:

            return ""

        # -------------------------------------------------
        # SPEECH WAS NOT UNDERSTOOD
        # -------------------------------------------------

        except sr.UnknownValueError:

            if not silent:

                speak(
                    "Sorry, I didn't catch that."
                )

            return ""

        # -------------------------------------------------
        # INTERNET / GOOGLE SPEECH ERROR
        # -------------------------------------------------

        except sr.RequestError:

            if not silent:

                speak(
                    "Network error"
                )

            return ""

        # -------------------------------------------------
        # JSON ERROR
        # -------------------------------------------------

        except json.JSONDecodeError:

            if not silent:

                speak(
                    "I couldn't process that. "
                    "Please try again."
                )

            return ""

        # -------------------------------------------------
        # OTHER ERRORS
        # -------------------------------------------------

        except Exception as e:

            print(
                "Speech error:",
                e
            )

            if not silent:

                speak(
                    "Something went wrong "
                    "while listening."
                )

            return ""