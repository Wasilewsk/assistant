import threading
import queue
import time
import sys

engine = None
speech_queue = queue.Queue()
_speaking = False
_stop_requested = False
_speed = 190
_voice_index = 0
_voice_cache = None
_worker_thread = None
_ready = threading.Event()

def _patch_sapi5():
    try:
        import pyttsx3.drivers.sapi5 as sapi5
        from pyttsx3.voice import Voice
    except ImportError:
        return
    orig = sapi5.SAPI5Driver._toVoice
    @staticmethod
    def safe_toVoice(attr):
        try:
            return orig(attr)
        except ValueError:
            return Voice(id=attr.Id, name=attr.GetDescription(), languages=[], gender=None, age=None)
    sapi5.SAPI5Driver._toVoice = safe_toVoice

def _worker():
    global engine, _speaking, _stop_requested, _voice_cache
    _patch_sapi5()
    if sys.platform == "win32":
        import pythoncom
        pythoncom.CoInitialize()
    import pyttsx3
    engine = pyttsx3.init()
    _voice_cache = engine.getProperty('voices')
    if _voice_cache:
        preferred = _pick_best_voice(_voice_cache)
        engine.setProperty('voice', preferred)
        print(f"[speaker] Using voice: {_voice_cache[0].name if _voice_cache else 'none'}")
    else:
        print("[speaker] WARNING: No voices found!")
    engine.setProperty('rate', _speed)
    _ready.set()
    while True:
        item = speech_queue.get()
        if item is None:
            break
        text, done = item
        try:
            _speaking = True
            engine.setProperty('rate', _speed)
            if _voice_cache and 0 <= _voice_index < len(_voice_cache):
                engine.setProperty('voice', _voice_cache[_voice_index].id)
            print(f"[speaker] saying: {text[:60]}...")
            engine.say(text)
            engine.runAndWait()
            print(f"[speaker] done: {text[:40]}...")
        except Exception as e:
            print(f"[speaker] Error: {e}", file=sys.stderr)
        finally:
            _speaking = False
        if done:
            done.set()

def _pick_best_voice(voices):
    keywords = ["zira", "hazel", "jenny", "aria", "emma", "kendra"]
    for kw in keywords:
        for i, v in enumerate(voices):
            if kw in v.name.lower():
                return v.id
    return voices[1].id if len(voices) > 1 else voices[0].id

def get_voices():
    global _voice_cache
    if _voice_cache is None:
        _patch_sapi5()
        import pyttsx3
        eng = pyttsx3.init()
        _voice_cache = eng.getProperty('voices')
        eng.stop()
    return _voice_cache

def init():
    global _worker_thread
    _worker_thread = threading.Thread(target=_worker, daemon=True)
    _worker_thread.start()
    _ready.wait()

def set_speed(rate):
    global _speed
    _speed = max(50, min(400, rate))

def speed_up(amount=20):
    set_speed(_speed + amount)

def slow_down(amount=20):
    set_speed(_speed - amount)

def get_speed():
    return _speed

def set_voice(index):
    global _voice_index
    _voice_index = index

def speak(text):
    if not text:
        return
    print(f"[speaker] speak: {text[:60]}...")
    done = threading.Event()
    speech_queue.put((text, done))
    done.wait()

def speak_async(text):
    if not text:
        return
    print(f"[speaker] speak_async: {text[:60]}...")
    if _speaking:
        stop()
    speech_queue.put((text, None))

def stop():
    while not speech_queue.empty():
        try:
            speech_queue.get_nowait()
        except queue.Empty:
            break
    try:
        if sys.platform == "win32":
            import pythoncom
            pythoncom.CoInitialize()
        if engine:
            engine.stop()
    except Exception:
        pass

def say_welcome():
    import app.config as config
    speak(f"Hello, I am {config.ai_name}, your accessibility assistant. Say 'Hey {config.wake_word}' to begin.")
