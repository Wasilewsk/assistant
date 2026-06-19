import wx
import os
import app.config as config

class SettingsDialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, title=f"{config.ai_name} Settings", size=(420, 480),
                           style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.Centre()
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        nb = wx.Notebook(panel)
        sizer.Add(nb, 1, wx.EXPAND | wx.ALL, 8)

        # --- Notifications tab ---
        notif_panel = wx.Panel(nb)
        notif_sizer = wx.BoxSizer(wx.VERTICAL)

        self.cb_bat_low = wx.CheckBox(notif_panel, label="Low battery")
        self.cb_bat_low.SetValue(config.notify_low_battery)
        notif_sizer.Add(self.cb_bat_low, 0, wx.ALL, 4)

        self.cb_bat_plug = wx.CheckBox(notif_panel, label="Battery plugged in")
        self.cb_bat_plug.SetValue(config.notify_battery_plugged)
        notif_sizer.Add(self.cb_bat_plug, 0, wx.ALL, 4)

        self.cb_bat_unplug = wx.CheckBox(notif_panel, label="Battery unplugged")
        self.cb_bat_unplug.SetValue(config.notify_battery_unplugged)
        notif_sizer.Add(self.cb_bat_unplug, 0, wx.ALL, 4)

        self.cb_usb = wx.CheckBox(notif_panel, label="USB device attached")
        self.cb_usb.SetValue(config.notify_usb_attached)
        notif_sizer.Add(self.cb_usb, 0, wx.ALL, 4)

        self.cb_ram = wx.CheckBox(notif_panel, label="High RAM usage")
        self.cb_ram.SetValue(config.notify_high_ram)
        notif_sizer.Add(self.cb_ram, 0, wx.ALL, 4)

        self.cb_disk = wx.CheckBox(notif_panel, label="Low disk space")
        self.cb_disk.SetValue(config.notify_low_disk)
        notif_sizer.Add(self.cb_disk, 0, wx.ALL, 4)

        notif_sizer.Add(wx.StaticLine(notif_panel), 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 8)

        notif_sizer.Add(wx.StaticText(notif_panel, label="Notification sound:"), 0, wx.ALL, 4)
        self.notif_sound_choice = wx.Choice(notif_panel)
        self._populate_sounds(self.notif_sound_choice, config.notifications_dir, config.notification_sound)
        notif_sizer.Add(self.notif_sound_choice, 0, wx.EXPAND | wx.ALL, 4)

        notif_panel.SetSizer(notif_sizer)
        nb.AddPage(notif_panel, "Notifications")

        # --- Alarms tab ---
        alarm_panel = wx.Panel(nb)
        alarm_sizer = wx.BoxSizer(wx.VERTICAL)

        alarm_sizer.Add(wx.StaticText(alarm_panel, label="Default alarm sound:"), 0, wx.ALL, 4)
        self.alarm_sound_choice = wx.Choice(alarm_panel)
        self._populate_sounds(self.alarm_sound_choice, config.alarms_dir, config.alarm_sound)
        alarm_sizer.Add(self.alarm_sound_choice, 0, wx.EXPAND | wx.ALL, 4)

        alarm_panel.SetSizer(alarm_sizer)
        nb.AddPage(alarm_panel, "Alarms")

        # --- Buttons ---
        btn_sizer = wx.StdDialogButtonSizer()
        save_btn = wx.Button(panel, wx.ID_OK, "&Save")
        save_btn.SetDefault()
        cancel_btn = wx.Button(panel, wx.ID_CANCEL, "&Cancel")
        btn_sizer.AddButton(save_btn)
        btn_sizer.AddButton(cancel_btn)
        btn_sizer.Realize()
        sizer.Add(btn_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)

        panel.SetSizer(sizer)
        self.SetAffirmativeId(save_btn.GetId())

    def _populate_sounds(self, choice, directory, current):
        if os.path.isdir(directory):
            files = sorted([f for f in os.listdir(directory) if f.lower().endswith('.ogg')])
            choice.AppendItems(files)
            if current in files:
                choice.SetStringSelection(current)
            elif files:
                choice.SetSelection(0)

    def save(self):
        config.notify_low_battery = self.cb_bat_low.GetValue()
        config.notify_battery_plugged = self.cb_bat_plug.GetValue()
        config.notify_battery_unplugged = self.cb_bat_unplug.GetValue()
        config.notify_usb_attached = self.cb_usb.GetValue()
        config.notify_high_ram = self.cb_ram.GetValue()
        config.notify_low_disk = self.cb_disk.GetValue()
        if self.notif_sound_choice.GetSelection() >= 0:
            config.notification_sound = self.notif_sound_choice.GetStringSelection()
        if self.alarm_sound_choice.GetSelection() >= 0:
            config.alarm_sound = self.alarm_sound_choice.GetStringSelection()
