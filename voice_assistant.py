import queue
import sounddevice as sd
import json
from vosk import Model, KaldiRecognizer
from command_engine import process_command

# ⭐ Audio Performance Settings (ADD BEFORE STREAM)
sd.default.latency = 'low'
sd.default.device = 30
sd.default.samplerate = 16000

q = queue.Queue()

def callback(indata, frames, time, status):
    if status:
        print(status)
    q.put(bytes(indata))

# ⭐ Load Model
model = Model("model")
recognizer = KaldiRecognizer(model, 16000)

print("🎤 Assistant started... Speak now")

# ⭐ Audio Stream
with sd.RawInputStream(
        samplerate=16000,
        blocksize=16000,   # lower = faster response
        device=30,        # ← Your final best mic
        dtype='int16',
        channels=1,
        callback=callback):

    while True:
        data = q.get()
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            text = result.get("text")

            if text:
                print("You said:", text)
                process_command(text)
