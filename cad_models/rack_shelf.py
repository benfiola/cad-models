import math

from build123d import *

from cad_models.common import *


class Device:
    height: float
    width: float
    depth: float

    def build_part(self, part: Part) -> BuildPart:
        builder = BuildPart()
        builder.part = part
        return builder

    def tray(self, part: Part, plane: Plane, p: "Parameters") -> Part:
        raise NotImplementedError()

    def panel(self, part: Part, plane: Plane, p: "Parameters") -> Part:
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
    mount_lip: float = 2 * MM
    rack_width: float = 222 * MM

    @property
    def device_spacing(self):
        return sum(d.width for d in self.devices) / len(self.devices) + 1

    @property
    def tray_width(self):
        return p.rack_width + (p.mount_thickness * 2)

    @property
    def tray_depth(self):
        return max(d.depth for d in self.devices) + self.mount_thickness


class Thinkcentre(Device):
    width = 179 * MM + 1.0 * MM
    height = 34.5 * MM
    depth = 183 * MM + 1.0 * MM

    def tray(self, part: Part, plane: Plane, p: Parameters) -> Part:
        builder = BuildPart()
        builder.part = part
        with builder:
            with BuildSketch(Plane(face.without_holes(), x_dir=(1, 0, 0))):
                location = Location((0, 0))
                location *= Pos(Y=-p.tray_depth / 2)
                with Locations(location):
                    inset_height = self.depth
                    Rectangle(self.width, inset_height, align=(Align.CENTER, Align.MIN))
            extrude(amount=-p.mount_lip, mode=Mode.SUBTRACT)
        return require(builder.part)

    def panel(self, part: Part, plane: Plane, p: Parameters) -> Part:
        builder = BuildPart()
        builder.part = part
        with builder:
            pass
        return require(builder.part)


class HueBridge(Device):
    width = 91.82 * MM + 1.0 * MM
    height = 26.9 * MM
    depth = 89.42 * MM + 1.0 * MM

    def tray(self, part: Part, plane: Plane, location: Location, p: Parameters) -> Part:
        builder = BuildPart()
        builder.part = part
        with builder:
            with BuildSketch(Plane(face.without_holes(), x_dir=(1, 0, 0))):
                location = Location((0, 0))
                location *= Pos(Y=-p.tray_depth / 2)
                with Locations(location):
                    inset_height = self.depth
                    Rectangle(self.width, inset_height, align=(Align.CENTER, Align.MIN))
            extrude(amount=-p.mount_lip, mode=Mode.SUBTRACT)
        return require(builder.part)

    def panel(
        self, part: Part, plane: Plane, location: Location, p: Parameters
    ) -> Part:
        builder = BuildPart()
        builder.part = part
        with builder:
            pass
        return require(builder.part)


p = Parameters(devices=[HueBridge()])


with BuildPart() as builder:
    inner_width = p.mount_width - (p.ear_width * 2)

    # front panel
    with BuildSketch(Plane.XZ):
        Rectangle(p.mount_width, p.mount_height)
    extrude(amount=p.mount_thickness)

    # ear holes
    face = builder.faces().filter_by(Axis.Y).sort_by(Axis.Y)[0]
    with BuildSketch(Plane(face, x_dir=(1, 0, 0))):
        location = Location((0, 0))
        location *= Pos(X=-(inner_width + p.ear_width) / 2)
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
            Rectangle(p.tray_width / 2, p.mount_thickness, align=(Align.MIN, Align.MIN))
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

    # device tray inset
    face = builder.faces().filter_by(Axis.Z).sort_by(Axis.Z)[3]
    plane = Plane(face.without_holes(), x_dir=(1, 0, 0))
    location = Location((0, 0))
    for device in p.devices:
        location *= Pos(X=p.device_spacing)
        location *= Pos(X=device.width / 2)
        builder.part = device.tray(require(builder.part), plane, p)
        location *= Pos(X=device.width / 2)

    # device tray inset hex grid
    face = builder.faces().filter_by(Axis.Z).sort_by(Axis.Z)[1]
    with BuildSketch(Plane(face, x_dir=(1, 0, 0))):
        spacing = p.hex_radius + (p.hex_spacing / 2)
        hex_count_x = int(p.device_width / (math.sqrt(3) * spacing))
        hex_count_y = int(p.device_depth / (2 * spacing))
        with HexLocations(
            spacing,
            hex_count_x,
            hex_count_y,
            major_radius=False,
        ):
            RegularPolygon(p.hex_radius, 6, major_radius=False)
    extrude(amount=-p.mount_thickness, mode=Mode.SUBTRACT)

    # front panel cutout
    face = builder.faces().filter_by(Axis.Y).sort_by(Axis.Y)[0]
    cutout_width = p.device_width
    with BuildSketch(Plane(face, x_dir=(1, 0, 0))):
        location = Location((0, 0))
        location *= Pos(Y=-p.mount_height / 2)
        location *= Pos(Y=p.mount_thickness)
        with Locations(location):
            Rectangle(cutout_width, p.device_height, align=(Align.CENTER, Align.MIN))
    extrude(amount=-p.mount_thickness, mode=Mode.SUBTRACT)

main(builder)
