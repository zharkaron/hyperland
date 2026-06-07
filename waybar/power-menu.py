#!/usr/bin/env python3
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib
import subprocess
import sys

CSS = """
window {
  background: rgba(16, 14, 22, 0.95);
  border: 1px solid rgba(224, 179, 65, 0.55);
  border-radius: 6px;
}
button {
  background: transparent;
  color: #c0c0c0;
  border: none;
  padding: 8px 14px;
  font-family: "JetBrains Mono", "Noto Sans", sans-serif;
  font-size: 13px;
  outline: none;
  min-height: 0;
}
button:hover {
  background: rgba(156, 204, 101, 0.12);
  color: #9ccc65;
}
"""

ITEMS = [
    ("⏻", "Shutdown", "systemctl poweroff"),
    ("⭮", "Reboot",   "systemctl reboot"),
    ("⏾", "Suspend",  "systemctl suspend"),
    ("", "Logout",   "hyprctl dispatch exit"),
]

TITLE = "hyper-power-menu"

class PowerPopup(Gtk.Window):
    def __init__(self, x, y):
        super().__init__()
        self.set_title(TITLE)
        self.set_decorated(False)
        self.set_skip_taskbar_hint(True)
        self.set_keep_above(True)
        self.set_accept_focus(True)
        self.set_position(Gtk.WindowPosition.NONE)
        self.set_default_size(150, -1)
        self.set_resizable(False)

        self._pos_x = x
        self._pos_y = y

        self._apply_css()
        self.connect("focus-out-event", lambda *_: Gtk.main_quit())
        self.connect("key-press-event", self._on_key)
        self.connect("map", lambda *_: GLib.timeout_add(50, self._reposition))

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add(vbox)

        for icon, label, cmd in ITEMS:
            btn = Gtk.Button(label=f"{icon}  {label}")
            btn.connect("clicked", lambda _, c=cmd: self._run(c))
            vbox.pack_start(btn, False, False, 0)

        self.show_all()

    def _apply_css(self):
        css = Gtk.CssProvider()
        css.load_from_data(CSS.encode())
        Gtk.StyleContext.add_provider_for_screen(
            self.get_screen(), css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def _reposition(self):
        subprocess.run([
            "hyprctl", "dispatch", "movewindowpixel",
            f"exact {self._pos_x} {self._pos_y},title:{TITLE}"
        ])
        return False

    def _on_key(self, _, event):
        if event.keyval in (Gdk.KEY_Escape, Gdk.KEY_q):
            Gtk.main_quit()

    def _run(self, cmd):
        subprocess.Popen(cmd.split())
        Gtk.main_quit()

if __name__ == "__main__":
    x, y = int(sys.argv[1]), int(sys.argv[2])
    PowerPopup(x, y)
    Gtk.main()
