import pyttsx3
import threading
import queue

engine = pyttsx3.init()
tts_queue = queue.Queue()

def _tts_worker():
    while True:
        text = tts_queue.get()
        if text is None:
            break
        engine.say(text)
        engine.runAndWait()
        tts_queue.task_done()

tts_thread = threading.Thread(target=_tts_worker, daemon=True)
tts_thread.start()

def speak(text):
    tts_queue.put(text)

def stop_tts():
    tts_queue.put(None)
    tts_thread.join()
