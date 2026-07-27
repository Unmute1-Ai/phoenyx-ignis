profile_phoenyx() {
	profile_standard
	profile_abbrev="phoenyx"
	title="Phoenyx Ignis"
	desc="Policy-controlled Alpine Linux recovery environment"
	hostname="phoenyx"
	apks="$apks python3 py3-pip iwd efibootmgr util-linux lsblk iproute2
		e2fsprogs dosfstools ntfs-3g ca-certificates"
	apkovl="genapkovl-phoenyx.sh"
}
