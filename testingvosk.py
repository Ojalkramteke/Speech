import os
import queue
import sounddevice as sd
import json
from vosk import Model, KaldiRecognizer

# Path to your model directory
MODEL_PATH = "vosk-model-en-us-0.22"

# Sample rate must match your microphone settings (usually 16000)
SAMPLE_RATE = 16000

# Load the Vosk model
if not os.path.exists(MODEL_PATH):
    print("Model not found! Please download it from https://alphacephei.com/vosk/models")
    exit(1)

model = Model(MODEL_PATH)
recognizer = KaldiRecognizer(model, SAMPLE_RATE)
recognizer.SetWords(True)

# Queue for audio data
q = queue.Queue()

# Callback for audio stream
def callback(indata, frames, time, status):
    if status:
        print("Status:", status)
    q.put(bytes(indata))

# Start streaming
try:
    print("🎙️ Speak into the mic (press Ctrl+C to stop)")
    with sd.RawInputStream(samplerate=SAMPLE_RATE, blocksize=8000, dtype='int16',
                           channels=1, callback=callback):
        while True:
            data = q.get()
            if recognizer.AcceptWaveform(data):
                result = recognizer.Result()
                text = json.loads(result).get("text", "")
                if text:
                    print("🗣️ You said:", text)
            else:
                partial = recognizer.PartialResult()
                partial_text = json.loads(partial).get("partial", "")
                if partial_text:
                    print("...Listening:", partial_text, end='\r')
except KeyboardInterrupt:
    print("\n🛑 Exiting")
except Exception as e:
    print("Error:", e)
