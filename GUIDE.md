# Cortana Accessibility Guide — Voice-Controlled Assistant for the Blind

## Getting Started

### Installation

1. Install Python 3.9 or later from [python.org](https://python.org)
2. Open a terminal or command prompt
3. Navigate to the Project-Cortana folder
4. Run: `pip install -r requirements.txt`
5. Run: `python app/main.py`

### First Launch

When you start Cortana, you will hear a chime followed by:
> "Cortana online. Say 'Hey Cortana' to begin."

Say **"Hey Cortana"** to wake the assistant. You will hear a short acknowledgment tone.

## How to Speak Commands

### Wake Word
Always start with **"Hey Cortana"** before your command.

### Basic Pattern
```
"Hey Cortana, [your command]"
```

### Cancelling
Say **"stop"** or **"cancel"** during any read operation.

### Sleep Mode
Say **"go to sleep"** or **"goodbye"** to pause the assistant.
Say **"Hey Cortana"** again to wake it back up.

---

## Commands Reference

### Reading & Documents

| Say | What happens |
|-----|-------------|
| "read [filename]" | Reads a text file aloud |
| "read clipboard" | Reads whatever is copied to clipboard |
| "read PDF [filename]" | Reads a PDF document |
| "read Word [filename]" | Reads a Word document |
| "read image [filename]" | OCR: reads text from an image |
| "read screen" | Reads selected or visible text (screen reader mode) |
| "read this page" | Reads the current web page aloud |
| "stop reading" | Pauses/stop the current reading |
| "resume reading" | Resumes paused reading |
| "speed up" | Increases reading speed |
| "slow down" | Decreases reading speed |

### Web

| Say | What happens |
|-----|-------------|
| "search for [query]" | Searches the web and reads top results |
| "open [website]" | Opens a website (YouTube, Google, Wikipedia, etc.) |
| "read Wikipedia about [topic]" | Reads Wikipedia summary |
| "what's new" | Reads latest news headlines |

### System Control

| Say | What happens |
|-----|-------------|
| "open [app]" | Opens an application (Chrome, Notepad, etc.) |
| "list files" | Lists files in current directory |
| "list folders" | Lists folders in current directory |
| "where am I" | Tells you the current directory path |
| "go to [folder]" | Changes to a specified folder |
| "volume up" | Increases system volume |
| "volume down" | Decreases system volume |
| "mute" | Mutes system audio |
| "unmute" | Unmutes system audio |
| "shutdown" | Shuts down the computer (with confirmation) |
| "restart" | Restarts the computer (with confirmation) |
| "lock" | Locks the computer |

### Information

| Say | What happens |
|-----|-------------|
| "what time is it" | Tells current time |
| "what's the date" | Tells current date |
| "weather in [city]" | Reads weather forecast |
| "news" | Reads latest headlines |
| "define [word]" | Dictionary definition |
| "Wikipedia [topic]" | Reads Wikipedia summary |

### Productivity

| Say | What happens |
|-----|-------------|
| "set timer [X] minutes" | Sets a countdown timer |
| "set alarm for [time]" | Sets an alarm |
| "take a note" | Records a voice note |
| "read my notes" | Reads saved notes |
| "calculate [expression]" | Performs a calculation |
| "remind me to [task]" | Sets a reminder |
| "start stopwatch" | Starts a stopwatch |
| "stop stopwatch" | Stops and reports elapsed time |

### Assistant Control

| Say | What happens |
|-----|-------------|
| "help" | Lists available commands |
| "what can you do" | Lists your capabilities |
| "who are you" | Assistant introduction |
| "good morning/afternoon/evening" | Time-appropriate greeting |
| "go to sleep" | Puts assistant in standby |
| "goodbye" | Exits the assistant |
| "thank you" | Acknowledges thanks |

---

## Audio Cues

| Sound | Meaning |
|-------|---------|
| Short ascending tone | Wake word detected, listening |
| Short descending tone | Command received, processing |
| Double beep | Task completed |
| Long tone | Error or could not understand |
| Tick-tock | Timer counting down |
| Alarm sound | Timer or alarm completed |

---

## Tips for Blind Users

1. **Start simple** — Begin with "Hey Cortana, what time is it?" to verify setup
2. **Speak clearly** — Natural pace, not too slow or too fast
3. **Use the wake word** — Wait for the acknowledgment tone before your command
4. **Background noise** — A quiet environment improves recognition accuracy
5. **Reading speed** — Use "speed up" or "slow down" to find comfortable pace
6. **Stuck?** — Say "Hey Cortana, help" for a list of commands
7. **File paths** — When reading files, you can say the full path or just the filename for files in the current directory

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "I don't hear anything" | Check speakers/headphones, volume, and microphone |
| "Cortana doesn't wake" | Ensure microphone is connected and not muted |
| "Speech not recognized" | Try speaking more clearly; reduce background noise |
| "Can't read PDFs" | Install `pdfplumber`: `pip install pdfplumber` |
| "OCR not working" | Install Tesseract from https://github.com/UB-Mannheim/tesseract/wiki |

---

## Keyboard Shortcuts (for users with partial sight)

| Key | Action |
|-----|--------|
| Ctrl+Shift+C | Toggle Cortana listening mode |
| Ctrl+Shift+Q | Quit Cortana |
| Ctrl+Shift+S | Stop current speech |
| Ctrl+Shift+V | Read clipboard aloud |
| Ctrl+Shift+F | Re-read last spoken text |

---

## Customization

Edit `app/config.py` to change:
- **Voice speed** — `speech_rate` (default 190)
- **Voice index** — `voice_index` (0 or 1)
- **Wake word** — `wake_word` (default "cortana")
- **User name** — `user_name` (default "User")
- **AI name** — `ai_name` (default "Cortana")
- **Auto-save notes** — `save_notes` (True/False)
- **Startup greeting** — Toggle on/off
