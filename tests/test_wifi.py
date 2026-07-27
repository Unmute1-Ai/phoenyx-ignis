from ignis.wifi import WifiManager

from .fakes import FakeRunner


def test_connect_passes_credentials_as_arguments_without_shell():
    runner = FakeRunner()
    manager = WifiManager(runner)
    manager.connect("Recovery Net", device="wlan0", passphrase="correct horse")
    assert runner.calls == [
        (
            "iwctl",
            "--dont-ask",
            "--passphrase",
            "correct horse",
            "station",
            "wlan0",
            "connect",
            "Recovery Net",
        )
    ]


def test_devices_parses_iwctl_table():
    runner = FakeRunner(
        {("iwctl", "device", "list"): "Name          Mode\nwlan0        station\n"}
    )
    assert WifiManager(runner).devices() == ["wlan0"]
