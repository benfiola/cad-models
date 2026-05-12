from build123d import *

from cad_models.common import *


class Device:
    p: "Parameters"
    width: float
    depth: float

    def tray(self) -> Part:
        raise NotImplementedError()

    def panel(self) -> Sketch:
        raise NotImplementedError()


@dataclass
class Parameters:
    devices: list[Device]
    ear_hole_width: float = 12 * MM
    ear_hole_height: float = 6 * MM
    ear_width: float = 15 * MM
    hex_radius: float = 3.0 * MM
    hex_spacing: float = 3.0 * MM
    mount_width: float = 252 * MM
    mount_height: float = 1 * U
    mount_thickness: float = 5 * MM
    rack_width: float = 222 * MM

    def __post_init__(self):
        for device in self.devices:
            device.p = self

    @property
    def device_spacing(self):
        return (self.tray_inner_width - sum(d.width for d in self.devices)) / (
            len(self.devices) + 1
        )

    @property
    def tray_inner_width(self):
        return self.rack_width - (self.mount_thickness * 2)

    @property
    def tray_width(self):
        return self.rack_width

    @property
    def tray_depth(self):
        return max(d.depth for d in self.devices) - self.mount_thickness


class RaspberryPi(Device):
    adapter_height: float = 15 * MM
    device_width = 70.1 * MM
    device_depth = 100.1 * MM
    device_height: float = 34 * MM
    lip: float = 2 * MM
    fillet_radius: float = 2 * MM
    wall_opening_x: float = 60 * MM
    wall_opening_y: float = 90 * MM

    @property
    def width(self):
        return self.device_width + (self.p.mount_thickness * 2)

    @property
    def depth(self):
        return self.device_depth + (self.p.mount_thickness * 2)

    @property
    def height(self):
        return self.adapter_height + (self.p.mount_thickness - self.lip)

    @property
    def grid_width(self):
        return self.device_width - (self.fillet_radius / 2)

    @property
    def grid_height(self):
        return self.device_depth - (self.fillet_radius / 2)

    @property
    def panel_opening_width(self):
        return self.wall_opening_x

    @property
    def panel_opening_height(self):
        return self.device_height - self.lip

    @property
    def wall_height(self):
        return self.adapter_height - self.lip

    def tray(self) -> Part:
        with BuildPart(mode=Mode.PRIVATE) as builder:
            # outer tray
            with BuildSketch() as sketch:
                Rectangle(self.width, self.depth)
                fillet(sketch.vertices(), radius=self.fillet_radius)
            extrude(amount=self.height)

            # inner tray
            face = builder.faces().filter_by(Axis.Z).sort_by(Axis.Z)[-1]
            with BuildSketch(Plane(face, x_dir=(1, 0, 0))) as sketch:
                Rectangle(self.device_width, self.device_depth)
                fillet(sketch.vertices(), radius=self.fillet_radius)
            extrude(amount=-self.adapter_height, mode=Mode.SUBTRACT)

            # wall openings
            face = builder.faces().filter_by(Axis.Z).sort_by(Axis.Z)[-1]
            with BuildSketch(Plane(face.without_holes(), x_dir=(1, 0, 0))):
                Rectangle(self.width, self.wall_opening_y)
                Rectangle(self.wall_opening_x, self.depth)
            extrude(amount=-self.wall_height, mode=Mode.SUBTRACT)

            # hex grid
            face = builder.faces().sort_by(Axis.Z).filter_by(Axis.Z)[1]
            with BuildSketch(Plane(face, x_dir=(1, 0, 0))):
                add(
                    hex_grid(
                        self.grid_width,
                        self.grid_height,
                        self.p.hex_radius,
                        self.p.hex_spacing,
                    )
                )
            extrude(amount=-self.p.mount_thickness, mode=Mode.SUBTRACT)

            # remove back wall
            face = builder.faces().filter_by(Axis.Z).sort_by(Axis.Y)[-1]
            with BuildSketch(Plane(face.without_holes(), x_dir=(1, 0, 0))):
                Rectangle(self.wall_opening_x, self.p.mount_thickness)
            extrude(amount=-self.lip, mode=Mode.SUBTRACT)

            # joint
            face = builder.faces().sort_by(Axis.Z).filter_by(Axis.Z)[0]
            edge = face.edges().filter_by(Axis.X).sort_by(Axis.Y)[0]
            location = Location(edge.position_at(0.5))
            RigidJoint("tray", joint_location=location)
        return require(builder.part)

    def panel(self) -> Sketch:
        with BuildSketch(mode=Mode.PRIVATE) as sketch:
            Rectangle(
                self.panel_opening_width,
                self.panel_opening_height,
                align=(Align.CENTER, Align.MIN),
            )
        return sketch.sketch


