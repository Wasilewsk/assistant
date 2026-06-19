import threading
import time
import os
import sys
import app.config as config
import app.speaker as speaker

try:
    from playsound import playsound
except ImportError:
    playsound = None

_HISTORY = {}
_last_usb = set()

def _play_sound(filepath):
    if playsound and filepath and os.path.exists(filepath):
        threading.Thread(target=playsound, args=(filepath,), daemon=True).start()

def _notify(title, message, sound=None):
    print(f"[notifier] {title}: {message}")
    try:
        import wx
        if wx.GetApp():
            from wx.adv import TaskBarIcon
            ti = wx.GetApp().GetTopWindow()
            if hasattr(ti, 'tray') and ti.tray:
                ti.tray.ShowBalloon(title, message, 3000, wx.adv.TBI_INFO)
    except Exception:
        pass
    speaker.speak_async(f"{title}: {message}")
    if sound:
        _play_sound(sound)

def _get_usb_devices():
    import subprocess
    try:
        result = subprocess.run(
            ["wmic", "path", "Win32_USBControllerDevice", "get", "Dependent"],
            capture_output=True, text=True, timeout=5
        )
        devices = set()
        for line in result.stdout.splitlines():
            line = line.strip()
            if line and "Win32_PnPEntity" in line:
                try:
                    did = line.split("=")[1].strip('"')
                    devices.add(did)
                except IndexError:
                    pass
        return devices
    except Exception:
        return set()

def _get_battery():
    import psutil
    bat = psutil.sensors_battery()
    if bat:
        return bat.percent, bat.power_plugged
    return None, None

def _get_ram_percent():
    import psutil
    return psutil.virtual_memory().percent

def _get_disk_percent(path=None):
    import psutil
    if path is None:
        path = os.path.splitdrive(os.path.abspath("."))[0] + "\\"
    return psutil.disk_usage(path).percent

def check():
    global _last_usb
    triggered = []

    # Battery checks
    pct, plugged = _get_battery()
    if pct is not None:
        key = ("battery_low", pct < config.low_battery_threshold and not plugged)
        if key not in _HISTORY or _HISTORY[key] != (pct, plugged):
            _HISTORY[key] = (pct, plugged)
            if key[1] and config.notify_low_battery:
                triggered.append(("Low Battery", f"Battery at {pct}%", config.notification_sound))

        key_p = ("battery_plugged", plugged)
        if key_p not in _HISTORY:
            _HISTORY[key_p] = plugged
        elif _HISTORY[key_p] != plugged:
            _HISTORY[key_p] = plugged
            if plugged and config.notify_battery_plugged:
                triggered.append(("Charging", "Power adapter connected.", config.notification_sound))
            elif not plugged and config.notify_battery_unplugged:
                triggered.append(("On Battery", "Power adapter disconnected.", config.notification_sound))

    # RAM check
    ram = _get_ram_percent()
    key_r = ("ram_high", ram > config.high_ram_threshold)
    if key_r not in _HISTORY or _HISTORY[key_r] != ram:
        _HISTORY[key_r] = ram
        if key_r[1] and config.notify_high_ram:
            triggered.append(("High RAM Usage", f"RAM at {ram:.0f}%", config.notification_sound))

    # Disk check
    dp = _get_disk_percent()
    key_d = ("disk_low", dp > (100 - config.low_disk_threshold))
    if key_d not in _HISTORY or _HISTORY[key_d] != dp:
        _HISTORY[key_d] = dp
        if key_d[1] and config.notify_low_disk:
            triggered.append(("Low Disk Space", f"Disk at {dp:.0f}% used", config.notification_sound))

    # USB check
    current_usb = _get_usb_devices()
    if _last_usb and current_usb:
        new_devices = current_usb - _last_usb
        for _ in new_devices:
            if config.notify_usb_attached:
                triggered.append(("USB Device", "New USB device attached.", config.notification_sound))
    _last_usb = current_usb

    for title, msg, sound in triggered:
        sound_path = os.path.join(config.notifications_dir, sound) if sound else None
        _notify(title, msg, sound_path)

def monitor_loop(interval=5):
    while True:
        try:
            check()
        except Exception as e:
            print(f"[notifier] Error: {e}")
        time.sleep(interval)

def start():
    t = threading.Thread(target=monitor_loop, daemon=True)
    t.start()
    print("[notifier] Started")
