import queue
import sounddevice as sd
import vosk
import json

model = vosk.Model("assets/vosk-model")
q = queue.Queue()

def callback(indata, frames, time, status):
    q.put(bytes(indata))

def listen():
    with sd.RawInputStream(samplerate=16000, blocksize=8000,
                           dtype='int16', channels=1, callback=callback):
        rec = vosk.KaldiRecognizer(model, 16000)
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                text = result.get("text", "").lower().strip()
                words = text.split()

                for word in words:
                    if word in ["a", "ay", "ae"]:
                        return "a"
                    if word in ["b", "bee", "be"]:
                        return "b"
                    if word in ["c", "see", "sea"]:
                        return "c"
                    if word in ["d", "dee", "the"]:
                        return "d"
                return text
