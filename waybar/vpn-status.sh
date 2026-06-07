#!/bin/bash

check_vpn() {
  if command -v mullvad &>/dev/null; then
    mullvad status | head -n1 | grep -qi "connected" && return 0
  fi
  if command -v nordvpn &>/dev/null; then
    nordvpn status | grep -qi "Status.*Connected" && return 0
  fi
  ip -br link show 2>/dev/null | grep -qE '^(wg|tun)[0-9]+' && return 0
  return 1
}

if [ "$1" = "--check" ]; then
  check_vpn
  exit $?
fi

if check_vpn; then
  echo '{"text":"","class":"connected","tooltip":"VPN connected"}'
else
  echo '{"text":"","class":"disconnected"}'
fi
