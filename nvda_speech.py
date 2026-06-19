import ctypes
import os

_dll = None

def _load_dll():
    global _dll
    if _dll is not None:
        return True
    dll_name = "nvdaControllerClient64.dll"
    dll_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), dll_name)
    if not os.path.exists(dll_path):
        dll_path = dll_name
    if not os.path.exists(dll_path):
        return False
    try:
        _dll = ctypes.windll.LoadLibrary(dll_path)
        _dll.nvdaController_testIfRunning.restype = ctypes.c_int
        _dll.nvdaController_speakText.argtypes = [ctypes.c_wchar_p]
        _dll.nvdaController_speakText.restype = ctypes.c_int
        _dll.nvdaController_cancelSpeech.restype = ctypes.c_int
        return True
    except Exception:
        _dll = None
        return False

def is_running():
    if not _load_dll():
        return False
    try:
        return _dll.nvdaController_testIfRunning() == 0
    except Exception:
        return False

def speak(text):
    if not text:
        return
    if not is_running():
        return False
    try:
        _dll.nvdaController_speakText(ctypes.c_wchar_p(text))
        return True
    except Exception:
        return False
