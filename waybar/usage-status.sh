#!/bin/bash

prev=$(grep '^cpu ' /proc/stat)
sleep 0.1
curr=$(grep '^cpu ' /proc/stat)

prev_idle=$(echo "$prev" | awk '{print $5}')
prev_total=$(echo "$prev" | awk '{for(i=2;i<=NF;i++) t+=$i; print t}')
curr_idle=$(echo "$curr" | awk '{print $5}')
curr_total=$(echo "$curr" | awk '{for(i=2;i<=NF;i++) t+=$i; print t}')

delta_total=$((curr_total - prev_total))
delta_idle=$((curr_idle - prev_idle))
cpu=$(( (delta_total - delta_idle) * 100 / delta_total ))
[ "$cpu" -lt 0 ] && cpu=0
[ "$cpu" -gt 100 ] && cpu=100

ram=$(free | awk '/Mem/ {printf "%d", $3/$2 * 100}')

max=$(( cpu > ram ? cpu : ram ))

if   [ "$max" -lt 50 ]; then cls="low"
elif [ "$max" -lt 80 ]; then cls="medium"
else                         cls="high"
fi

echo "{\"text\":\"${cpu}% ${ram}%\",\"class\":\"${cls}\",\"tooltip\":\"CPU: ${cpu}%\\nRAM: ${ram}%\"}"
