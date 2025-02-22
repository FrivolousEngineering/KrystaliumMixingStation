from enum import Enum

class Action(str, Enum):
    """
    All the actions that a sample of Krystalium can have. Each sample of raw Krystalium has two actions;
    One positively charged action and one negatively charged action.

    In the case of refined Krystalium, it no longer has negative / positive charge, only two pairs of actions & targets.
    """
    expanding: str = "Expanding"
    contracting: str = "Contracting"
    conducting: str = "Conducting"
    insulating: str = "Insulating"
    deteriorating: str = "Deteriorating"
    creating: str = "Creating"
    destroying: str = "Destroying"
    increasing: str = "Increasing"
    decreasing: str = "Decreasing"
    absorbing: str = "Absorbing"
    releasing: str = "Releasing"
    solidifying: str = "Solidifying"
    lightening: str = "Lightening"
    encumbering: str = "Encumbering"
    fortifying: str = "Fortifying"
    heating: str = "Heating"
    cooling: str = "Cooling"