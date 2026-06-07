#!/bin/bash

active_ws=$(hyprctl activeworkspace -j 2>/dev/null | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")

clients=$(hyprctl clients -j 2>/dev/null)

icons=$(echo "$clients" | python3 -c "
import sys, json

ICON_MAP = {
    'firefox': '',
    'kitty': '',
    'Alacritty': '',
    'Code': '',
    'discord': '',
    'org.gnome.Nautilus': '',
    'org.gnome.Settings': '',
    'spotify': '',
    'vlc': '嗢',
    'pavucontrol': '',
    'blueman-manager': '',
    'org.gnome.Calculator': '',
    'evince': '',
}

ws_id = int(sys.argv[1])
clients = json.load(sys.stdin)
seen = set()
icons_list = []
for c in clients:
    if c.get('workspace', {}).get('id') == ws_id:
        cls = c.get('class', '')
        icon = ICON_MAP.get(cls, '')
        if icon not in seen:
            seen.add(icon)
            icons_list.append(icon)

print(' '.join(icons_list))
" "$active_ws")

text="$icons"

if [ -z "$text" ]; then
  echo '{"text":"","class":"empty"}'
else
  echo "{\"text\":\"$text\",\"class\":\"active\"}"
fi
