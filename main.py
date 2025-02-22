from typing import List

from RFIDController import RFIDController
import time
import logging
import sys

from SampleController import SampleController


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


if __name__ == '__main__':
    setupLogging()


    sampleController = SampleController()
    print(sampleController.createSampleFromReaderString("REFINED EXPANDING LIGHT EXPANDING LIGHT TARNISHED ACTIVE"))

    '''controller = RFIDController(on_card_detected_callback=onCardDetected,
                                on_card_lost_callback = onCardLost,
                                traits_detected_callback= traitsDetectedCallback)'''


    #controller.start()
    # block!
    #while True:
    #    time.sleep(0.1)