class Thinkcentre(Device):
    device_width = 179 * MM + 1.0 * MM
    device_depth = 183 * MM + 1.0 * MM
    device_height = 34.5 * MM
    foot_width = 16.0 * MM
    foot_height = 7.5 * MM
    foot_depth = 2.5 * MM
    foot_spacing_x = 162.5 * MM
    foot_spacing_y = 133 * MM
    foot_offset_y = -0.5 * MM
    panel_lip = 2 * MM
    tray_lip = 1 * MM

    @property
    def foot_outer_width(self):
        return self.foot_width + self.tray_lip

    @property
    def foot_outer_height(self):
        return self.foot_height + self.tray_lip

    @property
    def width(self):
        return self.device_width + (self.p.mount_thickness * 2)

    @property
    def depth(self):
        return self.device_depth + (self.p.mount_thickness * 2)

    @property
    def panel_opening_height(self):
        return self.device_height - self.panel_lip

    @property
    def panel_opening_width(self):
        return self.device_width - (self.panel_lip * 2)

    @property
    def tray_inner_thickness(self):
        return self.p.mount_thickness - self.tray_lip

    def tray(self) -> Part:
        with BuildPart(mode=Mode.PRIVATE) as builder:
            # outer tray
            with BuildSketch():
                Rectangle(self.width, self.depth)
            extrude(amount=self.p.mount_thickness)

            # inner tray
            face = builder.faces().filter_by(Axis.Z).sort_by(Axis.Z)[-1]
            with BuildSketch(Plane(face, x_dir=(1, 0, 0))):
                Rectangle(self.device_width, self.device_depth)
            extrude(amount=-self.tray_lip, mode=Mode.SUBTRACT)

            # hex grid
            face = builder.faces().sort_by(Axis.Z).filter_by(Axis.Z)[1]
            with BuildSketch(Plane(face, x_dir=(1, 0, 0))):
                add(
                    hex_grid(
                        self.device_width,
                        self.device_depth,
                        self.p.hex_radius,
                        self.p.hex_spacing,
                    )
                )
            extrude(amount=-self.p.mount_thickness, mode=Mode.SUBTRACT)

            # feet
            face = builder.faces().sort_by(Axis.Z).filter_by(Axis.Z)[1]
            with BuildSketch(Plane(face.without_holes(), x_dir=(1, 0, 0))):
                location = Location((0, 0))
                location *= Pos(Y=self.foot_offset_y)
                with Locations(location):
                    with GridLocations(self.foot_spacing_x, self.foot_spacing_y, 2, 2):
                        SlotOverall(
                            self.foot_outer_width, self.foot_outer_height, rotation=90
                        )
            extrude(amount=-self.tray_inner_thickness)
            face = builder.faces().sort_by(Axis.Z).filter_by(Axis.Z)[1]
            with BuildSketch(Plane(face.without_holes(), x_dir=(1, 0, 0))):
                location = Location((0, 0))
                location *= Pos(Y=self.foot_offset_y)
                with Locations(location):
                    with GridLocations(self.foot_spacing_x, self.foot_spacing_y, 2, 2):
                        SlotOverall(self.foot_width, self.foot_height, rotation=90)
            extrude(amount=-self.foot_depth, mode=Mode.SUBTRACT)

            # joint
            face = builder.faces().sort_by(Axis.Z).filter_by(Axis.Z)[0]
            edge = face.edges().filter_by(Axis.X).sort_by(Axis.Y)[0]
            location = Location(edge.position_at(0.5))
            RigidJoint("tray", joint_location=location)
        return require(builder.part)

    def panel(self) -> Sketch:
        with BuildSketch(mode=Mode.PRIVATE) as sketch:
            Rectangle(
                self.panel_opening_width,
                self.panel_opening_height,
                align=(Align.CENTER, Align.MIN),
            )
        return sketch.sketch


