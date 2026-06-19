import app.speaker as speaker
import app.config as config
from app.features import reader, web, system, info, utils

_last_spoken = ""

def _say(text):
    global _last_spoken
    _last_spoken = text
    speaker.speak_async(text)

def _say_block(text):
    global _last_spoken
    _last_spoken = text
    speaker.speak(text)

def handle_command(command):
    global _last_spoken
    _last_spoken = ""
    cmd = command.lower().strip()
    name = config.user_name

    if not cmd:
        return None, ""

    if cmd in ["exit", "quit", "goodbye", "bye", "see you"]:
        _say_block(f"Goodbye, {name}. {config.ai_name} is signing off.")
        return "exit", _last_spoken

    if cmd in ["go to sleep", "sleep", "standby"]:
        _say_block(f"Going to sleep, {name}. Say '{config.wake_word.capitalize()}' to wake me.")
        return "sleep", _last_spoken

    if cmd in ["minimize", "hide", "go to tray", "minimise"]:
        _say_block(f"Hiding to tray, {name}. Say '{config.wake_word.capitalize()}' or double-click the tray icon to bring me back.")
        return "hide", _last_spoken

    if cmd in ["show", "come back", "come here", "show window", "restore"]:
        return "show", _last_spoken

    if cmd in ["help", "what can you do", "commands", "list commands", "capabilities", "what are you capable of"]:
        _say(f"{name}, here's what I can do. To read: 'read clipboard', 'read file name.txt', 'read PDF report', 'read image photo.png'. To search: 'search for Python tutorial', 'open YouTube', 'Wikipedia machine learning'. For info: 'what time is it', 'weather in London', 'define computer', 'get news'. Files: 'list files', 'where am I', 'go to Downloads'. System: 'open Chrome', 'volume up', 'lock computer', 'shutdown'. Tools: 'set timer 5 minutes', 'set alarm for 7 AM', 'start stopwatch', 'take a note', 'calculate 5 times 7'.")
        return None, _last_spoken

    if cmd in ["thank you", "thanks", "good", "nice"]:
        _say(f"You're welcome, {name}. I'm happy to help.")
        return None, _last_spoken

    if cmd in ["good morning"]:
        _say(f"Good morning, {name}. How can I assist you today?")
        return None, _last_spoken

    if cmd in ["good afternoon"]:
        _say(f"Good afternoon, {name}. How can I assist you today?")
        return None, _last_spoken

    if cmd in ["good evening"]:
        _say(f"Good evening, {name}. How can I assist you today?")
        return None, _last_spoken

    if cmd in ["good night"]:
        _say(f"Good night, {name}. Sleep well.")
        return None, _last_spoken

    if cmd in ["who are you", "what are you", "introduce yourself"]:
        _say(f"I am {config.ai_name}, {name}. I'm your personal voice-controlled assistant.")
        return None, _last_spoken

    if cmd in ["what is my name", "what's my name", "who am i"]:
        _say(f"Your name is {name}.")
        return None, _last_spoken

    if cmd in ["what voice", "current voice", "which voice", "voice settings", "settings"]:
        _say(f"{name}, your current settings: AI name is {config.ai_name}, reading speed is {speaker.get_speed()} words per minute, wake word is {config.wake_word.capitalize()}.")
        return None, _last_spoken

    if cmd in ["repeat", "say that again", "repeat that", "what did you say"]:
        _say(_last_spoken or f"I haven't said anything yet, {name}.")
        return None, _last_spoken

    if "speed up" in cmd:
        speaker.speed_up()
        _say(f"Reading speed increased to {speaker.get_speed()}, {name}.")
        return None, _last_spoken

    if "slow down" in cmd or cmd == "slow down":
        speaker.slow_down()
        _say(f"Reading speed decreased to {speaker.get_speed()}, {name}.")
        return None, _last_spoken

    if cmd in ["stop", "stop reading", "cancel", "shut up"]:
        speaker.stop()
        _last_spoken = "Stopped."
        return None, _last_spoken

    if system.handle_system_command(command):
        _last_spoken = _last_spoken or f"Executed system command, {name}."
        return None, _last_spoken

    if reader.handle_read_command(command):
        _last_spoken = f"Read command done, {name}."
        return None, _last_spoken

    if reader.handle_file_navigation(command):
        _last_spoken = f"File navigation done, {name}."
        return None, _last_spoken

    if web.handle_web_command(command):
        _last_spoken = f"Web command done, {name}."
        return None, _last_spoken

    if info.handle_info_command(command):
        _last_spoken = f"Info command done, {name}."
        return None, _last_spoken

    if utils.handle_utils_command(command):
        _last_spoken = f"Utility done, {name}."
        return None, _last_spoken

    _say(f"Sorry, {name}, I didn't understand that. Say help to see what I can do.")
    return None, _last_spoken
