from ignis.twin import MachineTwinGenerator

from .fakes import FakeRunner


def test_machine_twin_uses_structured_command_data():
    runner = FakeRunner(
        {
            (
                "lsblk",
                "--json",
                "--output",
                "NAME,PATH,TYPE,SIZE,FSTYPE,LABEL,UUID,MOUNTPOINTS",
            ): '{"blockdevices":[{"name":"sda"}]}',
            ("ip", "-json", "address"): '[{"ifname":"lo"}]',
        }
    )
    twin = MachineTwinGenerator(runner).generate()
    assert twin["schema"].endswith("/v1")
    assert twin["block_devices"] == [{"name": "sda"}]
    assert twin["network"] == [{"ifname": "lo"}]
