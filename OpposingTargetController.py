from OpposingTraitController import OpposingTraitController
from Target import Target


class OpposingTargetController(OpposingTraitController):

    def __init__(self):
        super().__init__()
        self.addPair(Target.mind, Target.flesh)
        self.addPair(Target.flesh, Target.plant)
        self.addPair(Target.gas, Target.solid)
        self.addPair(Target.gas, Target.liquid)
        self.addPair(Target.liquid, Target.gas)
        self.addPair(Target.krystal, Target.energy)