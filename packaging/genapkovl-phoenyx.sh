#!/bin/sh
set -eu

hostname="${1:-phoenyx}"
source_dir="${PHOENYX_SOURCE:?PHOENYX_SOURCE is required}"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

mkdir -p \
  "$tmp/etc/apk" \
  "$tmp/etc/ignis" \
  "$tmp/etc/local.d" \
  "$tmp/etc/runlevels/default" \
  "$tmp/opt/phoenyx-ignis" \
  "$tmp/var/lib/ignis/receipts"

cat > "$tmp/etc/apk/world" <<'EOF'
alpine-base
python3
py3-pip
iwd
efibootmgr
util-linux
lsblk
iproute2
e2fsprogs
dosfstools
ntfs-3g
ca-certificates
EOF

cp -R "$source_dir/ignis" "$tmp/opt/phoenyx-ignis/"
cp "$source_dir/pyproject.toml" "$source_dir/README.md" "$source_dir/LICENSE" \
  "$tmp/opt/phoenyx-ignis/"
cp "$source_dir/packaging/policy.json" "$tmp/etc/ignis/policy.json"
cp "$source_dir/packaging/ignis.start" "$tmp/etc/local.d/ignis.start"
chmod 0755 "$tmp/etc/local.d/ignis.start"
chmod 0700 "$tmp/var/lib/ignis/receipts"
ln -s /etc/init.d/iwd "$tmp/etc/runlevels/default/iwd"
ln -s /etc/init.d/local "$tmp/etc/runlevels/default/local"

tar -C "$tmp" -czf "$hostname.apkovl.tar.gz" .
