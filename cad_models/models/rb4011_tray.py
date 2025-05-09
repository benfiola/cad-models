from build123d import BuildPart, BuildSketch

from cad_models.common import Model, main


class RB4011Tray(Model):
    def __init__(self, **kwargs):
        with BuildPart() as builder:
            with BuildSketch():
                pass

        super().__init__(builder.part, **kwargs)


if __name__ == "__main__":
    main(RB4011Tray())
