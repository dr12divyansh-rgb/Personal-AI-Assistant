import queue
import sounddevice as sd
import json
import numpy as np
from vosk import Model, KaldiRecognizer
from command_engine import process_command
from voice_reply import speak

# Audio tuning
sd.default.latency = 'low'
sd.default.device = 30
sd.default.samplerate = 16000

q = queue.Queue()

import numpy as np

def callback(indata, frames, time, status):
    if status:
        print(status)

    audio = np.frombuffer(indata, dtype=np.int16)

    # ⭐ Speech Energy Detection
    volume = np.linalg.norm(audio) / len(audio)

    # Adjust threshold if needed
    if volume > 50:   # try 50–200 range later
        q.put(bytes(indata))



model = Model("model")
recognizer = KaldiRecognizer(model, 16000)

print("🎤 Assistant started...")

speak("Assistant started and ready")

with sd.RawInputStream(
        device=30,
        dtype='int16',
        callback=callback):

    while True:
        data = q.get()
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            text = result.get("text")

            if text:
                print("You said:", text)

                speak("You said " + text)

                process_command(text)
