#!/usr/bin/env python3
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib
import sys
import os

CSS = """
window {
  background: rgba(16, 14, 22, 0.95);
  border: 1px solid rgba(224, 179, 65, 0.55);
  border-radius: 6px;
}
calendar {
  background: transparent;
  color: #c0c0c0;
  font-family: "JetBrains Mono", "Noto Sans", sans-serif;
  font-size: 13px;
  border: none;
  padding: 8px;
}
calendar:selected {
  color: #9ccc65;
  background: rgba(156, 204, 101, 0.12);
}
calendar.header {
  color: #9ccc65;
  font-weight: bold;
}
calendar.button {
  color: #c0c0c0;
}
calendar.highlight {
  color: #9ccc65;
}
"""


class CalendarPopup(Gtk.Window):
    def __init__(self, screen_center_x, y):
        super().__init__()
        self.set_title('hyper-calendar-popup')
        self.set_decorated(False)
        self.set_skip_taskbar_hint(True)
        self.set_keep_above(True)
        self.set_accept_focus(True)
        self.set_position(Gtk.WindowPosition.NONE)
        self.set_resizable(False)

        self._screen_center_x = screen_center_x
        self._pos_y = y

        self._apply_css()
        self.connect('focus-out-event', lambda *_: Gtk.main_quit())
        self.connect('key-press-event', self._on_key)
        self.connect('map', lambda *_: GLib.timeout_add(50, self._reposition))

        cal = Gtk.Calendar()
        cal.props.show_week_numbers = True
        cal.props.show_day_names = True
        cal.props.show_details = False
        self.add(cal)

        self.show_all()

    def _apply_css(self):
        css = Gtk.CssProvider()
        css.load_from_data(CSS.encode())
        Gtk.StyleContext.add_provider_for_screen(
            self.get_screen(), css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def _reposition(self):
        win_x = self._screen_center_x - self.get_allocated_width() // 2
        os.system(
            f'hyprctl dispatch movewindowpixel '
            f'exact {win_x} {self._pos_y},title:hyper-calendar-popup')
        return False

    def _on_key(self, _, event):
        if event.keyval in (Gdk.KEY_Escape, Gdk.KEY_q):
            Gtk.main_quit()


if __name__ == '__main__':
    x, y = int(sys.argv[1]), int(sys.argv[2])
    CalendarPopup(x, y)
    Gtk.main()
