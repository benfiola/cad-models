from build123d import BuildPart, Vector

from cad_models.common import Model


class RB4011(Model):
    def __init__(self, **kwargs):
        # parameters
        dimensions = Vector()

        with BuildPart() as builder:
            pass

        super().__init__(builder.part, **kwargs)
