import os
import json
import time
import pyttsx3
import app.config as config
import app.speaker as speaker
import app.listener as listener
from app.beeps import error as beep_error

SETUP_FILE = os.path.join(os.path.dirname(config.notes_dir), ".cortana_setup.json")

def load_config():
    try:
        if os.path.exists(SETUP_FILE):
            with open(SETUP_FILE, "r") as f:
                data = json.load(f)
            config.user_name = data.get("user_name", config.user_name)
            config.ai_name = data.get("ai_name", config.ai_name)
            config.voice_index = data.get("voice_index", config.voice_index)
            config.speech_rate = data.get("speech_rate", config.speech_rate)
            speaker.set_speed(config.speech_rate)
            speaker.set_voice(config.voice_index)
            return data.get("setup_complete", False)
    except Exception:
        pass
    return False

def is_first_run():
    return not load_config()

def save_config():
    try:
        data = {
            "setup_complete": True,
            "user_name": config.user_name,
            "ai_name": config.ai_name,
            "voice_index": config.voice_index,
            "speech_rate": config.speech_rate,
        }
        with open(SETUP_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass

def _voice_or_keyboard(prompt, timeout=10):
    print(f"\n[ASSISTANT] {prompt}")
    speaker.speak(prompt)
    time.sleep(0.5)
    print("[LISTENING] Speak now, or type your answer below:")
    result = listener.listen_for_simple(timeout=timeout, phrase_limit=6)
    if result:
        print(f"[YOU SAID] {result}")
        return result, "voice"
    answer = input("> ").strip().lower()
    if answer:
        print(f"[YOU TYPED] {answer}")
        return answer, "keyboard"
    return None, None

def run_setup():
    speaker.speak("Hello. I don't think we've met before. Let me introduce myself.")
    speaker.speak("I'm your personal AI assistant. I can help you navigate your computer, read documents, search the web, and much more, all by using your voice.")
    speaker.speak("First things first.")

    name = None
    while not name:
        answer, source = _voice_or_keyboard("What is your name?")
        if answer:
            cleaned = " ".join(w.capitalize() for w in answer.strip().split())
            if cleaned:
                name = cleaned
                speaker.speak(f"Ah, {name}. That is a wonderful name. It's an honor to meet you.")
        else:
            beep_error()
            speaker.speak("I didn't catch that. Please tell me your name.")

    config.user_name = name

    speaker.speak(f"Now, {name}, I need a name for myself too.")

    ai = None
    while not ai:
        answer, source = _voice_or_keyboard("What would you like to call your AI assistant? You can name me anything you like. Cortana, Jarvis, or something entirely your own.")
        if answer:
            cleaned = answer.strip().title()
            if cleaned:
                ai = cleaned
                speaker.speak(f"{ai}. I like it. It has a nice ring to it.")
        else:
            beep_error()
            speaker.speak("I didn't catch that. What would you like to name me?")

    config.ai_name = ai

    speaker.speak(f"Perfect. Here is how this works, {name}. Whenever you need me, simply say the word Computer, followed by what you want. For example, Computer, what time is it? Or Computer, read my notes.")

    speaker.speak("Now, let's find a voice that sounds good to you. I'll play a few samples.")

    voices = speaker.get_voices()

    if voices and len(voices) > 1:
        candidates = []
        seen = set()
        for i, v in enumerate(voices):
            name_lower = v.name.lower()
            key = name_lower.split("-")[0].strip() if "-" in name_lower else name_lower.split("(")[0].strip()
            if key and key not in seen:
                for kw in ["zira", "hazel", "jenny", "aria", "emma", "kendra", "natasha", "eva", "sonia", "heather", "joey", "eric", "brian", "guy", "ryan", "thomas", "andrew", "christopher", "roger", "steffan", "william", "libby", "maisie", "ana", "michelle", "ava", "serena", "heather"]:
                    if kw in name_lower:
                        candidates.append((i, v))
                        seen.add(key)
                        break
            if len(candidates) >= 4:
                break
        if not candidates:
            for i, v in enumerate(voices):
                if 0 < i < 6:
                    candidates.append((i, v))

        chosen_idx = None
        for idx, (voice_idx, voice) in enumerate(candidates):
            print(f"\n[VOICE {idx+1}] {voice.name}")
            answer, source = _voice_or_keyboard(f"Voice number {idx + 1}: {voice.name}. Would you like to hear a sample?")
            if answer and any(w in answer for w in ["yes", "sure", "ok", "hear", "play", "yeah"]):
                test = pyttsx3.init()
                test.setProperty('voice', voice.id)
                test.setProperty('rate', config.speech_rate)
                test.say(f"Hello {name}. My name is {config.ai_name}. How do I sound? I can read documents, search the web, tell you the news, and much more.")
                test.runAndWait()
                test.stop()

                answer2, source2 = _voice_or_keyboard("Do you like this voice? Say yes or no.")
                if answer2 and any(w in answer2 for w in ["yes", "yeah", "good", "perfect", "love"]):
                    chosen_idx = voice_idx
                    speaker.speak(f"Then {voice.name} it is. Wonderful choice.")
                    break
            else:
                speaker.speak("No problem. Let's move to the next one.")

        if chosen_idx is not None:
            config.voice_index = chosen_idx
            speaker.set_voice(chosen_idx)
        else:
            idx_input = input(f"\n[VOICE] No voice selected. Pick a number 0-{len(candidates)-1}, or press Enter for default: ").strip()
            if idx_input.isdigit() and 0 <= int(idx_input) < len(candidates):
                config.voice_index = candidates[int(idx_input)][0]
                speaker.set_voice(config.voice_index)
            else:
                config.voice_index = 0
                speaker.set_voice(0)
            speaker.speak("Voice set.")

    speaker.speak(f"Almost done, {name}. Let me check my reading speed.")

    for attempt in range(5):
        answer, source = _voice_or_keyboard("Would you like me to read faster or slower? Just say faster, slower, or good.")
        if answer:
            r = answer.lower()
            if "faster" in r or "speed up" in r:
                config.speech_rate = min(350, config.speech_rate + 30)
                speaker.set_speed(config.speech_rate)
                speaker.speak("How about this? I'm now reading at a quicker pace.")
            elif "slower" in r or "slow down" in r:
                config.speech_rate = max(80, config.speech_rate - 30)
                speaker.set_speed(config.speech_rate)
                speaker.speak("How about this? I'm now reading a bit slower.")
            elif "good" in r or "perfect" in r or "done" in r or "fine" in r or "yes" in r or "ok" in r:
                speaker.speak("Perfect. This speed feels right.")
                break
        else:
            speaker.speak("No problem. I'll keep my current speed for now.")

    config.speech_rate = speaker.get_speed()
    save_config()

    speaker.speak(f"Setup is complete. Welcome to the team, {name}.")
    speaker.speak(f"I am {config.ai_name}. Whenever you need me, just say Computer, followed by your request.")
    speaker.speak(f"I'm here to help. Let's get started.")
