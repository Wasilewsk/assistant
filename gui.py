import wx
import wx.adv
import threading
import time
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import app.config as config
import app.speaker as speaker
import app.listener as listener
import app.notifier as notifier
from app.assistant import handle_command
from app.beeps import ready as beep_ready, wake as beep_wake, stop_listen as beep_stop_listen, processing_start, processing_stop
from app.setup_wizard import is_first_run
from app.setup_gui import SetupWizard
from app.settings_dialog import SettingsDialog

class CortanaTaskBarIcon(wx.adv.TaskBarIcon):
    def __init__(self, frame):
        super().__init__()
        self.frame = frame
        icon = self._make_icon()
        self.SetIcon(icon, f"{config.ai_name} - {config.user_name}")

    def _make_icon(self):
        bmp = wx.Bitmap(16, 16)
        dc = wx.MemoryDC(bmp)
        dc.SetBackground(wx.Brush(wx.Colour(0, 120, 215)))
        dc.Clear()
        dc.SetBrush(wx.Brush(wx.Colour(255, 255, 255)))
        dc.DrawCircle(8, 6, 4)
        dc.SetPen(wx.Pen(wx.Colour(255, 255, 255), 2))
        dc.DrawArc(8, 13, 4, 8, 8, 9)
        dc.SelectObject(wx.NullBitmap)
        icon = wx.Icon()
        icon.CopyFromBitmap(bmp)
        return icon

    def OnTaskBarActivate(self, event):
        self.frame.Show()
        self.frame.Raise()
        self.frame.Restore()

    def CreatePopupMenu(self):
        menu = wx.Menu()
        show = menu.Append(wx.ID_ANY, "Show")
        hide = menu.Append(wx.ID_ANY, "Hide")
        menu.AppendSeparator()
        settings_item = menu.Append(wx.ID_ANY, "Setti&ngs")
        menu.AppendSeparator()
        quit_item = menu.Append(wx.ID_EXIT, "Quit")
        self.Bind(wx.EVT_MENU, lambda e: self.frame.Show(True), show)
        self.Bind(wx.EVT_MENU, lambda e: self.frame.Hide(), hide)
        self.Bind(wx.EVT_MENU, lambda e: self.frame._open_settings(), settings_item)
        self.Bind(wx.EVT_MENU, lambda e: self.frame._quit(), quit_item)
        return menu

