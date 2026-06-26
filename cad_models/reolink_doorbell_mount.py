from bd_warehouse.fastener import *
from build123d import *
from common import *


@dataclass
class Parameters:
    channel_edge_radius: float = 0.5 * MM
    channel_size: float = 7 * MM
    inner_slot_width: float = 25 * MM
    inner_slot_height: float = 64 * MM
    mount_depth: float = 10 * MM
    mount_height: float = 133 * MM
    mount_width: float = 48 * MM
    doorbell_peg_depth: float = 1.4 * MM
    doorbell_peg_spacing_x: float = 30 * MM
    doorbell_screw_diameter: float = 2 * MM
    doorbell_screw_spacing_y: float = 75 * MM
    wall_screw_thread_diameter: float = 4.1 * MM
    wall_screw_head_diameter: float = 8.0 * MM
    wall_slot_outer_height: float = 18 * MM
    wall_slot_outer_depth: float = 5 * MM
    wall_slot_spacing_y: float = 104 * MM

    @property
    def channel_offset_x(self) -> float:
        return (self.inner_slot_width / 2) - (self.channel_size / 2)

    @property
    def doorbell_peg_diameter(self) -> float:
        return self.doorbell_screw_diameter

    @property
    def doorbell_peg_spacing_y(self) -> float:
        return self.doorbell_screw_spacing_y

    @property
    def wall_slot_outer_width(self) -> float:
        return self.wall_screw_head_diameter

    @property
    def wall_slot_inner_height(self) -> float:
        return self.wall_slot_outer_height - self.wall_screw_thread_diameter

    @property
    def wall_slot_inner_width(self) -> float:
        return self.wall_screw_thread_diameter


def builder_fn(p: Parameters):
    with BuildPart() as builder:
        # mount
        with BuildSketch(Plane.XZ):
            SlotOverall(p.mount_height, p.mount_width, rotation=90)
        extrude(amount=p.mount_depth)

        # holes
        face = builder.faces().filter_by(Axis.Y).sort_by(Axis.Y)[0]
        with BuildSketch(Plane(face, x_dir=(1, 0, 0))):
            # inner slot
            SlotOverall(p.inner_slot_height, p.inner_slot_width, rotation=90)
            # doorbell mount plate
            with GridLocations(0, p.doorbell_screw_spacing_y, 1, 2):
                Circle(p.doorbell_screw_diameter / 2)
            # wall slot
            with GridLocations(0, p.wall_slot_spacing_y, 1, 2):
                SlotOverall(
                    p.wall_slot_inner_height, p.wall_slot_inner_width, rotation=90
                )
        extrude(amount=-p.mount_depth, mode=Mode.SUBTRACT)

        # wall outer slot
        face = builder.faces().filter_by(Axis.Y).sort_by(Axis.Y)[0]
        with BuildSketch(Plane(face.without_holes(), x_dir=(1, 0, 0))):
            with GridLocations(0, p.wall_slot_spacing_y, 1, 2):
                SlotOverall(
                    p.wall_slot_outer_height, p.wall_slot_outer_width, rotation=90
                )
        extrude(amount=-p.wall_slot_outer_depth, mode=Mode.SUBTRACT)

        # doorbell pegs
        face = builder.faces().filter_by(Axis.Y).sort_by(Axis.Y)[0]
        with BuildSketch(Plane(face.without_holes(), x_dir=(1, 0, 0))):
            with GridLocations(
                p.doorbell_peg_spacing_x, p.doorbell_peg_spacing_y, 2, 2
            ):
                Circle(p.doorbell_peg_diameter / 2)
        extrude(amount=p.doorbell_peg_depth)

        # channel
        with BuildPart(mode=Mode.PRIVATE) as channel_builder:
            Box(p.channel_size, p.channel_size, p.mount_height)
            edges = channel_builder.edges().filter_by(Axis.Z).sort_by(Axis.Y)[:2]
            fillet(edges, radius=p.channel_edge_radius)
        face = builder.faces().filter_by(Axis.Y).sort_by(Axis.Y)[-1]
        location = face.without_holes().location_at(0.0, 0.5, x_dir=(1, 0, 0))
        location *= Pos(X=p.channel_offset_x)
        location *= Pos(Z=p.channel_size / 2)
        location *= Rot(X=90)
        location *= Rot(Z=180)
        with Locations(location):
            add(channel_builder, mode=Mode.SUBTRACT)
    return builder


main(builder_fn, Parameters())
