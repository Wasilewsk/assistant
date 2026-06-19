import datetime
import app.speaker as speaker

try:
    import feedparser
    HAS_FEED = True
except ImportError:
    HAS_FEED = False

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

def get_time():
    now = datetime.datetime.now()
    time_str = now.strftime("%I:%M %p").lstrip("0")
    speaker.speak(f"The time is {time_str}")

def get_date():
    now = datetime.datetime.now()
    date_str = now.strftime("%A, %B %d, %Y")
    speaker.speak(f"Today is {date_str}")

def get_weather(command):
    city = command.replace("weather", "").replace("in", "").replace("at", "").strip()
    if not city:
        speaker.speak("Which city would you like the weather for?")
        return

    if not HAS_REQUESTS:
        speaker.speak(f"Weather lookup requires the requests library.")
        return

    try:
        url = f"https://wttr.in/{city}?format=%C+%t+%w+%h"
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200 and resp.text.strip():
            speaker.speak(f"Weather in {city}: {resp.text}")
        else:
            speaker.speak(f"Could not get weather for {city}.")
    except Exception:
        speaker.speak(f"Weather service unavailable.")

def get_news():
    if not HAS_FEED:
        speaker.speak("News reader requires feedparser. Install: pip install feedparser")
        return

    try:
        feed = feedparser.parse("https://feeds.bbci.co.uk/news/rss.xml")
        headlines = [entry.title for entry in feed.entries[:8]]
        if headlines:
            speaker.speak("Top news headlines: " + ". ".join(headlines))
        else:
            speaker.speak("No news headlines available right now.")
    except Exception:
        speaker.speak("Could not fetch the news.")

def get_definition(command):
    word = command.replace("define", "").replace("definition", "").replace("meaning of", "").replace("what does", "").replace("mean", "").strip()
    if not word:
        speaker.speak("What word would you like me to define?")
        return

    if not HAS_REQUESTS:
        speaker.speak(f"Dictionary requires the requests library.")
        return

    try:
        resp = requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}", timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            meanings = data[0].get("meanings", [])
            if meanings:
                defs = meanings[0].get("definitions", [])
                if defs:
                    definition = defs[0].get("definition", "No definition found.")
                    example = defs[0].get("example", "")
                    result = f"{word}: {definition}"
                    if example:
                        result += f". Example: {example}"
                    speaker.speak(result)
                    return
        speaker.speak(f"Could not find a definition for {word}.")
    except Exception:
        speaker.speak(f"Dictionary service unavailable.")

def handle_info_command(command):
    cmd = command.lower()

    if "time" in cmd:
        get_time()
        return True

    if "date" in cmd or "day" in cmd:
        get_date()
        return True

    if "weather" in cmd or "temperature" in cmd:
        get_weather(command)
        return True

    if "news" in cmd or "headlines" in cmd:
        get_news()
        return True

    if "define" in cmd or "definition" in cmd or "meaning of" in cmd or ("what does" in cmd and "mean" in cmd):
        get_definition(command)
        return True

    return False
