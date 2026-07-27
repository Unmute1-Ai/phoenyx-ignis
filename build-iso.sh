#!/bin/sh
set -eu

[ "$(id -u)" -eq 0 ] || {
  echo "build-iso.sh must run as root" >&2
  exit 1
}
command -v apk >/dev/null 2>&1 || {
  echo "build-iso.sh must run on Alpine Linux" >&2
  exit 1
}

ALPINE_BRANCH="${ALPINE_BRANCH:-3.20-stable}"
ALPINE_VERSION="${ALPINE_VERSION:-3.20}"
ALPINE_MIRROR="${ALPINE_MIRROR:-https://dl-cdn.alpinelinux.org/alpine}"
TARGET_ARCH="${TARGET_ARCH:-x86_64}"
WORK_DIR="${WORK_DIR:-$PWD/.iso-work}"
DIST="${DIST:-$PWD/dist}"
APORTS_DIR="$WORK_DIR/aports"

case "$WORK_DIR" in
  "$PWD"/*) ;;
  *) echo "WORK_DIR must be inside the project directory" >&2; exit 1 ;;
esac

apk add --no-cache alpine-sdk alpine-conf syslinux xorriso squashfs-tools \
  grub grub-efi mtools git
mkdir -p "$WORK_DIR" "$DIST"

if ! find /root/.abuild -name '*.rsa' -print -quit 2>/dev/null | grep -q .; then
  abuild-keygen -a -n
  cp /root/.abuild/*.rsa.pub /etc/apk/keys/
fi

if [ ! -d "$APORTS_DIR/.git" ]; then
  git clone --depth 1 --branch "$ALPINE_BRANCH" \
    https://gitlab.alpinelinux.org/alpine/aports.git "$APORTS_DIR"
fi
git -C "$APORTS_DIR" fetch --force --tags

cp packaging/mkimg.phoenyx.sh "$APORTS_DIR/scripts/"
cp packaging/genapkovl-phoenyx.sh "$APORTS_DIR/scripts/"
chmod 0755 "$APORTS_DIR/scripts/genapkovl-phoenyx.sh"

PHOENYX_SOURCE="$PWD" sh "$APORTS_DIR/scripts/mkimage.sh" \
  --tag "v$ALPINE_VERSION" \
  --outdir "$DIST" \
  --workdir "$WORK_DIR/cache" \
  --arch "$TARGET_ARCH" \
  --repository "$ALPINE_MIRROR/v$ALPINE_VERSION/main" \
  --repository "$ALPINE_MIRROR/v$ALPINE_VERSION/community" \
  --profile phoenyx

iso="$(find "$DIST" -maxdepth 1 -name '*phoenyx*.iso' -print | head -n 1)"
[ -n "$iso" ] || {
  echo "mkimage completed without producing a Phoenyx ISO" >&2
  exit 1
}
sha256sum "$iso" > "$iso.sha256"
echo "Built $iso"
