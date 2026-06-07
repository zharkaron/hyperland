#!/bin/bash
eval "$(hyprctl monitors -j | jq -r '.[] | select(.focused == true) | "width=\(.width); height=\(.height); scale=\(.scale)"')"
logical_width=$(awk "BEGIN {printf \"%d\", $width / $scale}")
x=$((logical_width / 2))
y=40
exec python3 "$HOME/Projects/hyperland/waybar/calendar-popup.py" "$x" "$y" "$logical_width"
