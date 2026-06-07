#!/usr/bin/env python3
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib
import subprocess
import sys
import os

NORMAL = [
    'systemd-', 'dbus-', 'polkit', 'accounts-daemon', 'alsa-state', 'atd',
    'auditd', 'avahi-daemon', 'chronyd', 'colord', 'crond', 'gdm',
    'gssproxy', 'irqbalance', 'mcelog', 'ModemManager', 'NetworkManager',
    'rtkit-daemon', 'smartd', 'switcheroo-control', 'thermald', 'tuned',
    'udisks2', 'upower', 'uresourced', 'user@', 'wpa_supplicant', 'abrt',
    'rsyslog', 'bluetooth',
]

CSS = """
window {
  background: rgba(16, 14, 22, 0.95);
  border: 1px solid rgba(224, 179, 65, 0.55);
  border-radius: 6px;
}
label {
  color: #c0c0c0;
  font-family: "JetBrains Mono", "Noto Sans", sans-serif;
  font-size: 11px;
}
.title {
  font-weight: bold;
  font-size: 12px;
  color: #9ccc65;
}
.normal {
  color: #9ccc65;
}
.other {
  color: #e0b341;
}
"""


def is_normal(name):
    for p in NORMAL:
        if name.startswith(p):
            return True
    return False


def get_services():
    out = subprocess.run(
        ['systemctl', 'list-units', '--type=service', '--state=running',
         '--no-pager', '--plain'],
        capture_output=True, text=True
    ).stdout
    services = []
    for line in out.splitlines():
        if '.service' not in line:
            continue
        parts = line.split()
        if len(parts) < 1:
            continue
        name = parts[0].replace('.service', '')
        services.append(name)
    return services


class ServicesPopup(Gtk.Window):
    def __init__(self, x, y):
        super().__init__()
        self.set_title('hyper-services-popup')
        self.set_decorated(False)
        self.set_skip_taskbar_hint(True)
        self.set_keep_above(True)
        self.set_accept_focus(True)
        self.set_position(Gtk.WindowPosition.NONE)
        self.set_resizable(False)

        self._pos_x = x
        self._pos_y = y

        self._apply_css()
        self.connect('focus-out-event', lambda *_: Gtk.main_quit())
        self.connect('key-press-event', self._on_key)
        self.connect('map', lambda *_: GLib.timeout_add(50, self._reposition))

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        vbox.set_margin_start(10)
        vbox.set_margin_end(10)
        vbox.set_margin_top(6)
        vbox.set_margin_bottom(6)
        self.add(vbox)

        title = Gtk.Label(label='Running Services', xalign=0)
        title.get_style_context().add_class('title')
        title.set_margin_bottom(4)
        vbox.pack_start(title, False, False, 0)

        sw = Gtk.ScrolledWindow()
        sw.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        sw.set_min_content_height(120)
        sw.set_max_content_height(300)

        list_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=1)

        services = get_services()
        for svc in services:
            row = Gtk.Box(spacing=6)
            norm = is_normal(svc)
            mark = Gtk.Label(label='✓' if norm else '✗')
            mark.get_style_context().add_class('normal' if norm else 'other')
            lbl = Gtk.Label(label=svc, xalign=0)
            row.pack_start(mark, False, False, 0)
            row.pack_start(lbl, False, False, 0)
            list_box.pack_start(row, False, False, 0)

        sw.add(list_box)
        vbox.pack_start(sw, True, True, 0)

        self.show_all()

    def _apply_css(self):
        css = Gtk.CssProvider()
        css.load_from_data(CSS.encode())
        Gtk.StyleContext.add_provider_for_screen(
            self.get_screen(), css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def _reposition(self):
        os.system(
            f'hyprctl dispatch movewindowpixel '
            f'exact {self._pos_x} {self._pos_y},title:hyper-services-popup')
        return False

    def _on_key(self, _, event):
        if event.keyval in (Gdk.KEY_Escape, Gdk.KEY_q):
            Gtk.main_quit()


if __name__ == '__main__':
    x, y = int(sys.argv[1]), int(sys.argv[2])
    ServicesPopup(x, y)
    Gtk.main()
