#!/bin/bash

eval "$(hyprctl monitors -j | jq -r '.[] | select(.focused == true) | "width=\(.width); scale=\(.scale)"')"
logical_width=$(awk "BEGIN {printf \"%d\", $width / $scale}")
x=$((logical_width - 175))
y=35

exec "$HOME/Projects/hyperland/waybar/power-menu.py" "$x" "$y"
