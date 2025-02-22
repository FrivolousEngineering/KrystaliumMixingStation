from Action import Action
from OpposingTraitController import OpposingTraitController


class OpposingActionController(OpposingTraitController):
    def __init__(self):
        super().__init__()
        self.addPair(Action.expanding, Action.contracting)
        self.addPair(Action.conducting, Action.insulating)
        self.addPair(Action.fortifying, Action.deteriorating)
        self.addPair(Action.creating, Action.destroying)
        self.addPair(Action.increasing, Action.decreasing)
        self.addPair(Action.absorbing, Action.releasing)
        self.addPair(Action.heating, Action.cooling)
        self.addPair(Action.solidifying, Action.lightening)
        self.addPair(Action.lightening, Action.encumbering)