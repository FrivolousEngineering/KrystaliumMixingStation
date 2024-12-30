from typing import List, Callable, Dict

import serial
import logging
import threading
import time

from RFIDDevice import RFIDDevice


class RFIDController:
    def __init__(self,
                 on_card_detected_callback: Callable[[str, str], None],
                 on_card_lost_callback: Callable[[str, str], None],
                 traits_detected_callback: Callable[[str, List[str]], None],
                 baud_rate=9600):
        self._baud_rate = baud_rate
        self._devices: Dict[str, RFIDDevice] = {}
        self._on_card_detected_callback = on_card_detected_callback
        self._on_card_lost_callback = on_card_lost_callback
        self._traits_detected_callback = traits_detected_callback
        self._lock = threading.Lock()
        self._startScan()

    def _startScan(self):
        threading.Thread(target=self._handleScanLoop, daemon=True).start()

    def _handleScanLoop(self):
        while True:
            logging.info("Checking for devices")
            for i in range(0, 10):
                for prefix in ["/dev/ttyUSB", "/dev/ttyACM"]:
                    port = f"{prefix}{i}"
                    if port not in self._devices:
                        try:
                            device = RFIDDevice(port, self._baud_rate,
                                                self._on_card_detected_callback,
                                                self._on_card_lost_callback,
                                                self._traits_detected_callback)
                            self._devices[port] = device
                        except Exception:
                            pass
            time.sleep(5)  # Scan every 5 seconds

    def stop(self):
        with self._lock:
            for device in self._devices.values():
                device.close()
            self._devices.clear()