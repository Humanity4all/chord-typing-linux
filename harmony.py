"""Chord typing emulation for Linux."""
import sys
import yaml
import evdev
from asyncore import file_dispatcher, loop
from daemon import Daemon
from colorlog import log, LOGLEVEL
from switchboard import SwitchBoard

# pylint: disable=invalid-name
CONFIG = {}
with open('harmony_keymap.yml') as f:
    CONFIG = yaml.safe_load(f.read())

LOGLEVEL.set_level(CONFIG['config']['log_level'])
SWITCHBOARD = SwitchBoard(CONFIG)


def process_event(event, config=CONFIG):
    """Take even through translation chain."""
    # TODO forward events that aren't relevant to the chord translation
    chord_events = SWITCHBOARD.process_event(event)
    for event in chord_events:
        # TODO: translate chord event into key event
        pass


class InputDeviceDispatcher(file_dispatcher):

    """Asynchronous device dispatcher."""

    def __init__(self, device):
        """Store device."""
        self.device = device
        file_dispatcher.__init__(self, device)

    def recv(self, _):
        """Read device."""
        return self.device.read()

    def handle_read(self):
        """Dispatch event."""
        for event in self.recv():
            process_event(event)


class Harmony(Daemon):

    """Chord typing emulation daemon."""

    def run(self, config=CONFIG):
        """Setup and teardown."""
        # TODO: see if user indicated which device(s) to grab
        # for now, just grab anything that looks remotely like a keyboard
        all_devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]
        self.devices = []
        for device in all_devices:
            if "Keyboard" in device.name or "HID" in device.name:
                self.devices.append(device)
                device.grab()
                InputDeviceDispatcher(device)
        loop()

    def stop(self):
        """Teardown."""
        for device in self.devices:
            device.ungrab()
        Daemon.stop(self)

if __name__ == "__main__":
    daemon = Harmony(CONFIG['config']['pid_file'])
    if len(sys.argv) == 2:
        if sys.argv[1] == "start":
            log("info", "Starting Harmony")
            daemon.start()
        elif sys.argv[1] == "stop":
            log("info", "Stopping Harmony")
            daemon.stop()
        elif sys.argv[1] == "restart":
            log("info", "Restarting Harmony")
            daemon.restart()
        else:
            log("fail", "Unknown command")
            sys.exit(2)
        sys.exit(0)
    else:
        log("info", "Usage %s start|stop|restart" % sys.argv[0])
        sys.exit(2)
