from typing import Union

from enum import Enum

class Vulgarity(str, Enum):
    """
    Vulgarity defines how stable a Krystalium sample is, with precious being most stable and vulgar being the least stable.

    When two traits (action or target) are the same, we call this 'invariant'.

    When two traits (action or target) are somewhat related (mind vs body, solid vs gas) we call it opposing. This is
    less stable than invariant, but more stable than conflicted.

    When two traits (action or target) are not related (not opposing and not the same), we call this conflicted.

    When both pairs are invariant, the substance is precious.
    When one of the pairs is invariant, it's semi-precious. High semi-precious have the other pair opposing, low has
    the other pair conflicting

    When all pairs are conflicting, it's vulgar.

    When there are no invariants, but one or two opposing, it's mundane (two opposing being high, one low)
    """
    vulgar = "Vulgar"
    low_mundane = "Low Mundane"
    high_mundane = "High Mundane"
    low_semi_precious = "Low Semi-Precious"
    high_semi_precious = "High Semi-Precious"
    precious = "Precious"

    @staticmethod
    def getScore(vulgarity: Union["Vulgarity", str]) -> int:
        return list(Vulgarity).index(vulgarity) + 1

    @staticmethod
    def getByScore(score: int) -> "Vulgarity":
        return list(Vulgarity)[score - 1]
