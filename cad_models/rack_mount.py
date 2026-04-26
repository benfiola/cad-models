from build123d import *
from build123d import BuildPart
from common import *

from cad_models.common import BuildPart


@dataclass
class Device:
    width: float
    height: float
    depth: float


class RB4011(Device):
    def __init__(self):
        super().__init__(width=227.7 * MM, height=26 * MM, depth=117.7 * MM)


@dataclass
class Parameters:
    devices: list[Device]
    ear_hole_width = 12 * MM
    ear_hole_height = 6 * MM
    ear_width = 15 * MM
    mount_width = 252 * MM
    mount_height = 1 * U
    mount_oversize_offset = 10 * MM
    mount_thickness = 5 * MM
    mount_lip = 2 * MM
    rack_width = 222 * MM
    rib_depth = 10 * MM


rb4011 = Parameters(devices=[RB4011()])


p = rb4011

with BuildPart() as builder:
    # front panel
    with BuildSketch(Plane.XZ):
        Rectangle(p.mount_width, p.mount_height)
    extruded = extrude(amount=p.mount_thickness)

    # ear slices
    face = builder.faces().filter_by(Axis.X).sort_by(Axis.X)[0]
    slice_plane = Plane(face.offset(-p.ear_width))
    split(bisect_by=slice_plane, keep=Keep.BOTH)
    slice_plane = Plane(face.offset(-(p.mount_width - p.ear_width)))
    split(bisect_by=slice_plane, keep=Keep.BOTH)

    # ear holes
    face = builder.faces().filter_by(Axis.X).sort_by(Axis.X)[0]
    mirror_plane = Plane(face.offset(-p.mount_width / 2))
    face = builder.faces().filter_by(Axis.Y).sort_by(Axis.Y)[:2].sort_by(Axis.X)[0]
    with BuildSketch(Plane(face, x_dir=(1, 0, 0))) as sketch:
        vertical_spacing = p.mount_height - (0.5 * IN)
        with GridLocations(0, vertical_spacing, 1, 2):
            SlotOverall(p.ear_hole_width, p.ear_hole_height)
    extruded = extrude(amount=-p.mount_thickness, mode=Mode.SUBTRACT)
    mirror(extruded, about=mirror_plane, mode=Mode.SUBTRACT)

    # tray
    min_tray_width = 222 * MM
    tray_depth = max(map(lambda d: d.width, p.devices)) + (p.mount_thickness
    for device in p.devices:
        tray_width += device.width
    tray_width = max(tray_width, min_tray_width)
    oversized = tray_width > min_tray_width
    tray_builder: BuildPart
    tray_depth = max(map(lambda d: d.depth, p.devices)) + p.mount_thickness
    if oversized:
        tray_depth += p.mount_oversize_offset
    face = builder.faces().filter_by(Axis.Y).sort_by(Axis.Y)[-3:].sort_by(Axis.X)[1]
    with BuildSketch(Plane(face, x_dir=(-1, 0, 0))):
        with BuildLine() as build_line:
            if oversized:
                inner_width = tray_width - (p.mount_thickness * 2)
                oversize_offset = (tray_width - min_tray_width) / 2
                Polyline(
                    (0, 0),
                    (0, p.mount_height),
                    (oversize_offset, p.mount_height),
                    (oversize_offset, p.mount_height - p.mount_thickness),
                    (p.mount_thickness, p.mount_height - p.mount_thickness),
                    (p.mount_thickness, p.mount_thickness),
                    (tray_width - p.mount_thickness, p.mount_thickness),
                    (
                        tray_width - p.mount_thickness,
                        p.mount_height - p.mount_thickness,
                    ),
                    (
                        tray_width - oversize_offset,
                        p.mount_height - p.mount_thickness,
                    ),
                    (
                        tray_width - oversize_offset,
                        p.mount_height,
                    ),
                    (
                        tray_width,
                        p.mount_height,
                    ),
                    (
                        tray_width,
                        0,
                    ),
                    (0, 0),
                )
            else:
                raise NotImplementedError()
        make_face()
    extrude(amount=tray_depth)

main(builder)
