
from OpposingActionController import OpposingActionController
from OpposingTargetController import OpposingTargetController

from Vulgarity import Vulgarity


class SampleController:
    opposingActionController = OpposingActionController()
    opposingTargetController = OpposingTargetController()

    def __init__(self):
        pass


    @staticmethod
    def findVulgarityFromProperties(positive_action, negative_action, positive_target, negative_target, *args,
                                    **kwargs) -> Vulgarity:
        target_invariant = positive_target == negative_target
        action_invariant = positive_action == negative_action

        if target_invariant and action_invariant:
            return Vulgarity.precious

        is_action_opposing = SampleController.opposingActionController.areOpposed(positive_action, negative_action)

        is_target_opposing = SampleController.opposingTargetController.areOpposed(positive_target.value, negative_target)

        if target_invariant or action_invariant:
            # It's semi-precious, but now to figure out if it's high or low!
            if target_invariant:
                return Vulgarity.high_semi_precious if is_action_opposing else Vulgarity.low_semi_precious
            else:
                return Vulgarity.high_semi_precious if is_target_opposing else Vulgarity.low_semi_precious

        if not is_action_opposing and not is_target_opposing:
            return Vulgarity.vulgar

        # Now to find out if it's high or low mundane
        if is_action_opposing and is_target_opposing:
            return Vulgarity.high_mundane

        # Only one left, so it's low mundane
        return Vulgarity.low_mundane