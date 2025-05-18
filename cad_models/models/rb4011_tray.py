from bd_warehouse.fastener import ClearanceHole
from build123d import (
    MM,
    Align,
    Axis,
    BuildPart,
    BuildSketch,
    GridLocations,
    Keep,
    Location,
    Locations,
    Mode,
    Plane,
    Pos,
    Rectangle,
    RigidJoint,
    Vector,
    extrude,
)

from cad_models.common import Model, ServerRackInterfaceScrew, main, row_major
from cad_models.models.rb4011 import RB4011


class RB4011Tray(Model):
    def __init__(self, **kwargs):
        router = RB4011()
        interface_thickness = 6.0 * MM
        interface_hole_count = Vector(3, 2)
        interface_hole_spacing = Vector(40 * MM, 20 * MM)
        interface_screw = ServerRackInterfaceScrew()
        lip_thickness = 2 * MM
        tray_dimensions = Vector(0, 44.35 * MM, 0)
        tray_thickness = 4.0 * MM

        # derived values
        tray_dimensions.X = (interface_thickness * 2) + router.dimensions.X
        tray_dimensions.Z = (tray_thickness * 2) + router.dimensions.Z

        with BuildPart() as builder:
            # make box
            with BuildSketch(Plane.XZ):
                Rectangle(tray_dimensions.X, tray_dimensions.Y)
            extrude(amount=tray_dimensions.Z)

            # cut out tray
            face = builder.part.faces().filter_by(Axis.Z).sort_by(Axis.Z)[-1]
            with BuildSketch(face):
                dimensions = Vector(tray_dimensions)
                dimensions.X -= interface_thickness * 2
                dimensions.Y -= tray_thickness
                location = Location((0, tray_thickness))
                with Locations(location):
                    Rectangle(dimensions.X, dimensions.Z)
            extrude(amount=-dimensions.Y, mode=Mode.SUBTRACT)

            # create holes
            split_plane = builder.part.faces().filter_by(Axis.Z).sort_by(Axis.Z)[-1]
            split_plane = Plane(split_plane).offset(-tray_thickness)
            faces = builder.part.faces().filter_by(Axis.X).sort_by(Axis.X)[1:3]
            for side, face in enumerate(faces):
                split_faces = face.split(split_plane, keep=Keep.BOTH)
                face = split_faces.faces().sort_by(Axis.Z)[0]
                with BuildSketch(face, mode=Mode.PRIVATE):
                    with GridLocations(
                        interface_hole_spacing.X,
                        interface_hole_spacing.Y,
                        int(interface_hole_count.X),
                        int(interface_hole_count.Y),
                    ) as grid_locations:
                        hole_locations = grid_locations.locations
                hole_locations = sorted(
                    hole_locations, key=row_major(x_dir=(0, 1, 0), y_dir=(0, 0, -1))
                )
                for hole, hole_location in enumerate(hole_locations):
                    location = Location(hole_location)
                    with Locations(location):
                        ClearanceHole(interface_screw)
                    location = Location(hole_location)
                    location *= Pos(Z=-interface_thickness)
                    RigidJoint(f"interface-{side}-{hole}", joint_location=location)

            # create back lip
            face = builder.part.faces().filter_by(Axis.Z).sort_by(Axis.Z)[1]
            with BuildSketch(face):
                location = Location((0, face.width / 2))
                with Locations(location):
                    Rectangle(
                        face.length, tray_thickness, align=(Align.CENTER, Align.MAX)
                    )
            extrude(amount=lip_thickness)

            # create front cutout
            face = builder.part.faces().filter_by(Axis.Y).sort_by(Axis.Y)[1]
            with BuildSketch(face) as sketch:
                location = Location((0, face.width / 2))
                location *= Pos(Y=-lip_thickness)
                with Locations(location):
                    dimensions = Vector(router.dimensions.X, router.dimensions.Y)
                    dimensions.X -= lip_thickness * 2
                    dimensions.Y -= lip_thickness
                    Rectangle(
                        dimensions.X, dimensions.Y, align=(Align.CENTER, Align.MAX)
                    )
            extrude(amount=-tray_thickness, mode=Mode.SUBTRACT)

            # create tray joint
            face = builder.part.faces().filter_by(Axis.Z).sort_by(Axis.Z)[1]
            location = face.location_at(0.5, 0.5)
            RigidJoint("router", joint_location=location)

        super().__init__(builder.part, **kwargs)

        self.dimensions = tray_dimensions


if __name__ == "__main__":
    main(RB4011Tray())
