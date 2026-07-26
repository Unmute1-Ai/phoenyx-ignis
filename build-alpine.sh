#!/bin/sh
set -eu

if [ "$(id -u)" -ne 0 ]; then
  echo "build-alpine.sh must run as root" >&2
  exit 1
fi
if ! command -v apk >/dev/null 2>&1; then
  echo "build-alpine.sh must run on Alpine Linux" >&2
  exit 1
fi

ALPINE_VERSION="${ALPINE_VERSION:-3.20}"
ALPINE_MIRROR="${ALPINE_MIRROR:-https://dl-cdn.alpinelinux.org/alpine}"
TARGET_ARCH="${TARGET_ARCH:-$(apk --print-arch)}"
ROOTFS="${ROOTFS:-$PWD/rootfs}"
DIST="${DIST:-$PWD/dist}"

case "$ROOTFS" in
  "$PWD"/*) ;;
  *) echo "ROOTFS must be inside the project directory" >&2; exit 1 ;;
esac

mkdir -p "$ROOTFS" "$DIST"
apk --root "$ROOTFS" --arch "$TARGET_ARCH" --initdb \
  --repository "$ALPINE_MIRROR/v$ALPINE_VERSION/main" \
  --repository "$ALPINE_MIRROR/v$ALPINE_VERSION/community" \
  add alpine-base python3~3.12 py3-pip iwd efibootmgr util-linux lsblk iproute2 \
  e2fsprogs dosfstools ntfs-3g ca-certificates

mkdir -p "$ROOTFS/opt/phoenyx-ignis" "$ROOTFS/etc/ignis" "$ROOTFS/var/lib/ignis/receipts"
cp -R ignis pyproject.toml README.md LICENSE "$ROOTFS/opt/phoenyx-ignis/"
chroot "$ROOTFS" python3 -m pip install --break-system-packages --no-deps /opt/phoenyx-ignis
cat > "$ROOTFS/etc/ignis/policy.json" <<'EOF'
{
  "allowed_primitives": ["repair.windows.bootmanager_entry"],
  "require_approval": true,
  "constraints": {
    "repair.windows.bootmanager_entry": {"require_uefi": true}
  }
}
EOF

chmod 0700 "$ROOTFS/var/lib/ignis/receipts"
tar -C "$ROOTFS" -czf "$DIST/phoenyx-ignis-$ALPINE_VERSION-$TARGET_ARCH.tar.gz" .
sha256sum "$DIST/phoenyx-ignis-$ALPINE_VERSION-$TARGET_ARCH.tar.gz" \
  > "$DIST/phoenyx-ignis-$ALPINE_VERSION-$TARGET_ARCH.tar.gz.sha256"
echo "Built $DIST/phoenyx-ignis-$ALPINE_VERSION-$TARGET_ARCH.tar.gz"
