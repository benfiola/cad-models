from cad_models.common import main
from cad_models.models.thinkcentre_bracket import ThinkcentreBracket


class ThinkcentreBracketPower(ThinkcentreBracket):
    def __init__(self, **kwargs):
        super().__init__(
            flipped_joints=True, keystone_receivers=False, power_supply_tray=True
        )


if __name__ == "__main__":
    main(ThinkcentreBracketPower())
