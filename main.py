from typing import List

import time
import logging
import sys
import os
import pygame
import random

# Fuck around with the paths so that it can find the fe-RFID stuff.
current_dir = os.path.dirname(os.path.abspath(__file__))
fe_rfid_path = os.path.join(current_dir, '..', 'fe-rfid')
sys.path.insert(0, fe_rfid_path)

# Import the RFIDController from fe-rfid
from rfid import RFIDController


def onCardDetected(name: str, card_id: str):
    print(f"CARD DETECTED by reader {name}: {card_id}")


def onCardLost(name: str, card_id: str):
    print(f"CARD LOST by reader {name}: {card_id}")


def traitsDetectedCallback(name: str, traits: List[str]):
    print(f"TRAITS DETECTED by reader {name}: {traits}")


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
    sound_0_completed_event = pygame.USEREVENT + 1
    sound_1_completed_event = pygame.USEREVENT + 2
    def __init__(self):
        """
        In order to easily handle sound (and have an event loop), we use pygame
        """
        pygame.init()

        self._sound_0_list= [pygame.mixer.Sound("sounds/MagicOverlay/magic-normal.mp3"), pygame.mixer.Sound("sounds/MagicOverlay/magic-high.mp3"), pygame.mixer.Sound("sounds/MagicOverlay/magic-low.mp3"), pygame.mixer.Sound("sounds/MagicOverlay/magic-distorted.mp3")]
        self._sound_1 = pygame.mixer.Sound("sounds/magical-spinning-60410.mp3")

        self._sound_channel_0 = pygame.mixer.Channel(0)
        self._sound_channel_0.set_endevent(self.sound_0_completed_event)
        self._sound_channel_1 = pygame.mixer.Channel(1)
        self._sound_channel_1.set_endevent(self.sound_1_completed_event)

    def run(self) -> None:
        self._sound_channel_0.queue(random.choice(self._sound_0_list))
        self._sound_channel_1.queue(self._sound_1)
        while True:
            for event in pygame.event.get():
                if event.type == self.sound_0_completed_event:
                    self._sound_channel_0.queue(random.choice(self._sound_0_list))
                elif event.type == self.sound_1_completed_event:
                    self._sound_channel_1.queue(self._sound_1)

                pass
        pass


if __name__ == '__main__':
    setupLogging()

    bla = PygameWrapper()
    bla.run()
    """controller = RFIDController(on_card_detected_callback=onCardDetected,
                                on_card_lost_callback = onCardLost,
                                traits_detected_callback= traitsDetectedCallback)


    controller.start()
    # block!
    while True:
        time.sleep(0.1)"""


