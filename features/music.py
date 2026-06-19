import os
import threading
import time
import random
import pygame
import app.config as config
import app.speaker as speaker

_EXTS = {".mp3", ".wav", ".ogg", ".flac", ".m4a", ".wma", ".aac"}
_music_dir = os.path.join(os.path.expanduser("~"), "Music")
if not os.path.isdir(_music_dir):
    _music_dir = os.path.join(os.path.expanduser("~"), "music")

_playlist = []
_current_index = 0
_playing = False
_paused = False
_volume = 0.7
_stop_event = threading.Event()

def _scan():
    global _playlist
    _playlist = []
    if not os.path.isdir(_music_dir):
        return
    for root, dirs, files in os.walk(_music_dir):
        for f in sorted(files):
            if os.path.splitext(f)[1].lower() in _EXTS:
                _playlist.append(os.path.join(root, f))

def _player_loop():
    global _playing, _paused, _current_index
    while not _stop_event.is_set():
        if not _playlist:
            _playing = False
            break
        if _current_index < 0 or _current_index >= len(_playlist):
            _playing = False
            break
        path = _playlist[_current_index]
        name = os.path.splitext(os.path.basename(path))[0]
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(_volume)
            pygame.mixer.music.play()
            _playing = True
            _paused = False
            print(f"[music] Playing: {name}")
            speaker.speak_async(f"Playing {name}")
            while pygame.mixer.music.get_busy() and not _stop_event.is_set():
                time.sleep(0.5)
            if _stop_event.is_set():
                pygame.mixer.music.stop()
                break
            _current_index += 1
        except Exception as e:
            print(f"[music] Error playing {path}: {e}")
            _current_index += 1
    _playing = False

def start_playback():
    global _playing, _paused
    if _playing or _paused:
        return
    if not _playlist:
        _scan()
    if not _playlist:
        speaker.speak(f"No music files found in {_music_dir}")
        return
    _stop_event.clear()
    t = threading.Thread(target=_player_loop, daemon=True)
    t.start()

def play_song(query):
    global _current_index
    if not _playlist:
        _scan()
    if not _playlist:
        speaker.speak(f"No music files found in {_music_dir}")
        return
    query_lower = query.lower()
    matches = []
    for i, path in enumerate(_playlist):
        name = os.path.splitext(os.path.basename(path))[0]
        if query_lower in name.lower():
            matches.append((i, path, name))
    if not matches:
        speaker.speak(f"No songs match {query}")
        return
    stop()
    _current_index = matches[0][0]
    speaker.speak(f"Playing {matches[0][2]}")
    _stop_event.clear()
    t = threading.Thread(target=_player_loop, daemon=True)
    t.start()

def stop():
    global _playing, _paused
    _stop_event.set()
    pygame.mixer.music.stop()
    _playing = False
    _paused = False

def pause():
    global _paused
    if _playing and not _paused:
        pygame.mixer.music.pause()
        _paused = True
        speaker.speak_async("Music paused")

def resume():
    global _paused
    if _paused:
        pygame.mixer.music.unpause()
        _paused = False
        speaker.speak_async("Resuming")

def next_track():
    global _current_index
    if _playlist:
        stop()
        _current_index = (_current_index + 1) % len(_playlist)
        _stop_event.clear()
        t = threading.Thread(target=_player_loop, daemon=True)
        t.start()

def prev_track():
    global _current_index
    if _playlist:
        stop()
        _current_index = (_current_index - 1) % len(_playlist)
        _stop_event.clear()
        t = threading.Thread(target=_player_loop, daemon=True)
        t.start()

def list_music():
    if not _playlist:
        _scan()
    if not _playlist:
        speaker.speak(f"No music files found in {_music_dir}")
        return
    names = [os.path.splitext(os.path.basename(p))[0] for p in _playlist]
    text = f"You have {len(names)} songs. " + ", ".join(names[:20])
    if len(names) > 20:
        text += f", and {len(names) - 20} more."
    speaker.speak_async(text)

def shuffle():
    global _current_index, _playlist
    if not _playlist:
        _scan()
    if _playlist:
        random.shuffle(_playlist)
        _current_index = 0
        stop()
        speaker.speak("Playlist shuffled")
        start_playback()

def volume(level):
    global _volume
    try:
        v = max(0.0, min(1.0, int(level) / 100))
        _volume = v
        pygame.mixer.music.set_volume(v)
        speaker.speak_async(f"Volume set to {int(v * 100)} percent")
    except Exception:
        speaker.speak_async("Please say a number between 0 and 100")

def handle_music_command(command):
    cmd = command.lower().strip()

    if cmd in ["play music", "start music", "play songs", "play my music"]:
        start_playback()
        return True

    if cmd in ["stop music", "stop song", "end music"]:
        stop()
        speaker.speak_async("Music stopped")
        return True

    if cmd in ["pause music", "pause song"]:
        pause()
        return True

    if cmd in ["resume music", "resume song", "continue music", "unpause"]:
        resume()
        return True

    if cmd in ["next song", "next track", "skip", "skip song"]:
        next_track()
        return True

    if cmd in ["previous song", "previous track", "prev", "go back"]:
        prev_track()
        return True

    if cmd in ["list music", "list songs", "show music", "my playlist"]:
        list_music()
        return True

    if cmd in ["shuffle", "shuffle music", "shuffle playlist"]:
        shuffle()
        return True

    if cmd.startswith("volume ") or cmd.startswith("set volume "):
        parts = cmd.split()
        for p in parts:
            if p.isdigit():
                volume(p)
                return True

    if cmd.startswith("play ") and not any(
        cmd.startswith(x) for x in ["play music", "play songs", "play my music"]
    ):
        query = cmd.replace("play ", "", 1).strip()
        if query:
            play_song(query)
            return True

    return False
