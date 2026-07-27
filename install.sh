#!/bin/sh
set -eu

if [ "$(id -u)" -ne 0 ]; then
  echo "install.sh must run as root" >&2
  exit 1
fi

apk add --no-cache \
  python3~3.12 py3-pip iwd efibootmgr util-linux lsblk iproute2 e2fsprogs \
  dosfstools ntfs-3g

python3 -m pip install --break-system-packages --no-deps .
rc-update add iwd default
rc-service iwd start 2>/dev/null || true

install -d -m 0700 /var/lib/ignis/receipts
echo "Phoenyx Ignis installed. Run: ignis --help"
