#!/bin/bash

bluetooth_on() {
  systemctl is-active bluetooth &>/dev/null || return 1
  ! rfkill list bluetooth 2>/dev/null | grep -q "Soft blocked: yes" || return 1
  return 0
}

if [ "$1" = "--check" ]; then
  bluetooth_on
  exit $?
fi

if bluetooth_on; then
  connected=$(bluetoothctl devices Connected 2>/dev/null | wc -l)
  if [ "$connected" -gt 0 ]; then
    echo "{\"text\":\"${connected}\",\"class\":\"connected\",\"tooltip\":\"${connected} device(s) connected\"}"
  else
    echo '{"text":"","class":"on","tooltip":"Bluetooth on"}'
  fi
else
  echo '{"text":"","class":"off"}'
fi
