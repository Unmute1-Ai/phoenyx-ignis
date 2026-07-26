# Recovery runbook

1. Boot trusted Ignis media in UEFI mode.
2. Connect to a known network only if recovery requires it.
3. Generate and export a Machine Twin before modifying the machine.
4. Identify and mount the EFI System Partition at `/mnt/esp`.
5. Confirm `EFI/Microsoft/Boot/bootmgfw.efi` exists.
6. Run the primitive with `--dry-run` and review its command plan.
7. Load a receipt key from separate trusted media.
8. Repeat with `--approve --receipt /var/lib/ignis/receipts/<case>.receipt.json`.
9. Verify the firmware entry with `efibootmgr -v`, unmount filesystems, and
   reboot.

Example:

```sh
mount -o ro /dev/sda1 /mnt/esp
ignis twin -o /tmp/before.json
ignis repair windows-bootmanager-entry \
  --esp /mnt/esp --disk /dev/sda --part 1 --dry-run
umount /mnt/esp
mount /dev/sda1 /mnt/esp
export IGNIS_RECEIPT_KEY_FILE=/media/key/ignis.key
ignis repair windows-bootmanager-entry \
  --esp /mnt/esp --disk /dev/sda --part 1 --approve \
  --receipt /var/lib/ignis/receipts/case-001.receipt.json
```
