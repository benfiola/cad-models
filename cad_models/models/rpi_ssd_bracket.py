from bd_warehouse.fastener import ClearanceHole, HexNut, PanHeadScrew
from build123d import (
    MM,
    Axis,
    BuildPart,
    BuildSketch,
    Circle,
    GridLocations,
    Location,
    Locations,
    Mode,
    Plane,
    Pos,
    Rectangle,
    RigidJoint,
    Vector,
    extrude,
    fillet,
    mirror,
)

from cad_models.common import CaptiveNutSlot, Iso, Model, main


class BracketScrew(PanHeadScrew):
    def __init__(self, **kwargs):
        kwargs["size"] = "M3-0.5"
        kwargs.setdefault("length", 5 * MM)
        super().__init__(**kwargs)


class BracketNut(HexNut):
    cm_size = "M3-0.5"

    fastener_data = {
        cm_size: {
            f"custom:{Iso.NutWidth}": "5.5",
            f"custom:{Iso.NutHeight}": "2.5",
        }
    }

    def __init__(self, **kwargs):
        kwargs["size"] = self.cm_size
        kwargs["fastener_type"] = "custom"
        super().__init__(**kwargs)


class RpiSsdBracket(Model):
    def __init__(self, **kwargs):
        # parameters
        corner_radius = 2 * MM
        dimensions = Vector(70 * MM, 100 * MM)
        magnet_arm_dimensions = Vector(10 * MM, 10 * MM)
        magnet_dimensions = Vector(6.5 * MM, 3 * MM)
        with BuildPart(mode=Mode.PRIVATE):
            nut = BracketNut()
        rpi_standoff_dimensions = Vector(8.5 * MM, 8.5 * MM, 5 * MM)
        rpi_standoff_offset = 5.5 * MM
        rpi_standoff_spacing = Vector(49 * MM, 58 * MM)
        with BuildPart(mode=Mode.PRIVATE):
            screw = BracketScrew()
        ssd_hole_spacing = Vector(62.0 * MM, 77.0 * MM)
        ssd_hole_offset = 2.5 * MM
        thickness = 5 * MM

        with BuildPart() as builder:
            fillet_edges = []

            # create ssd bracket
            with BuildSketch(Plane.XZ):
                Rectangle(dimensions.X, thickness)
            solid = extrude(amount=dimensions.Y)
            edges = solid.edges().filter_by(Axis.Z)
            fillet_edges.extend(edges)

            # create ssd joint
            face = builder.faces().filter_by(Axis.Z).sort_by(Axis.Z)[0]
            location = face.location_at(0.5, 0.5)
            RigidJoint("ssd", joint_location=location)

            # create ssd bracket holes
            face = builder.faces().filter_by(Axis.Z).sort_by(Axis.Z)[1]
            with BuildSketch(face, mode=Mode.PRIVATE):
                location = Location((0, -ssd_hole_offset))
                with Locations(location):
                    with GridLocations(
                        ssd_hole_spacing.X, ssd_hole_spacing.Y, 2, 2
                    ) as grid_locs:
                        locations = grid_locs.locations
            with Locations(*locations):
                ClearanceHole(screw, counter_sunk=True, depth=thickness)

            # create raspberry pi standoffs
            face = builder.faces().filter_by(Axis.Z).sort_by(Axis.Z)[-1]
            with BuildSketch(face):
                location = Location((0, -rpi_standoff_offset))
                with Locations(location) as loc:
                    joint_location = loc.locations[0]
                    joint_location *= Pos(Z=rpi_standoff_dimensions.Z)
                    with GridLocations(
                        rpi_standoff_spacing.X, rpi_standoff_spacing.Y, 2, 2
                    ) as grid_locs:
                        Rectangle(rpi_standoff_dimensions.X, rpi_standoff_dimensions.Y)
            extrude(amount=rpi_standoff_dimensions.Z)
            RigidJoint("rpi", joint_location=joint_location)

            # create raspberry pi standoff holes and slots
            faces = builder.faces().filter_by(Axis.Z).sort_by(Axis.Z)[-4:]
            locations = [f.location_at(0.5, 0.5) for f in faces]
            with Locations(*locations):
                ClearanceHole(
                    screw, counter_sunk=False, depth=rpi_standoff_dimensions.Z
                )
            nut_offset = (rpi_standoff_dimensions.Z + nut.nut_thickness) / 2
            locations = [l * Pos(Z=-nut_offset) for l in locations]
            with Locations(*locations):
                CaptiveNutSlot(nut, width=rpi_standoff_dimensions.X)

            # create magnet arms
            face = builder.faces().filter_by(Axis.X).sort_by(Axis.X)[0]
            with BuildSketch(face):
                Rectangle(thickness, magnet_arm_dimensions.Y)
            mirror_plane = Plane(face.offset(-dimensions.X / 2))
            solid = magnet_arm = extrude(amount=magnet_arm_dimensions.X)
            edges = solid.edges().filter_by(Axis.Z).sort_by(Axis.X)[:2]
            fillet_edges.extend(edges)
            solid = mirror(magnet_arm, mirror_plane)
            edges = solid.edges().filter_by(Axis.Z).sort_by(Axis.X)[-2:]
            fillet_edges.extend(edges)

            # create magnet holes
            face = magnet_arm.faces().filter_by(Axis.Z).sort_by(Axis.Z)[0]
            with BuildSketch(face):
                Circle(magnet_dimensions.X / 2)
            solid = extrude(amount=-magnet_dimensions.Y, mode=Mode.SUBTRACT)
            mirror(solid, mirror_plane, mode=Mode.SUBTRACT)

            # create fillet
            fillet(fillet_edges, corner_radius)

        super().__init__(builder.part, **kwargs)


if __name__ == "__main__":
    main(RpiSsdBracket())
