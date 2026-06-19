import threading
import time
import os
import pygame
import app.config as config
import app.speaker as speaker

_prev_plugged = None
_prev_battery_pct = None
_low_battery_notified = False
_prev_ram_high = False
_prev_disk_low = False
_prev_usb = set()

def _play_sound(filepath):
    if not filepath or not os.path.exists(filepath):
        return
    try:
        s = pygame.mixer.Sound(filepath)
        s.play()
    except Exception as e:
        print(f"[notifier] Sound error: {e}")

def _notify(title, message, sound=None):
    print(f"[notifier] {title}: {message}")
    try:
        import wx
        if wx.GetApp():
            ti = wx.GetApp().GetTopWindow()
            if hasattr(ti, 'tray') and ti.tray:
                ti.tray.ShowBalloon(title, message, 3000, wx.adv.TBI_INFO)
    except Exception:
        pass
    text = f"{title}: {message}"
    print(f"[notifier] Speaking: '{text}'")
    speaker.speak_async(text)
    print(f"[notifier] Speak queued")
    if sound:
        _play_sound(sound)

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

def check():
    global _prev_plugged, _prev_battery_pct, _low_battery_notified
    global _prev_ram_high, _prev_disk_low, _prev_usb
    triggered = []

    pct, plugged = _get_battery()
    if pct is not None:
        # Plug / unplug transition
        if _prev_plugged is not None and plugged != _prev_plugged:
            if plugged and config.notify_battery_plugged:
                triggered.append(("Charging", "Power adapter connected.", config.notification_sound))
                _low_battery_notified = False  # reset on plug
            elif not plugged and config.notify_battery_unplugged:
                triggered.append(("On Battery", "Power adapter disconnected.", config.notification_sound))
        _prev_plugged = plugged

        # Low battery — only notify once per low-battery episode
        low_now = (not plugged) and (pct <= config.low_battery_threshold)
        if low_now and not _low_battery_notified and config.notify_low_battery:
            triggered.append(("Low Battery", f"Battery at {pct}%", config.notification_sound))
            _low_battery_notified = True
        elif not low_now:
            _low_battery_notified = False
        _prev_battery_pct = pct

    # High RAM — notify on transition into high zone
    ram = _get_ram_percent()
    ram_high_now = ram > config.high_ram_threshold
    if ram_high_now and not _prev_ram_high and config.notify_high_ram:
        triggered.append(("High RAM Usage", f"RAM at {ram:.0f}%", config.notification_sound))
    _prev_ram_high = ram_high_now

    # Low disk — notify on transition into low zone
    dp = _get_disk_percent()
    disk_low_now = dp > (100 - config.low_disk_threshold)
    if disk_low_now and not _prev_disk_low and config.notify_low_disk:
        triggered.append(("Low Disk Space", f"Disk at {dp:.0f}% used", config.notification_sound))
    _prev_disk_low = disk_low_now

    # USB device attach
    current_usb = _get_usb_devices()
    if _prev_usb and current_usb:
        new_devices = current_usb - _prev_usb
        for _ in new_devices:
            if config.notify_usb_attached:
                triggered.append(("USB Device", "New USB device attached.", config.notification_sound))
    _prev_usb = current_usb

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
