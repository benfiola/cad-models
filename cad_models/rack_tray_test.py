from build123d import *

from cad_models.common import *


class Device:
    p: "Parameters"
    height: float
    width: float
    depth: float

    def tray(self) -> Part:
        raise NotImplementedError()

    def panel(self) -> Sketch:
        raise NotImplementedError()


@dataclass
class Parameters:
    device: Device
    mount_width: float = 252 * MM
    mount_height: float = 1 * U
    mount_thickness: float = 5 * MM
    rack_width: float = 222 * MM

    def __post_init__(self):
        self.device.p = self


class HueBridge(Device):
    width = 90 * MM + 1.0 * MM
    height = 26.5 * MM
    depth = 90 * MM + 1.0 * MM
    outer_fillet_radius = 24 * MM
    tray_lip = 2 * MM

    @property
    def outer_width(self):
        return self.width + (self.p.mount_thickness * 2)

    @property
    def outer_depth(self):
        return self.depth + (self.p.mount_thickness * 2)

    @property
    def outer_height(self):
        return self.height + self.p.mount_thickness

    @property
    def inner_height(self):
        return self.height + self.tray_lip

    @property
    def inner_fillet_radius(self):
        return self.outer_fillet_radius - self.p.mount_thickness

    @property
    def wall_opening(self):
        return self.outer_fillet_radius * 2

    @property
    def grid_width(self):
        return self.width - (self.inner_fillet_radius / 2)

    @property
    def grid_height(self):
        return self.depth - (self.inner_fillet_radius / 2)

    @property
    def panel_opening_width(self):
        return self.wall_opening

    @property
    def panel_opening_height(self):
        return self.height - self.tray_lip

    def tray(self) -> Part:
        with BuildPart(mode=Mode.PRIVATE) as builder:
            # outer tray
            with BuildSketch() as sketch:
                Rectangle(self.outer_width, self.outer_depth)
                fillet(sketch.vertices(), radius=self.outer_fillet_radius)
            extrude(amount=self.outer_height)

            # inner tray
            face = builder.faces().filter_by(Axis.Z).sort_by(Axis.Z)[-1]
            with BuildSketch(Plane(face, x_dir=(1, 0, 0))) as sketch:
                Rectangle(self.width, self.depth)
                fillet(sketch.vertices(), radius=self.inner_fillet_radius)
            extrude(amount=-self.inner_height, mode=Mode.SUBTRACT)

            # wall openings
            face = builder.faces().filter_by(Axis.Z).sort_by(Axis.Z)[-1]
            with BuildSketch(Plane(face.without_holes(), x_dir=(1, 0, 0))):
                Rectangle(self.outer_width, self.wall_opening)
                Rectangle(self.wall_opening, self.outer_depth)
            extrude(amount=-self.height, mode=Mode.SUBTRACT)

            # joint
            face = builder.faces().sort_by(Axis.Z).filter_by(Axis.Z)[0]
            edge = face.edges().filter_by(Axis.X).sort_by(Axis.Y)[0]
            location = Location(edge.position_at(0.5))
            RigidJoint("tray", joint_location=location)
        return require(builder.part)


class RaspberryPI(Device):
    width = 70 * MM
    height = 18 * MM
    depth = 100 * MM

    lip: float = 2 * MM
    fillet_radius: float = 2 * MM
    wall_opening_x: float = 60 * MM
    wall_opening_y: float = 90 * MM

    @property
    def outer_width(self):
        return self.width + (self.p.mount_thickness * 2)

    @property
    def outer_depth(self):
        return self.depth + (self.p.mount_thickness * 2)

    @property
    def outer_height(self):
        return self.height + self.p.mount_thickness

    @property
    def inner_height(self):
        return self.height + self.lip

    @property
    def grid_width(self):
        return self.width - (self.fillet_radius / 2)

    @property
    def grid_height(self):
        return self.depth - (self.fillet_radius / 2)

    @property
    def panel_opening_width(self):
        return self.wall_opening_x

    @property
    def panel_opening_height(self):
        return self.height - self.lip

    def tray(self) -> Part:
        with BuildPart(mode=Mode.PRIVATE) as builder:
            # outer tray
            with BuildSketch() as sketch:
                Rectangle(self.outer_width, self.outer_depth)
                fillet(sketch.vertices(), radius=self.fillet_radius)
            extrude(amount=self.outer_height)

            # inner tray
            face = builder.faces().filter_by(Axis.Z).sort_by(Axis.Z)[-1]
            with BuildSketch(Plane(face, x_dir=(1, 0, 0))) as sketch:
                Rectangle(self.width, self.depth)
                fillet(sketch.vertices(), radius=self.fillet_radius)
            extrude(amount=-self.inner_height, mode=Mode.SUBTRACT)

            # wall openings
            face = builder.faces().filter_by(Axis.Z).sort_by(Axis.Z)[-1]
            with BuildSketch(Plane(face.without_holes(), x_dir=(1, 0, 0))):
                Rectangle(self.outer_width, self.wall_opening_y)
                Rectangle(self.wall_opening_x, self.outer_depth)
            extrude(amount=-self.height, mode=Mode.SUBTRACT)

            # remove back wall
            face = builder.faces().filter_by(Axis.Z).sort_by(Axis.Y)[-1]
            with BuildSketch(Plane(face.without_holes(), x_dir=(1, 0, 0))):
                Rectangle(self.wall_opening_x, self.p.mount_thickness)
            extrude(amount=-self.lip, mode=Mode.SUBTRACT)
        return require(builder.part)


def builder_fn(p: Parameters):
    with BuildPart() as builder:
        add(p.device.tray())
    return builder


main(
    builder_fn,
    {
        "hue-bridge": Parameters(device=HueBridge()),
        "raspberry-pi": Parameters(device=RaspberryPI()),
    },
)