class HueBridge(Device):
    device_width = 91 * MM
    device_depth = 90.7 * MM
    device_height = 26.5 * MM
    outer_fillet_radius = 24 * MM
    lip = 2 * MM

    @property
    def width(self):
        return self.device_width + (self.p.mount_thickness * 2)

    @property
    def depth(self):
        return self.device_depth + (self.p.mount_thickness * 2)

    @property
    def height(self):
        return self.device_height + (self.p.mount_thickness - self.lip)

    @property
    def inner_fillet_radius(self):
        return self.outer_fillet_radius - self.p.mount_thickness

    @property
    def wall_opening(self):
        return self.outer_fillet_radius * 2

    @property
    def wall_height(self):
        return self.device_height - self.lip

    @property
    def grid_width(self):
        return self.device_width - (self.inner_fillet_radius / 2)

    @property
    def grid_height(self):
        return self.device_depth - (self.inner_fillet_radius / 2)

    @property
    def panel_opening_width(self):
        return self.wall_opening

    @property
    def panel_opening_height(self):
        return self.device_height - self.lip

    def tray(self) -> Part:
        with BuildPart(mode=Mode.PRIVATE) as builder:
            # outer tray
            with BuildSketch() as sketch:
                Rectangle(self.width, self.depth)
                fillet(sketch.vertices(), radius=self.outer_fillet_radius)
            extrude(amount=self.height)

            # inner tray
            face = builder.faces().filter_by(Axis.Z).sort_by(Axis.Z)[-1]
            with BuildSketch(Plane(face, x_dir=(1, 0, 0))) as sketch:
                Rectangle(self.device_width, self.device_depth)
                fillet(sketch.vertices(), radius=self.inner_fillet_radius)
            extrude(amount=-self.device_height, mode=Mode.SUBTRACT)

            # wall openings
            face = builder.faces().filter_by(Axis.Z).sort_by(Axis.Z)[-1]
            with BuildSketch(Plane(face.without_holes(), x_dir=(1, 0, 0))):
                Rectangle(self.width, self.wall_opening)
                Rectangle(self.wall_opening, self.depth)
            extrude(amount=-self.wall_height, mode=Mode.SUBTRACT)

            # hex grid
            face = builder.faces().sort_by(Axis.Z).filter_by(Axis.Z)[1]
            with BuildSketch(Plane(face, x_dir=(1, 0, 0))):
                add(
                    hex_grid(
                        self.grid_width,
                        self.grid_height,
                        self.p.hex_radius,
                        self.p.hex_spacing,
                    )
                )
            extrude(amount=-self.p.mount_thickness, mode=Mode.SUBTRACT)

            # joint
            face = builder.faces().sort_by(Axis.Z).filter_by(Axis.Z)[0]
            edge = face.edges().filter_by(Axis.X).sort_by(Axis.Y)[0]
            location = Location(edge.position_at(0.5))
            RigidJoint("tray", joint_location=location)
        return require(builder.part)

    def panel(self) -> Sketch:
        with BuildSketch(mode=Mode.PRIVATE) as sketch:
            Rectangle(
                self.panel_opening_width,
                self.panel_opening_height,
                align=(Align.CENTER, Align.MIN),
            )
        return sketch.sketch


def get_tray_cutout(part: Part) -> Face:
    face = part.faces().filter_by(Axis.Z).sort_by(Axis.Z)[0]
    return Face(face.outer_wire())


