from typing import Union

from enum import Enum

class Purity(str, Enum):
    """
    Purity is calculated relatively simply. As we have 6 steps of vulgarity, we simply give precious a score of 6
    and vulgar a score of 1. We then just combine the score of both samples to find out the purity of the sample
    """

    polluted = "Polluted"
    tarnished = "Tarnished"
    dirty = "Dirty"
    blemished = "Blemished"
    impure = "Impure"
    unblemished = "Unblemished"
    lucid = "Lucid"
    stainless = "Stainless"
    pristine = "Pristine"
    immaculate = "Immaculate"
    perfect = "Perfect"

    @staticmethod
    def getScore(purity: Union["Purity", str]) -> int:
        return list(Purity).index(purity) + 2

    @staticmethod
    def getByScore(score: int) -> "Purity":
        return list(Purity)[score - 2]
