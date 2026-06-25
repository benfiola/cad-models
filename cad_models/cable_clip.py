from bd_warehouse.fastener import *
from build123d import *
from common import *

ethernet_cable_thickness = 6 * MM


@dataclass
class Parameters:
    clip_height: float
    clip_width: float = 8 * MM
    clip_depth: float = ethernet_cable_thickness
    clip_tab_height: float = 8 * MM
    clip_thickness: float = 2 * MM
    fillet_radius: float = 2 * MM
    screw_diameter: float = 4 * MM
    screw_head_diameter: float = 6.75 * MM
    two_sided: bool = False


def builder_fn(p: Parameters):
    with BuildPart() as builder:
        # clip
        with BuildSketch(Plane.YZ) as sketch:
            outer_width = p.clip_height + (p.clip_thickness * 2)
            outer_height = p.clip_depth + p.clip_thickness
            Rectangle(outer_width, outer_height, align=(Align.CENTER, Align.MIN))
            Rectangle(
                p.clip_height,
                p.clip_depth,
                align=(Align.CENTER, Align.MIN),
                mode=Mode.SUBTRACT,
            )
            location = Location((0, 0))
            location *= Pos(X=-outer_width / 2)
            with Locations(location):
                shape = Rectangle(
                    p.clip_tab_height, p.clip_thickness, align=(Align.MAX, Align.MIN)
                )
            if p.two_sided:
                mirror(shape, about=Plane.YZ)
        extrude(amount=p.clip_width)

        # screw holes
        face = builder.faces().filter_by(Axis.Z).sort_by(Axis.Z)[-3]
        with Locations(Plane(face, x_dir=(0, -1, 0))):
            obj = CounterSinkHole(
                p.screw_diameter / 2, p.screw_head_diameter / 2, p.clip_thickness
            )
        if p.two_sided:
            mirror(obj, about=Plane.XZ, mode=Mode.SUBTRACT)

        # fillet
        edges = []
        some_edges = builder.edges().filter_by(Axis.X).sort_by(Axis.Z)[-4:]
        edges += some_edges
        some_edges = builder.edges().filter_by(Axis.Z).sort_by(Axis.Y)[:2]
        edges += some_edges
        if p.two_sided:
            some_edges = builder.edges().filter_by(Axis.Z).sort_by(Axis.Y)[-2:]
            edges += some_edges
        fillet(edges, radius=p.fillet_radius)

    return builder


main(
    builder_fn,
    {
        "2-cable": Parameters(
            clip_height=2 * ethernet_cable_thickness, two_sided=False
        ),
        "3-cable": Parameters(clip_height=3 * ethernet_cable_thickness),
        "4-cable": Parameters(clip_height=4 * ethernet_cable_thickness),
    },
)
