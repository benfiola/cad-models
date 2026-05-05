from build123d import *

from cad_models.common import *


class Device:
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
    ear_hole_width: float = 12 * MM
    ear_hole_height: float = 6 * MM
    ear_width: float = 15 * MM
    hex_radius: float = 3.0 * MM
    hex_spacing: float = 3.0 * MM
    mount_width: float = 252 * MM
    mount_height: float = 1 * U
    mount_thickness: float = 5 * MM
    mount_lip: float = 2 * MM
    oversize_taper_offset: float = 10 * MM
    oversize_taper_length: float = 10 * MM
    rack_width: float = 222 * MM

    @property
    def inner_width(self):
        return self.mount_width - (self.ear_width * 2)

    @property
    def tray_width(self):
        return self.device.width + (self.mount_thickness * 2)

    @property
    def oversize_top_width(self):
        return (self.tray_width - self.rack_width) + (self.mount_thickness * 2)

    @property
    def tray_depth(self):
        return self.device.depth + self.mount_thickness

    @property
    def taper_width(self):
        return (self.oversize_top_width / 2) - self.mount_thickness


class RB4011(Device):
    height = 26 * MM
    width = 227.7 * MM + 1.0 * MM
    depth = 117.7 * MM + 1.0 * MM

    foot_diameter = 15 * MM
    foot_depth = 3.5 * MM
    foot_spacing_x = 162.2 * MM
    foot_spacing_y = 65.34 * MM
    foot_offset_y = -7.9 * MM
    foot_lip = 1 * MM
    tray_lip = 0.5 * MM
    panel_lip = 2 * MM

    @property
    def outer_width(self):
        return self.width + (p.mount_thickness * 2)

    @property
    def outer_depth(self):
        return self.depth + (p.mount_thickness * 2)

    @property
    def foot_outer_diameter(self):
        return self.foot_diameter + self.foot_lip

    @property
    def tray_inner_thickness(self):
        return p.mount_thickness - self.tray_lip

    @property
    def panel_opening_height(self):
        return self.height - self.panel_lip

    def tray(self) -> Part:
        with BuildPart(mode=Mode.PRIVATE) as builder:
            # outer tray
            with BuildSketch():
                Rectangle(self.outer_width, self.outer_depth)
            extrude(amount=p.mount_thickness)

            # inner tray
            face = builder.faces().filter_by(Axis.Z).sort_by(Axis.Z)[-1]
            with BuildSketch(Plane(face, x_dir=(1, 0, 0))):
                Rectangle(self.width, self.depth)
            extrude(amount=-self.tray_lip, mode=Mode.SUBTRACT)

            # hex grid
            face = builder.faces().sort_by(Axis.Z).filter_by(Axis.Z)[1]
            with BuildSketch(Plane(face, x_dir=(1, 0, 0))):
                add(hex_grid(self.width, self.depth, p.hex_radius, p.hex_spacing))
            extrude(amount=-p.mount_thickness, mode=Mode.SUBTRACT)

            # feet
            face = builder.faces().sort_by(Axis.Z).filter_by(Axis.Z)[1]
            with BuildSketch(Plane(face.without_holes(), x_dir=(1, 0, 0))):
                location = Location((0, 0))
                location *= Pos(Y=self.foot_offset_y)
                with Locations(location):
                    with GridLocations(self.foot_spacing_x, self.foot_spacing_y, 2, 2):
                        Circle(self.foot_outer_diameter / 2)
            extrude(amount=-self.tray_inner_thickness)
            face = builder.faces().sort_by(Axis.Z).filter_by(Axis.Z)[1]
            with BuildSketch(Plane(face.without_holes(), x_dir=(1, 0, 0))):
                location = Location((0, 0))
                location *= Pos(Y=self.foot_offset_y)
                with Locations(location):
                    with GridLocations(self.foot_spacing_x, self.foot_spacing_y, 2, 2):
                        Circle(self.foot_diameter / 2)
            extrude(amount=-self.foot_depth, mode=Mode.SUBTRACT)

            # joint
            face = builder.faces().sort_by(Axis.Z).filter_by(Axis.Z)[0]
            edge = face.edges().filter_by(Axis.X).sort_by(Axis.Y)[0]
            location = Location(edge.position_at(0.5))
            RigidJoint("tray", joint_location=location)
        return require(builder.part)

    def panel(self) -> Sketch:
        with BuildSketch(mode=Mode.PRIVATE) as builder:
            Rectangle(
                p.rack_width, self.panel_opening_height, align=(Align.CENTER, Align.MIN)
            )
        return require(builder.sketch)


def get_tray_cutout(part: Part) -> Face:
    face = part.faces().filter_by(Axis.Z).sort_by(Axis.Z)[0]
    return Face(face.outer_wire())


rb4011 = Parameters(device=RB4011())


p = rb4011


