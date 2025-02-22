
from enum import Enum

class Target(str, Enum):
    """
    All the targets that a sample of Krystalium can have. Each sample of raw Krystalium has two targets; One positively
    charged target and one negatively charged target.

    In the case of refined Krystalium, it no longer has negative / positive charge, only two pairs of actions & targets.
    """
    flesh: str = "Flesh"
    mind: str = "Mind"
    gas: str = "Gas"
    solid: str = "Solid"
    liquid: str = "Liquid"
    energy: str = "Energy"
    light: str = "Light"
    sound: str = "Sound"
    krystal: str = "Krystal"
    plant: str = "Plant"
