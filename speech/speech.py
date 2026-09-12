import time
import threading
import speech_recognition as sr
import pyttsx3
import json


# =========================================================
# SPEECH RECOGNIZER
# =========================================================

recognizer = sr.Recognizer()


# =========================================================
# SPEECH DETECTION SETTINGS
# =========================================================

# Allows natural pauses while speaking.
# 3 seconds gives enough time to complete a full sentence.
recognizer.pause_threshold = 3.0

# Detect speech reasonably quickly.
recognizer.phrase_threshold = 0.2

# Silence required before speech is considered started.
recognizer.non_speaking_duration = 0.3


# =========================================================
# TEXT TO SPEECH
# =========================================================

# Prevent two background tasks from speaking at the
# exact same time.
tts_lock = threading.Lock()


def speak(text):

    try:

        text = str(text)

        print(
            "Assistant:",
            text
        )

        # Create a fresh engine just like the original
        # working version.
        with tts_lock:

            engine = pyttsx3.init()

            voices = engine.getProperty(
                "voices"
            )

            if len(voices) > 1:

                engine.setProperty(
                    "voice",
                    voices[1].id
                )

            engine.setProperty(
                "rate",
                170
            )

            engine.say(
                text
            )

            engine.runAndWait()

            engine.stop()

    except Exception as e:

        print(
            "TTS error:",
            e
        )


# =========================================================
# TAKE COMMAND
# =========================================================

def take_command(silent=False):

    with sr.Microphone() as source:

        print(
            "\nListening..."
        )

        # Short microphone calibration.
        recognizer.adjust_for_ambient_noise(
            source,
            duration=0.3
        )

        try:

            # -------------------------------------------------
            # LISTEN
            # -------------------------------------------------

            listen_start = time.time()

            audio = recognizer.listen(
                source,
                timeout=5
            )

            listening_time = (
                time.time()
                - listen_start
            )

            print(
                f"Listening time: "
                f"{listening_time:.2f} seconds"
            )

            # -------------------------------------------------
            # RECOGNIZE
            # -------------------------------------------------

            print(
                "Recognizing..."
            )

            recognize_start = time.time()

            query = recognizer.recognize_google(
                audio,
                language="en-in"
            )

            recognition_time = (
                time.time()
                - recognize_start
            )

            print(
                f"Recognition time: "
                f"{recognition_time:.2f} seconds"
            )

            print(
                "You said:",
                query
            )

            return query.lower()

        # -----------------------------------------------------
        # NO SPEECH
        # -----------------------------------------------------

        except sr.WaitTimeoutError:

            return ""

        # -----------------------------------------------------
        # SPEECH NOT UNDERSTOOD
        # -----------------------------------------------------

        except sr.UnknownValueError:

            if not silent:

                speak(
                    "Sorry, I didn't catch that."
                )

            return ""

        # -----------------------------------------------------
        # NETWORK ERROR
        # -----------------------------------------------------

        except sr.RequestError:

            if not silent:

                speak(
                    "Network error"
                )

            return ""

        # -----------------------------------------------------
        # JSON ERROR
        # -----------------------------------------------------

        except json.JSONDecodeError:

            if not silent:

                speak(
                    "I couldn't process that. "
                    "Please try again."
                )

            return ""

        # -----------------------------------------------------
        # OTHER ERROR
        # -----------------------------------------------------

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