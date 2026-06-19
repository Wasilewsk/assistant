import os

speech_rate = 190
voice_index = 1
wake_word = "computer"
user_name = "User"
ai_name = "Cortana"
save_notes = True
startup_greeting = True

# Notification toggles
notify_low_battery = True
notify_battery_plugged = True
notify_battery_unplugged = True
notify_usb_attached = True
notify_high_ram = True
notify_low_disk = True

# Thresholds
low_battery_threshold = 20
high_ram_threshold = 85
low_disk_threshold = 10

# Selected sound files
alarm_sound = "Rise.ogg"
notification_sound = "Note.ogg"

notes_dir = os.path.join(os.path.expanduser("~"), "CortanaNotes")
os.makedirs(notes_dir, exist_ok=True)

home_dir = os.path.expanduser("~")
current_dir = home_dir

sounds_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sounds")
alarms_dir = os.path.join(sounds_dir, "alarms")
notifications_dir = os.path.join(sounds_dir, "notifications")
