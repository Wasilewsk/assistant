import urllib.parse
import app.speaker as speaker

try:
    import requests
    from bs4 import BeautifulSoup
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    import wikipedia
    HAS_WIKI = True
except ImportError:
    HAS_WIKI = False

try:
    import pywhatkit
    HAS_WHATSAPP = True
except ImportError:
    HAS_WHATSAPP = False

COMMON_SITES = {
    "youtube": "https://www.youtube.com",
    "google": "https://www.google.com",
    "gmail": "https://mail.google.com",
    "wikipedia": "https://www.wikipedia.org",
    "github": "https://github.com",
    "reddit": "https://www.reddit.com",
    "stackoverflow": "https://stackoverflow.com",
    "twitter": "https://twitter.com",
    "x": "https://x.com",
    "facebook": "https://www.facebook.com",
    "instagram": "https://www.instagram.com",
    "discord": "https://discord.com",
    "netflix": "https://www.netflix.com",
    "amazon": "https://www.amazon.com",
    "news": "https://news.google.com",
    "bing": "https://www.bing.com",
    "duckduckgo": "https://duckduckgo.com",
}

def open_website(name):
    name = name.lower().strip()
    if name in COMMON_SITES:
        url = COMMON_SITES[name]
    else:
        if "." not in name:
            name = name + ".com"
        url = "https://www." + name
    try:
        import webbrowser
        webbrowser.open(url)
        speaker.speak(f"Opening {name}")
    except Exception as e:
        speaker.speak(f"Could not open {name}")

def search_web(query):
    query = query.replace("search for", "").replace("search", "").replace("the web", "").replace("internet", "").strip()
    if not query:
        speaker.speak("What would you like to search for?")
        return

    speaker.speak(f"Searching for {query}")
    try:
        import webbrowser
        encoded = urllib.parse.quote(query)
        webbrowser.open(f"https://www.google.com/search?q={encoded}")
        speaker.speak(f"Search results opened for {query}")
    except Exception as e:
        speaker.speak("Could not open the search.")

def read_wikipedia(topic):
    if not HAS_WIKI:
        speaker.speak("Wikipedia is not available. Install wikipedia: pip install wikipedia")
        return

    topic = topic.replace("wikipedia", "").replace("read", "").replace("about", "").strip()
    if not topic:
        speaker.speak("What topic would you like to read about on Wikipedia?")
        return

    try:
        summary = wikipedia.summary(topic, sentences=5)
        speaker.speak(summary)
    except wikipedia.exceptions.DisambiguationError as e:
        options = e.options[:5]
        speaker.speak(f"Multiple results found: {', '.join(options)}. Please be more specific.")
    except wikipedia.exceptions.PageError:
        speaker.speak(f"Could not find a Wikipedia page for {topic}.")
    except Exception as e:
        speaker.speak(f"Error reading Wikipedia: {str(e)}")

def read_webpage(url=None):
    if not HAS_REQUESTS:
        speaker.speak("Web page reading requires requests and beautifulsoup4. Install: pip install requests beautifulsoup4")
        return

    if not url:
        speaker.speak("Which web page should I read?")
        return

    if not url.startswith("http"):
        url = "https://" + url

    try:
        response = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(response.text, 'html.parser')
        for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
            tag.decompose()
        text = soup.get_text(separator=' ', strip=True)
        if text:
            speaker.speak(text[:1500])
        else:
            speaker.speak("No readable content found on that page.")
    except Exception as e:
        speaker.speak(f"Could not read the web page: {str(e)}")

def handle_web_command(command):
    cmd = command.lower()

    if "search for" in cmd or "search the web" in cmd or "google" in cmd:
        search_web(command)
        return True

    if "wikipedia" in cmd:
        read_wikipedia(command)
        return True

    if "open" in cmd:
        for site in COMMON_SITES:
            if site in cmd:
                open_website(site)
                return True
        rest = cmd.replace("open", "").strip()
        if rest:
            open_website(rest)
            return True

    if "read" in cmd and ("page" in cmd or "website" in cmd or "web" in cmd or "http" in cmd):
        parts = cmd.replace("read", "").replace("the", "").replace("page", "").replace("website", "").replace("web", "").strip()
        read_webpage(parts if parts else None)
        return True

    if "play" in cmd and ("youtube" in cmd or "video" in cmd):
        song = cmd.replace("play", "").replace("on youtube", "").replace("youtube", "").replace("video", "").strip()
        if song and HAS_WHATSAPP:
            try:
                pywhatkit.playonyt(song)
                speaker.speak(f"Playing {song} on YouTube")
            except Exception:
                speaker.speak("Could not play that on YouTube.")
            return True

    return False
