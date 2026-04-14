import copy
from typing import ClassVar

from build123d import (
    Align,
    Axis,
    BasePartObject,
    BuildPart,
    Location,
    Mode,
    Part,
    RigidJoint,
    RotationLike,
    Solid,
    import_step,
)

from cad_models.data import get_data_file


def ensure_part(part: Part | None) -> Part:
    if not part:
        raise ValueError("part is None")
    return part


class KeystoneReceiver(BasePartObject):
    _applies_to = [BuildPart._tag]
    _solid: ClassVar[Solid | None] = None

    @classmethod
    def get_solid(cls) -> Solid:
        if not cls._solid:
            step_file = get_data_file("keystone-receiver.step")
            solid = import_step(step_file)
            if not isinstance(solid, Solid):
                raise TypeError(solid)
            cls._solid = solid
        return copy.copy(cls._solid)

    @classmethod
    def depth(cls) -> float:
        with BuildPart(mode=Mode.PRIVATE):
            return cls.get_solid().bounding_box().size.Y

    @classmethod
    def height(cls) -> float:
        with BuildPart(mode=Mode.PRIVATE):
            return cls.get_solid().bounding_box().size.Z

    @classmethod
    def width(cls) -> float:
        with BuildPart(mode=Mode.PRIVATE):
            return cls.get_solid().bounding_box().size.X

    def __init__(
        self,
        rotation: RotationLike | tuple[float, float, float] = (0, 0, 0),
        align: Align | tuple[Align, Align, Align] | None = (
            Align.CENTER,
            Align.CENTER,
            Align.CENTER,
        ),
        mode: Mode = Mode.ADD,
    ):
        solid = self.get_solid()
        super().__init__(solid, rotation, align, mode)
        face = solid.faces().filter_by(Axis.Y).sort_by(Axis.Y)[0]
        joint_location = Location(face.location_at(0.5, 0.5).position, (0, 0, 0))
        RigidJoint("joint", self, joint_location)
