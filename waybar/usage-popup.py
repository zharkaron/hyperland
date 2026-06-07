#!/usr/bin/env python3
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib, Pango
import sys
import os
import time

CSS = """
window {
  background: rgba(16, 14, 22, 0.95);
  border: 1px solid rgba(224, 179, 65, 0.55);
  border-radius: 6px;
}
label {
  color: #c0c0c0;
  font-family: "JetBrains Mono", "Noto Sans", sans-serif;
  font-size: 12px;
}
.section {
  font-weight: bold;
  font-size: 13px;
  padding: 2px 0;
}
.cpu-label {
  color: #9ccc65;
}
.ram-label {
  color: #e0b341;
}
.swap-label {
  color: #c0c0c0;
}
.usage-low {
  color: #9ccc65;
}
.usage-medium {
  color: #e0b341;
}
.usage-high {
  color: #f44336;
}
"""


def get_cpu_per_core():
    with open('/proc/stat') as f:
        lines = f.readlines()
    cores = {}
    for line in lines:
        if line.startswith('cpu') and line[3].isdigit():
            parts = line.split()
            core_id = parts[0]
            vals = [int(v) for v in parts[1:]]
            total = sum(vals)
            idle = vals[3]
            cores[core_id] = (total, idle)
    return cores


def get_cpu_total():
    with open('/proc/stat') as f:
        for line in f:
            if line.startswith('cpu '):
                parts = line.split()
                vals = [int(v) for v in parts[1:]]
                return sum(vals), vals[3]
    return 1, 0


def get_memory():
    with open('/proc/meminfo') as f:
        data = {}
        for line in f:
            parts = line.split(':')
            if len(parts) == 2:
                key = parts[0].strip()
                val = parts[1].strip().split()[0]
                data[key] = int(val)
    mem_total = data['MemTotal']
    mem_avail = data['MemAvailable']
    mem_used = mem_total - mem_avail
    swap_total = data.get('SwapTotal', 0)
    swap_free = data.get('SwapFree', 0)
    swap_used = swap_total - swap_free
    return (mem_total, mem_used), (swap_total, swap_used)


def fmt_size(kb):
    for unit in ('KiB', 'MiB', 'GiB'):
        if kb < 1024:
            return f"{kb:.1f}{unit}"
        kb /= 1024
    return f"{kb:.1f}TiB"


def usage_class(pct):
    if pct < 50:
        return 'usage-low'
    elif pct < 80:
        return 'usage-medium'
    return 'usage-high'


class UsagePopup(Gtk.Window):
    def __init__(self, x, y):
        super().__init__()
        self.set_title('hyper-usage-popup')
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

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        vbox.set_margin_start(14)
        vbox.set_margin_end(14)
        vbox.set_margin_top(10)
        vbox.set_margin_bottom(10)
        self.add(vbox)

        # CPU section
        cpu_label = Gtk.Label(label='CPU', xalign=0)
        cpu_label.get_style_context().add_class('section')
        cpu_label.get_style_context().add_class('cpu-label')
        vbox.pack_start(cpu_label, False, False, 0)

        cores_before = get_cpu_per_core()
        time.sleep(0.15)
        cores_after = get_cpu_per_core()

        core_list = sorted(cores_before.keys(), key=lambda k: int(k[3:]))
        for cid in core_list:
            t1, i1 = cores_before[cid]
            t2, i2 = cores_after[cid]
            dt = t2 - t1
            di = i2 - i1
            pct = (dt - di) * 100 // dt if dt else 0
            pct = max(0, min(100, pct))
            h = Gtk.Box(spacing=6)
            core_num = cid[3:]
            lbl = Gtk.Label(label=f'C{core_num}', xalign=0, width_chars=3)
            lbl.get_style_context().add_class('cpu-label')
            pct_lbl = Gtk.Label(label=f'{pct}%', xalign=0, width_chars=4)
            pct_lbl.get_style_context().add_class(usage_class(pct))
            bar = self._make_bar(pct, 130)
            h.pack_start(lbl, False, False, 0)
            h.pack_start(pct_lbl, False, False, 0)
            h.pack_start(bar, False, False, 0)
            vbox.pack_start(h, False, False, 0)

        vbox.pack_start(Gtk.Label(label=''), False, False, 0)

        # Memory section
        mem_label = Gtk.Label(label='RAM', xalign=0)
        mem_label.get_style_context().add_class('section')
        mem_label.get_style_context().add_class('ram-label')
        vbox.pack_start(mem_label, False, False, 0)

        (mem_total, mem_used), (swap_total, swap_used) = get_memory()
        mem_pct = int(mem_used * 100 / mem_total) if mem_total else 0

        mh = Gtk.Box(spacing=6)
        m_lbl = Gtk.Label(
            label=f'{fmt_size(mem_used)} / {fmt_size(mem_total)}',
            xalign=0
        )
        m_lbl.get_style_context().add_class(usage_class(mem_pct))
        m_pct = Gtk.Label(label=f'{mem_pct}%', xalign=0, width_chars=4)
        m_pct.get_style_context().add_class(usage_class(mem_pct))
        mh.pack_start(m_lbl, False, False, 0)
        mh.pack_start(m_pct, False, False, 0)
        vbox.pack_start(mh, False, False, 0)

        vbox.pack_start(self._make_bar(mem_pct, 250), False, False, 0)

        if swap_total > 0:
            swap_pct = int(swap_used * 100 / swap_total) if swap_total else 0

            vbox.pack_start(Gtk.Label(label=''), False, False, 0)

            swap_label = Gtk.Label(label='Swap', xalign=0)
            swap_label.get_style_context().add_class('section')
            swap_label.get_style_context().add_class('swap-label')
            vbox.pack_start(swap_label, False, False, 0)

            sh = Gtk.Box(spacing=6)
            s_lbl = Gtk.Label(
                label=f'{fmt_size(swap_used)} / {fmt_size(swap_total)}',
                xalign=0
            )
            s_lbl.get_style_context().add_class(usage_class(swap_pct))
            s_pct = Gtk.Label(label=f'{swap_pct}%', xalign=0, width_chars=4)
            s_pct.get_style_context().add_class(usage_class(swap_pct))
            sh.pack_start(s_lbl, False, False, 0)
            sh.pack_start(s_pct, False, False, 0)
            vbox.pack_start(sh, False, False, 0)

            vbox.pack_start(self._make_bar(swap_pct, 250), False, False, 0)

        self.show_all()

    def _make_bar(self, pct, width_px):
        fill = int(pct / 100 * 20)
        empty = 20 - fill
        text = '█' * fill + '░' * empty
        lbl = Gtk.Label(label=text, xalign=0)
        lbl.get_style_context().add_class(usage_class(pct))
        lbl.set_size_request(width_px, -1)
        return lbl

    def _apply_css(self):
        css = Gtk.CssProvider()
        css.load_from_data(CSS.encode())
        Gtk.StyleContext.add_provider_for_screen(
            self.get_screen(), css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def _reposition(self):
        os.system(f'hyprctl dispatch movewindowpixel '
                  f'exact {self._pos_x} {self._pos_y},title:hyper-usage-popup')
        return False

    def _on_key(self, _, event):
        if event.keyval in (Gdk.KEY_Escape, Gdk.KEY_q):
            Gtk.main_quit()


if __name__ == '__main__':
    x, y = int(sys.argv[1]), int(sys.argv[2])
    UsagePopup(x, y)
    Gtk.main()
