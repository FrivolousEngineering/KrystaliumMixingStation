
from pydantic import BaseModel, computed_field

from Action import Action
from Target import Target
from Vulgarity import Vulgarity

class RawSample(BaseModel):
    positive_target: Target
    negative_target: Target
    positive_action: Action
    negative_action: Action
    vulgarity: Vulgarity

    depleted: bool

    @computed_field(
        description="The numerical representation of the vulgarity. One indicates vulgar, 6 indicates precious")
    @property
    def vulgarity_score(self) -> int:
        return Vulgarity.getScore(self.vulgarity)