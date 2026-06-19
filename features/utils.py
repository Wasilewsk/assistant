import threading
import time
import datetime
import os
import app.config as config
import app.speaker as speaker

_timers = []
_alarms = []
_notes = []
_stopwatch_start = None
_stopwatch_running = False

def _timer_thread(seconds, label):
    time.sleep(seconds)
    speaker.speak(f"{label} Timer finished.")

def set_timer(command):
    import re
    match = re.search(r"(\d+)\s*(?:minutes?|mins?|min|m)\s*(\d+)?\s*(?:seconds?|secs?|sec|s)?", command.lower())
    if match:
        minutes = int(match.group(1))
        seconds = int(match.group(2) or 0)
        total = minutes * 60 + seconds
    else:
        match = re.search(r"(\d+)\s*(?:seconds?|secs?|sec|s)", command.lower())
        if match:
            total = int(match.group(1))
            minutes = 0
        else:
            match = re.search(r"(\d+)", command)
            if match:
                total = int(match.group(1)) * 60
                minutes = int(match.group(1))
            else:
                speaker.speak("How many minutes should I set the timer for?")
                return

    label = f"{minutes} minute" if minutes > 0 else ""
    if minutes > 1:
        label += "s"

    t = threading.Thread(target=_timer_thread, args=(total, label), daemon=True)
    t.start()
    _timers.append(t)
    speaker.speak(f"Timer set for {label}.")

def set_alarm(command):
    import re
    match = re.search(r"(\d{1,2})\s*:\s*(\d{2})\s*(am|pm)?", command.lower())
    if match:
        hour = int(match.group(1))
        minute = int(match.group(2))
        ampm = match.group(3)

        now = datetime.datetime.now()
        if ampm:
            if ampm == "pm" and hour < 12:
                hour += 12
            elif ampm == "am" and hour == 12:
                hour = 0

        alarm_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if alarm_time <= now:
            alarm_time += datetime.timedelta(days=1)

        diff = (alarm_time - now).total_seconds()
        label = alarm_time.strftime("%I:%M %p").lstrip("0")

        t = threading.Thread(target=_timer_thread, args=(diff, f"Alarm for {label}"), daemon=True)
        t.start()
        _alarms.append(t)
        speaker.speak(f"Alarm set for {label}.")
    else:
        match = re.search(r"(\d{1,2})\s*(am|pm)", command.lower())
        if match:
            hour = int(match.group(1))
            ampm = match.group(2)
            minute = 0

            now = datetime.datetime.now()
            if ampm == "pm" and hour < 12:
                hour += 12
            elif ampm == "am" and hour == 12:
                hour = 0

            alarm_time = now.replace(hour=hour, minute=0, second=0, microsecond=0)
            if alarm_time <= now:
                alarm_time += datetime.timedelta(days=1)

            diff = (alarm_time - now).total_seconds()
            label = alarm_time.strftime("%I:%M %p").lstrip("0")

            t = threading.Thread(target=_timer_thread, args=(diff, f"Alarm for {label}"), daemon=True)
            t.start()
            _alarms.append(t)
            speaker.speak(f"Alarm set for {label}.")
        else:
            speaker.speak("What time should I set the alarm for? Example: set alarm for 7:30 am")

def stopwatch_start():
    global _stopwatch_start, _stopwatch_running
    if _stopwatch_running:
        speaker.speak("Stopwatch is already running.")
        return
    _stopwatch_start = time.time()
    _stopwatch_running = True
    speaker.speak("Stopwatch started.")

def stopwatch_stop():
    global _stopwatch_running
    if not _stopwatch_running:
        speaker.speak("No stopwatch is running.")
        return
    elapsed = time.time() - _stopwatch_start
    _stopwatch_running = False
    minutes = int(elapsed // 60)
    seconds = int(elapsed % 60)
    speaker.speak(f"Stopwatch stopped at {minutes} minutes and {seconds} seconds.")

def take_note(command):
    note = command.replace("take a note", "").replace("write a note", "").replace("note", "").strip()
    if not note:
        speaker.speak("What should I write down?")
        return

    _notes.append(note)
    if config.save_notes:
        try:
            filepath = os.path.join(config.notes_dir, "notes.txt")
            with open(filepath, "a", encoding="utf-8") as f:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                f.write(f"[{timestamp}] {note}\n")
        except Exception:
            pass
    speaker.speak("Note saved.")

def read_notes():
    if not _notes and config.save_notes:
        try:
            filepath = os.path.join(config.notes_dir, "notes.txt")
            if os.path.exists(filepath):
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                if content.strip():
                    speaker.speak(f"Your notes: {content[:1000]}")
                    return
        except Exception:
            pass

    if _notes:
        speaker.speak(f"Your notes for this session: {'. '.join(_notes)}")
    else:
        speaker.speak("You have no saved notes.")

def calculate(command):
    import re
    expr = command.replace("calculate", "").replace("compute", "").replace("what is", "").replace("equals", "").replace("=", "").strip()
    expr = re.sub(r"[^0-9+\-*/.%() ]", "", expr)
    if not expr:
        speaker.speak("What should I calculate?")
        return
    try:
        result = eval(expr)
        speaker.speak(f"The result is {result}")
    except Exception:
        speaker.speak("Could not calculate that expression.")

def handle_utils_command(command):
    cmd = command.lower()

    if "timer" in cmd:
        set_timer(command)
        return True

    if "alarm" in cmd:
        set_alarm(command)
        return True

    if "start stopwatch" in cmd:
        stopwatch_start()
        return True

    if "stop stopwatch" in cmd:
        stopwatch_stop()
        return True

    if "take a note" in cmd or "write a note" in cmd or "take note" in cmd:
        take_note(command)
        return True

    if "read my notes" in cmd or "read notes" in cmd or "show notes" in cmd:
        read_notes()
        return True

    if "calculate" in cmd or "compute" in cmd or ("what is" in cmd and any(c in cmd for c in "0123456789")):
        calculate(command)
        return True

    if "remind me" in cmd or "set reminder" in cmd:
        reminder = cmd.replace("remind me to", "").replace("set a reminder", "").replace("set reminder", "").strip()
        if reminder:
            speaker.speak(f"I'll remind you to {reminder}. However, timed reminders are not yet implemented. Note saved instead.")
            _notes.append(f"Reminder: {reminder}")
        else:
            speaker.speak("What should I remind you about?")
        return True

    return False
