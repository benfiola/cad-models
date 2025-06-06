from build123d import (
    MM,
    Align,
    Axis,
    BuildPart,
    BuildSketch,
    Circle,
    Location,
    Locations,
    Mode,
    Plane,
    Pos,
    Rectangle,
    Vector,
    extrude,
    fillet,
    mirror,
)

from cad_models.common import Model, filter_by_edge_length, main


class Test(Model):
    def __init__(self, **kwargs):
        # parameters
        lip_thickness = 2.0 * MM
        rpi_power_cable_diameter = 4.1 * MM
        rpi_power_cable_slot_width = 3.6 * MM
        rpi_power_cable_slot_corner_radius = 0.75 * MM
        rpi_dimensions = Vector(71 * MM, 35 * MM, 101 * MM)
        rpi_magnet_dimensions = Vector(6.5 * MM, 3 * MM)
        rpi_magnet_offset = 0.25 * MM
        rpi_magnet_standoff_corner_radius = 2.0 * MM
        rpi_magnet_standoff_dimensions = Vector(9.5 * MM, 10 * MM, 5 * MM)
        rpi_power_switch_dimensions = Vector(62.5 * MM, 19.6 * MM)
        rpi_power_switch_inset = 3.5
        rpi_power_switch_spacing = 5 * MM
        tray_thickness = 4.0 * MM

        with BuildPart() as builder:
            # create tray
            with BuildSketch(Plane.XZ):
                width = (
                    lip_thickness
                    + rpi_magnet_standoff_dimensions.X
                    + rpi_dimensions.X
                    + rpi_magnet_standoff_dimensions.X
                    + lip_thickness
                )
                depth = (
                    lip_thickness
                    + rpi_power_switch_dimensions.Y
                    + rpi_power_switch_spacing
                    + rpi_dimensions.Z
                    + lip_thickness
                )
                thickness = tray_thickness + lip_thickness
                Rectangle(width, thickness, align=(Align.CENTER, Align.MAX))
            extrude(amount=depth)

            # create rpi mount
            face = builder.part.faces().filter_by(Axis.Z).sort_by(Axis.Z)[1]
            tray_face = face
            with BuildSketch(face):
                location = Location((0, -face.width / 2))
                location *= Pos(Y=rpi_power_switch_dimensions.Y)
                location *= Pos(Y=rpi_power_switch_spacing)
                location *= Pos(Y=rpi_dimensions.Z / 2)
                with Locations(location) as locs:
                    rpi_mount_local_location = locs.local_locations[0]
                    Rectangle(
                        rpi_dimensions.X,
                        rpi_dimensions.Z,
                    )
            rpi_mount = extrude(amount=-lip_thickness, mode=Mode.SUBTRACT)

            # create magnet standoffs
            face = tray_face
            with BuildSketch(face):
                location = rpi_mount_local_location
                location *= Pos(X=-rpi_dimensions.X / 2)
                location *= Pos(X=-rpi_magnet_standoff_dimensions.X / 2)
                with Locations(location):
                    Rectangle(
                        rpi_magnet_standoff_dimensions.X,
                        rpi_magnet_standoff_dimensions.Y,
                    )
            solid = extrude(amount=rpi_magnet_standoff_dimensions.Z)
            edges = solid.edges().filter_by(Axis.Z).group_by(Axis.X)
            rpi_magnet_standoff_fillet_edges = edges[0]
            face = rpi_mount.faces().sort_by(Axis.X)[0]
            mirror_plane = Plane(face).offset(-rpi_dimensions.X / 2)
            face = solid.faces().filter_by(Axis.Z).sort_by(Axis.Z)[-1]
            solid = mirror(solid, mirror_plane)
            edges = solid.edges().filter_by(Axis.Z).group_by(Axis.X)
            rpi_magnet_standoff_fillet_edges.extend(edges[-1])
            with BuildSketch(face):
                location = Location((0, 0))
                location *= Pos(X=rpi_magnet_offset)
                with Locations(location):
                    Circle(rpi_magnet_dimensions.X / 2)
            solid = extrude(amount=-rpi_magnet_dimensions.Y, mode=Mode.SUBTRACT)
            mirror(solid, mirror_plane, mode=Mode.SUBTRACT)

            # create power switch mount
            height = lip_thickness + rpi_power_cable_diameter
            face = tray_face
            with BuildSketch(face):
                location = Location((0, -face.width / 2))
                location *= Pos(Y=lip_thickness)
                location *= Pos(Y=rpi_power_switch_dimensions.Y / 2)
                with Locations(location) as locs:
                    width = rpi_power_switch_dimensions.X + lip_thickness
                    length = rpi_power_switch_dimensions.Y + lip_thickness
                    Rectangle(width, length)
            solid = extrude(amount=height)
            face = solid.faces().filter_by(Axis.Z).sort_by(Axis.Z)[-1]
            depth = height + rpi_power_switch_inset
            with BuildSketch(face):
                Rectangle(rpi_power_switch_dimensions.X, rpi_power_switch_dimensions.Y)
            solid = extrude(amount=-depth, mode=Mode.SUBTRACT)
            face = solid.faces().filter_by(Axis.X).sort_by(Axis.X)[0]
            with BuildSketch(face):
                location = Location((0, -face.width / 2))
                location *= Pos(Y=lip_thickness)
                location *= Pos(Y=rpi_power_cable_diameter / 2)
                with Locations(location):
                    Circle(rpi_power_cable_diameter / 2)
                location = Location((0, -face.width / 2))
                slot_height = lip_thickness + rpi_power_cable_diameter / 2
                with Locations(location):
                    Rectangle(
                        rpi_power_cable_slot_width,
                        slot_height,
                        align=(Align.CENTER, Align.MIN),
                    )
            solid = extrude(amount=lip_thickness, mode=Mode.SUBTRACT)
            mirror_plane = Plane(face).offset(-rpi_power_switch_dimensions.X / 2)
            mirror(solid, mirror_plane, mode=Mode.SUBTRACT)
            edge_length = lip_thickness / 2
            rpi_power_switch_slot_fillet_edges = (
                builder.edges()
                .filter_by(Axis.X)
                .filter_by(filter_by_edge_length(edge_length))
                .group_by(Axis.Z)
            )[2]

            # fillet edges
            fillet(rpi_magnet_standoff_fillet_edges, rpi_magnet_standoff_corner_radius)
            fillet(
                rpi_power_switch_slot_fillet_edges, rpi_power_cable_slot_corner_radius
            )
        super().__init__(builder.part, **kwargs)


if __name__ == "__main__":
    main(Test())
