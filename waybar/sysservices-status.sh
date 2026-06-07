#!/bin/bash

running=$(systemctl list-units --type=service --state=running --no-pager --plain 2>/dev/null \
  | grep '\.service' | awk '{print $1}' | sed 's/\.service$//')

skip_patterns="systemd- dbus- polkit accounts-daemon alsa-state atd auditd avahi-daemon chronyd colord crond gdm gssproxy irqbalance mcelog ModemManager rtkit-daemon smartd switcheroo-control thermald tuned udisks2 upower uresourced user@ wpa_supplicant abrt rsyslog"

result=""
for svc in $running; do
  skip=0
  for p in $skip_patterns; do
    case "$svc" in
      $p*) skip=1; break ;;
    esac
  done
  [ "$svc" = "NetworkManager" ] && skip=1
  [ "$svc" = "bluetooth" ] && skip=1
  if [ "$skip" = 0 ]; then
    result+="$svc "
  fi
done

if [ -n "$result" ]; then
  echo "{\"text\":\"$result\",\"class\":\"active\",\"tooltip\":\"Services: $(echo "$running" | tr '\n' ' ')\"}"
else
  echo '{"text":"","class":"inactive"}'
fi
