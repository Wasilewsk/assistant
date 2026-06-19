import speech_recognition as sr
import app.config as config
from app.beeps import listen as beep_listen, error as beep_error

recognizer = sr.Recognizer()
recognizer.dynamic_energy_threshold = True
recognizer.pause_threshold = 0.8

def _log(msg):
    print(f"[listener] {msg}")

def listen(source, timeout=6, phrase_limit=10):
    try:
        audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_limit)
    except sr.WaitTimeoutError:
        return None
    except Exception as e:
        _log(f"Listen error: {e}")
        return None

    try:
        text = recognizer.recognize_google(audio).lower().strip()
        return text
    except sr.UnknownValueError:
        return None
    except sr.RequestError as e:
        _log(f"Google API error: {e}")
        return None

def listen_for_wake(source, wake_word=None, timeout=30):
    if wake_word is None:
        wake_word = config.wake_word
    try:
        audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=4)
    except sr.WaitTimeoutError:
        return False
    except Exception as e:
        _log(f"Wake listen error: {e}")
        beep_error()
        return False

    try:
        text = recognizer.recognize_google(audio).lower().strip()
        if wake_word not in text:
            _log(f"Heard: '{text}' (wake word not found)")
        return wake_word in text
    except sr.UnknownValueError:
        return False
    except sr.RequestError as e:
        _log(f"Google API error (wake): {e}")
        return False

def listen_for_command(source, timeout=8, phrase_limit=8):
    beep_listen()
    return listen(source, timeout=timeout, phrase_limit=phrase_limit)

def listen_for_simple(source, timeout=8, phrase_limit=5):
    return listen(source, timeout=timeout, phrase_limit=phrase_limit)
