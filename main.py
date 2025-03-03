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
    error_reset = pygame.USEREVENT + 3
    bell_completed = pygame.USEREVENT + 4


    refined_depleted_error_state = 1
    left_raw_depleted_error_state = 2
    right_raw_depleted_error_state = 3

    other_error_state = 4

    ERROR_TIMEOUT = 10000  # 10 seconds  # After how many seconds should the error on voltmeter be removed?

    def __init__(self):
        """
        In order to easily handle sound (and have an event loop), we use pygame
        """
        pygame.mixer.pre_init(44100, -16, 2, 2048)
        pygame.init()

        self._overlay_sounds= [pygame.mixer.Sound("sounds/MagicOverlay/magic-normal.mp3"), pygame.mixer.Sound("sounds/MagicOverlay/magic-high.mp3"), pygame.mixer.Sound("sounds/MagicOverlay/magic-low.mp3"), pygame.mixer.Sound("sounds/MagicOverlay/magic-distorted.mp3")]
        self._drone_sound = pygame.mixer.Sound("sounds/magical-spinning-fixed.mp3")
        self._final_bell_sound = pygame.mixer.Sound("sounds/final_bell.mp3")

        self._error_sounds = [pygame.mixer.Sound("sounds/clank1.mp3"), pygame.mixer.Sound("sounds/clank2.mp3"), pygame.mixer.Sound("sounds/clank3.mp3")]

        self._overlay_sounds_count = 0

        self._overlay_sound_channel = pygame.mixer.Channel(0)
        self._overlay_sound_channel.set_endevent(self.overlay_sound_completed)
        self._drone_sound_channel = pygame.mixer.Channel(1)
        self._overlay_sound_channel.set_volume(0.2)
        self._drone_sound_channel.set_endevent(self.drone_completed)

        self._final_bell_channel = pygame.mixer.Channel(2)
        self._final_bell_channel.set_endevent(self.bell_completed)

        self._error_channel = pygame.mixer.Channel(3)
        self._device_controller = RFIDController(on_card_detected_callback=onCardDetected,
                                    on_card_lost_callback=self.onCardLost,
                                    traits_detected_callback=self.traitsDetectedCallback)

        '''self._left_sample = SampleController.createSampleFromReaderString("RAW RELEASING SOLID ABSORBING GAS ACTIVE")
        self._right_sample = SampleController.createSampleFromReaderString("RAW HEATING FLESH COOLING MIND ACTIVE")'''
        self._left_sample = None
        self._right_sample = None
        self._front_sample = None

        self._is_mixing = False  # Is the mixing station doing it's thing (eg lights & sound are on)
        self._sample_to_write = None

    def setErrorState(self, error_state: int):
        light_device = self._device_controller.getDeviceByName("LIGHT")
        volt = error_state * 45

        if light_device:
            light_device.sendRawCommand(f"VOLT {volt}")
            logging.info(f"Setting error state to {volt}")
        if error_state > 0:
            self._error_channel.play(random.choice(self._error_sounds))
            if error_state == self.refined_depleted_error_state:
                light_device.sendRawCommand(f"ERROR BOTH")
            elif error_state == self.right_raw_depleted_error_state:
                light_device.sendRawCommand(f"ERROR RIGHT")
            elif error_state == self.left_raw_depleted_error_state:
                light_device.sendRawCommand("ERROR LEFT")
            self._triggerEvent(self.error_reset, self.ERROR_TIMEOUT)

    def startMixingProcess(self):
        if self._is_mixing:
            logging.info("Mixing is already happening. Cant start twice")
            return

        errors = []
        error_state = None
        # Ensure that all the samples are set!
        if self._left_sample is None:
            errors.append("Left sample is missing")
            error_state = self.other_error_state
        if self._right_sample is None:
            errors.append("Right sample is missing")
            error_state = self.other_error_state
        if self._front_sample is None:
            errors.append("Front sample is missing")
            error_state = self.other_error_state

        if not isinstance(self._left_sample, RawSample):
            errors.append("Left sample is not of type RawSample")
            error_state = self.other_error_state
        if not isinstance(self._right_sample, RawSample):
            errors.append("Right sample is not of type RawSample")
            error_state = self.other_error_state
        if not isinstance(self._front_sample, RefinedSample):
            errors.append("Front sample is not of type RefinedSample")
            error_state = self.other_error_state

        if self._left_sample and self._left_sample.depleted:
            errors.append("Left sample is depleted")
            error_state = self.left_raw_depleted_error_state
        if self._right_sample and self._right_sample.depleted:
            errors.append("Right sample is depleted")
            error_state = self.right_raw_depleted_error_state
        if self._front_sample and not self._front_sample.depleted:
            errors.append("Front sample isn't depleted")
            error_state = self.refined_depleted_error_state

        left_device = self._device_controller.getDeviceByName("LEFT")
        right_device = self._device_controller.getDeviceByName("RIGHT")
        front_device = self._device_controller.getDeviceByName("FRONT")

        if not left_device:
            errors.append("Could not find RFID reader on left")
            error_state = self.other_error_state
        if not right_device:
            errors.append("Could not find RFID reader on right")
            error_state = self.other_error_state
        if not front_device:
            errors.append("Could not find RFID reader on front")
            error_state = self.other_error_state

        if error_state is not None:
            self.setErrorState(error_state)

        if errors:
            logging.warning(f"Not starting mixing because of errors: {errors}")
            return

        # Everything should be good! Whooo
        self._sample_to_write = SampleController.createRefinedSampleFromRawSamples(self._left_sample, self._right_sample)
        self.markSampleAsDepleted("RIGHT")
        self.markSampleAsDepleted("LEFT")

        # Start the light effects
        light_device = self._device_controller.getDeviceByName("LIGHT")
        light_device.sendRawCommand("LIGHT ON 33000")
        self.startSounds()
        self._is_mixing = True


    def _lightCallback(self, line: str):
        if line.startswith("SWITCH: "):
            # The arm just changed state.
            if "down" in line:
                self.startMixingProcess()

    @staticmethod
    def _triggerEvent(event_type, min_time: int, max_time: int = 0) -> None:
        """
        Trigger an event for the pygame loop
        :param event_type:
        :param min_time: The minimum time it should take for this to be triggered.
        :param max_time: The max time that this event should be triggered in. If left to 0, no randomness is aplied and
                            the min_time is leading
        :return:
        """
        time_to_use = random.randint(min_time, max_time) if max_time != 0 else min_time
        pygame.time.set_timer(event_type, time_to_use, loops=1)


    def markSampleAsDepleted(self, reader_name: str):
        """
        This function marks a sample that is on the reader (as defined by reader name) as depleted.
        This will write some data to the tag
        """
        device = self._device_controller.getDeviceByName(reader_name)
        if device:
            device.sendRawCommand("DEPLETESAMPLE")
        else:
            logging.warning(f"Failed to mark sample as depleted for reader {reader_name}")

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

        light_device = self._device_controller.getDeviceByName("LIGHT")

        if name == "LEFT":
            self._left_sample = found_sample
            if light_device:
                if self._left_sample.depleted:
                    self.setErrorState(self.left_raw_depleted_error_state)
                else:
                    light_device.sendRawCommand("FLASH LEFT")
            if self._front_sample is None:
                light_device.sendRawCommand("ERROR LEFT")
                self._error_channel.play(random.choice(self._error_sounds))

            else:
                if not isinstance(self._left_sample, RawSample):
                    light_device.sendRawCommand("ERROR RIGHT")
                    self._error_channel.play(random.choice(self._error_sounds))
                elif self._right_sample is not None:
                    self.startMixingProcess()
        elif name == "RIGHT":
            self._right_sample = found_sample
            if light_device:
                if self._right_sample.depleted:
                    self.setErrorState(self.right_raw_depleted_error_state)
                else:
                    light_device.sendRawCommand("FLASH RIGHT")
                if self._front_sample is None:
                    light_device.sendRawCommand("ERROR RIGHT")
                    self._error_channel.play(random.choice(self._error_sounds))
                else:
                    if not isinstance(self._right_sample, RawSample):
                        light_device.sendRawCommand("ERROR RIGHT")
                        self._error_channel.play(random.choice(self._error_sounds))
                    elif self._left_sample is not None:
                        self.startMixingProcess()
        elif name == "FRONT":
            self._front_sample = found_sample
            if (self._left_sample is not None or self._right_sample is not None) and not self._is_mixing:
                light_device.sendRawCommand("ERROR BOTH")
                self.setErrorState(4)
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
                    device.setCustomResponseCallback(self._lightCallback)
                    self.setErrorState(0)
                    # Send a command so that we know stuff has booted
                    device.sendRawCommand("LIGHT ON 1000")

            for event in pygame.event.get():
                if event.type == self.overlay_sound_completed:
                    self._overlay_sounds_count += 1
                    # Okok, this is a bit nasty. But the overlay sounds are 5 sec each and the drone clip is 36...
                    if self._overlay_sounds_count < 8:
                        self._overlay_sound_channel.play(random.choice(self._overlay_sounds))
                if event.type == self.drone_completed:
                    # Mixing has completed!
                    self._overlay_sounds_count = 0


                    trait_list = [self._sample_to_write.primary_action, self._sample_to_write.primary_target, self._sample_to_write.secondary_action,
                                  self._sample_to_write.secondary_target, self._sample_to_write.purity]

                    trait_list = [str(trait.value).upper() for trait in trait_list]
                    logging.info(f"WRITING! {trait_list}")
                    front_device = self._device_controller.getDeviceByName("FRONT")
                    front_device.writeSample("REFINED", trait_list)
                    self._sample_to_write = None
                    # Play PING sound
                    self._final_bell_channel.play(self._final_bell_sound)

                if event.type == self.error_reset:
                    self.setErrorState(0)

                if event.type == self.bell_completed:
                    self._is_mixing = False



if __name__ == '__main__':
    setupLogging()

    bla = PygameWrapper()
    bla.run()
    """


    controller.start()
    # block!
    while True:
        time.sleep(0.1)"""


