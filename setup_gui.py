import wx
import pyttsx3
import threading
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import app.config as config
import app.speaker as speaker
from app.beeps import listen as beep_listen
from app.setup_wizard import save_config

class SetupWizard(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, title="Cortana Setup", size=(480, 420),
                           style=wx.DEFAULT_DIALOG_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
        self.SetMinSize((480, 420))
        self.Centre()

        self._page = 0
        self._user_name = ""
        self._ai_name = ""
        self._voice_idx = 0
        self._voice_candidates = []
        self._speed = config.speech_rate
        self._listening = False

        self._build_pages()
        self._show_page(0)
        self.Bind(wx.EVT_CLOSE, self._on_close)
        self.SetAffirmativeId(self.next_btn.GetId())

    def _build_pages(self):
        self.panel = wx.Panel(self)
        self.sizer = wx.BoxSizer(wx.VERTICAL)

        self.title = wx.StaticText(self.panel, style=wx.ALIGN_CENTER)
        self.title.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.sizer.Add(self.title, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 20)

        self.desc = wx.StaticText(self.panel, style=wx.ALIGN_CENTER)
        self.sizer.Add(self.desc, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 20)

        self.content = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.content, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 20)

        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.back_btn = wx.Button(self.panel, label="< &Back")
        self.back_btn.SetName("Back button. Alt+B to go back.")
        self.back_btn.Bind(wx.EVT_BUTTON, self._on_back)
        self.back_btn.Disable()
        btn_sizer.Add(self.back_btn, 0)
        btn_sizer.AddStretchSpacer()
        self.next_btn = wx.Button(self.panel, label="&Next >")
        self.next_btn.SetName("Next button. Alt+N to continue.")
        self.next_btn.SetDefault()
        self.next_btn.Bind(wx.EVT_BUTTON, self._on_next)
        btn_sizer.Add(self.next_btn, 0)
        self.sizer.Add(btn_sizer, 0, wx.EXPAND | wx.ALL, 20)
        self.panel.SetSizer(self.sizer)

    def _speak(self, text):
        threading.Thread(target=speaker.speak, args=(text,), daemon=True).start()

    def _clear_content(self):
        for item in self.content.GetChildren():
            win = item.GetWindow()
            if win:
                self.content.Detach(win)
                win.Destroy()

    def _show_page(self, idx):
        self._page = idx
        self._clear_content()
        pages = [
            self._page_welcome,
            self._page_user_name,
            self._page_ai_name,
            self._page_voice,
            self._page_speed,
            self._page_finish,
        ]
        if idx < len(pages):
            pages[idx]()
        self.back_btn.Enable(idx > 0)
        self.next_btn.SetLabel("&Finish" if idx == len(pages) - 1 else "&Next >")
        self.panel.Layout()

    def _page_welcome(self):
        self.title.SetLabel("Welcome to Cortana")
        self.desc.SetLabel("Let's set up your AI assistant in a few quick steps.")
        text = wx.StaticText(self.panel, label="I'll be your personal voice assistant.\n\nI can read documents, search the web, control your computer,\nand so much more.\n\nClick Next to get started.")
        self.content.Add(text, 1, wx.EXPAND)
        self._speak("Welcome to Cortana setup. I'll be your personal voice assistant. I can read documents, search the web, control your computer, and much more. Click Next to get started.")

    def _page_user_name(self):
        self.title.SetLabel("What's your name?")
        self.desc.SetLabel("I'd like to know who I'm working with.")
        lbl = wx.StaticText(self.panel, label="Enter your name:")
        self.content.Add(lbl, 0, wx.BOTTOM, 4)
        self.name_input = wx.TextCtrl(self.panel, value=self._user_name)
        self.name_input.SetHint("e.g. John")
        self.name_input.Bind(wx.EVT_TEXT, lambda e: setattr(self, '_user_name', self.name_input.GetValue().strip()))
        self.content.Add(self.name_input, 0, wx.EXPAND)
        self._speak("What is your name? Type it in the box below.")

    def _page_ai_name(self):
        self.title.SetLabel("Name your AI")
        self.desc.SetLabel("What would you like to call me?")
        lbl = wx.StaticText(self.panel, label="AI Assistant Name:")
        self.content.Add(lbl, 0, wx.BOTTOM, 4)
        self.ai_input = wx.TextCtrl(self.panel, value=self._ai_name or "Cortana")
        self.ai_input.SetHint("e.g. Cortana, Jarvis, Samantha")
        self.ai_input.Bind(wx.EVT_TEXT, lambda e: setattr(self, '_ai_name', self.ai_input.GetValue().strip()))
        self.content.Add(self.ai_input, 0, wx.EXPAND)
        info = wx.StaticText(self.panel, label="Wake word will always be \"Computer\".")
        info.SetForegroundColour(wx.Colour(100, 100, 100))
        self.content.Add(info, 0, wx.TOP, 8)
        self._speak("What would you like to call your AI assistant? You can name me anything you like. Cortana, Jarvis, or something entirely your own. The wake word to get my attention will always be Computer.")

    def _page_voice(self):
        self.title.SetLabel("Choose a voice")
        self.desc.SetLabel("Select a voice you like, then click Preview to hear it.")
        self.content.Add(wx.StaticText(self.panel, label="Available voices:"), 0, wx.BOTTOM, 4)

        voices = speaker.get_voices()
        self._voice_candidates = []
        seen = set()
        for i, v in enumerate(voices):
            key = v.name.split("-")[0].strip() if "-" in v.name else v.name.split("(")[0].strip()
            if key and key not in seen:
                for kw in ["zira", "hazel", "jenny", "aria", "emma", "kendra", "natasha", "eva", "sonia", "heather", "joey", "eric", "brian", "guy", "ryan", "thomas", "andrew", "ana", "michelle", "ava", "heather"]:
                    if kw in v.name.lower():
                        self._voice_candidates.append((i, v))
                        seen.add(key)
                        break
        if not self._voice_candidates:
            for i, v in enumerate(voices[:8]):
                self._voice_candidates.append((i, v))

        choices = [f"{v.name}" for _, v in self._voice_candidates]
        self.voice_list = wx.ListBox(self.panel, choices=choices, style=wx.LB_SINGLE)
        self.voice_list.SetSelection(0)
        self.content.Add(self.voice_list, 1, wx.EXPAND | wx.BOTTOM, 8)

        preview_btn = wx.Button(self.panel, label="\u25B6 Preview")
        preview_btn.Bind(wx.EVT_BUTTON, self._on_preview_voice)
        self.content.Add(preview_btn, 0, wx.ALIGN_CENTER)
        self._speak("Choose a voice you like. Select one from the list and click Preview to hear it.")

    def _on_preview_voice(self, event):
        sel = self.voice_list.GetSelection()
        if sel < 0 or sel >= len(self._voice_candidates):
            return
        idx, v = self._voice_candidates[sel]
        threading.Thread(target=self._play_voice, args=(v,), daemon=True).start()

    def _play_voice(self, v):
        engine = pyttsx3.init()
        engine.setProperty('voice', v.id)
        engine.setProperty('rate', self._speed)
        name = self._user_name or "there"
        engine.say(f"Hello {name}. My name is {self._ai_name or 'Cortana'}. How do I sound?")
        engine.runAndWait()
        engine.stop()

    def _page_speed(self):
        self.title.SetLabel("Adjust reading speed")
        self.desc.SetLabel("Use the slider to find a comfortable speed.")
        self.speed_slider = wx.Slider(self.panel, value=self._speed, minValue=80, maxValue=350,
                                      style=wx.SL_HORIZONTAL | wx.SL_LABELS)
        self.speed_slider.SetTickFreq(30)
        self.content.Add(self.speed_slider, 0, wx.EXPAND | wx.BOTTOM, 8)
        lbl = wx.StaticText(self.panel, label="Slow  \u2190                                     \u2192  Fast")
        self.content.Add(lbl, 0, wx.ALIGN_CENTER)
        test_btn = wx.Button(self.panel, label="\u25B6 Test Speed")
        test_btn.Bind(wx.EVT_BUTTON, self._on_test_speed)
        self.content.Add(test_btn, 0, wx.ALIGN_CENTER | wx.TOP, 8)
        self._speak("Adjust my reading speed with the slider. Slide left for slower, right for faster. Click Test Speed to hear it.")

    def _on_test_speed(self, event):
        speed = self.speed_slider.GetValue()
        threading.Thread(target=self._play_speed, args=(speed,), daemon=True).start()

    def _play_speed(self, speed):
        engine = pyttsx3.init()
        engine.setProperty('rate', speed)
        engine.say("The quick brown fox jumps over the lazy dog. This is how fast I will read.")
        engine.runAndWait()
        engine.stop()

    def _page_finish(self):
        self.title.SetLabel("All set!")
        name = self._user_name or "User"
        ai = self._ai_name or "Cortana"
        speed = self.speed_slider.GetValue() if hasattr(self, 'speed_slider') else self._speed
        voice_name = ""
        if hasattr(self, 'voice_list') and self._voice_candidates:
            sel = self.voice_list.GetSelection()
            if sel >= 0 and sel < len(self._voice_candidates):
                voice_name = self._voice_candidates[sel][1].name
        summary = (
            f"Name: {name}\n"
            f"AI Name: {ai}\n"
            f"Voice: {voice_name or 'Default'}\n"
            f"Reading Speed: {speed}\n\n"
            f"Wake word: \"Computer\"\n\n"
            f"Click Finish to save and get started!"
        )
        self.content.Add(wx.StaticText(self.panel, label=summary), 1, wx.EXPAND)
        self._speak(f"Setup complete. Your name is {name}. I am {ai}. My reading speed is set to {speed}. Click Finish to save and get started.")

    def _on_back(self, event):
        if self._page > 0:
            self._save_current()
            self._show_page(self._page - 1)

    def _on_next(self, event):
        if self._page == 5:
            self._save_final()
            self.EndModal(wx.ID_OK)
            return
        self._save_current()
        self._show_page(self._page + 1)

    def _save_current(self):
        if self._page == 1 and hasattr(self, 'name_input'):
            self._user_name = self.name_input.GetValue().strip()
        elif self._page == 2 and hasattr(self, 'ai_input'):
            self._ai_name = self.ai_input.GetValue().strip()
        elif self._page == 3 and hasattr(self, 'voice_list'):
            sel = self.voice_list.GetSelection()
            if sel >= 0 and sel < len(self._voice_candidates):
                self._voice_idx = self._voice_candidates[sel][0]
        elif self._page == 4 and hasattr(self, 'speed_slider'):
            self._speed = self.speed_slider.GetValue()

    def _save_final(self):
        self._save_current()
        config.user_name = self._user_name or "User"
        config.ai_name = self._ai_name or "Cortana"
        config.wake_word = "computer"
        config.speech_rate = self._speed
        config.voice_index = self._voice_idx
        speaker.set_speed(config.speech_rate)
        speaker.set_voice(config.voice_index)
        save_config()

    def _on_close(self, event):
        self.EndModal(wx.ID_CANCEL)
        self.Destroy()
