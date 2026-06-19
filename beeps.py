import winsound
import time
import threading

_processing = threading.Event()
_processing.clear()

def _seq(notes):
    for freq, dur in notes:
        winsound.Beep(freq, dur)
        time.sleep(0.05)

def ready():
    _seq([(660, 100), (880, 150)])

def wake():
    _seq([(440, 80), (660, 120)])

def listen():
    _seq([(880, 60), (1100, 80)])

def stop_listen():
    _seq([(660, 80), (440, 120)])

def error():
    _seq([(330, 150), (220, 250)])

def processing_start():
    _processing.set()
    threading.Thread(target=_processing_loop, daemon=True).start()

def processing_stop():
    _processing.clear()

def _processing_loop():
    while _processing.is_set():
        winsound.Beep(880, 40)
        time.sleep(0.6)
