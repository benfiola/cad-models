from cad_models.common import main
from cad_models.models.generic_blank import GenericBlank


class GenericBlankCaptive(GenericBlank):
    def __init__(self, **kwargs):
        kwargs["interface_hole_captive_nut"] = True
        super().__init__(**kwargs)


if __name__ == "__main__":
    main(GenericBlankCaptive())
