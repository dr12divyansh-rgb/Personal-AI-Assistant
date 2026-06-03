import sounddevice as sd

device_id = 30  # your mic

try:
    sd.check_input_settings(device=device_id, samplerate=16000)
    print("✅ Device 30 is working perfectly!")

except Exception as e:
    print("❌ Device error:", e)