def builder_fn(p: Parameters):
    with BuildPart() as builder:
        # front panel
        with BuildSketch(Plane.XZ):
            Rectangle(p.mount_width, p.mount_height)
        extrude(amount=p.mount_thickness)

        # ear holes
        face = builder.faces().filter_by(Axis.Y).sort_by(Axis.Y)[0]
        with BuildSketch(Plane(face, x_dir=(1, 0, 0))):
            location = Location((0, 0))
            location *= Pos(X=-(p.tray_width + p.ear_width) / 2)
            with Locations(location):
                vertical_spacing = p.mount_height - (0.5 * IN)
                with GridLocations(0, vertical_spacing, 1, 2):
                    SlotOverall(p.ear_hole_width, p.ear_hole_height)
            mirror(about=Plane.YZ)
        extrude(amount=-p.mount_thickness, mode=Mode.SUBTRACT)

        # tray
        face = builder.faces().filter_by(Axis.Y).sort_by(Axis.Y)[-1]
        with BuildSketch(Plane(face.without_holes(), x_dir=(-1, 0, 0))):
            location = Location((0, 0))
            location *= Pos(X=-(p.tray_width) / 2)
            location *= Pos(Y=-p.mount_height / 2)
            with Locations(location):
                Rectangle(
                    p.tray_width / 2, p.mount_thickness, align=(Align.MIN, Align.MIN)
                )
                Rectangle(p.mount_thickness, p.mount_height, align=(Align.MIN))
            mirror(about=Plane.YZ)
        extrude(amount=p.tray_depth)

        # tray rib via subtraction
        face = builder.faces().filter_by(Axis.X).sort_by(Axis.X)[1]
        mirror_plane = Plane(face.offset(-p.tray_width / 2))
        rib_thickness = p.mount_thickness
        with BuildSketch(Plane(face, x_dir=(0, -1, 0))):
            rib_width = p.tray_depth
            rib_height = p.mount_height - p.mount_thickness
            location = Location((0, 0))
            location *= Pos(Y=p.mount_height / 2)
            location *= Pos(X=p.tray_depth / 2)
            with Locations(location):
                Triangle(
                    C=90,
                    a=rib_width,
                    b=rib_height,
                    align=(Align.MIN, Align.MIN),
                    rotation=180,
                )
        extruded = extrude(amount=-rib_thickness, mode=Mode.SUBTRACT)
        mirror(extruded, about=mirror_plane, mode=Mode.SUBTRACT)

        # device trays
        face = builder.faces().filter_by(Axis.Z).sort_by(Axis.Z)[3]
        location = Location(face.position_at(0.0, 1.0))
        location *= Pos(Z=-p.mount_thickness)
        location *= Pos(Y=-p.mount_thickness)
        for index, device in enumerate(p.devices):
            location *= Pos(X=p.device_spacing)
            location *= Pos(X=device.width / 2)
            part = device.tray()
            part_joint = typing.cast(RigidJoint, part.joints["tray"])
            tray_joint = RigidJoint(f"device-{index}", joint_location=location)
            tray_joint.connect_to(part_joint)
            extrude(get_tray_cutout(part), amount=p.mount_thickness, mode=Mode.SUBTRACT)
            add(part)
            location *= Pos(X=device.width / 2)

        # front panel cutout
        face = builder.faces().filter_by(Axis.Y).sort_by(Axis.Y)[0]
        location = Location(face.without_holes().position_at(0.5, 1.0))
        location *= Pos(X=-p.tray_inner_width / 2)
        location *= Pos(Z=p.mount_thickness)
        for device in p.devices:
            location *= Pos(X=p.device_spacing)
            location *= Pos(X=device.width / 2)
            plane = Plane(location.position, x_dir=(1, 0, 0), z_dir=face.normal_at())
            with BuildSketch(plane):
                cutout = device.panel()
                add(cutout)
            extrude(amount=-p.mount_thickness, mode=Mode.SUBTRACT)
            location *= Pos(X=device.width / 2)
    return builder


main(
    builder_fn,
    {
        "hue-bridge": Parameters(devices=[HueBridge()]),
        "thinkcentre": Parameters(devices=[Thinkcentre()]),
        "one-raspberry-pi": Parameters(devices=[RaspberryPi()]),
        "two-raspberry-pis": Parameters(devices=[RaspberryPi(), RaspberryPi()]),
    },
)
