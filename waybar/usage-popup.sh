#!/bin/bash
cursor=$(hyprctl cursorpos)
x=$(echo "$cursor" | cut -d, -f1)
y=$(echo "$cursor" | cut -d, -f2)
y=$((y + 5))
exec python3 "$HOME/Projects/hyperland/waybar/usage-popup.py" "$x" "$y"
