import os
import subprocess
import sys
import app.config as config
import app.speaker as speaker

def open_application(app_name):
    app_name = app_name.lower().strip()

    app_map = {
        "chrome": "chrome" if sys.platform == "win32" else "google-chrome",
        "google chrome": "chrome" if sys.platform == "win32" else "google-chrome",
        "firefox": "firefox" if sys.platform == "win32" else "firefox",
        "edge": "msedge" if sys.platform == "win32" else "microsoft-edge",
        "browser": "chrome" if sys.platform == "win32" else "google-chrome",
        "notepad": "notepad" if sys.platform == "win32" else "gedit",
        "calculator": "calc" if sys.platform == "win32" else "gnome-calculator",
        "terminal": "powershell" if sys.platform == "win32" else "gnome-terminal",
        "command prompt": "cmd" if sys.platform == "win32" else "xterm",
        "cmd": "cmd" if sys.platform == "win32" else "xterm",
        "powershell": "powershell" if sys.platform == "win32" else "pwsh",
        "explorer": "explorer" if sys.platform == "win32" else "nautilus",
        "file manager": "explorer" if sys.platform == "win32" else "nautilus",
        "word": "winword" if sys.platform == "win32" else "libreoffice",
        "excel": "excel" if sys.platform == "win32" else "libreoffice --calc",
        "vscode": "code" if sys.platform == "win32" else "code",
        "visual studio code": "code" if sys.platform == "win32" else "code",
        "spotify": "spotify" if sys.platform == "win32" else "spotify",
        "camera": "microsoft.windows.camera:" if sys.platform == "win32" else "cheese",
        "control panel": "control" if sys.platform == "win32" else "gnome-control-center",
        "settings": "start ms-settings:" if sys.platform == "win32" else "gnome-control-center",
    }

    if app_name in app_map:
        target = app_map[app_name]
    else:
        target = app_name

    try:
        if sys.platform == "win32":
            if target.endswith(":"):
                subprocess.Popen(f"start {target}", shell=True)
            elif target == "chrome":
                chrome_paths = [
                    "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
                    "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
                ]
                found = False
                for p in chrome_paths:
                    if os.path.exists(p):
                        subprocess.Popen([p])
                        found = True
                        break
                if not found:
                    subprocess.Popen(target, shell=True)
            else:
                subprocess.Popen(target, shell=True)
        else:
            subprocess.Popen(target.split(), shell=False)
        speaker.speak(f"Opening {app_name}")
    except Exception:
        speaker.speak(f"Could not open {app_name}.")

def volume_control(command):
    cmd = command.lower()
    if sys.platform != "win32":
        try:
            if "up" in cmd:
                subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", "+10%"], capture_output=True)
                speaker.speak("Volume up")
            elif "down" in cmd:
                subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", "-10%"], capture_output=True)
                speaker.speak("Volume down")
            elif "mute" in cmd:
                subprocess.run(["pactl", "set-sink-mute", "@DEFAULT_SINK@", "1"], capture_output=True)
                speaker.speak("Muted")
            elif "unmute" in cmd:
                subprocess.run(["pactl", "set-sink-mute", "@DEFAULT_SINK@", "0"], capture_output=True)
                speaker.speak("Unmuted")
        except Exception:
            speaker.speak("Volume control not available on this system.")
        return

    try:
        import ctypes
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    except ImportError:
        speaker.speak("Volume control requires pycaw. Install: pip install pycaw comtypes")
        return

    try:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))

        if "up" in cmd:
            current = volume.GetMasterVolumeLevelScalar()
            volume.SetMasterVolumeLevelScalar(min(1.0, current + 0.1), None)
            speaker.speak("Volume up")
        elif "down" in cmd:
            current = volume.GetMasterVolumeLevelScalar()
            volume.SetMasterVolumeLevelScalar(max(0.0, current - 0.1), None)
            speaker.speak("Volume down")
        elif "mute" in cmd:
            volume.SetMute(1, None)
            speaker.speak("Muted")
        elif "unmute" in cmd:
            volume.SetMute(0, None)
            speaker.speak("Unmuted")
    except Exception:
        speaker.speak("Could not control volume.")

def system_command(command):
    cmd = command.lower()

    if "shutdown" in cmd or "power off" in cmd or "turn off" in cmd:
        speaker.speak("Shutting down the computer. Are you sure? Say yes to confirm.")
        return "confirm_shutdown"

    if "restart" in cmd or "reboot" in cmd:
        speaker.speak("Restarting the computer. Are you sure? Say yes to confirm.")
        return "confirm_restart"

    if "lock" in cmd:
        try:
            if sys.platform == "win32":
                ctypes.windll.user32.LockWorkStation()
            else:
                subprocess.run(["gnome-screensaver-command", "-l"], capture_output=True)
            speaker.speak("Computer locked.")
        except Exception:
            speaker.speak("Could not lock the computer.")
        return "done"

    return None

def execute_shutdown():
    try:
        if sys.platform == "win32":
            subprocess.run(["shutdown", "/s", "/t", "5"], capture_output=True)
        else:
            subprocess.run(["shutdown", "-h", "+1"], capture_output=True)
        speaker.speak("Shutting down in 5 seconds.")
    except Exception:
        speaker.speak("Could not shutdown.")

def execute_restart():
    try:
        if sys.platform == "win32":
            subprocess.run(["shutdown", "/r", "/t", "5"], capture_output=True)
        else:
            subprocess.run(["reboot"], capture_output=True)
        speaker.speak("Restarting in 5 seconds.")
    except Exception:
        speaker.speak("Could not restart.")

def handle_system_command(command):
    cmd = command.lower()

    if "open" in cmd:
        app = cmd.replace("open", "").strip()
        if app:
            open_application(app)
            return True

    if "volume" in cmd or "mute" in cmd or "unmute" in cmd:
        volume_control(command)
        return True

    result = system_command(command)
    if result == "confirm_shutdown":
        return "confirm_shutdown"
    if result == "confirm_restart":
        return "confirm_restart"

    return False
