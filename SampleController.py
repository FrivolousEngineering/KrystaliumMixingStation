from typing import Union, Optional, List

from Action import Action
from Purity import Purity
from RefinedSample import RefinedSample
from OpposingActionController import OpposingActionController
from OpposingTargetController import OpposingTargetController
from RawSample import RawSample
from Target import Target

from Vulgarity import Vulgarity


class SampleController:
    opposingActionController = OpposingActionController()
    opposingTargetController = OpposingTargetController()

    def __init__(self):
        pass



    @staticmethod
    def createSampleFromReaderString(data: Union[str, List[str]]) -> Union[RawSample, RefinedSample]:
        """
        Create a sample from the string as provided by the RFID reader. These are the strings it provides over serial.
        """

        if isinstance(data, str):
            properties = data.split(" ")
        else:
            properties = data

        # Convert from all Uppercase to capitalized word (aka, title)
        properties = [prop.title() for prop in properties]

        # The first property defines if it's a Raw or a Refined type
        if properties[0] == "Raw":

            prop_dict = {"positive_action": properties[1], "positive_target": properties[2],
                         "negative_action": properties[3], "negative_target": properties[4]}
            vulgarity = SampleController.findVulgarityFromProperties(**prop_dict)
            sample = RawSample(**prop_dict, vulgarity=vulgarity, depleted=properties[5] != "Active")
        elif properties[0] == "Refined":
            sample = RefinedSample(primary_action=properties[1], primary_target=properties[2],
                                   secondary_action=properties[3], secondary_target=properties[4],
                                   purity=properties[6], depleted=properties[5] != "Active")


        else:
            raise ValueError("Unknown sample type")

        return sample

    @staticmethod
    def findVulgarityFromProperties(positive_action: Action, negative_action:Action, positive_target: Target, negative_target: Target, *args,
                                    **kwargs) -> Vulgarity:
        target_invariant = positive_target == negative_target
        action_invariant = positive_action == negative_action

        if target_invariant and action_invariant:
            return Vulgarity.precious

        is_action_opposing = SampleController.opposingActionController.areOpposed(positive_action, negative_action)

        is_target_opposing = SampleController.opposingTargetController.areOpposed(positive_target,
                                                                                  negative_target)

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

    @staticmethod
    def createRefinedSampleFromRawSamples(positive_sample: RawSample, negative_sample: RawSample) -> Optional[RefinedSample]:
        if positive_sample.depleted or negative_sample.depleted:
            # One (or both) of the samples provided have already been depleted. Don't return a refined sample!
            return None

        return RefinedSample(primary_action=positive_sample.positive_action,
                             primary_target=negative_sample.negative_target,
                             secondary_action=negative_sample.negative_action,
                             secondary_target=positive_sample.positive_target, depleted=False, purity=Purity.getByScore(
                Vulgarity.getScore(positive_sample.vulgarity) + Vulgarity.getScore(negative_sample.vulgarity)))
