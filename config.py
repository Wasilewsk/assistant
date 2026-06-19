import os

speech_rate = 190
voice_index = 1
wake_word = "computer"
user_name = "User"
ai_name = "Cortana"
save_notes = True
startup_greeting = True

notes_dir = os.path.join(os.path.expanduser("~"), "CortanaNotes")
os.makedirs(notes_dir, exist_ok=True)

home_dir = os.path.expanduser("~")
current_dir = home_dir
