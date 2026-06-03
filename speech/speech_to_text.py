import queue
import sounddevice as sd
import json
from vosk import Model, KaldiRecognizer

q = queue.Queue()

def callback(indata, frames, time, status):
    if status:
        print(status)
    q.put(bytes(indata))

model = Model("model")   # folder where vosk model is stored
recognizer = KaldiRecognizer(model, 16000)

with sd.RawInputStream(samplerate=16000, blocksize=8000,
                       dtype='int16', channels=1, callback=callback):

    print("Speak now...")

    while True:
        data = q.get()
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            print("You said:", result.get("text"))
