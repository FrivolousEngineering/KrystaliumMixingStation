from typing import List

import logging
import sys
import os
import pygame
import random

from RawSample import RawSample
from RefinedSample import RefinedSample
from SampleController import SampleController

# Fuck around with the paths so that it can find the fe-RFID stuff.
current_dir = os.path.dirname(os.path.abspath(__file__))
fe_rfid_path = os.path.join(current_dir, '..', 'fe-rfid')
sys.path.insert(0, fe_rfid_path)

# Import the RFIDController from fe-rfid
from rfid import RFIDController


def onCardDetected(name: str, card_id: str):
    print(f"CARD DETECTED by reader {name}: {card_id}")







def setupLogging() -> None:
    root = logging.getLogger()

    # Kick out the default handler (if any!)
    if root.handlers:
        root.removeHandler(root.handlers[0])

    root.setLevel(logging.DEBUG)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    root.addHandler(handler)


class PygameWrapper:
    overlay_sound_completed = pygame.USEREVENT + 1
    drone_completed = pygame.USEREVENT + 2
    def __init__(self):
        """
        In order to easily handle sound (and have an event loop), we use pygame
        """
        pygame.mixer.pre_init(44100, -16, 2, 2048)
        pygame.init()

        self._overlay_sounds= [pygame.mixer.Sound("sounds/MagicOverlay/magic-normal.mp3"), pygame.mixer.Sound("sounds/MagicOverlay/magic-high.mp3"), pygame.mixer.Sound("sounds/MagicOverlay/magic-low.mp3"), pygame.mixer.Sound("sounds/MagicOverlay/magic-distorted.mp3")]
        self._drone_sound = pygame.mixer.Sound("sounds/magical-spinning-fixed.mp3")

        self._overlay_sounds_count = 0

        self._overlay_sound_channel = pygame.mixer.Channel(0)
        self._overlay_sound_channel.set_endevent(self.overlay_sound_completed)
        self._drone_sound_channel = pygame.mixer.Channel(1)
        self._overlay_sound_channel.set_volume(0.2)
        self._drone_sound_channel.set_endevent(self.drone_completed)
        self._device_controller = RFIDController(on_card_detected_callback=onCardDetected,
                                    on_card_lost_callback=self.onCardLost,
                                    traits_detected_callback=self.traitsDetectedCallback)

        self._left_sample = None
        self._right_sample = None
        self._front_sample = None

    def onCardLost(self, name: str, card_id: str):
        logging.info(f"Card lost by reader {name}")
        if name == "LEFT":
            self._left_sample = None
        elif name == "RIGHT":
            self._right_sample = None
        elif name == "FRONT":
            self._front_sample = None
        else:
            logging.warning(f"Got a reader with a weird name (lost): {name}")

    def traitsDetectedCallback(self, name: str, traits: List[str]):
        try:
            found_sample = SampleController.createSampleFromReaderString(traits)
        except:
            logging.error(f"Something went wrong parsing the sample with traits {traits} on reader {name}")
            return

        logging.info(f"Reader {name} found sample {found_sample}")

        if name == "LEFT":
            self._left_sample = found_sample
        elif name == "RIGHT":
            self._right_sample = found_sample
        elif name == "FRONT":
            self._front_sample = found_sample
        else:
            logging.warning(f"Got a reader with a weird name: {name}")


    def startSounds(self):
        self._overlay_sound_channel.play(random.choice(self._overlay_sounds), fade_ms= 10000)
        self._drone_sound_channel.play(self._drone_sound)

    def run(self) -> None:
        self._device_controller.start()

        found_lights = False
        while True:
            if not found_lights:
                device = self._device_controller.getDeviceByName("LIGHT")
                if device:
                    found_lights = True
                    # Since there is some time in the fadeout, we tell it to stop before the end of the soundfile
                    device.sendRawCommand("LIGHT ON 33000")
                    self.startSounds()
            for event in pygame.event.get():
                if event.type == self.overlay_sound_completed:
                    self._overlay_sounds_count += 1
                    # Okok, this is a bit nasty. But the overlay sounds are 5 sec each and the drone clip is 36...
                    if self._overlay_sounds_count < 8:
                        self._overlay_sound_channel.play(random.choice(self._overlay_sounds))
                if event.type == self.drone_completed:
                    # Reset the overlay sound count again
                    self._overlay_sounds_count = 0


if __name__ == '__main__':
    setupLogging()

    bla = PygameWrapper()
    bla.run()
    """


    controller.start()
    # block!
    while True:
        time.sleep(0.1)"""


