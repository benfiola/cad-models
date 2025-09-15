from bd_warehouse.fastener import PanHeadScrew
from build123d import (
    IN,
    MM,
    Axis,
    BuildLine,
    BuildPart,
    BuildSketch,
    Locations,
    Mode,
    Plane,
    Polyline,
    Pos,
    RigidJoint,
    Rot,
    SlotOverall,
    Vector,
    extrude,
    make_face,
)

from cad_models.common import Model, centered_point_list, main


class DrywallAnchorScrew(PanHeadScrew):
    """
    Screw used in conjunction with wall anchors to secure the canvas hanger to the wall.
    """

    def __init__(self, **kwargs):
        kwargs["fastener_type"] = "asme_b_18.6.3"
        kwargs["length"] = 1.5 * IN
        kwargs["size"] = "#8-32"
        super().__init__(**kwargs)


class WallSlatCanvasHanger(Model):
    def __init__(self, **kwargs):
        dimensions = Vector(0.495 * IN, 2 * IN, 0.5 * IN)
        hook_depth = 0.5 * IN
        hook_height = 0.5 * IN
        hook_thickness = 0.1 * IN
        with BuildPart(mode=Mode.PRIVATE):
            screw = DrywallAnchorScrew()
        slot_height = 0.75 * IN

        slot_inner_dimensions = Vector(
            screw.clearance_hole_diameters["Normal"], slot_height, 0.2 * IN
        )
        slot_outer_dimensions = Vector(
            screw.head_diameter + 0.8 * MM,
            slot_height + (screw.head_diameter / 2),
            dimensions.Z - slot_inner_dimensions.Z,
        )

        with BuildPart() as builder:
            # create hangar (via side profile)
            with BuildSketch(Plane.YZ):
                with BuildLine():
                    d = dimensions
                    hd = hook_depth
                    hh = hook_height
                    ht = hook_thickness

                    points = centered_point_list(
                        (0, 0),
                        (0, d.Y),
                        (d.Z, d.Y),
                        (d.Z, ht),
                        (d.Z + hd, ht),
                        (d.Z + hd, ht + hh),
                        (d.Z + hd + ht, ht + hh),
                        (d.Z + hd + ht, 0),
                        (0, 0),
                    )
                    Polyline(*points)
                make_face()
            solid = extrude(amount=dimensions.X)

            # create slot
            face = solid.faces().filter_by(Axis.Y).sort_by(Axis.Y)[1]
            with BuildSketch(face):
                with Locations((-hook_height / 2, 0)) as locs:
                    location = locs.locations[0]
                    SlotOverall(slot_inner_dimensions.Y, slot_inner_dimensions.X)
            extrude(amount=-dimensions.Z, mode=Mode.SUBTRACT)
            with BuildSketch(face):
                with Locations((-hook_height / 2, 0)):
                    SlotOverall(slot_outer_dimensions.Y, slot_outer_dimensions.X)
            extrude(amount=-slot_outer_dimensions.Z, mode=Mode.SUBTRACT)

            # create joint
            location *= Rot(Y=-90, Z=-90)
            location *= Pos(Y=-dimensions.Z)
            RigidJoint("mount", joint_location=location)

        super().__init__(builder.part, **kwargs)


if __name__ == "__main__":
    main(WallSlatCanvasHanger())