class CortanaFrame(wx.Frame):
    def __init__(self):
        style = wx.DEFAULT_FRAME_STYLE & ~(wx.MAXIMIZE_BOX | wx.RESIZE_BORDER)
        super().__init__(None, title=f"{config.ai_name} - {config.user_name}", size=(500, 500), style=style)
        self.SetMinSize((400, 350))
        self.SetName(f"{config.ai_name} Assistant")
        self.Bind(wx.EVT_CLOSE, self._on_close)
        self.Bind(wx.EVT_ACTIVATE, self._on_activate)

        self._running = True
        self._wake_thread = None

        self._build_ui()
        self._create_tray()
        self.Centre()
        self.Show()
        self.input.SetFocus()

        self._log(f"{config.ai_name} ready. Say '{config.wake_word.capitalize()}' or type below.")
        speaker.speak_async(f"{config.ai_name} ready. Say '{config.wake_word.capitalize()}' or type below.")
        self._start_wake_listener()

    def _build_ui(self):
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        self.log = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.log.SetName("Conversation log")
        self.log.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        sizer.Add(self.log, 1, wx.EXPAND | wx.ALL, 8)

        bar = wx.BoxSizer(wx.HORIZONTAL)

        self.mic_btn = wx.Button(panel, label="S&peak", size=(70, 32))
        self.mic_btn.SetName("Speak button. Alt+P to activate.")
        self.mic_btn.SetToolTip("Alt+P to speak a command")
        self.mic_btn.Bind(wx.EVT_BUTTON, self._on_mic_click)
        bar.Add(self.mic_btn, 0, wx.RIGHT, 4)

        self.input = wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER)
        self.input.SetName("Command input. Type your command and press Enter.")
        self.input.SetHint("Type a command and press Enter...")
        self.input.Bind(wx.EVT_TEXT_ENTER, self._on_send)
        bar.Add(self.input, 1, wx.RIGHT, 4)

        self.send_btn = wx.Button(panel, label="&Send")
        self.send_btn.SetName("Send button. Alt+S to activate.")
        self.send_btn.SetDefault()
        self.send_btn.Bind(wx.EVT_BUTTON, self._on_send)
        bar.Add(self.send_btn, 0)
        sizer.Add(bar, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)

        self.status = wx.StaticText(panel, label=f"Say \"{config.wake_word.capitalize()}\" or type a command.")
        self.status.SetName("Status")
        self.status.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        sizer.Add(self.status, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)

        panel.SetSizer(sizer)

    def _create_tray(self):
        self.tray = CortanaTaskBarIcon(self)
        self.tray.Bind(wx.adv.EVT_TASKBAR_LEFT_DCLICK, lambda e: self.Show(True) or self.Raise())

    def _on_activate(self, event):
        if not event.GetActive():
            self.Hide()

    def _open_settings(self):
        dlg = SettingsDialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            dlg.save()
            speaker.speak_async("Settings saved.")
        dlg.Destroy()

    def _on_sleep(self):
        self.Hide()
        self.tray.ShowBalloon(f"{config.ai_name} Sleeping",
                              f"Say '{config.wake_word.capitalize()}' to wake me.",
                              2000, wx.adv.TBI_INFO)

    def _on_close(self, event):
        self.Hide()
        self.tray.ShowBalloon(f"{config.ai_name}",
                              f"{config.ai_name} is still running. Say '{config.wake_word.capitalize()}' to interact.",
                              2000, wx.adv.TBI_INFO)

    def _quit(self):
        self._running = False
        self.tray.RemoveIcon()
        self.Destroy()

    def _on_mic_click(self, event):
        self._set_status("Listening...")
        threading.Thread(target=self._do_voice_command, daemon=True).start()

    def _on_text_enter(self, event):
        self._process_text(self.input.GetValue().strip())

    def _on_send(self, event):
        self._process_text(self.input.GetValue().strip())

    def _process_text(self, text):
        if not text:
            return
        self.input.Clear()
        self._log(f"You: {text}")
        processing_start()
        threading.Thread(target=self._run_async, args=(text,), daemon=True).start()
        wx.CallAfter(self.input.SetFocus)

    def _do_voice_command(self):
        import speech_recognition as sr
        try:
            with sr.Microphone() as source:
                listener.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                cmd = listener.listen_for_command(source, timeout=8, phrase_limit=8)
                if cmd:
                    wx.CallAfter(self._log, f"You: {cmd}")
                    processing_start()
                    threading.Thread(target=self._run_async, args=(cmd,), daemon=True).start()
                else:
                    wx.CallAfter(self._set_status, "I didn't hear anything.")
                    beep_stop()
        except Exception as e:
            print(f"[core] Mic button error: {e}")
            wx.CallAfter(self._set_status, "Microphone error.")
        wx.CallAfter(self._set_status, f"Say \"{config.wake_word.capitalize()}\" or type a command.")

    def _log(self, text):
        ts = time.strftime("%H:%M")
        self.log.AppendText(f"[{ts}] {text}\n")
        self.log.ShowPosition(self.log.GetLastPosition())

    def _set_status(self, text):
        self.status.SetLabel(text)

    def _start_wake_listener(self):
        self._wake_thread = threading.Thread(target=self._wake_loop, daemon=True)
        self._wake_thread.start()

    def _wake_loop(self):
        import speech_recognition as sr
        print("[core] Wake listener started")
        beep_ready()
        wx.CallAfter(self._set_status, f"Say \"{config.wake_word.capitalize()}\" or type.")
        try:
            with sr.Microphone() as source:
                listener.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                while self._running:
                    try:
                        print("[core] Waiting for wake...")
                        detected = listener.listen_for_wake(source, config.wake_word, timeout=60)
                    except Exception as e:
                        print(f"[core] Wake error: {e}")
                        detected = False
                    if not detected or not self._running:
                        continue
                    beep_wake()
                    print("[core] Wake! Listening for command...")
                    wx.CallAfter(self._set_status, "Listening...")
                    try:
                        cmd = listener.listen_for_command(source, timeout=10, phrase_limit=8)
                    except Exception as e:
                        print(f"[core] Command error: {e}")
                        cmd = None
                    if cmd:
                        print(f"[core] Command: '{cmd}'")
                        wx.CallAfter(self._log, f"You: {cmd}")
                        processing_start()
                        threading.Thread(target=self._run_async, args=(cmd,), daemon=True).start()
                    else:
                        print("[core] No command")
                        beep_stop_listen()
                    wx.CallAfter(self._set_status, f"Say \"{config.wake_word.capitalize()}\" or type.")
        except Exception as e:
            print(f"[core] Mic error in wake loop: {e}")

    def _run_async(self, cmd):
        try:
            result, response = handle_command(cmd)
            if response:
                wx.CallAfter(self._log, f"{config.ai_name}: {response[:300]}")
            if result == "exit":
                wx.CallAfter(self._quit)
            elif result == "hide":
                wx.CallAfter(self.Hide)
            elif result == "show":
                wx.CallAfter(self.Show)
                wx.CallAfter(self.Raise)
            elif result == "sleep":
                wx.CallAfter(self._on_sleep)
            elif result == "settings":
                wx.CallAfter(self._open_settings)
        finally:
            processing_stop()

def launch_gui():
    print("Initializing speech engine...")
    speaker.init()
    print("Starting GUI...")
    app = wx.App(False)
    if is_first_run():
        dlg = SetupWizard(None)
        dlg.ShowModal()
        dlg.Destroy()
    CortanaFrame()
    notifier.start()
    app.MainLoop()