with BuildPart() as builder:
    # front panel
    with BuildSketch(Plane.XZ):
        Rectangle(p.mount_width, p.mount_height)
    extrude(amount=p.mount_thickness)

    # tray
    face = builder.faces().filter_by(Axis.Y).sort_by(Axis.Y)[-1]
    with BuildSketch(Plane(face.without_holes(), x_dir=(-1, 0, 0))):
        location = Location((0, 0))
        location *= Pos(X=-(p.tray_width) / 2)
        location *= Pos(Y=-p.mount_height / 2)
        with Locations(location):
            Rectangle(p.tray_width / 2, p.mount_thickness, align=(Align.MIN, Align.MIN))
            Rectangle(p.mount_thickness, p.mount_height, align=(Align.MIN))
        location *= Pos(Y=p.mount_height)
        with Locations(location):
            Rectangle(
                p.oversize_top_width / 2,
                p.mount_thickness,
                align=(Align.MIN, Align.MAX),
            )
        mirror(about=Plane.YZ)
    extrude(amount=p.tray_depth)

    # tray rib via subtraction
    face = builder.faces().filter_by(Axis.X).sort_by(Axis.X)[1]
    mirror_plane = Plane(face.offset(-p.tray_width / 2))
    rib_thickness = p.oversize_top_width
    with BuildSketch(Plane(face, x_dir=(0, -1, 0))):
        rib_width = p.tray_depth - (
            (p.oversize_taper_offset * 2) + p.oversize_taper_length
        )
        rib_height = p.mount_height - p.mount_thickness
        location = Location((0, 0))
        location *= Pos(Y=p.mount_height / 2)
        location *= Pos(X=p.tray_depth / 2)
        location *= Pos(X=-((p.oversize_taper_offset * 2) + p.oversize_taper_length))
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
    face = builder.faces().filter_by(Axis.Z).sort_by(Axis.Z)[1]
    location = Location(face.position_at(0.5, 1.0))
    location *= Pos(Z=-p.mount_thickness)
    location *= Pos(Y=-p.mount_thickness)
    part = p.device.tray()
    part_joint = typing.cast(RigidJoint, part.joints["tray"])
    tray_joint = RigidJoint(f"device", joint_location=location)
    tray_joint.connect_to(part_joint)
    extrude(get_tray_cutout(part), amount=p.mount_thickness, mode=Mode.SUBTRACT)
    add(part)

    # oversize tray cutouts
    face = builder.faces().filter_by(Axis.X).sort_by(Axis.X)[1]
    mirror_plane = Plane(face.offset(-p.tray_width / 2))
    test = Plane(face.offset(-p.tray_width))
    face = builder.faces().filter_by(Axis.Z).sort_by(Axis.Z)[-1]
    edge = face.edges().filter_by(Axis.Y).sort_by(Axis.X)[1]
    location = edge.location_at(1.0)
    with BuildSketch(
        Plane(location.position, x_dir=(0, -1, 0), z_dir=face.normal_at())
    ):
        location = Location((0, 0))
        with Locations(location):
            Rectangle(
                p.oversize_taper_offset, p.taper_width, align=(Align.MAX, Align.MIN)
            )
        location = Location((0, 0))
        location *= Pos(X=-p.oversize_taper_offset)
        with Locations(location):
            Triangle(
                C=90,
                a=p.oversize_taper_length,
                b=p.taper_width,
                align=(Align.MAX, Align.MIN),
            )
    extruded = extrude(amount=-p.mount_height, mode=Mode.SUBTRACT)
    mirror(extruded, about=mirror_plane, mode=Mode.SUBTRACT)

    # ear holes
    face = builder.faces().filter_by(Axis.Y).sort_by(Axis.Y)[0]
    with BuildSketch(Plane(face, x_dir=(1, 0, 0))):
        location = Location((0, 0))
        location *= Pos(X=-(p.inner_width + p.ear_width) / 2)
        with Locations(location):
            vertical_spacing = p.mount_height - (0.5 * IN)
            with GridLocations(0, vertical_spacing, 1, 2):
                SlotOverall(p.ear_hole_width, p.ear_hole_height)
        mirror(about=Plane.YZ)
    extrude(amount=-p.mount_thickness, mode=Mode.SUBTRACT)

    # front panel cutout
    face = builder.faces().filter_by(Axis.Y).sort_by(Axis.Y)[0]
    location = Location(face.without_holes().position_at(0.5, 1.0))
    location *= Pos(Z=p.mount_thickness)
    plane = Plane(location.position, x_dir=(1, 0, 0), z_dir=face.normal_at())
    with BuildSketch(plane) as sketch:
        cutout = p.device.panel()
        add(cutout)
    sketch_face = sketch.face()
    extrude(amount=-p.mount_thickness, mode=Mode.SUBTRACT)

main(builder)
